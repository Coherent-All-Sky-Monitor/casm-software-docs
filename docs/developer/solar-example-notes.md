# Solar example provenance and limits

Tutorial figures were checked on 2026-09-13. The filterbank figure was subsequently
refreshed for the shared dynamic-spectrum renderer at `casm_vis_analysis`
revision `af8ecd0`; the phase example remains checked against revision
`5039eb4714b5c62eb72b6b8f82527c787ca4f214`. No recording was requested.
Per-figure inputs and execution details follow.

## Three-panel filterbank waterfall

Extracted on 2026-09-13 using the tutorial's `split_filterbank` call. Refreshed
for renderer `af8ecd0` using the same saved bounded cutout and tutorial
`plot_waterfall` parameters; the full source observation was not read again.
Output: `docs/_static/tutorials/solar/solar-waterfall.png`, SHA256
`219778e56396cde990cd506507de25a421d8c1c089ccca40e9877677edb46610`.

The site displays a WebP copy made by `scripts/prepare_web_figures.py` with
Pillow, quality 90, at the original dimensions. It is 635,990 bytes instead
of the PNG's 1,735,811 bytes (63% smaller). This is lossy web compression,
not a new science rendering; the original PNG remains linked in the tutorial.
Regenerate the WebP after changing the PNG. Both versions were visually checked.

Input: `/mnt/nvme5/solar0819/solartrack_fil/ib_IB.fil`, 77,309,411,670 bytes.
Header: `tstart=61272.01780093231`, `tsamp=0.001048576` seconds,
`nchans=3072`, `nbits=32`, `nbeams=1`, `fch1=484.375` MHz,
`foff=-0.030517578125` MHz. Only the header and selected data were read.
The tutorial selects samples `[2667427, 2696037)`, approximately
2026-08-20 01:12:15–01:12:45 UTC. Output cutout:
`_build/tutorial-data/solar_IB_20260820_011215.fil`, SHA256
`e8066d82fb7201c768c96fa68b3216dff036374ad485bfc05820f919550fa17e`.
The cutout is a disposable build artifact, not committed source data.

Extraction used `casm_io.filterbank.split.split_filterbank` at revision
`22ef826d9f2ba355388523265081da1468e5a4ff`; module SHA256
`a64cc9335d8abd07bceddcfebb8bd42ced420c96db6095b4c6be838cc3227f18`.
Its seek-and-read path fetched 351,559,680 payload bytes. The combined
original extraction and rendering took 4.40 seconds with peak RSS 810,852 KiB.
No conversion of the whole observation or new science implementation was used.

Renderer: `src/casm_vis_analysis/solar_waterfall.py`, SHA256
`034bcf149a27b9826b9dbfafd4de4c207f48547e8cc9d81278597819553ad849`.
Parameters: `beam="IB"`, `tfac=48`, `tz="America/Los_Angeles"`,
`cmap="inferno"`; default channel selection `(505, 1200, 1500, 2000)`.
The renderer averages 48 samples per bin (50.331648 ms), retaining 596 complete
bins and dropping two final samples. It divides each channel by its temporal
mean over those bins, including the burst, and clips the waterfall colour range
at the fifth/ninety-fifth percentiles. The colour bar explicitly labels power
divided by the channel mean. Peak values
are not calibrated fluxes, and are not directly comparable to an off-event
baseline excess. The increasing displayed frequency axis was visually checked against
the bandpass and channel-frequency labels.

The solar identification is historical, not derived from this plotting run.
Evidence and independent e-CALLISTO/RSTN confirmation are recorded in
`/home/casm/software/dev/casm-wiki/solar-burst-2026-08-20.md`, with original
analysis under `/mnt/nvme5/solar0819/event0112/`. The tutorial makes no new burst
classification, drift-rate, flux or array-health claim. No antenna layout is
applied to an already beamformed incoherent-beam filterbank.

The renderer has no time-window option and always reads the whole supplied
filterbank. Increasing `tfac` reduces output size, not the bytes read. The
bounded extraction is therefore part of this tutorial, rather than an implied
optimization. The input's `nbeams=1` was verified before using the splitter;
historical mislabelled multi-beam headers need separate validation.

## Solar phase panels

`scripts/render_solar_phase_tutorial.py` executes the displayed Python blocks
in `docs/guides/solar-phase.md` and saves the figure through Agg. Generated
2026-09-13: `docs/_static/tutorials/solar/solar-phase-two-antennas.png`.
The three-hour window extends the same observation and uses the August-7
layout from the [visibility example](io-example-notes.md). The directed
reference-9 to target-19 read returns `(79, 3072, 1)` complex64, 1,941,504 bytes.
`with_inactive()` selects
only those two antennas in memory; no layout file is changed. No static
background, frequency mask or calibration is applied.

Requested interval: August 23, 19:20–22:20 UTC, rooted at
`/mnt/nvme4/data/casm`. Data come from
`visibilities_64ant/2026-08-23-19:18:14.dat.{0,1,2}`. Discovery also checks
`2026-08-21-03:14:39.dat.52`; that truncated final part contributes zero
integrations in this window. The reader reports no gaps or missing files.
The single-worker, single-BLAS-thread execution completed within the 90-second
timeout. Only the selected cross-correlation is materialized, not the full
triangle. The new figure was visually checked: raw bands curve with time;
stopped bands are flatter, with late-window residual structure still visible.

The displayed snippet temporarily disables Astropy IERS downloads and permits
older predictions for this illustration, restoring settings afterward.
The installed `astropy-iers-data` is `0.2026.2.23.0.48.33`, using its
`data/finals2000A.all` table. Its age check otherwise rejects this date.
This is not a calibration validation; refresh Earth-orientation data before
scientific calibration. The 79 integrations cover 19:20:31–22:19:11 UTC
on August 23, long enough to show geometric phase evolution.

Renderer: `plot_fringe_diagnostic` in `src/casm_vis_analysis/plotting/fringe_diag.py`,
SHA256 `ce1922df763a630997c75ebfab28ef1614bc36a1bb998a77c8749cd8420ca99d`.
It uses `RdBu`, `Normalize(-pi, pi)`, complex angle extraction, and white for
masked channels. Arrays have shape `(time, frequency, target baseline)`.
The time axis remains elapsed hours; the header states the local interval.

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
