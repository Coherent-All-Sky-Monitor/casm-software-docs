# Investigate an observation

The dark monitoring workspace runs separately at **http://localhost:8061/**.
Observation, Readiness and Antennas are the primary tabs. The monitor on 8060,
T2/T3 on 8050, scratchpad on 8501 and Medusa remain unchanged. Forward port
8061 to use the preview remotely. No Plotly code is loaded by this interface.

## Start with recovery and search pressure

Observation shows rolling 24-hour injection outcomes, recent misses, existing
replay plots, product freshness and array geometry. Completed fired trials,
pending trials and firing failures are separate. A missing ledger is
unavailable, not zero failures. The seven-day trend uses UTC dates; the headline
is a rolling interval. Read [injection recovery](injection-recovery.md) before
interpreting a saved replay as live search evidence.

Open **T1 / RFI**, select an interval and inspect emitted candidates per gulp,
beam/time, DM/time and width distributions. Hella's 10,000 raw-peak cap applies
per gulp. Stored candidates are post-clustering: their count cannot establish
whether the raw-peak cap was reached. The separate log table shows explicit cap
warnings and processed/instance beam counts when recorded. Logs are a bounded
tail, not guaranteed full-day coverage. No warning in that tail does not prove
a cap-free day. Follow the interval link into visibilities to inspect frequency
structure. RFI, satellites, bad channels and storage problems are investigation
hypotheses until supported by evidence.

## Select a baseline and render

Open **Visibilities**. Defaults select a few long N-S baselines from matched
recorded payload membership when available; the interface discloses an
intended-layout fallback. Choose by physical length, orientation or station.
The nearby-row filter is a geometric separation filter, not a verified plank
adjacency graph. Hardware identities remain in the selection/provenance panel.
At most six pairs are rendered together.

Choose today, another date or explicit UTC bounds, then a frequency range.
Select phase waterfall, amplitude waterfall, phase/frequency, amplitude
spectrum or autocorrelations. Raw and Sun-fringe-stopped processing reuse the
existing scientific modules. Click **Render selection**; changing controls
alone does not read data. Narrow the bounds and render again to examine a
feature. Every product provides PNG, numerical NPZ and JSON provenance downloads.

The resolution choice is explicit:

- **8-channel average:** up to a week of cached complex averages. Averaging
  already occurred before fringe stopping and can irreversibly decorrelate
  phase; use native channels for calibration-phase decisions.
- **Native cache:** up to six hours per requested view, subject to actual
  retention. Missing coverage is reported, with no automatic raw-data fallback.
- **Native recording:** at most one hour per interval and a 64 MiB selected
  triangle budget, through the existing `casm_io` reader. This is an explicit
  disk read. Current writes are excluded; archived head-node access is not
  searched automatically.

Historical windows use the matching dated layout. Cross-epoch comparisons are
rejected rather than silently comparing different physical baselines.
The amplitude waterfall uses the shared [solar rendering](solar-waterfall.md)
style: channel-normalized waterfall, raw spectrum and light curves. Correlated
amplitude is not calibrated solar flux or a coherent-beam recording. Gaps,
normalization scope and actual timestamps remain in the product. Solar
variability and low-signal phase structure alone do not establish a fault.

## Compare calibration-day phase

Open **Calibration-day comparison** and select the same baseline and frequency
band for two observing windows. Use the saved calibration report/notebook
linked from **Calibration** to identify the actual reference window.
Match solar geometry and processing. The tool compares Sun-fringe-stopped
phase spectra; it does not divide today's data by deployed calibration.
Changed sawtooth structure calls for investigation, not automatic deployment.

**Independent Cyg A transit** uses native cached visibilities, the selected
ledger calibration, a stationary beam and an explicitly chosen stationary
control. Enter the pointings appropriate to the observation; the example
control is not a verified null. The exact array-factor expectation has its
own normalized axis, separate from measured cross-correlation power. No
amplitude fitting or pass/fail threshold is applied. Bounds are limited to
two hours, one UTC date, 55 native integrations and a 500 MiB selected-matrix
budget. A short successful render is not validation of a full transit or
of calibration quality. See [the worked transit](check-calibration.md).

