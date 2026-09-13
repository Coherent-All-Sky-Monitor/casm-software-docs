# Calibration and deployment implementation notes

Use the existing `bf_weights_generator.make_cal_and_weights` driver to build a
calibration, coherent-beam weights, verification report, and diagnostic notebook.
It coordinates the scientific packages and never uploads its products.

This tutorial covers the driver at revision `06004c75afad`. Commands use current
interfaces; the build requires an operator-reviewed configuration and available
visibility data. No science job was run to prepare this tutorial.

## 1. Select the environment and inputs

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
cd /home/casm
python -m bf_weights_generator.make_cal_and_weights --help
```

Run outside `/home/casm/software/dev`, where repository names can shadow installed
packages. Begin with the configuration associated with a verified recent product.
Preserve its scientific choices until there is evidence to change them.

Before building, review these fields in the JSON configuration:

| Fields | Decision required |
|---|---|
| `out_dir`, `tag` | New output directory and unique product identity |
| `layout_csv`, `antennas`, `ref_ant` | `/home/casm/software/dev/antenna_layouts/current` for new observations; matching dated geometry for historical data, explicit participating IDs, active reference |
| `cal_source`, `source_window` | Source and two UTC timestamps spanning the approved solve window |
| `static_window`, `static_path` | Matched static template, or explicit absence of subtraction |
| `grid_mode`, `n_beams`, `alt_min_deg` | Approved grid coverage; use `exact` for exact array-factor placement |
| `prev_cal_path` | Previous calibration to compare |
| `beam_check_window`, `beam_check_source` | Independent bright-source evaluation |
| `diagnostics`, `notebook`, `execute_notebook` | Keep the reviewable diagnostic outputs enabled |

The driver defaults to the historical `bounds` grid, so select `grid_mode="exact"`
explicitly for the currently required exact-model placement. Default active
antennas come from the layout, which may differ from the deployed product.
Check both the solve membership and `include_in_beamforming` before building.
Use a fresh `out_dir`: calibration writing inside the driver allows overwrite.

## 2. Preview the resolved parameter block

For an existing reviewed configuration saved as `reviewed-recipe.json`:

```bash
python -m bf_weights_generator.make_cal_and_weights \
  --config /path/to/reviewed-recipe.json --print-params
```

You can inspect a proposed override without running the solve:

```bash
python -m bf_weights_generator.make_cal_and_weights \
  --config /path/to/reviewed-recipe.json \
  --param grid_mode "'exact'" \
  --param tag "'reviewed-rebuild'" \
  --print-params
```

`--param` values are parsed as Python literals; quoted strings above are
intentional. This preview prints defaults plus overrides and exits before
`run()`. It does **not** validate data coverage, geometry, antenna membership,
source elevation, or the physical suitability of a static template.

## 3. Run the reviewed build

Once the configuration is complete and the analysis is authorized:

```bash
python -m bf_weights_generator.make_cal_and_weights \
  --config /path/to/reviewed-recipe.json
```

For orchestration code, the equivalent existing interface is:

```python
import json
from bf_weights_generator.make_cal_and_weights import RecipeParams, run

with open("/path/to/reviewed-recipe.json") as handle:
    params = RecipeParams(**json.load(handle))
outputs = run(params)
print(outputs["cal_file"])
```

Both forms read observation data and write products. They can consume substantial
memory, time, and disk. This is not a command to put on a webpage request thread.

To rebuild only geometry from an existing calibration, use `cal_path` and remove
`source_window`, `static_window`, `static_path`, `cal_ra`, and `cal_dec`.
The driver rejects these conflicting intents. This skips a new solve; it does
not establish that the reused calibration remains valid.

## 4. Review the products and checks

| Output | Inspect |
|---|---|
| `cal_<tag>.h5` | Antenna IDs, frequency axis, channel flags and gains |
| `weights_<tag>_..._int8.h5` | Actual populated slots, pointings, frequency ordering |
| `report_<tag>.json` | Parameters, versions, subband occupancy, pointing checks, diagnostics errors |
| `cal_<tag>_diagnostics.ipynb` | Phase stages, delay fits, SVD panels, independent beam check |
| `figs/` | Scientific figures for human review |

The build checks source-elevation coverage, static-window metadata agreement,
subband occupancy, payload sanity at a sampled channel, and selected pointing
fits. A sampled nonzero payload does not prove every intended antenna is present.
The wiki documents a near-empty product passing those checks after a layout/cal
membership mismatch. Verify populated slots against the requested antenna IDs.

Diagnostic failures may appear as **SKIPPED** notebook sections or
`diagnostics_error` in the report while products still exist. Read the report;
an exit or a file on disk is not an astronomical validation.

Read [rank-1 diagnostics](../guides/rank1-diagnostics.md) and run the
[cross-day phase and Cyg A checks](../guides/check-calibration.md). Calibration generation
and [deployment](../guides/deploy-weights.md) are separate stages.

```{figure} ../_static/tutorials/calibration/beam_check_cyga_20260820.png
:alt: Archived Cyg A beam check comparing new calibration, previous calibration, and an offset control.

An existing notebook's independent Cyg A check, 2026-08-20. The new calibration
has a higher mean in this metric, but the control is structured and the spectral
response oscillates. Inspect both panels before making a scientific claim. This
is a normalized cross-baseline diagnostic, not a flux-calibrated stationary
transit or certification of whole-sky performance. [Provenance](../guides/calibration-figures.md).
```

The canonical driver builds the CB file. Obtain the matched IB companion through
the established workflow referenced in wiki `weights-and-deploy.md`; it must
represent the same intended membership and scaling. Do not reuse an arbitrary
old IB product because its filename looks familiar.

## Source and revision notes

[Canonical recipe](https://github.com/Coherent-All-Sky-Monitor/bf_weights_generator/blob/06004c75afad0af6ea3f3f2206944f342cb04730/docs/canonical-recipe.md)
contains historical worked configurations. Their dates, antenna lists, windows,
and older `bounds`/`track` placement examples are not current operating defaults.

Reviewed source: `bf_weights_generator/make_cal_and_weights.py`, SHA256
`d63f2c2a146361ce6e5ff0578e80356ee2763176735d091ffdcdc39a6fc58600`.
The source repository was clean at inspection on 2026-09-13. This tutorial adds
documentation only; it does not change the driver or its policy.

## Deployment source

Source revision `06004c75afad0af6ea3f3f2206944f342cb04730`, clean at inspection
on 2026-09-13. [Deployment implementation](https://github.com/Coherent-All-Sky-Monitor/bf_weights_generator/blob/06004c75afad0af6ea3f3f2206944f342cb04730/bf_weights_generator/deploy_bf_weights.py)
SHA256: `b78b99da7aa8bc3db9b4e9dfcfcd13cb53c2df76df4aa5428475261685445ab3`.
The registry call is not gated by `--dry-run`, so offline previews need
`--no-registry`. This is established by code inspection, not a live reproduction.
Source fixes are outside this documentation task.
