# Calibration figure provenance

The tutorial figures are byte-for-byte copies of existing commissioning outputs,
visually inspected on 2026-09-13. They were not regenerated, cropped, or edited.
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
The original exact Git revision is not established by the saved report;
the currently inspected source revision is `06004c75afad`.
Do not interpret that current revision as the historical renderer identity.

## Files and SHA256

All originals are under the product directory's `figs/` subdirectory. Copies
are under `docs/_static/tutorials/calibration/` in this documentation repository.

| File | SHA256 |
|---|---|
| `rank1_vs_freq_20260820.png` | `829f47daa1f504dfe8b3a70361398872b52b5c40a5add3b260edf6cf0fe98c9f` |
| `svd_vs_freq_20260820.png` | `832934276d845483296a463781b8816dad2c7443369a976d9e19d9bddb15694e` |
| `beam_check_cyga_20260820.png` | `ec2e1f7b930e53e44b8b58c1f7e2264727f2ce8a93bb2b94f2fb32c15a928592` |

The rank-1 plot contrasts static-subtracted and unsubtracted solar solves.
The SVD plot shows singular values and the leading fraction for the primary
solve. Its ideal 0.5 fraction applies to the zero-diagonal phase-only matrix;
the `1/N` guide is a lower bound, not a measured noise prediction.

The Cyg A figure uses UTC 2026-08-20 05:29:09–06:28:42, 27 integrations and
2425 selected channels. It compares the new calibration, the previous Aug-15
calibration, and an altitude-offset null direction. The structured null and
frequency oscillations limit a simple “better calibration” interpretation.
It is not a measurement of absolute flux, telescope SEFD, or FRB recovery.

The canonical recipe documents byte-for-byte reproduction of three historical
products in this family, with its tested scope. That historical result is not
a new validation performed by this documentation build.

Return to [SVD interpretation](rank1-diagnostics.md) or
[calibration generation](generate-weights.md).
