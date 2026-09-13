# Solar waterfall

The existing `casm-solar-waterfall` command creates the team's three-panel
scientific figure: normalized dynamic spectrum, raw bandpass, and selected
channel light curves. It belongs to `casm_vis_analysis`.

## Current input contract

`plot_waterfall` currently takes a **single-beam SIGPROC filterbank path**.
It does not accept a visibility array. The first monitor redesign is intended
to use visibilities; adapting this presentation to that input is future work.
There is no new fast-beam recording workflow in this documentation preview.

## Existing filterbank usage

Illustrative invocation for an already available file:

```bash
python -m casm_vis_analysis.solar_waterfall /path/to/solar.fil \
  --out-dir /path/to/figures --beam IB --tz America/Los_Angeles
```

This writes a figure. It does not request a recording or change telescope state.
Use the [generated reference](../packages/vis-analysis-api.md) for the exact
function signature in the inspected revision.

## Reading the figure

The implementation time-averages the data, computes the temporal mean of each
channel, and divides each channel by that bandpass. The waterfall display uses
the fifth and ninety-fifth percentiles for its colour limits. The raw bandpass
is plotted on a logarithmic power axis; the lower panel includes selected
channels and the mean normalized power.

This normalization emphasizes variability. It does not create an absolute
flux scale, and its denominator must be suitable for the input quantity.
Signed or near-zero visibility-derived estimates require separate treatment.
The current renderer's percentile clipping is a display choice, not data deletion.

## Scientific cautions

Solar variability is part of the signal. Do not apply a generic transient/RFI
cleaner that removes broadband temporal structure before producing a solar
diagnostic. Compare on-source and control measurements where available, keeping
the response geometry and data coverage explicit.

A visibility-based view must state its integration time. A roughly 137-second
integration cannot reveal millisecond structure. Gaps and stale products should
remain visible, including when the Sun is below the useful observing range.

The canonical operational procedure is linked from [the wiki](../knowledge.md).
