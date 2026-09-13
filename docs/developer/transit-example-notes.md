---
myst:
  html_meta:
    description: "Processing details and source files for the saved stationary-beam Cyg A transit."
---

# Cyg A transit example: implementation and provenance

The beginner [calibration check](../guides/check-calibration.md) uses the
existing stationary-beam transit product published in the CASM scratchpad.
The PNG was visually inspected and copied unchanged on 2026-09-13.

## Source and dataset

The scratchpad page at
`/home/casm/software/casm_analysis_tools/webconsole/pages/3_Scratchpad.py`
lists figures under `/mnt/nvme5/casm_pipeline/scratchpad`, displays same-stem
Markdown captions, and finds producer scripts by stripping a final date suffix.
It explicitly describes the scratchpad as non-permanent.

The inspected evidence files in that directory are:

- `cyga_stationary_beam_20260805.png`: the copied waterfall and transit curve.
- `cyga_stationary_beam_20260805.md`: historical interpretation and correction note.
- `cyga_stationary_beam_20260805.npz`: saved `coh`, `freq`, `time_unix`, `good_f`, `lc`.
- `cyga_stationary_beam.py`: producing code, inspected without running.
- `cyga_run.log`: execution log confirming the selected data and reported numbers.

The log records observation `2026-08-05-05:15:42`, requested window
05:20–10:30 UTC, actual timestamps 05:20:16–10:29:31 UTC, and visibility
shape `(136, 3072, 8256)`, complex64. Frequency order is descending,
484.375 to 390.656 MHz. The calculation retains 136 integrations,
uses 75 off-source integrations, and keeps 2459 channels.

The script names calibration
`/home/casm/software/vishnu/beamforming_weights/20260804/cal_sun_2026-08-02_thr1_stable18_invvar.h5`
and the then-current layout symlink
`/home/casm/software/dev/antenna_layouts/current`.
The exact resolved layout-file identity and runtime dependency revisions were
not preserved in this artifact. Do not claim a fully reconstructed environment.

## What the producer computes

The beam direction is fixed at altitude 86.43°, azimuth 0.47°. Calibration
weights receive geometric steering for this direction, independent of time.
Cross-baseline static subtraction uses the real and imaginary medians from
samples more than 70 minutes from 06:58 UTC. Channels must pass the
calibration rank-1 threshold of 5 and an off-source RMS filter. This is a
channel-selection rule, not a calibration-quality ranking.

The saved waterfall is twice the real weighted cross-baseline sum. The
light curve averages the surviving channels. Its plot divides by its own
maximum. The log reports peak +14.5 minutes, a threshold-crossing width of
about 124 minutes, and peak/off-source RMS 5.3. That ratio is not a formal
Gaussian detection significance; the baseline estimator and samples also
enter the plotted result.

The original sidecar called the width expected from an approximate wide
east-west beam and interpreted a shoulder as Galactic-plane emission. The
figure contains no computed beam-model overlay or independent component
separation. The tutorial teaches the visible rise/fall and does not adopt
those interpretations as validated findings. Detailed predictions should use
the established exact array-factor machinery; the wiki records failures of
analytic beam ellipses away from the beam centre.

## Reuse boundaries

Do not rerun this historical script unchanged. It uses epoch-specific
`ant_id - 1` mapping, legacy layout columns, and a mutable layout path.
New evaluations should resolve physical antennas through `AntennaMapping`
and use the existing `beam_power_vs_time` API with fixed pointing tuples.
That API consumes the original full triangle, descending data when calibration
is supplied, and a visibility mask with `True = bad`. It does not reproduce
this script's static subtraction or channel selection automatically.

No source code or observation data was changed. No scientific job was run.
The figure demonstrates an existing fixed-direction measurement; the short
call demonstrates the maintained entry point for a prepared future experiment.

## SHA-256 evidence identities

Paths below are relative to `/mnt/nvme5/casm_pipeline/scratchpad`.

```text
f81295a82c8d37f7a496110e84e30675599321a41f148f5cbaf449372149ad96  cyga_stationary_beam_20260805.png
00956c515229acfa0ce23e8fe5af404a3889f54d562f5fca7ef287356b17a2d7  cyga_stationary_beam_20260805.md
c38928b7ccfd68266aa01e3ab736791ed1afe63fdd2dfae5f47b40aa2d33ae7d  cyga_stationary_beam_20260805.npz
23003ec1bc8ab7729f63977ba2fa02fbd4d0add1cd9610bc28ae7a419049087a  cyga_stationary_beam.py
1174cac1f6df27ba0b71ed2e67d77657df04914684b2e858bc3a03a39f4f8613  cyga_run.log
```

The copied PNG at `docs/_static/tutorials/transit/` has the same digest.
The maintained beam API was inspected at `casm_vis_analysis`
`5039eb4714b5c62eb72b6b8f82527c787ca4f214`; its file hash is recorded in
the [imaging notes](imaging-notes.md).
