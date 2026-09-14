# Calibration figure provenance

The tutorial figures are unmodified copies of existing commissioning outputs.
They illustrate interpretation of historical measurements, not current array state.

## Dataset and recipe

Original product directory:
`/mnt/nvme5/solar0819/recipe_demo_20260820/`.
The sibling `params_20260820.json`, `report_20260820.json`, and
`cal_20260820_diagnostics.ipynb` identify the analysis configuration and outputs.

The solar solve uses UTC 2026-08-19 20:41:30–21:41:30, with the static window
2026-08-20 02:45–03:15 and template
`/mnt/nvme5/solar0819/cal_static_night/static_aug20_0245_0315UT.npz`.
The source recipe names reference antenna 9 and antennas
9, 10, 15, 19, 22, 23, 24, 26, 30, 32, 36, 38, 40, 42, 44, 45.
Its layout is `casm_antenna_layout_2026-08-07.csv`.

These historical frequency axes extend approximately 390–484 MHz. Preserve the
actual recorded coordinates rather than relabeling the figures with another
configuration's nominal passband. The example recipe's old `bounds` grid is not
the exact-grid placement required for a new build.

The producing workflow is `bf_weights_generator.make_cal_and_weights`, with
renderers in `bf_weights_generator/recipe_diagnostics.py`:
`plot_rank1`, `plot_svd_vs_freq`, and `beamform_source_check`.
The original exact Git revision is not established by the saved report.
Do not interpret the currently installed source revision as the historical
renderer identity.

## Files

All originals are under the product directory's `figs/` subdirectory. Copies
are under `docs/_static/tutorials/calibration/` in this documentation
repository: `rank1_vs_freq_20260820.png`, `svd_vs_freq_20260820.png`,
`beam_check_cyga_20260820.png`. File hashes: `tutorial-inputs.json` in the
repository.

The rank-1 plot contrasts static-subtracted and unsubtracted solar solves.
The SVD plot shows singular values and the leading fraction for the primary
solve. Its ideal 0.5 fraction applies to the zero-diagonal phase-only matrix;
the `1/N` guide is a lower bound, not a measured noise prediction.

The Cyg A figure uses UTC 2026-08-20 05:29:09–06:28:42, 27 integrations and
2425 selected channels. It compares the new calibration, the previous Aug-15
calibration, and an altitude-offset null direction. The structured null and
frequency oscillations limit a simple “better calibration” interpretation.
It is not a measurement of absolute flux, telescope SEFD, or FRB recovery.

The canonical recipe documents byte-identical reproduction of three historical
products in this family, with its tested scope.

Return to [SVD interpretation](../guides/rank1-diagnostics.md) or
[calibration generation](../guides/generate-weights.md).
