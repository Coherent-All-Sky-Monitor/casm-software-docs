# Investigate an observation

The dark monitoring workspace runs separately at **http://localhost:8061/**.
Observation, Readiness and Antennas are the primary tabs. The monitor on 8060,
T2/T3 on 8050, scratchpad on 8501 and Medusa remain unchanged. Forward port
8061 to use the preview remotely. The page background is black and no Plotly
code is loaded. Imaging is removed from this preview's navigation and frontend
routes because the operator rejected its current plots. Other viewers and
the existing scientific/backend imaging implementation remain unchanged.

The opening **Overview** replaces Injection recovery. Four live status cards
show observation state, search streams, rolling-24-hour injection recovery and
cached-visibility age. An attention strip links to checks that need review.
The cards refresh every 30 seconds while visible and remain labelled **Now**.
Stale or unavailable evidence cannot remain green.
The live recovery card is yellow for 18 or more recovered trials in 24 hours
(including 24/24), orange for 12–17 and red below 12. Missing or empty evidence
stays unknown; stale/incomplete counts are labelled separately. These display
bands do not apply to shorter historical intervals or individual trial markers.

Below, injection recovery and current array/calibration context sit side by
side. A white timeline shows each trial's recorded outcome; click a marker for
details, or expand the trial table and seven-day UTC totals. The station map
uses the Visibilities inspection set, with wired and intended beam membership
reported separately. Its colours describe configuration, not antenna health.
Recorded weights membership and the ledger calibration do not prove runtime activation.

The bottom row shows one purple stream-count heatmap and one raw reference-baseline
dynamic spectrum, with amplitude/phase selection. Click plots to enlarge;
follow their links to Search or the detailed visibility inspector with the same
interval. A single reference baseline is not a whole-array health test.
All history panels share the selected interval and time zone, default rolling
24 hours with two-minute refresh while visible. A historical selection pauses
history, not the live cards. **Live · rolling 24 h** restores rolling.
Automatic views use bounded cache reads only; no injection or telescope job starts.

## Start with recovery and search pressure

Overview retains injection outcomes, trial details, product freshness and array
context. Completed fired trials,
pending trials and firing failures are separate. A missing ledger is
unavailable, not zero failures. The seven-day trend uses UTC dates; the headline
is a rolling interval. Read [injection recovery](injection-recovery.md) before
interpreting a saved replay as live search evidence.

Open **Search (T1)** to see the past 24 hours immediately, then change the interval
if needed. Inspect emitted candidates per stream, beam/time, DM/time and width
distributions. The stream title includes the approximate 8.59-second gulp.
Stream and DM heatmaps show counts per time bin (3 minutes in the default
24-hour view), with logarithmic pale-lavender-to-deep-purple colour scales:
higher counts are darker.
All three panels share the palette and range, from 1 to their largest displayed
count (2 when all counts are zero or one). Colourbars label decades and the exact
maximum, omitting nearby decade labels to keep the maximum readable. The DM
panel counts candidates per DM bucket across all streams, without normalising
each time column. Across all three time panels, off-white means zero recorded
candidates with gulp evidence; grey means no recorded gulp or candidates.
Beam cells use their parent stream's gulp evidence; DM cells use any stream's.
This does not establish whether an individual beam was processed, especially
during capped gulps. Hella's 10,000 raw-peak cap applies
per gulp. Stored candidates are post-clustering: their count cannot establish
whether the raw-peak cap was reached. Red strips on the stream panel show
explicit cap warnings from the gulp log ledger without hiding the count colours.
The top y-axis is stream ID (0–7), each combining 64 beams. A red strip at
the upper edge flags the whole stream/time bin, not a beam position. Candidate
counts are not corrected for skipped beams. Colourbar labels wrap onto two lines.
Log coverage is bounded, not guaranteed full-day coverage. No warning does not prove
a cap-free day. Follow the interval link into visibilities to inspect frequency
structure. RFI, satellites, bad channels and storage problems are investigation
hypotheses until supported by evidence.
Both DM displays span 10–3000 pc cm^-3. All recorded bins/counts remain in
the evidence; no search limit or collector setting is changed by this display.

The white-background Matplotlib figures match Visibilities, with dark labels,
clear time-zone/unit labels, subtle gridlines and muted-blue histograms. Click the
figure for the same zoom, Fit and pan controls; zoom keeps the selected PNG
and interval fixed and does not reread or rebin data. Downloads and the link
to inspect those times in visibilities remain available. The page still
refreshes the rolling window every five minutes. The off-white stream cards use
dark text and full-width coloured status bands with white labels: green OK,
amber late, red silent, grey unknown. Matching top borders reinforce the status.
Gulp age, observed/expected gulps per hour and empty-gulp fraction
remain visible; missing evidence is not displayed as zero. Cards wrap on phones.

## Read the array snapshot

