# Channel Circuit Paper Lab

A Python/Tkinter app for single-cell models on macOS. See `PAPER_MAC_SETUP.md` for installation and launch instructions.

## Models

- E: Tatsuki AN, Sato NAN, Sato FNAN, Yoshida SAN.
- I: Tatsuki AN or Yamada RAN. The I assignment is a research choice, not a cell-type-specific fit.

The Values and bounds tab displays representative parameters and editable search domains. The Equations tab groups currents and gates by channel. The Channels tab lets you turn individual conductances off (g=0) for baseline traces and searches. Re-enabling a channel restores its edited representative value.

The **Build model** tab assembles a custom single-cell model from any channel in the included paper models, including those in FNAN. Select a row, choose a parameter source, and add, change or remove the channel. The source supplies its representative conductance and default range; the Values and bounds tab can then edit them. The custom model sums the selected currents and records its configuration with every run. It is a new exploratory combination, not a fitted or published cell model. Changing modules resets queued searches; custom sweeps use edited bounds.

## Hand-entered current equations

The **Custom equations** tab adds experimental current modules to the selected cell. **New current** opens a form for the current-density expression (µA/cm²), variables, parameters and optional Na/Ca concentration rates. Choose **instant** for an algebraic value evaluated at each time step. An **ode** variable requires an initial value and one of two forms: **relaxation** interprets the entered expression as a target and computes `d(h)/dt = (target - h) / tau`, where `tau` is an entered expression in ms; **derivative** interprets the entered expression literally as `d(h)/dt`. Earlier saved JSON definitions without an ODE form retain their literal derivative meaning. A module can refer to the selected model's existing parameters and constants (including `x` and `y` where defined). New parameters have editable baseline values and search ranges and can be combined with paper-model parameters in random or sweep searches. Multiple modules can be edited and saved/loaded as JSON. The equations display shows the evaluated derivative, and the output configuration includes the entered definitions.

Use `*` for multiplication and parentheses for grouping; `^` means exponentiation. Allowed functions include `exp`, `log`, `sqrt`, `sigmoid`, `min` and `max`; mathematical conditionals such as `a if V < -40 else b` are supported. The editor checks symbols and instantaneous dependency cycles before running. Each current contributes `-I/C` to `dV/dt`; optional extra concentration rates are entered in mM/ms for Na and µM/ms for Ca. The base cell must contain the corresponding ion state. The expression engine supports algebraic expressions and ODEs; delay equations, stochastic channels and spatial PDEs need separate solver support. User-entered equations are experimental definitions, not claims about the papers.

## Joint search

Each parameter starts with 100 draws / levels. Enter a number in **All draws / levels** and click **Apply to all** to update every parameter and queued group at once. Individual counts remain editable. For two parameters at 100 each, random computes 100 conditions and sweep computes 100 × 100 = 10,000 conditions. For four parameters:

- **random**: independently draw 100 values from each parameter's range and pair them into 100 joint conditions, such as `(a2, b3, c12, d5)`. All selected parameters must have the same draw count. Log / neglog distributions draw uniformly in log magnitude; uniform distributions draw linearly.
- **sweep**: evaluate the entire Cartesian product. Four axes at 100 levels each would require 100,000,000 conditions, above the app's 2,000,000-condition limit. Reduce the levels for large sweeps; the condition count appears before running.

The app records one-based candidate indices, actual parameter values, disabled channels and an automatically generated sampling seed in the result CSV and JSON. An off channel cannot be selected as a search axis. It detects the Mac's logical CPUs and lets you choose the number of worker processes. The progress bar tracks simulated time for a single trace or completed joint conditions for a search.

Search defaults include Sato intrinsic conductances at 0.01–100 mS/cm² and synaptic conductances at 0.001–10 µS. Every model's domains are visible in the app.

Every model simulates 20 s and classifies only the last 10 s. Outputs include `summary.csv`, `search_config.json`, vector `trace.pdf` plots using Arial on macOS, and compressed state arrays. Automatic SWO candidates require visual review.

This release runs single-cell searches; it does not simulate an E–I network. See `PAPER_PROVENANCE.md` for sources and validation scope.
