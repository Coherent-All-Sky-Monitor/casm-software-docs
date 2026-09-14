# Plot a solar dynamic spectrum

This example plots 30 seconds from an archived solar observation: August 20,
2026, 01:12:15–01:12:45 UTC, or August 19, 18:12:15–18:12:45 PDT at OVRO.
It uses a single-beam filterbank, not visibilities. On a new day, make that
filterbank first: [convert a beam dump to a
filterbank](beamdump-to-filterbank.md).

## Extract a short interval

Run in `casm_offline_env`. The reader seeks directly to the selected samples,
so this example reads about 352 MB rather than the full 77 GB file. Compute the
sample numbers from the header rather than copying them: `tstart` is the MJD of
sample 0 and `tsamp` the sample interval in seconds.

```python
from astropy.time import Time
from casm_io.filterbank.header import read_sigproc_header

fil = "/mnt/nvme5/solar0819/solartrack_fil/ib_IB.fil"
header, _ = read_sigproc_header(fil)
t_utc = Time("2026-08-20T01:12:15", format="isot", scale="utc")
start_sample = round((t_utc.mjd - header["tstart"]) * 86400.0 / header["tsamp"])
nsamples = round(30.0 / header["tsamp"])   # 30 s window
print(start_sample, nsamples)              # 2667427 28610
```

```python
from casm_io.filterbank.split import split_filterbank
from casm_vis_analysis.solar_waterfall import plot_waterfall

cutout = "solar_IB_20260820_011215.fil"
split_filterbank(fil, cutout, start_sample=start_sample, nsamples=nsamples)
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

The same plot from the shell, one filterbank per run:

```bash
python -m casm_vis_analysis.solar_waterfall solar_IB_20260820_011215.fil \
  --out-dir . --beam IB --tfac 48 --tz America/Los_Angeles --cmap inferno
```

`--chans I,J,K,L` picks the light-curve channels, `--role` appends a label such
as `Null` to the title, and `--out-name` sets the PNG basename. The
`casm-solar-waterfall` console script declared by `casm_vis_analysis` calls the
same entry point; it is absent from the installed `casm_offline_env`, so use
the module form there.

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

## Provenance

Data: `/mnt/nvme5/solar0819/solartrack_fil/ib_IB.fil` (header `tstart=61272.01780093231`,
`tsamp=0.001048576` s, `nbeams=1`). `start_sample=2667427` selects
2026-08-20 01:12:15 UTC; `nsamples=28610` covers the 30-second window. Solar
identification for this event is independent of this plot: see casm-wiki
`solar-burst-2026-08-20.md`.