**Visibilities** opens larger white figures grouped by station row, with an
interactive north-up, east-right layout map beside the controls. All 17 antennas
in the saved inspection preset start selected; click map entries to toggle
them off or select other wired inputs. This is an inspection choice, not a
claim about current deployment or antenna health. **Compact panels** packs
occupied positions into up to three columns, with sparse rows sharing space.
Each row's small six-position key shows selected antennas, hidden antennas
(`off`), and positions without a wired antenna (`×`). **Station grid** restores
the aligned physical columns. The full map always retains the station layout.
This removes unused plot space without removing time gaps from the data.

Each antenna panel shows its layout-recorded SNAP, slot and ADC below the
antenna number. **SNAP order** keeps the compact panel sizes but groups by
SNAP/slot and sorts by ADC. Switching arrangements preserves antenna selection
and the loaded snapshot. Matrix wiring is available on hover and in the
enlarged plot; the triangle remains station-ordered.

Choose autos or baselines to a reference, then **Real(V)**, **Imag(V)**,
**|V|**, or **Phase**. Switch between frequency spectra, **Dynamic spectrum**
(time versus frequency), and **All pairs**. Cross-correlations opens in Dynamic
spectrum; autos opens in Spectrum. All pairs is an upper triangle of miniature
dynamic spectra, with autos on the diagonal and no repeated lower triangle.
It loads progressively in bounded batches, ordered by station position.
Cross tiles use `V(target, reference)`; matrix cells use `V(row, column)`;
the reference tile is an auto. The detailed inspector labels the stored
ascending packet pair, which can have the conjugate phase/imaginary sign.

The default is Raw and a 24-hour rolling cache window. Spectra select the latest
integration unless Window mean is chosen. The page refreshes each minute while
visible, showing the actual sample date/time and age even when the cache is
stale. Window averaging and
Sun fringe stopping are explicit options. Spectrum plots retain cached
channels; dynamic previews reduce frequency to at most 128 bins and retain
every recorded integration. Spectrum axes are Frequency (MHz) and the selected
quantity: counts for Real(V), Imag(V) and magnitude, radians for phase. Counts
are correlator units, not Jy. Dynamic-spectrum axes are time (with time zone)
and Frequency (MHz); the colourbar labels the quantity and units. Phase has a cyclic
−π to π scale, signed values a symmetric scale, magnitude a logarithmic scale.
These per-baseline colour limits do not normalize the data; compare the labelled
ranges, not brightness alone. Zero-amplitude phase is blank.
Intermediate axis ticks use rounded frequencies and clock times, with denser
frequency labels when enlarged. Tick spacing follows available plot space to
avoid overlap; dates sit beneath the time axis rather than on every tick.
Autos and crosses share the same rolling-window control. Enlarged plots and
detailed Matplotlib figures use white backgrounds too. Opening a detailed
plot from the array keeps the rolling window and minute refresh; choosing a
historical date or explicit range pauses it. Phones stack the larger panels.

Click any plot surface, matrix thumbnail or detailed PNG to enlarge it. The
viewer offers +/−, Fit, double-click zoom and drag/scroll panning; Escape closes
it. This changes display size only, not averaging or samples. A matrix
enlargement pins its selected snapshot and shows full axes and a colourbar.
Use **Open stored-pair plot** for the detailed cached-channel view and downloads.
Matrix thumbnail size can be increased; sticky station labels stay visible
while scrolling. The lower triangle is intentionally blank. Loading cells are
labelled separately from missing/undefined data pixels.

## Select a detailed baseline and render

Open **Detailed baseline inspector** from Visibilities. Defaults select a few long N-S baselines from matched
recorded payload membership when available; the interface discloses an
intended-layout fallback. Choose by physical length, orientation or station.
The nearby-row filter is a geometric separation filter, not a verified plank
adjacency graph. Hardware identities remain in the selection/provenance panel.
At most six pairs are rendered together.

Choose today, another date or explicit bounds, then a frequency range.
Select a phase/amplitude/real/imaginary dynamic spectrum, frequency spectrum
or autocorrelations. Spectrum views default to the latest integration, with
an explicit window-mean option. Raw is the default; Sun fringe stopping remains
an explicit choice. Both processing modes reuse the
existing scientific modules. Cached views load automatically and update when
controls change. Native reads and calibration comparisons still require
**Render selection**. Narrow the bounds to examine a
feature. Every product provides PNG, numerical NPZ and JSON provenance downloads.

Raw retains every available integration, including the first integration in each
recording file; the eight-channel averaging option remains available. Sun
fringe-stopped views retain the same samples. Actual missing timestamps or values
still appear as gaps. Before 2026-09-24, a blanket file-boundary exclusion created
regular white stripes in continuous data. Re-render those views to obtain the
corrected products; saved historical artifacts remain unchanged.

