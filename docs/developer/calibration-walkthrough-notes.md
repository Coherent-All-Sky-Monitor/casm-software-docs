# Calibration walkthrough evidence

The calibration walkthrough follows one saved run under
`/mnt/nvme5/vishnu/cal_build_20260824/`, tagged `aug23_exact512_CAL0823N`.
No large read, solve, grid generation, or deployment was rerun to write it.

## Notebook and configuration

The original report notebook has 27 cells, 13 executed image-display cells and
17 embedded PNG outputs. Its code changes into the archive directory and displays
existing images. It contains no science execution or upload code. All code cells,
configuration and textual outputs were inspected before copying; no credential
markers were found. This is the original notebook, not a fabricated executable
walkthrough. Embedded outputs can be read without executing its cells.

The archive's scientific run is evidenced by `make.log`, the report JSON, products
and figures. The report records Python 3.13.5 and NumPy 2.4.2; it does not pin
the historical Git revisions. Current API inspection used `bf_weights_generator`
`9065aa069ec5e7ec1a5f094af1139886b6067720` and the existing documented analysis stack.

The tutorial code is a readable explanation of the same underlying calls and
saved configuration. It deliberately does not assemble a second save/deploy
pipeline. `make_cal_and_weights` remains the production build entrypoint.
The saved config points to the archive output directory; the tutorial's replay
command overrides it with `mktemp -d` before any build is proposed.

| Stage | Archived notebook cells, zero-based |
|---|---|
| Configuration/provenance | 0 |
| Raw autocorrelation check | 2–3 |
| Baseline sawtooth and unwrapped phase | 4–5 |
| Fringe-stopped phase and corrected residual | 6–9 |
| Gain phase and fitted delays | 10–11 |
| Rank-1 versus frequency | 12–13 |
| Full singular spectrum, omitted from tutorial | 14–15 |
| RdBu phase stages | 16–17 |
| Static A/B | 18 |
| Comparison with previous calibration | 19–20 |
| Tracking Cyg A diagnostic | 21–22 |
| Exact 512-beam grid | 23–24 |
| Source tracks | 25–26 |

## Scientific selection

The source window is 2026-08-23 20:41:30–21:41:30 UTC; the actual plotted
integrations span 20:42:59–21:40:15. There are 26 integrations and reference
antenna 9. Membership is 9, 10, 15, 19, 22, 23, 24, 26, 30, 32, 36, 38,
40, 42, 44, 45, with the dated August 7 layout named in the configuration.

The static request is August 24 03:00–03:30 UTC. Its saved template records
13 integrations spanning approximately 27 minutes, from observation
`2026-08-24-01:54:29`. This later window avoids overlapping observations and
a stub file affecting the earlier candidate window. The report's static notes
give Sun altitude −11.3…−5.7°, Cyg A 58.3…63.9°, and Cas A 30.3…33.9°.
This is a selected background template, not sky devoid of bright sources.

In these recipe figures, “raw phase” is `fs_primary['vis']`, already
static-subtracted but not fringe-stopped. True pre-subtraction autocorrelations
are separately collected from the raw data. Corrected-phase panels in the
downloadable notebook apply the solved calibration back to the solve window;
they are not independent cross-day validation.

`grid_mode="exact"` uses the active positions and frequency configuration in
`generate_beam_grid_exact`. The original config contains historical `track_*`
fields too, but exact placement does not use those to create a track-box grid.
Source tracks are plotted separately for August 25. Geometry/coverage is predicted;
the report's Cyg A diagnostic instead evaluates August 24 visibilities.

The original report's Cyg A plot tracks the source and uses normalized
cross-baseline coherence. The tutorial does not relabel it as a stationary
beam transit. The stationary test remains linked as an additional validation.

Current plotting code and older source prose contain differing descriptions of
ellipse hit regions. Use exact array-factor timing tables for timing decisions.
The diagram's altitude shading is not measured sensitivity, and source-footprint
markers alone do not certify an on-source observation.

## Original downloads and hashes

All files copied below are from the archive root or its `figs/` directory.
The PNGs were visually inspected and copied byte-for-byte. Web delivery uses
same-dimension WebP previews encoded with Pillow, quality 90, method 6; these are
lossy display derivatives. Original PNGs remain available for quantitative reading.

| Original | SHA256 |
|---|---|
| [Notebook](../_static/tutorials/calibration-walkthrough/cal_aug23_exact512_CAL0823N_diagnostics.ipynb) | `182e09a3dd304c27a85d2607fe5d2630bb952cc4bdde3c10a5cc76cc6949ac20` |
| [Parameters](../_static/tutorials/calibration-walkthrough/params_aug23_exact512.json) | `98dccaea4746ef507c12d28f3d5d935c3dc400df954be75e5b07a7676e5d6ed0` |
| [Report](../_static/tutorials/calibration-walkthrough/report_aug23_exact512_CAL0823N.json) | `882479ef1057a65a706d63fbe67517bd61ec3813ddc74581e75f0fadab7392ac` |
| [Phase stages](../_static/tutorials/calibration-walkthrough/fringe_diag_snap0_to_2.png) | `64cee331b93d5650bd285bb44ba549422d5a4b565536432ec6a4ffc0c268c1ca` |
| [Baseline sawtooth](../_static/tutorials/calibration-walkthrough/phase_raw_sawtooth_aug23_exact512_CAL0823N.png) | `0dab4d0842b60cd7ef6834120dc8fc9c6671d58500944e15162f1ccdd4111ddf` |
| [Rank-1 curve](../_static/tutorials/calibration-walkthrough/rank1_vs_freq_aug23_exact512_CAL0823N.png) | `16cb6085801988e4259610e35d8d814d5503294c0aecbeaf9fb6a372fdd038a0` |
| [Gain phases](../_static/tutorials/calibration-walkthrough/gain_delay_fits_aug23_exact512_CAL0823N.png) | `fae445c690896e205c1aa5604be7ac7b33804e4a92be31f9ef5f91bac1481950` |
| [Beam grid](../_static/tutorials/calibration-walkthrough/beam_grid_aug23_exact512_CAL0823N.png) | `d04685784dda1c726f1b00f86a47f6f6b93c42e7741dfd618558e4ea41b84dac` |
| [Source tracks](../_static/tutorials/calibration-walkthrough/source_transit_aug23_exact512_CAL0823N.png) | `f824d883e539d5b57366df1fcd50b941ed27643cbe0a82ae6dbe8e2933eb8478` |

The source-transit figure retains its historical annotation layout, including a
clipped label on the beam-grid plot. No scientific image was redrawn or cropped.

## Why the older hand-edited notebook is not the build recipe

`casm_vis_analysis/notebooks/casm_calibration_and_beamforming.ipynb` informed the
teaching order and remains unchanged. Its saved August 5–6 run uses different
membership, mixed execution order, manual phase extrapolation, a May-era grid,
obsolete IB scaling metadata, and an obsolete scratch deployment script.
Those operations were not imported into this tutorial. Likewise, historical
“higher rank-1 means better calibration” claims are qualified using the wiki's
independent-source evidence.
