# Calibration walkthrough evidence

The calibration walkthrough follows one saved run under
`/mnt/nvme5/vishnu/cal_build_20260824/`, tagged `aug23_exact512_CAL0823N`.
No large read, solve, grid generation, or deployment was rerun to write it.

## Notebook and configuration

The original report notebook's code changes into the archive directory and
displays existing images; it contains no science execution or upload code.
This is the original notebook, not a fabricated executable walkthrough.
Embedded outputs can be read without executing its cells.

The archive's scientific run is evidenced by `make.log`, the report JSON,
products and figures.

The tutorial code is a readable explanation of the same underlying calls and
saved configuration. It deliberately does not assemble a second save/deploy
pipeline. `make_cal_and_weights` remains the production build entrypoint.
The saved config points to the archive output directory; the tutorial's replay
command overrides it with `mktemp -d` before any build is proposed.

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

## Original downloads

All files linked below are unmodified copies from the archive root or its
`figs/` directory: [notebook](../_static/tutorials/calibration-walkthrough/cal_aug23_exact512_CAL0823N_diagnostics.ipynb),
[parameters](../_static/tutorials/calibration-walkthrough/params_aug23_exact512.json),
[report](../_static/tutorials/calibration-walkthrough/report_aug23_exact512_CAL0823N.json),
[phase stages](../_static/tutorials/calibration-walkthrough/fringe_diag_snap0_to_2.png),
[baseline sawtooth](../_static/tutorials/calibration-walkthrough/phase_raw_sawtooth_aug23_exact512_CAL0823N.png),
[rank-1 curve](../_static/tutorials/calibration-walkthrough/rank1_vs_freq_aug23_exact512_CAL0823N.png),
[gain phases](../_static/tutorials/calibration-walkthrough/gain_delay_fits_aug23_exact512_CAL0823N.png),
[beam grid](../_static/tutorials/calibration-walkthrough/beam_grid_aug23_exact512_CAL0823N.png),
[source tracks](../_static/tutorials/calibration-walkthrough/source_transit_aug23_exact512_CAL0823N.png).
Source revisions and file hashes: `source-snapshot.json` and
`tutorial-inputs.json` in the repository.

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