The selection and plot clock defaults to OVRO local time, using PDT/PST for
the actual date. A UTC toggle changes the displayed clock, not the selected
instants. Date buttons use local midnight in the selected zone. API timestamps
remain UTC. A nonexistent spring-forward local time is rejected; a repeated
fall-back hour selects the earlier occurrence, with UTC available to select
the later one. Local dates can span 23 or 25 hours across these transitions.

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
Amplitude dynamic spectra show magnitude without per-channel normalization;
the legacy channel-normalized [solar rendering](solar-waterfall.md) remains an
explicit API option. Magnitude means average `|V|`; phase uses the angle of
the complex mean, never a mean of wrapped angles. Real and imaginary values
retain their signs. Autos are not squared again. Correlated amplitude is not
calibrated solar flux or a coherent-beam recording. Gaps, estimator,
normalization scope and actual timestamps remain in the product. Solar
variability and low-signal phase structure alone do not establish a fault.

## Compare calibration-day phase

Open **Calibration-day comparison**. The recorded calibration reference supplies
its actual solve window and antenna set from a matching saved recipe report.
Choose today or another local day; both windows are shown before reading data.
The default is one long N-S baseline, with up to three selectable.
**Read both windows and compare phase** explicitly reads at most one hour and
64 MiB of selected native samples per window. An unfinished matching window
requires choosing an earlier day. A missing report is unavailable, not a
filename-derived date. Matching local clock time is only a starting point;
review solar geometry and analog changes. The tool compares Sun-fringe-stopped
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

Readiness opens with **What needs attention?**, using existing monitor flags
and evidence ages. Disk capacity and short observation/data-flow checks follow;
the full measurement table is expandable. A stale check is not proof of failed
hardware, and a high disk percentage is not authority to delete data.

**Antennas** starts with saved 4096-channel board spectra, using the existing
scientific renderer on black surfaces, with frequency/power axes and PNG
downloads. Each board's acquisition time is shown in OVRO local time.
**Get latest spectra** explicitly submits the existing bounded diagnostic job
through the production monitor queue, preserving its lease and cooldown.
The reader selects the diagnostic autocorrelator mux and arms readout; this
is not literally zero register writes. It does not program, change EQ,
synchronize PPS or change observing configuration. Navigation only reads saved
products; job state and overdue evidence remain separate from page refresh.
The configured two-hour scheduler has a shared-liveness-timer starvation bug.
The tested independent-timer fix is in the preview source, awaiting approval
to update and restart the production monitor collector. Two-hour acquisition
is not yet guaranteed. No duplicate reader or preview scheduler is added.
**Selected input history** retains the roughly last-hour transmitted-band
cache view, bounded to 256 MiB, refusing averaging that could hide gaps.

**Source history** opens B0329 detection dates with large saved PDMP plots
from filterbank dumps. Click a plot to zoom; **Notes & saved plots** holds the
full observing notes and other folds. **All observations** includes nulls,
disputed attempts and withdrawn claims. Missing images do not remove dates.
Older successes without the literal word “detection” use reviewed exact-row
overrides, not a guessed S/N threshold. Same-day rows share a card while
retaining their individual notes. Opening history does not fold or dump data.
Searching **Sun** or **cyg-a** shows dated source-tracking beam dynamic spectra
from native visibilities, ±1 hour around transit, with white axes, local times,
a transit marker and click-to-zoom. The latest deployment-ledger calibration
is the default for every date; its filename is visible and it is not claimed
to be the calibration deployed on each historical date. All of that calibration's
antennas must be present in the dated wiring. This set can differ from the
Visibilities inspection preset.

These plots show signed, calibrated cross-power with autos excluded, not total
tied-array power or Jy. No background subtraction or channel normalization is
applied. Calibration and tracking happen at native frequency resolution before
display averaging; actual gaps remain blank. Available history is limited to
the native cache, normally three days. Older averaged data are not silently
substituted. This is a read-only display, separate from PDMP folds and the
stationary-beam calibration test; it neither records data nor builds weights.

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

Source revision `07c39a8`, branch `observation-preview`. Source checkout:
`/home/casm/software/dev/casm_monitor/.claude/worktrees/observation-preview`.
The owning manuals are `docs/api-science.md`, `docs/api-review.md`,
`docs/api-commissioning.md` and `frontend/README.md`.
Artifacts and the review database are isolated under
`/home/casm/scratch/casm-observation-preview`. Production monitor Store handles
are read-only. Workspace-local rendering, queue persistence and explicitly
confirmed builds are authorized exceptions. The separately authorized SNAP
diagnostic button bridges only its fixed production queue endpoint; general
operational jobs remain disabled.

This guide supersedes the fixed-baseline preview at `369c34e`, which the
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

Verification on 2026-09-13 local date: 541 backend tests passed, followed by
69 focused checks covering the final plot labels and native-reference guard.
Browser checks cover raw default phase, dark SNAP spectra, product-led comparison,
automatic plots, local/UTC switching, historical dates and simplified Readiness.
`frontend/check-time.cjs` checks PDT/PST, DST gaps/repeated hours and 23/25-hour
days. Bounded real-data renders in the initial workspace verification exercised phase
comparison, amplitude, autos and a short Cyg A/control interval. The selected
last-hour transmitted-band SNAP cache was unavailable and returned an explicit
404; fixture tests cover that adapter. No Kafka repair or hardware query was
attempted. Evidence is in the source checkout's check scripts and
`/home/casm/scratch/casm-observation-preview/science-validation.json`.
