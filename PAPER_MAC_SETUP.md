# Run Channel Circuit Paper Lab on a Mac

1. Extract the ZIP. If Python 3.11 or later with Tkinter is missing, install the [python.org macOS universal2 build](https://www.python.org/downloads/macos/).
2. Double-click `Build Paper Search.command`. The first run installs dependencies, builds `dist/ChannelCircuitPaperLab.app`, and opens it.
3. On later runs, double-click the `.app` in `dist`.

The builder selects a Python interpreter compatible with the Mac's CPU. If it reports that Python/Tkinter is unavailable, reopen Terminal after installation and run the `.command` again.

Select E or I and a model at the top. Tatsuki AN is available for both roles. The Values and bounds tab edits representative values and constants. The Channels tab has an on/off switch for each conductance; switching one off applies g=0 to traces and searches. The Equations tab groups membrane, concentration, current and gate equations by channel and marks off currents.

To build a custom single-cell model, open **Build model**. Select a channel row, choose the paper model supplying its starting value and range, then click **Add / change selected**. Use **Remove selected** to exclude a current. All included models' channel types are listed, including FNAN channels. The equations view updates with the assembled model. The output records the selected modules. A custom assembly is exploratory; use edited bounds for sweeps. **Restore published model** returns to the selected paper model.

To enter a new current, open **Custom equations** and click **New current**. Enter the current density, then add each gate with **instant** or **ode** kinetics. ODE gates need an initial value. Add parameters with baseline values and ranges; existing model parameters can be referenced in equations. Enter additional Na/Ca concentration rates if required by the current, then click **Validate and save module**. The new parameters appear in the search table. Save or load definitions with the JSON buttons on that tab. The base model and any custom equations appear in the Equations tab.

To run a joint search:

1. Select any channel switches first. Switching off a channel removes searches that vary it. In Combinations and run, select multiple parameter rows. Use Command-click for nonadjacent rows.
2. Double-click a row to edit its range, distribution and draw / sweep-level count. The default is 100 per parameter. To set them all at once, type a number in **All draws / levels** and click **Apply to all**.
3. Choose **random** for 100 independent paired draws from the ranges (equal counts required), or **sweep** for the full Cartesian product of levels. Two parameters at 100 each make 100 random conditions or 10,000 sweep conditions. The app limits each search to 2,000,000 conditions. Sweeps containing a custom parameter use edited bounds.
4. Add the search, choose worker processes and an output folder, then click Run search.

The progress bar and count show completed conditions. Stop retains completed CSV rows. The results list shows candidate indices such as `gKNa2, tauNa3`; select a row to inspect its PDF plot or compute its trace. Plots are saved as `trace.pdf` with Arial text on macOS. All simulations run for 20 s; classification uses the final 10 s. Review every automatic SWO candidate visually.

Only single cells are simulated in this release. The I model assignment is a research assumption.
