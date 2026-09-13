# Plot a solar dynamic spectrum

Turn an existing **single-beam filterbank** into a waterfall, bandpass, and
light curves with the existing solar plotter. Run this in `casm_offline_env`:

```bash
python -m casm_vis_analysis.solar_waterfall /path/to/solar_IB.fil \
  --out-dir /path/to/figures --out-name solar-waterfall.png \
  --beam IB --tz America/Los_Angeles --cmap viridis
```

The command writes one PNG. Replace the paths with your input and output
locations; no new recording is requested. Here is an existing output from the
August 18 solar campaign:

```{figure} ../_static/tutorials/solar/solar-waterfall.png
:alt: Solar campaign incoherent-beam waterfall with frequency bandpass and channel light curves, August 18 2026.

Recorded incoherent-beam power. Frequency increases upward; the time axes use
OVRO local time. This is a saved historical example, not live data.
```

Read the three panels together:

- **Top:** each frequency channel divided by its mean over the plotted interval.
  Colour reveals changes with time, not absolute brightness.
- **Middle:** the original mean bandpass. Narrow peaks help locate persistent
  interference that normalization can hide.
- **Bottom:** selected channel light curves and the average normalized power.
  Compare a feature's timing across frequencies.

The Sun varies, and an incoherent beam also contains other sky and instrumental
signals. A bright feature alone does not identify a solar burst or an array fault.
The historical plot uses `viridis`; the current plotter's default is `inferno`.

For Python, the same renderer is
`casm_vis_analysis.solar_waterfall.plot_waterfall(path, out_path, beam="IB")`.
It currently accepts a filterbank path, **not visibilities**. To inspect solar
visibility phase, use [the phase tutorial](solar-phase.md).

[Source, data, and verification notes](../developer/solar-example-notes.md).