## Save evidence before requesting investigation

Use **Mark for investigation** on a plot, describe the feature and save it.
The review record snapshots the displayed PNG, selection, processing,
provenance and note. Newly observed injection misses are retained in the
preview-local queue even when they leave the source window. Existing misses
outside the inspected source history cannot be recovered retroactively.

Items remain queued until **Request investigation** is clicked. Requested
means a human asked for investigation, not that an agent is running.
There is no executor, Slack integration or autonomous cleanup/masking action.
Missing or stale evidence must remain explicit in any later recommendation.
Readiness can also save its infrastructure evidence without a plot.

## Antennas and source history

**Antennas** starts with roughly the last hour of cached transmitted-band SNAP
history. It reuses the existing history reader and scientific renderer.
Full 4096-channel board plots are existing collector products with their
actual acquisition times; opening this page does not query hardware or change
polling. Selected history reads are bounded to 256 MiB and refuse time
averaging that could hide gaps.

**Source history** searches the canonical B0329 ledger and existing saved
plots across its full history. Dated attempts include non-detections,
retractions and qualified S/N/width statements. A single scalar S/N would
misrepresent rows containing multiple folds, so the recorded outcome is
preserved. Opening history does not fold data or dump beams.

## Manually staged calibration

**Calibration** presents the existing Sun recipe, solve/static windows and
reviewed antenna selection. Staging writes a private recipe and layout snapshot.
It does not edit current wiring, CASMAN or intended beamforming membership.
A second confirmation, typing the staged build ID, starts only
`python -m bf_weights_generator.make_cal_and_weights` in an isolated directory.
The build generates diagnostics for review, with admission and process limits.

This preview builds CB products only. It does not build the paired IB product
or preserve a custom factorial deployment grid. Its output is therefore not
a complete deployment package. Deployment, registry writes and restart-default
changes are disabled. Build validation uses fixtures; no expensive real solve
was run to demonstrate the interface. Read the
[canonical build walkthrough](generate-weights.md) and deployment safeguards
before proposing operational work. Higher rank-1 is not proof of better beam
sensitivity.

## Implementation and documentation review

Source revision `fb97f57`, branch `observation-preview`. Source checkout:
`/home/casm/software/dev/casm_monitor/.claude/worktrees/observation-preview`.
The owning manuals are `docs/api-science.md`, `docs/api-review.md`,
`docs/api-commissioning.md` and `frontend/README.md`.
Artifacts and the review database are isolated under
`/home/casm/scratch/casm-observation-preview`. Production monitor Store handles
are read-only. Workspace-local rendering, queue persistence and explicitly
confirmed builds are authorized exceptions, not telescope operations.

This guide supersedes the fixed-baseline preview at `369c34e), which the
operator rejected as insufficient. The shared solar renderer remains
`casm_vis_analysis` `af8ecd0`. This change affects monitor APIs, defaults,
evidence persistence and build admission; source-local manuals and this guide
are updated together under [documentation maintenance](../maintaining-docs.md).
The preview also corrects a singleton-baseline Sun-delay broadcasting bug in
the monitor adapter. Old singleton Sun-reference views require re-rendering;
the locked production checkout has not received that fix. Unmocked canonical
transform/render tests cover the corrected time/baseline axes.
The three-package API snapshot has no new scientific source changes in this
task. Historical tutorial figures are preserved without rerunning their jobs.
Cross-repository CI/publishing, Grafana, Slack, fast-beam workflows, automatic
RFI attribution and layout exclusion-policy implementation remain deferred.

Verification on 2026-09-13 local date: 521 backend tests passed, the browser
workflow checks passed, and bounded real-data renders exercised phase
comparison, amplitude, autos and a short Cyg A/control interval. The selected
last-hour transmitted-band SNAP cache was unavailable and returned an explicit
404; fixture tests cover that adapter. No Kafka repair or hardware query was
attempted. Evidence is in the source checkout's check scripts and
`/home/casm/scratch/casm-observation-preview/science-validation.json`.
