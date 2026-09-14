# Plot a solar dynamic spectrum

This example plots 30 seconds from an archived solar observation: August 20,
2026, 01:12:15–01:12:45 UTC, or August 19, 18:12:15–18:12:45 PDT at OVRO.
It uses a single-beam filterbank, not visibilities.

## Extract a short interval

Run in `casm_offline_env`. The reader seeks directly to the selected samples,
so this example reads about 352 MB rather than the full 77 GB file. The sample
numbers below select this particular observation's 30-second window.

```python
from casm_io.filterbank.split import split_filterbank
from casm_vis_analysis.solar_waterfall import plot_waterfall

cutout = "solar_IB_20260820_011215.fil"
split_filterbank(
    "/mnt/nvme5/solar0819/solartrack_fil/ib_IB.fil",
    cutout, start_sample=2667427, nsamples=28610,
)
```

This creates a new filterbank with its start time adjusted automatically. The
original file is unchanged. Do not RFI-clean solar filterbanks before plotting:
those filters can remove the broadband, time-variable signal being studied.

## Make the plot

```python
plot_waterfall(
    cutout, "solar-waterfall.png",
    beam="IB", tfac=48, tz="America/Los_Angeles", cmap="inferno",
)
```

`tfac=48` averages 48 input samples per time bin, about 50 ms here. The output
below was regenerated with these calls using the current installed modules.

```{figure} ../_static/tutorials/solar/solar-waterfall.webp
:alt: Incoherent-beam solar dynamic spectrum, mean bandpass and channel light curves around 18:12:30 PDT on August 19 2026.

Archived solar radio burst in the incoherent beam, August 19, 2026, local time
(August 20 UTC). Frequency increases upward. The figure is historical data
rendered with the current module, not a live observation.
```

[Full-resolution PNG](../_static/tutorials/solar/solar-waterfall.png).

Read the three panels together:

- **Top:** each frequency channel divided by its mean over this interval.
  Colour shows relative changes with time, not calibrated brightness.
- **Middle:** the original mean bandpass. Narrow peaks help locate persistent
  interference that normalization can hide.
- **Bottom:** selected channel light curves and the full-band mean.
  The broadband rise near 18:12:30 appears across several frequencies.

The burst contributes to the normalization mean, so the quiet intervals sit
below one. Changing the plotted interval changes that reference level. The
waterfall clips its colour scale at the fifth and ninety-fifth percentiles;
use the light curves to inspect peak amplitude.

Solar identification for this archived event also used independent observations.
A bright feature alone does not establish solar origin or an instrumental fault.

For another existing filterbank, `plot_waterfall` reads its entire duration.
Extract a short interval first for a quick look. For solar visibility phase,
continue to [the phase tutorial](solar-phase.md).

## Use the same style with prepared visibility amplitudes

The monitor uses `plot_dynamic_spectrum` from the same module for a bounded
array already loaded from its visibility cache. It accepts real nonnegative
`(time, frequency)` samples, Unix bin-centre timestamps and monotonic frequency
centres in MHz. It does not read data or identify the signal as solar.

```python
from casm_vis_analysis.solar_waterfall import plot_dynamic_spectrum

# amplitude and axes come from a selected, documented visibility baseline.
figure = plot_dynamic_spectrum(
    amplitude, time_unix, freq_mhz,
    title="CASM correlated amplitude: selected baseline",
    quantity="Correlated amplitude", integration_s=integration_seconds,
)
```

This is an API example with prepared-array placeholders, not the recipe for
the archived filterbank figure above. The renderer leaves missing integrations
and invalid channels as gaps. Its interval-dependent normalization is shared
with `plot_waterfall`; a zero channel mean is masked. With no output path it
returns a Figure, otherwise it saves and closes the figure and returns the path.

A visibility magnitude is correlated amplitude in instrumental units, not a
recorded beam-power stream or calibrated solar flux. At correlator cadence it
cannot resolve the short burst structure in the historical filterbank example.
The [monitoring guide](monitoring.md) describes the preview's selection and
provenance.

[Source, data, and verification notes](../developer/solar-example-notes.md).
