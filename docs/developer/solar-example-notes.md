# Solar example provenance and limits

Both tutorial figures were visually inspected and copied unchanged on
2026-09-13. No source package was edited, science workflow rerun, or recording
requested. Python signatures and rendering options were checked against
`casm_vis_analysis` revision `5039eb4714b5c62eb72b6b8f82527c787ca4f214`.
The historical generating Git revisions are not established here.

## Three-panel filterbank waterfall

Original PNG:
`/mnt/nvme5/solar0819/waterfalls_v2/aug18/aug18_IB_waterfall_localtime.png`.
Documentation copy: `docs/_static/tutorials/solar/solar-waterfall.png`.
SHA256: `c84cdc169785a76ce22b8832f4b39c972b1b927ca86c5f46c8842237d29aa9f8`.

Input named in the generating script:
`/mnt/nvme5/solar0818/fil/aug18_IB.fil`.
It is an existing roughly 152 GB filterbank, not a visibility file; it was not
reread for this documentation. Observation ID `2026-08-18-07:01:53`; plotted
interval approximately 05:55–09:45 PDT. Antenna count and campaign window in
the image title are historical metadata, not current array state.

Generating script: `/mnt/nvme5/solar0819_v2/scripts/plot_aug18.sh`, SHA256
`246a1d0939ac197259062a5819ff028f02727dd52ff6000f5b11c6b18cd040ad`.
Later title annotations are described in the sibling v2 README and relabeling
workflow; this tutorial does not claim its short command exactly reproduces
every historical annotation.

The v2 README documents a corrected frequency orientation: descending channel
0 belongs at the upper edge using `origin="upper"`. Older images under
`/mnt/nvme5/solar0819/waterfalls/` have a mirrored frequency axis and were rejected
for this tutorial. The copied v2 image places the approximately 400 MHz comb
at the same frequency in waterfall and bandpass panels.

Current renderer: `src/casm_vis_analysis/solar_waterfall.py`, SHA256
`5553a9572f9fc20a50d7a18c5ca45b2f68a459cea39f2cd0e8d4ac3fa749a188`.
`plot_waterfall(path, out_path, beam, role=None, tfac=954, chans=..., tz=...,
cmap=...)` downsamples time, divides each channel by its full-interval mean,
and uses fifth/ninety-fifth percentiles for waterfall colour limits.
`viridis` reproduces this historical palette; current default is `inferno`.
The omitted colour bar limits quantitative reading of the image's colour.
The selected channel indices are zero-based and validated against file length.

## Solar phase panels

Original PNG:
`/mnt/nvme5/solar0819/recipe_demo_20260820/figs/fringe_20260820/fringe_diag_snap0_to_2.png`.
Documentation copy: `docs/_static/tutorials/solar/solar-phase.png`.
SHA256: `2c89f469e997917411147629a1c76c8a374a84ac5a9c6d4faa31e91ba07c8dd0`.

The archived recipe's `params_20260820.json`, `report_20260820.json`, and
`cal_20260820_diagnostics.ipynb` identify a Sun solve over
2026-08-19 20:41:30–21:41:30 UTC, with 16 antennas and reference 9.
The image spans the actual integrations to 21:41:03 UTC. Its four target
antennas are 26, 30, 32, and 36. The layout is
`casm_antenna_layout_2026-08-07.csv`.

The primary solve subtracts the Aug-20 02:45–03:15 UTC static template;
“Raw phase” means before fringe stopping within that recipe, not necessarily
untouched on-disk visibilities. The short tutorial intentionally demonstrates
the API on the reader's own selected `data`; reproducing these exact historical
pixels additionally requires that recorded selection and preprocessing.

Renderer: `plot_fringe_diagnostic` in `src/casm_vis_analysis/plotting/fringe_diag.py`,
SHA256 `ce1922df763a630997c75ebfab28ef1614bc36a1bb998a77c8749cd8420ca99d`.
It uses `RdBu`, `Normalize(-pi, pi)`, complex angle extraction, and white for
masked channels. Arrays have shape `(time, frequency, target baseline)`.
`bf_weights_generator.recipe_diagnostics.plot_fringe_stopped` produces the
archived panels and relabels the elapsed-hours axis to local clock time.

This is a near-transit observing window, not a claim that the entire transit
was captured or that the Sun was the only signal. The phase plot is not a
calibrated beam-power or flux plot. The public fringe-stop function can return
an all-true time mask when the source never rises; callers must establish
source visibility independently before scientific interpretation.

## Scratchpad review

The human viewer at
`/home/casm/software/casm_analysis_tools/webconsole/pages/3_Scratchpad.py`
uses same-stem `.md`/`.txt` captions and `.py` scripts under
`/mnt/nvme5/casm_pipeline/scratchpad`. Its solar stationary-beam examples were
reviewed for context. They are different beam-power analyses, so they were not
relabeled as phase or filterbank outputs here.

Return to [solar phase](../guides/solar-phase.md) or
[solar waterfall](../guides/solar-waterfall.md).
