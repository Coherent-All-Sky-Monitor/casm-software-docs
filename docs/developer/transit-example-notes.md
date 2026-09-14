---
myst:
  html_meta:
    description: "Provenance of the historical stationary-beam Cyg A transit figure."
---

# Cyg A transit example: provenance of the historical figure

The [calibration check](../guides/check-calibration.md) runs its own transit
on August 24 data. It also shows one historical figure,
`_static/tutorials/transit/cyga_stationary_beam_20260805.png`, for the
per-channel waterfall that a band-averaged curve hides. This page records
where that figure came from. File digests are in `tutorial-inputs.json`.

## Source

The figure is a byte copy from the CASM scratchpad,
`/mnt/nvme5/casm_pipeline/scratchpad`, which the web console describes as
non-permanent storage. The companion files there are
`cyga_stationary_beam_20260805.{md,npz}`, the producing script
`cyga_stationary_beam.py`, and `cyga_run.log`.

The log records observation `2026-08-05-05:15:42`, a requested window of
05:20-10:30 UTC, returned timestamps 05:20:16-10:29:31 UTC, and visibility
shape `(136, 3072, 8256)` complex64, descending from 484.375 to 390.656 MHz.
The calculation keeps 136 integrations, 75 of them off-source, and 2459
channels. Calibration was
`/home/casm/software/vishnu/beamforming_weights/20260804/cal_sun_2026-08-02_thr1_stable18_invvar.h5`
against the then-current layout symlink. The resolved layout file and the
runtime dependency revisions were not preserved.

## What the producer computed

Beam direction fixed at altitude 86.43, azimuth 0.47 degrees, with geometric
steering applied to the calibration weights and held constant in time.
Cross-baseline static subtraction used real and imaginary medians from
samples more than 70 minutes from 06:58 UTC. Channels had to pass a
calibration rank-1 threshold of 5 and an off-source RMS filter, a
channel-selection rule rather than a quality ranking. The waterfall is twice
the real weighted cross-baseline sum; the light curve averages the surviving
channels and is plotted divided by its own maximum.

Reported numbers: peak at +14.5 minutes after transit, threshold-crossing
width about 124 minutes, and peak over off-source RMS 5.3. That ratio is not
a Gaussian detection significance, since the baseline estimator and sample
count enter it.

The original sidecar attributed the width to an approximate wide east-west
beam and a shoulder to Galactic-plane emission. The figure carries no beam
model and no component separation, so the tutorial uses it for the visible
rise and fall only. Timing and shape predictions belong to the exact
array-factor tool, which the tutorial calls directly.

## Why the script is not rerun

It uses epoch-specific `ant_id - 1` mapping, legacy layout columns and a
mutable layout path. The maintained path is `AntennaMapping` plus
`beam_power_vs_time` with fixed pointing tuples, which the tutorial runs on
current data. That API takes the full triangle, descending frequencies when
calibration is supplied, and a visibility mask with `True = bad`. It does not
reproduce this script's static subtraction or channel selection; the tutorial
supplies both explicitly.
