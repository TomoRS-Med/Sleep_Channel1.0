"""Reference-figure behavior and parallel-search integration checks."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_catalog import (CELL_ROLE_MODELS, available_channels, get_model,
                           validate_assignment)
from paper_engine import classify, save_result, simulate
from paper_formulas import equations_for
from paper_search import candidate_parameters, choice_indices, group_total, run_search


class PaperModels(unittest.TestCase):
    def test_sato_domains_and_cell_assignment(self):
        nan = get_model("Sato 2025 NAN")
        fnan = get_model("Sato 2025 FNAN")
        self.assertEqual(nan["ranges"]["gK"][:2], (.01, 100.0))
        self.assertEqual(fnan["ranges"]["gLeak"][:2], (.01, 100.0))
        self.assertEqual(fnan["ranges"]["gAMPA"][:2], (.001, 10.0))
        self.assertEqual(fnan["ranges"]["gNMDA"][:2], (.001, 10.0))
        self.assertEqual(fnan["ranges"]["gGABA"][:2], (.001, 10.0))
        self.assertNotIn("SST", CELL_ROLE_MODELS)
        self.assertEqual(set(CELL_ROLE_MODELS["I"]),
                         {"Tatsuki 2016 AN", "Yamada 2022 RAN"})
        self.assertEqual({get_model(m)["family"] for m in CELL_ROLE_MODELS["I"]},
                         {"AN", "RAN"})
        self.assertEqual({get_model(m)["family"] for m in CELL_ROLE_MODELS["E"]},
                         {"AN", "NAN", "FNAN", "SAN"})
        self.assertIn("Tatsuki 2016 AN", CELL_ROLE_MODELS["E"])
        validate_assignment("E", "Tatsuki 2016 AN")
        for model in CELL_ROLE_MODELS["I"]:
            validate_assignment("I", model)
        with self.assertRaises(ValueError):
            validate_assignment("I", "Sato 2025 NAN")

    def test_published_representatives_have_expected_timescales(self):
        for name, ion, lo, hi in (
            ("Tatsuki 2016 AN", "Ca_uM", 1, 15),
            ("Sato 2025 NAN", "Na_mM", 4, 10),
            ("Sato 2025 FNAN", "Na_mM", 3, 10),
        ):
            with self.subTest(model=name):
                result = simulate(name)
                metric = classify(result)
                self.assertTrue(.2 < metric["peak_hz"] < 4, metric)
                active = result["time_ms"] >= result["analysis_from_ms"]
                value = result["states"][active, result["state_names"].index(ion)]
                self.assertTrue(lo < value.mean() < hi)
                self.assertGreater(np.ptp(result["states"][active, 0]), 80)
                if name == "Sato 2025 FNAN":
                    self.assertIn("Ca_uM", result["state_names"])
                    self.assertIn("tauCa", result["parameters"])
                    self.assertIn("tauNa", result["parameters"])

    def test_added_equations_run_and_wave_progress_reaches_end(self):
        for role in CELL_ROLE_MODELS:
            for name in CELL_ROLE_MODELS[role]:
                if name in ("Tatsuki 2016 AN", "Sato 2025 NAN", "Sato 2025 FNAN"):
                    continue
                with self.subTest(name=name):
                    steps = []
                    result = simulate(name, progress=lambda n, total: steps.append((n, total)))
                    self.assertTrue(np.all(np.isfinite(result["states"])))
                    self.assertEqual(steps[-1], (len(result["time_ms"])-1, len(result["time_ms"])-1))
                    self.assertGreater(len(steps), 1)
                    self.assertIn("dV/dt", equations_for(name))
                    self.assertEqual(result["states"].shape[1], len(result["state_names"]))

    def test_bifurcation_sweep_uses_paper_relative_values(self):
        for name, key, factor, last_factor in (("Tatsuki 2016 AN", "tauCa", .001, 10),
                                               ("Sato 2025 FNAN", "tauNa", .01, 100)):
            spec = get_model(name)
            group = {"name": "sensitivity", "kind": "sweep", "samples": 3,
                     "parameters": [key], "basis": "paper"}
            first = candidate_parameters(name, spec["ranges"], group, 0, 1, 0)
            last = candidate_parameters(name, spec["ranges"], group, 2, 1, 0)
            self.assertAlmostEqual(first[key], factor*spec["parameters"][key])
            self.assertAlmostEqual(last[key], last_factor*spec["parameters"][key])
        name = "Sato 2025 NAN"
        spec = get_model(name)
        group = {"name": "shift", "kind": "sweep", "samples": 3,
                 "parameters": ["x"], "basis": "paper"}
        first = candidate_parameters(name, spec["ranges"], group, 0, 1, 0)
        self.assertAlmostEqual(first["x"], spec["parameters"]["x"]-45)

    def test_parallel_search_records_seed_and_replayable_values(self):
        name = "Sato 2025 NAN"
        ranges = get_model(name)["ranges"]
        group = {"name": "KNa_tau", "kind": "random", "samples": 2,
                 "parameters": ["gKNa", "tauNa"]}
        with tempfile.TemporaryDirectory() as directory:
            rows = run_search(name, ranges, [group], directory, workers=2,
                              master_seed=81235, retain=(),
                              fixed_overrides={**get_model(name)["fixed"], "C": 1.2})
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(row["label"] != "ERROR" for row in rows), rows)
            config = json.loads((Path(directory)/"search_config.json").read_text())
            self.assertEqual(config["workers_used"], 2)
            self.assertEqual(config["master_seed"], 81235)
            self.assertEqual(config["fixed_values"]["C"], 1.2)
            self.assertEqual(config["published_fixed"]["C"], 1.0)
            self.assertEqual(config["default_ranges"]["gK"][:2], [.01, 100.0])
            self.assertTrue(all(row["cell_role"] == "E" for row in rows))
            with (Path(directory)/"summary.csv").open(newline="") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 2)
            for row in rows:
                replay = candidate_parameters(name, ranges, group, row["index"], 81235, 0)
                self.assertEqual(row["gKNa"], replay["gKNa"])
                self.assertEqual(row["tauNa"], replay["tauNa"])

    def test_random_paired_draws_and_cartesian_sweep(self):
        model = "Sato 2025 NAN"
        ranges = get_model(model)["ranges"]
        keys = ["gKNa", "tauNa", "gCa", "x"]
        group = {"name": "four_axis_random", "kind": "random", "samples": 24,
                 "parameters": keys, "points": dict.fromkeys(keys, 24)}
        self.assertEqual(group_total(group), 24)
        choices = [choice_indices(group, i, 416, 0) for i in range(24)]
        for key in keys:
            self.assertEqual({row[key] for row in choices}, set(range(24)))
        self.assertTrue(any(tuple(row.values()) != (i,)*4 for i, row in enumerate(choices)))
        draws = [candidate_parameters(model, ranges, group, i, 416, 0) for i in range(24)]
        for key in keys:
            low, high, distribution, _ = ranges[key]
            values = [row[key] for row in draws]
            self.assertEqual(len(set(values)), 24)
            self.assertTrue(all(low <= value <= high for value in values))
            levels = (np.geomspace(low, high, 24) if distribution == "log" else
                      np.linspace(low, high, 24))
            self.assertFalse(np.allclose(sorted(values), sorted(levels), rtol=1e-8, atol=1e-8))
        first, labels = candidate_parameters(model, ranges, group, 0, 416, 0,
                                              return_indices=True)
        self.assertEqual({k: v+1 for k, v in choices[0].items()}, labels)
        self.assertEqual(first, candidate_parameters(model, ranges, group, 0, 416, 0))
        self.assertNotEqual(first[keys[0]], candidate_parameters(model, ranges, group, 0, 417, 0)[keys[0]])

        two_random = {**group, "parameters": keys[:2],
                      "points": dict.fromkeys(keys[:2], 24)}
        two_sweep = {**two_random, "kind": "sweep", "basis": "edited", "samples": 576}
        self.assertEqual(group_total(two_random), 24)
        self.assertEqual(group_total(two_sweep), 576)
        self.assertEqual(len({tuple(choice_indices(two_sweep, i, 0, 0).values())
                              for i in range(576)}), 576)
        with self.assertRaisesRegex(ValueError, "same draw count"):
            group_total({**two_random, "points": {keys[0]: 24, keys[1]: 12}})

        grid = {"name": "all_combinations", "kind": "sweep", "basis": "edited",
                "samples": 12, "parameters": keys[:3],
                "points": {keys[0]: 2, keys[1]: 3, keys[2]: 2}}
        self.assertEqual(group_total(grid), 12)
        tuples = {tuple(choice_indices(grid, i, 0, 0).values()) for i in range(12)}
        self.assertEqual(len(tuples), 12)
        self.assertIn((1, 2, 1), tuples)

    def test_multiaxis_sweep_runs_each_joint_condition_once(self):
        model = "Yoshida 2018 SAN"
        spec = get_model(model)
        group = {"name": "gL_gCa_grid", "kind": "sweep", "basis": "edited",
                 "samples": 6, "parameters": ["gL", "gCa"],
                 "points": {"gL": 2, "gCa": 3},
                 "ranges": {"gL": (.07, .08, "log", "mS/cm²"),
                            "gCa": (.08, .09, "log", "mS/cm²")}}
        progress = []
        with tempfile.TemporaryDirectory() as directory:
            rows = run_search(model, spec["ranges"], [group], directory,
                              workers=2, master_seed=3, retain=(),
                              progress=lambda n, total, row: progress.append((n, total)))
            self.assertEqual(len(rows), 6)
            self.assertEqual(progress[-1], (6, 6))
            self.assertEqual({row["choice_indices"] for row in rows},
                             {f"gL{i}, gCa{j}" for i in (1, 2) for j in (1, 2, 3)})
            self.assertTrue(all(row["label"] != "ERROR" for row in rows), rows)

    def test_channel_switches_apply_to_trace_and_search_outputs(self):
        model = "Tatsuki 2016 AN"
        spec = get_model(model)
        self.assertIn("gAMPA", available_channels(model))
        trace = simulate(model, disabled_channels=("gAMPA",))
        self.assertEqual(trace["parameters"]["gAMPA"], 0.0)
        self.assertGreater(spec["parameters"]["gAMPA"], 0.0)
        self.assertEqual(trace["disabled_channels"], ("gAMPA",))
        self.assertIn("gAMPA = 0", equations_for(model, ("gAMPA",)))
        with tempfile.TemporaryDirectory() as directory:
            save_result(trace, directory)
            config = json.loads((Path(directory)/"config_metrics.json").read_text())
            self.assertEqual(config["disabled_channels"], ["gAMPA"])

        group = {"name": "knockout", "kind": "sweep", "basis": "edited",
                 "samples": 1, "parameters": ["gK"]}
        with tempfile.TemporaryDirectory() as directory:
            rows = run_search(model, spec["ranges"], [group], directory,
                              workers=1, master_seed=12, retain=(), cell_role="E",
                              disabled_channels=("gAMPA",))
            self.assertEqual(rows[0]["gAMPA"], 0.0)
            self.assertNotEqual(rows[0]["label"], "ERROR")
            config = json.loads((Path(directory)/"search_config.json").read_text())
            self.assertEqual(config["disabled_channels"], ["gAMPA"])
            self.assertGreater(config["selected_baseline_before_channel_switches"]["gAMPA"], 0)
            with self.assertRaises(ValueError):
                run_search(model, spec["ranges"], [{**group, "parameters": ["gAMPA"]}],
                           Path(directory)/"invalid", workers=1, disabled_channels=("gAMPA",))
        with self.assertRaises(ValueError):
            simulate(model, disabled_channels=("tauCa",))

    def test_i_label_is_recorded_with_ran_search(self):
        model = "Yamada 2022 RAN"
        spec = get_model(model)
        ranges = spec["ranges"]
        gk = spec["parameters"]["gKS"]
        ranges["gKS"] = (gk, gk*1.01, "log", "mS/cm²")
        group = {"name": "i_gKS", "kind": "sweep", "basis": "edited",
                 "samples": 1, "parameters": ["gKS"]}
        with tempfile.TemporaryDirectory() as directory:
            rows = run_search(model, ranges, [group], directory,
                              workers=1, master_seed=4, retain=(), cell_role="I")
            self.assertEqual(rows[0]["cell_role"], "I")
            self.assertNotEqual(rows[0]["label"], "ERROR")
            config = json.loads((Path(directory)/"search_config.json").read_text())
            self.assertEqual(config["cell_role"], "I")
