# Imaging implementation notes and provenance

Use the existing CASM beam-power and imaging routines to sum calibrated
cross-correlations toward chosen directions. Start with a few integrations to
check coordinates, antenna membership and signs; a complete source transit is
a separate, larger experiment.

These blocks read existing data and calibration products. They do not generate
or upload beamformer weights. A runnable source-centred image with a real
calibration and window is in the
[imaging tutorial](../guides/image-visibilities.md).

## An existing observation: Cyg A through and after transit

These are preserved notebook outputs from the 2026-06-28 observation, not
outputs of the short example below. Both used a solar calibration, static
subtraction, bandpass normalization, the full band, 32-channel averaging,
20 antennas and 67 cross-baselines at least 5 m long. The historical notebook
contains the processing calls and executed output; its identity is recorded
below.

```{figure} ../_static/tutorials/imaging/cyga-transit-lm.png
:alt: Signed Cyg A dirty image during transit, with a central positive peak and alternating positive and negative sidelobes.

2026-06-28, 02:00–04:00 America/Los_Angeles. The positive peak is close to
the expected source at the origin. Alternating red and blue structure is the
signed dirty response of the sparse array. Cyan circles mark the background
annulus used for the displayed image statistic, not beam boundaries.
```

```{figure} ../_static/tutorials/imaging/cyga-post-transit-lm.png
:alt: Post-transit Cyg A dirty image, with broader stripe-like sidelobes and a larger background relative to the peak.

2026-06-28, 04:00–05:30 America/Los_Angeles. The same imaging recipe produces
a less concentrated response and stronger outer structure relative to the
peak. Each figure uses its own color scale; compare its labeled values before
comparing color intensity.
```

The displayed image statistic falls from 22.9 to 6.6. The integration durations,
projected geometry and normalization windows differ, so this pair does not
measure a change in array sensitivity or calibration quality. It demonstrates
why a source-tracking image must retain its observing window and why imaging
comparisons need a matched PSF. The calibration-transfer guide describes a
different experiment: a fixed beam through which Cyg A transits.

## What the two outputs measure

For `V_ij = <v_i conjugate(v_j)>`, a calibrated beam uses
`c_i conjugate(c_j) V_ij` and the geometric phasor for the chosen direction.
`beam_power_vs_time` returns twice the real cross-baseline sum, averaged over
selected frequencies, separately at every integration. Autos are omitted, so
negative values are possible. This is not total tied-array power or a flux in Jy.

`image_around_source(grid="lm", estimator="real")` evaluates a grid of
directions around a moving source and averages over time, frequency and
cross-baselines. Its signed dirty image includes negative sidelobes. It has a
different normalization from the beam-power series; their values are not
directly interchangeable. A magnitude image (`estimator="abs"`) changes the
statistic and removes the sign.

## 1. Select a small, fully described input

Activate the shared offline environment as in
[Read and inspect visibilities](../guides/read-visibilities.md). The imaging package is
`casm_imaging`, supplied by the existing `casm-bf-imaging` repository. Its
calibration loader comes from `bf_weights_generator`.

Run these blocks in order in a notebook. Choose a short Cyg A window with the
source above the horizon, an epoch-matched layout, and an existing calibration.
The five-minute limit bounds this first read; it does not cover a full transit.

```python
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

from casm_io.correlator import AntennaMapping, read_visibilities
from bf_weights_generator import load_calibration_weights
from casm_vis_analysis.sources import source_altaz

data_dir = Path(input("Visibility directory: ")).expanduser().resolve()
layout_csv = Path(input("Dated layout CSV: ")).expanduser().resolve()
cal_path = Path(input("Existing calibration HDF5: ")).expanduser().resolve()
time_start = input("Start UTC (YYYY-MM-DD HH:MM:SS): ")
time_end = input("End UTC (YYYY-MM-DD HH:MM:SS): ")
parse_utc = lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(
    tzinfo=timezone.utc
)
duration = (parse_utc(time_end) - parse_utc(time_start)).total_seconds()
if not 0 < duration <= 300:
    raise ValueError("Use a positive window of at most five minutes initially")
if not data_dir.is_dir() or not layout_csv.is_file() or not cal_path.is_file():
    raise ValueError("Input paths must exist")

mapping = AntennaMapping.load(str(layout_csv))
cal = load_calibration_weights(str(cal_path))
selected = {int(s) for s in input("Evaluation antenna IDs, comma separated: ").split(",")}
if len(selected) < 2 or not selected <= set(mapping.active_antennas()):
    raise ValueError("Choose at least two functional mapped antennas")
if not selected <= set(map(int, cal.ant_ids)):
    raise ValueError("Every evaluation antenna needs a calibration row")
ant = mapping.with_inactive(sorted(set(mapping.active_antennas()) - selected))

data = read_visibilities(
    data_dir=str(data_dir), time_start=time_start, time_end=time_end,
    time_tz="UTC", freq_order="descending", workers=1, verbose=True,
)
print("vis:", data.vis.shape, data.vis.dtype, "bytes:", data.vis.nbytes)
print("frequency:", data.freq_mhz.shape, "MHz")
print("time:", data.time_unix.shape, "Unix seconds UTC")
print("metadata:", data.metadata)
```

