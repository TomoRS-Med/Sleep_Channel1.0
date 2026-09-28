# Channel Circuit Paper Lab

A Python/Tkinter app for single-cell models on macOS. See `PAPER_MAC_SETUP.md` for installation and launch instructions.

## Models

- E: Tatsuki AN, Sato NAN, Sato FNAN, Yoshida SAN.
- I: Tatsuki AN or Yamada RAN. The I assignment is a research choice, not a cell-type-specific fit.

The Values and bounds tab displays representative parameters and editable search domains. The Equations tab groups currents and gates by channel. The Channels tab lets you turn individual conductances off (g=0) for baseline traces and searches. Re-enabling a channel restores its edited representative value.

## Joint search

Each selected parameter has its own range, distribution and draw / sweep-level count (24 by default). For two parameters with counts of 24 each, random computes 24 conditions and sweep computes 24 × 24 = 576 conditions. For four parameters:

- **random**: independently draw 24 values from each parameter's range and pair them into 24 joint conditions, such as `(a2, b3, c12, d5)`. All selected parameters must have the same draw count. Log / neglog distributions draw uniformly in log magnitude; uniform distributions draw linearly. The total is 24 conditions for any number of selected parameters with 24 draws each.
- **sweep**: evaluate the entire Cartesian product, `24 × 24 × 24 × 24 = 331,776` conditions. The condition count appears before running.

The app records one-based candidate indices, actual parameter values, disabled channels and an automatically generated sampling seed in the result CSV and JSON. An off channel cannot be selected as a search axis. It detects the Mac's logical CPUs and lets you choose the number of worker processes. The progress bar tracks simulated time for a single trace or completed joint conditions for a search.

Search defaults include Sato intrinsic conductances at 0.01–100 mS/cm² and synaptic conductances at 0.001–10 µS. Every model's domains are visible in the app.

Outputs include `summary.csv`, `search_config.json`, candidate plots and compressed state arrays. Automatic SWO candidates require visual review.

This release runs single-cell searches. It does not simulate an E–I network or provide a GUI for adding arbitrary new equations. See `PAPER_PROVENANCE.md` for sources and validation scope.
