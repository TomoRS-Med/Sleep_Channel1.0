# Run Channel Circuit Paper Lab on a Mac

1. Extract the ZIP. If Python 3.11 or later with Tkinter is missing, install the [python.org macOS universal2 build](https://www.python.org/downloads/macos/).
2. Double-click `Build Paper Search.command`. The first run installs dependencies, builds `dist/ChannelCircuitPaperLab.app`, and opens it.
3. On later runs, double-click the `.app` in `dist`.

The builder selects a Python interpreter compatible with the Mac's CPU. If it reports that Python/Tkinter is unavailable, reopen Terminal after installation and run the `.command` again.

Select E or I and a model at the top. Tatsuki AN is available for both roles. The Values and bounds tab edits representative values and constants. The Channels tab has an on/off switch for each conductance; switching one off applies g=0 to traces and searches. The Equations tab groups membrane, concentration, current and gate equations by channel and marks off currents.

To run a joint search:

1. Select any channel switches first. Switching off a channel removes searches that vary it. In Combinations and run, select multiple parameter rows. Use Command-click for nonadjacent rows.
2. Double-click a row to edit its range, distribution and draw / sweep-level count. The default is 24 per parameter.
3. Choose **random** for 24 independent paired draws from the ranges (equal counts required), or **sweep** for the full Cartesian product of levels. Two parameters at 24 each make 24 random conditions or 576 sweep conditions. Four axes at 24 each make 24 random conditions or 331,776 sweep conditions. Sweep can use displayed absolute bounds or the paper's baseline-relative range.
4. Add the search, choose worker processes and an output folder, then click Run search.

The progress bar and count show completed conditions. Stop retains completed CSV rows. The results list shows candidate indices such as `gKNa2, tauNa3`; select a row to inspect its plot or compute its trace. Review every automatic SWO candidate visually.

Only single cells are simulated in this release. The I model assignment is a research assumption.