This particular consumer requires the full original correlator upper triangle,
`(T, F, N*(N+1)//2)`, including autos. Do not pass a reference-baseline read or
an `inputs=[...]` subset: `beam_power_vs_time` infers `N` from the last axis and
uses original packet indices, without a subset remapping. Restricting the
evaluation antenna list does not reduce the reader's full-triangle allocation.

`active_antennas()` follows the layout's `functional` column. It does not apply
`include_in_beamforming`. The explicit evaluation set above is deliberate;
record its scientific rationale and keep it identical across comparisons.

## 2. Check the contracts before applying calibration

Visibility frequencies are MHz; calibration frequencies are Hz. This guide
uses descending visibility channels because the beam-power implementation
reorients calibration weights to descending order. Its frequency-set comparison
alone does not protect an ascending visibility call.

```python
freq = np.asarray(data.freq_mhz)
times = np.asarray(data.time_unix)
if times.size == 0 or freq.size < 2 or not np.all(np.diff(freq) < 0):
    raise ValueError("Need nonempty data with descending frequency channels")
if np.any(np.diff(times) <= 0) or not np.isfinite(data.vis).all():
    raise ValueError("Inspect timestamp ordering or nonfinite visibilities")
cal_freq = np.sort(np.asarray(cal.frequencies_hz) / 1e6)[::-1]
if cal_freq.shape != freq.shape or not np.allclose(cal_freq, freq, rtol=0, atol=1e-6):
    raise ValueError("Calibration and visibility channel centers differ")
if not np.all(cal.flags) or not np.isfinite(cal.weights).all():
    raise ValueError("This initial full-band example needs valid finite cal channels")
alt, az = source_altaz("cyg-a", times)
if np.min(alt) <= 0:
    raise ValueError("Select a Cyg A window above the horizon")
print("Band:", freq[-1], freq[0], "MHz; Cyg A altitude:", alt.min(), alt.max())
```

Review gaps and missing-file warnings before continuing. Finite, zero-filled
samples can pass these numerical checks. Confirm the recording format from
its headers; headerless data require an explicitly verified `fmt`.

The calibration flag convention is `True = good`; visibility `freq_mask` uses
`True = bad`. The beam-power routine honours a supplied visibility mask but
does not consume calibration flags. The imaging wrapper does not apply
calibration flags either. This example therefore stops on bad calibration
channels instead of silently including them. An RFI-free calibration flag does
not certify that the evaluation observation is free of RFI.

## 3. Compare a tracked beam with a fixed direction

```python
from casm_vis_analysis.beam_power import beam_power_vs_time, plot_beam_power

mid = len(times) // 2
result = beam_power_vs_time(
    data, ant,
    sources=["cyg-a", ("Fixed at selected epoch", float(alt[mid]), float(az[mid]))],
    cal_weights=cal, freq_band_mhz=(float(freq[-1]), float(freq[0])), sign=-1,
)
print({name: values.shape for name, values in result["power"].items()})
print("Channels averaged:", result["n_chan_used"])
figure = plot_beam_power(result, time_tz="UTC")
```

`"cyg-a"` follows the source at every integration. The tuple stays at one
altitude and azimuth, in degrees (azimuth north through east). Over a complete
transit, the fixed beam measures the source moving through its response. The
tracked beam continuously changes direction and measures a different curve.
Their agreement over a short window is only a consistency check.

