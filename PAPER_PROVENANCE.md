# Model sources and validation scope

| Model | Equations | Representative values | Default search domains |
|---|---|---|---|
| Tatsuki AN | Tatsuki et al., 2016, Supplemental Procedures | Tatsuki et al., 2016, Table S1 | Intrinsic g 0.01–100 mS/cm²; synaptic g 0.002–20 µS; τCa 10–1000 ms |
| Yamada RAN | Yamada et al., 2022, STAR Methods | Yamada et al., 2022, Table S2, Figure 2A | Intrinsic g 0.01–100 mS/cm²; τCa 10–1000 ms |
| Yoshida SAN | Yoshida et al., 2018; Yamada et al., 2022, STAR Methods | Yamada et al., 2022, Table S2, Figure S2E | Intrinsic g 0.01–100 mS/cm²; τCa 10–1000 ms |
| Sato NAN / FNAN | Sato et al., 2025, STAR Methods | Sato et al., 2025, Tables S1 / S3 | Intrinsic g 0.01–100 mS/cm²; synaptic g 0.001–10 µS; τNa 1000–10000 ms; τCa 10–1000 ms; x/y −45–45 mV |

Sweep levels use geometric spacing for positive ranges and linear spacing for signed voltage shifts. A search group stores its parameter names, draw or sweep-level counts, ranges and mode. Random mode samples continuous values independently within each parameter's bounds and pairs them into one condition per draw; each parameter needs the same draw count. Sweep mode enumerates the entire Cartesian product of its levels. Thus two parameters with 24 draws or levels each produce 24 random conditions or 576 sweep conditions. Random draw indices are one-based in `summary.csv`; the seed and configuration allow exact replay. Turning off a listed channel sets its conductance to zero as an experimental knockout; the disabled names and effective zero values are saved with each run. The published representative values remain available in the model catalog.

The simulation runs for 10 s and analyzes the last 5 s for Tatsuki, Yamada and Yoshida, or 20 s and the last 10 s for Sato. The recorded time step is 1 ms. The automatic classifier follows Sato et al., 2025: −20 mV crossings, an FFT peak, RESTING below 2 spikes/s, AWAKE at a peak of at least 10 Hz, and a SWO candidate when spikes/s exceeds five times a positive peak below 10 Hz. Visual waveform review is required for SWO candidates.

Representative traces have not been verified for numerical identity with published figures. E/I labels in the app designate research assignments; the program does not fit inhibitory-cell physiology or implement network connections.