For stationary Cyg A validation, extend the selected window deliberately,
retain off-transit coverage, and add a fixed off-source control chosen using
the exact array factor. A nearby beam can contain a sidelobe response and is
not automatically a null. See [Beamform toward Cyg A and check a calibration](../guides/check-calibration.md).

## 4. Make a small source-tracking dirty image

The high-level imaging function performs its own `casm_io` read, with ascending
channels internally. It currently checks calibration channel count without
checking channel centers; the explicit preflight above supplies that missing
check for this same bounded dataset. Its `workers` controls the pixel loop,
not its internal reader's worker count.

```python
import matplotlib.pyplot as plt
from casm_imaging.imaging.pipeline import image_around_source
from casm_imaging.imaging import psf_for_result

# Release the full read before the wrapper reads this interval again.
del data
image_result = image_around_source(
    "cyg-a", cal_h5=cal, ant=ant,
    data_dir=str(data_dir), time_start=time_start, time_end=time_end,
    time_tz="UTC", fmt=None,
    grid="lm", estimator="real", ang_max_deg=10.0, npix=41,
    rfi_mask_version=None, normalize_bandpass=True, freq_avg=1,
    subtract_static=None, min_baseline_m=0.0,
    fs_sign=-1, workers=1, output_path=None, show=True,
)
print("image:", image_result["image"].shape)
print("geometry:", image_result["geometry"])
psf, x_deg, y_deg = psf_for_result(image_result, workers=1, verbose=True)
print("matching PSF:", psf.shape)
plt.show()
```

The `lm` grid avoids the alt/az coordinate degeneracy near zenith. The returned
legacy keys `daz_deg` and `dalt_deg` describe tangent-plane offsets for this
grid, not literal azimuth and altitude differences. The source is tracked at
each integration; averaging untracked complex visibilities first would smear
its motion.

This 41-pixel, ±10-degree grid is a starting inspection, not an automatically
adequate image for every layout. Check sampling against the longest retained
baseline and inspect a wider field when needed to characterize sidelobes.
`psf_for_result` reuses the retained baseline geometry, frequencies, track,
grid and estimator. It supplies a noiseless point-source geometry comparison,
not an absolute sensitivity measurement or a noise model for all sky emission.

Bandpass normalization divides each channel/baseline by its median calibrated
visibility magnitude over the selected time window. The output is consequently
dimensionless; changing that window can change the normalization. With
normalization disabled, values retain instrumental visibility units.
Neither mode is Jy/beam. Image `snr_info` is a peak/background-annulus statistic
affected by sidelobes and field size, not a pulsar detection significance.

The full-band example follows the historical imaging comparison but is not a
claim that every epoch should be unmasked. For controlled comparisons, hold
mask, normalization, antenna membership, baseline cuts and integration window
fixed. Keep `freq_avg=1` initially: larger blocks average adjacent *kept*
channels, can bridge masked frequency gaps, discard a trailing incomplete
block, and can lose coherence. Static subtraction requires an epoch-compatible
template with shape `(F, full_triangle)` in descending order; leave it off
until its amplitude, layout and frequency correspondence have been established.

## Reuse and provenance

For repeated snapshots or a new imaging mode, reuse the existing
`casm_imaging.imaging.calvis.BaselineSet` and all-sky routines rather than
implementing another baseline mapper or image sum. The reviewed high-level
wrapper still carries its own extraction code; this guide does not refactor it.
Keep the scientific interpretation with the canonical wiki's
`rank1-metric-caveat.md`, `weights-verification.md`, and
`beam-response-interpretation.md`; a calibration that works in one direction
need not transfer to all directions.

Figure source: `/home/casm/software/dev/casm_vis_analysis/notebooks/casm_calibration_and_beamforming.ipynb`,
zero-based cell 33, first and second PNG outputs. Cell 1 records the June-28
source windows, June-27 static night and `cal_sun_2026_06_28_thr1.h5` output
name. Cell 33 calls `image_around_source(grid="lm")` for the two windows.
These are historical outputs, not a fully reconstructed execution environment;
asset extraction preserved the PNG bytes without re-rendering.

Source revisions and file hashes: `source-snapshot.json` and
`tutorial-inputs.json` in the repository.

Preserve input file identities, the dated layout and selected antenna IDs,
calibration hash, requested and actual time coverage, frequency centers,
mask and preprocessing choices alongside any saved result.
