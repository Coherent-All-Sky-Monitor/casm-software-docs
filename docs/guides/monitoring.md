# Investigate an observation

The dark monitoring workspace runs at **http://localhost:8061/**.
The tabs are Overview, Search (T1), Visibilities, SNAPs, Source history,
Candidates and Calibration. The legacy web services on 8060 and 8050 were
stopped and disabled September 25, 2026. Collectors, workers, T2/T3 processing,
scratchpad on 8501 and Medusa remain unchanged. Forward port
8061 to use the preview remotely. The page background is black and no Plotly
code is loaded. Imaging is removed from this preview's navigation and frontend
routes because the operator rejected its current plots. Other viewers and
the existing scientific/backend imaging implementation remain unchanged.

Navigation labels are larger and semibold, with pale text on dark-blue tab
surfaces. The selected tab uses a brighter fill, border and underline; keyboard
focus has its own outline. Tabs wrap on narrow screens without hiding names.

The opening **Overview** replaces Injection recovery. Four live status cards
show observation state, search streams, rolling-24-hour injection recovery and
cached-visibility age. An attention strip links to checks that need review.
The cards refresh every 30 seconds while visible and remain labelled **Now**.
Stale or unavailable evidence cannot remain green.
The live recovery card is yellow, labelled **Needs attention**, for 18 or more recovered trials in 24 hours
(including 24/24), orange for 12–17 and red below 12. Missing or empty evidence
stays unknown; stale/incomplete counts are labelled separately. These display
bands do not apply to shorter historical intervals or individual trial markers.
The top-right CASM photograph opens in the same click-to-zoom viewer as the plots.
It is a supplied still image, not a live camera; the complete frame is retained.
The title names the telescope **Coherent All Sky Monitor (CASM)**, with
Owens Valley Radio Observatory, Big Pine, California on a separate location line.

Below, injection recovery and current array/calibration context sit side by
side. A white timeline shows each trial's recorded outcome; click a marker for
details, or enlarge the timeline and zoom. The station map
shows all wired inputs: green/BF marks the inspected nonzero coherent-beam weights
in the latest recorded deployment; blue marks other wired inputs. Unknown
membership is explicit. Colours describe membership, not antenna health.
Recorded weights membership and the ledger calibration do not prove runtime activation.

The bottom row shows one purple stream-count heatmap and one raw reference-baseline
dynamic spectrum, with amplitude/phase selection. Click plots to enlarge;
follow their links to Search or the detailed visibility inspector with the same
interval. A single reference baseline is not a whole-array health test.
All history panels share the selected interval and time zone, default rolling
24 hours with two-minute refresh while visible. A historical selection pauses
history, not the live cards. **Live · rolling 24 h** restores rolling.
Automatic views use bounded cache reads only; no injection or telescope job starts.

## Current page and resource use

The Overview below was captured on September 25, 2026 in OVRO local time from
the working preview. It is a saved example, not a live status image. The monitor
README includes current Search, Visibilities, SNAPs, Candidates and source-history
screenshots; its `docs/screenshots/2026-09-25-latest/manifest.json` records capture
times and image hashes. No Calibration actions or hardware reads were requested.

![Overview with injection timeline, array context and rolling plots](../_static/monitor/2026-09-25-latest/overview.png)

The September 24 warm-cache sample measured about 0.6 GiB of preview-process resident memory
and 0.2% of one CPU core over a quiet 20-second interval. Plot rendering causes
short CPU bursts; first native source-date loads took about 15 seconds. These
are shared-host measurements, not a cold-load capacity test. The preview's
4 GiB service limit includes filesystem cache. Collector and offline workers
are separate services; their cgroup totals can contain much more file cache
than their main processes' resident memory.

Preview products live under `/home/casm/scratch/casm-observation-preview` on
the root disk: `science/` for PNG/NPZ/metadata, `t1_products/` for Search PNGs,
`snap_views/` for saved SNAP renders, and `calibration/` for the separate worker.
This tree measured about 1.5 GiB. Production input caches remain under
`/mnt/nvme3/casm_monitor`; the T2 ledger and registry on NVMe5 are read-only
inputs to these pages, not where the preview writes new plot products.

Native/avg8 shard TTLs are three/60 days. **They do not expire preview render
files**: those currently accumulate without an automatic reaper. Source-beam
and array-overview responses are bounded memory caches. Source history loads
on selection/search, separate from the rolling overview refresh.

Exact counters, capture timestamps/hashes and limits are recorded in
`casm_monitor/docs/screenshots/2026-09-24/measurements.json`; the owning guide is
`casm_monitor/docs/resources-and-storage.md`. Regenerate the evidence with
`casm_monitor/scripts/capture_monitor_docs.py`, not with mocked browser results.

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
Both DM displays use logarithmic spacing over 10–1000 pc cm^-3 by operator
choice. The bottom histogram keeps linear counts per existing log-spaced bin,
with the y-axis labelled "Candidates".
The width histogram shows indices 0–6 with integer ticks and linear counts;
spare width bins 7–8 remain in stored/API evidence, outside the display and its
scaling. The September 25
read-only configuration check confirmed that all eight streams search 0–1000;
the 0–10 bucket is omitted only from the DM figures and their scaling, remaining
in stored/API evidence and the stream/beam totals. Stored edges
and counts are unchanged; the approximately 922–1122 bin keeps its full count
but ends visually at the 1000 display limit. No within-bin split is inferred.
All bins, including those outside the displayed range, remain in evidence JSON.
No production search limit or collector setting changed.

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

The main navigation is a single row: Overview, Search (T1), Visibilities, SNAPs,
Source history, Candidates and Calibration. There is no top-right tab group or
Readiness tab. Labels are text-only, with a high-contrast selected underline.
The larger title/Big Pine location and separate local, UTC and local-sidereal clocks frame the
Overview. All three array maps use larger keys on white cards: green for
recorded beamforming members, blue for other wired inputs, × for no antenna.
Map clicks only show/hide plots. Configuration details remain expandable.
Visibilities and SNAPs have a shallower header and wide compressed maps so the
first plots appear sooner. Touch targets remain larger on coarse-pointer devices.
The Overview trial-history/seven-day table disclosure is removed. Click its
injection timeline for zoom, then a trial for details. Data figures throughout
the current routes use the shared Fit/zoom/pan viewer, including candidate
statistics, Calibration galleries and saved review images; maps retain selection.

![Earlier September 25 preview tab bar; icons shown in this historical capture have since been removed](../_static/monitor/2026-09-25/navigation-latest.png)

**Visibilities** opens larger white figures grouped by station row, with an
interactive north-up, east-right layout map beside the controls. Its default
selection follows the inspected nonzero slots in the current recorded coherent
beam weights, matching Overview and SNAPs. Green marks those inputs; blue marks
other wired antennas and dashed borders mark hidden panels. Click entries to
toggle them. Manual selections survive refresh; the Beamforming preset follows
membership updates. Missing or mismatched inspection evidence gives an unknown
membership notice, not a substitute selection. This is recorded deployment
membership, not live hardware readback or an antenna-health verdict. **Compact panels** packs
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

## Candidate plot gallery

Candidates opens the latest 12 events with saved plots as a white-panel grid.
Choose 6, 12, 24 or 48 panels. The compact right sidebar lists up to 500 filtered
events, supports name/date/beam/label search, and outlines rows marked Shown.
Click an event to bring its image into the grid; click again to hide it.
Missing plots show the recorded outcome. Manual selections stay fixed while
the list refreshes every 15 seconds; Latest N restores the rolling selection.
Every image uses the shared zoom/pan viewer, including on event-detail pages.
Original PNGs are served unchanged; gallery browsing neither labels candidates
nor requests dumps or pipeline actions. On mobile the selector sits above the grid.

```{figure} ../_static/monitor/2026-09-25/candidates-grid.png
:alt: Saved candidate plots on white panels beside a compact selectable list

September 25 UTC: real saved candidate images; outlined sidebar rows are displayed.
```

## SNAPs and source history

Readiness opens with **What needs attention?**, using existing monitor flags
and evidence ages. Disk capacity and short observation/data-flow checks follow;
the full measurement table is expandable. A stale check is not proof of failed
hardware, and a high disk percentage is not authority to delete data.

**SNAPs** opens saved 4096-channel, 375–500 MHz board spectra on white panels,
with compact SNAP order by default. Compact station order, a six-position
station grid and an all-12-ADC switch are also available. The default is every
input in the latest recorded deployed coherent-beam weights (16 of 24 wired
inputs on September 25). Membership comes from a bounded offline inspection
of every stored channel/polarization/beam, matched to the six streams' latest
registry association and current board/ADC wiring. It does not use the layout's
intent flags or assume runtime readback. Unknown/mismatched evidence never
becomes an active input. All wired and all-12-ADC views remain available, with
green borders and Beamforming badges on deployed members. Station/antenna and
SNAP/slot/ADC labels appear together; status and expandable read-detail boxes
show IPs. The layout key shows all wired inputs, green/BF versus blue, and
marks empty positions. History retains explicitly current membership.

The preview membership cache can be refreshed with the offline
`scripts/check_beam_membership.py --output-root /home/casm/scratch/casm-observation-preview`
command. Only the small preview JSON is written; weights, wiring and hardware
remain unchanged. GETs never inspect the large weights payload. A new deployment
without matching cached inspection stays Unknown.

Spectra default to `10 log10(native power / 10⁻¹⁰)`, not dBm: the same fixed
reference across antennas and dates. Power-reference/scale/refit controls have
been removed; stored native values are unchanged.
The September 25 saved-data audit checked the native descending-frequency
mapping against visibility autos 21–26 seconds away; it did not reverse the
axis. A separately approved stale-TFTP-session release restored management
reads without reflash/re-sync. The subsequent PPS check measured zero delta on
SNAPs 0/2 and a stable −1 TT tick on 1/3, of unknown onset. Streaming alone
does not establish alignment. The monitor manual and wiki's
`snap-control-frequency-followup.md` record the frequency and timing checks.
All panels share 374.9–500.1 MHz and power limits covering every finite displayed
channel with padding. There is no percentile clipping; limits update with saved
reads and selection changes. Expanded spectra share those limits. All native channels are retained;
channel centres descend from 500 to 375.030518 MHz at 125/4096 MHz spacing.
History/overlay selectors are removed; the page shows the latest saved spectra.
The all-12-ADC control is a prominent labelled switch. Click a panel for its
enlarged spectrum and saved 30-day full-band power trend. The trend
averages all 4096 linear-power channels before converting to dB; an incomplete
band yields a missing point. Focused trend axes reveal drift in absolute dB.
Gaps and EQ/FFT-epoch changes break lines. Zero-power channels have no finite
dB value and are counted separately. Historical labels use current wiring;
comparisons track board IP and ADC.
The preview starts fresh history at September 25 05:12:31 UTC. Earlier spectra
are retained, not deleted; `archive=true` exposes them in the API. The default
trend and catalogue queries share the configured display epoch.

```{figure} ../_static/monitor/2026-09-25/snaps.png
:alt: Six stored SNAP 0 spectra with white axes, a fixed positive-reference dB scale and shared frequency limits

September 25 UTC preview: saved full-band SNAP 0 spectra. The capture only read
saved data. Orange clipping markers in this earlier capture are superseded by
the full-data shared limits now used on the page.
```

SNAPs has no extra Visibilities/transmitted-band submenu. Its white plots
include the enlarged full-band power trend.
Separate Streaming and PPS timing boxes also appear on the main Overview.
SNAP status chips have white backgrounds, larger labels and UTC timestamps.
Streaming OK means nonzero cached data from all wired inputs within 15 minutes,
not an instantaneous packet-counter test. A nominal PPS period cannot establish
cross-board alignment. Each all-antenna spectrum job now runs the same bounded
getter-only comparison as `scripts/check_snap_timing.py`, sequentially after
spectra under the same persisted lease. It requires two advancing common-edge
TT frames and publishes the newest attempt to the monitoring database, including
failures. The API chooses the newer database/local-JSON attempt, valid for
90 minutes; page refresh never contacts hardware. The hourly hook was installed
in the running monitor checkout at September 25 06:38 UTC; no observing service
or worker restart was needed. **Do not use `--sync-only` as a check**:
the configuration CLI flag changes synchronization. Control-read failure also leaves firmware state unknown,
even if the old reader reported `programmed=False`. The reader correction is
staged with the pending monitor-worker rollout, not deployed to production.
Job 863 subsequently completed an automatic spectra-plus-PPS cycle at
September 25 07:14:51 UTC, retaining all four accepted offsets.
Strict exact-match PPS results remain unchanged in the API. Displayed **PPS
timing** compares with explicitly accepted offsets: September 25's accepted
SNAP 0/1/2/3 reference is 0/−1/0/−1 ticks versus SNAP 0. Fresh advancing PPS with
unchanged offsets is green; changed offsets/reference or stopped PPS is red
Needs attention. Missing/failed/stale checks remain Unknown. The monitoring
database baseline never updates automatically; `--accept-saved-baseline`
requires fresh complete saved evidence and explicit operator approval.
Source-check records no longer gate this status, and no source re-check runs
hourly. A green accepted offset does not claim exact sample alignment.

The existing `snap_read` Zarr stream and SQLite manifest on NVMe3 supply this
history, without expiry or new preview disk products. Four boards acquired
hourly would add about 18 MiB/day of uncompressed array data. Trend reads have
a 512 MiB budget and an eight-selection memory cache; long selections can
require a shorter interval. Timestamps are per-board UTC, and stale successful
reads remain distinct from later read failures.

**Ping now · get spectra** explicitly submits the existing bounded diagnostic job
through the production monitor queue, preserving its lease and cooldown.
The reader selects the diagnostic autocorrelator mux and arms readout; this
is not literally zero register writes. It does not program, change EQ,
synchronize PPS or change observing configuration. Navigation only reads saved
products; job state and overdue evidence remain separate from page refresh.
Hourly acquisition was activated at September 25 05:30 UTC by applying the
independent scheduling slot and 3600-second interval to the running locked
monitor checkout. Only `casm-monitor-collect.service` restarted. Completed
manual reads postpone the next automatic pass by one hour; the scheduling tick
can add up to one minute plus queue delay. Five scheduler fixture tests passed
against that checkout. Acquisition timestamps, not the configured label, verify
ongoing cadence. No observing-pipeline change, duplicate reader or preview
scheduler was introduced. The old `/antennas` URL remains for bookmarks.
**Selected input history** retains the roughly last-hour transmitted-band
cache view, bounded to 256 MiB, refusing averaging that could hide gaps.

**Source history** opens B0329 detection dates with large saved PDMP plots
from filterbank dumps. Click a plot to zoom; **Notes & saved plots** holds the
full observing notes and other folds. **All observations** includes nulls,
disputed attempts and withdrawn claims. Missing images do not remove dates.
Older successes without the literal word “detection” use reviewed exact-row
overrides, not a guessed S/N threshold. Same-day rows share a card while
retaining their individual notes. Opening history does not fold or dump data.
The source bar offers **B0329** (default), **Sun**, **Cyg A**, **Cas A** and
**Tau A**. The latter four show native-visibility dynamic spectra with a
band-averaged power curve below each image. The beam stays fixed at the source's
transit altitude/azimuth, with a ±2-hour window for the crossing and shoulders,
white axes, local times, a transit marker and click-to-zoom. The latest deployment-ledger calibration
is the default for every date; its filename is visible and it is not claimed
to be the calibration deployed on each historical date. All of that calibration's
antennas must be present in the dated wiring. This set can differ from
a manually selected Visibilities view. Newly generated trial calibrations do
not change the default: it follows uploaded weights recorded in the deployment
ledger. The latest three completed four-hour windows per source are retained
in browser Cache Storage, with a tab-memory fallback. Switching sources keeps
loaded figures and in-flight reads. Only a new completed date replaces the
oldest figure; changed deployed calibration/layout identities invalidate reuse.
Only the small catalogue polls, every five minutes while selected. Browser
storage is not a permanent server archive; clearing it requires native cache
coverage to rebuild a figure.

These plots show signed, calibrated cross-power with autos excluded, not total
tied-array power or Jy. No background subtraction or channel normalization is
applied. Calibration and fixed geometric phasing happen at native frequency
resolution before display averaging. The curve averages the same fixed set of
usable native channels, without time smoothing or taking an absolute value;
missing channels/integrations leave gaps in the curve. Reads are sequential
groups of at most 26 integrations, at most 110 per four-hour window. Available history is limited to
the native cache, normally three days. Older averaged data are not silently
substituted. This is a read-only display, separate from PDMP folds and the
calibration comparison workflow; it neither records data nor builds weights.
A transit curve tests the applied calibration and phasing, not the quantized
weights uploaded to hardware. Other sources/RFI and incomplete coverage can
affect its peak; it is not an automatic calibration verdict.
The current one-maximum-per-UTC-date helper has a known rollover limitation:
Cyg A has two real transits on November 19, 2026 and one is omitted. Present
September views are unaffected. Event-based catalogue handling remains to be
implemented. The source page does not call the assumed Sun-flux model or
convert counts to Jy; a Sun-scaled absolute overlay needs an independently
checked flux/element-response calibration.

![Sun fixed-transit waterfalls and matching band-averaged power curves](../_static/monitor/2026-09-24/sources-sun.png)

September 24 preview: Sun transits from the native cache, using
`cal_sep17_core16_exact512.h5` for all shown dates. The signed cross-power is in
weighted correlator counts, not Jy; the plotted transit marker is the expected
position crossing, not a fitted peak or a detection claim.

## Calibration workspace

As of September 25, 2026, **Calibration** has Prepare, Solve & inspect,
Validate on sky, Generate beams, and Upload dry run views. Larger controls,
green antenna selections, white phase/transit figures, plot grids and click-to-zoom
match the rest of the workspace. Saved plots precede collapsed settings.
The old typed-UUID
Commissioning page is superseded. A reviewed solar solve freezes a private
layout and runs the canonical driver without generating a grid. Solve and static
windows and phase views each accept up to four hours; job execution resource
caps still apply. Saved recipes,
diagnostics, notebook, job log and cancellation survive page changes and web
restarts through a separate durable worker. Production monitor data stay read-only.

The phase explorer shows both 1D wrapped sawtooth curves and frequency/time
phase waterfalls for raw, fringe-stopped and fixed-delay-subtracted stages,
with Sun/Cyg A/Cas A diagnostic directions. Canonical recent-day comparisons
use matched solar windows with the solve's duration, up to four hours per day.
The sky check uses five-hour stationary-beam
visibilities, complex off-source subtraction, common antenna/channel masks,
signed power, normalized shape, and per-channel timing relative to an exact
ideal array-factor model. Low-S/N or edge-peaking channels do not get a timing
measurement. Rank-1 and peak/off-RMS are not absolute sensitivity measurements.

Grid generation separately reuses the saved calibration for exactly 512 exact
pointings and a matching IB product. Custom/factorial cells are not preserved.
The default sky illustration restores schematic ellipse footprints and dated
Sun/Cyg A/Cas A/Tau A tracks beside altitude versus UTC. Saved pointing coordinates
and source tracks remain exact; ellipses never supply transit times or coverage
scores. Full exact-response product checks remain available in a disclosure.
Scientific review precedes the hash/layout/scale-protected local dry run.
**Live upload is blocked by this workspace**, including when parent settings
are armed. Dry-run generation supplies `--no-registry` and omits both upload
and save-defaults flags. No trial becomes the deployed reference automatically.
Stage checks require 512 CB payload beams and matching metadata/pointing rows.
Transfer, registry, restart defaults and runtime activation are distinct;
the current reference box reports the deployment ledger, not fresh GPU identity.

September 25 acceptance reused an existing offline calibration for phase and
five-hour Cyg A renders, and generated 12 local CB/IB DADA files. Hashes of the
recorded deployed HDF5s, ledger and registry were unchanged. This is interface
acceptance, not scientific approval of that candidate. The source report is
`casm_monitor/docs/reviews/2026-09-25-calibration-and-web-retirement.md`.

Read `casm_monitor/docs/calibration-workspace.md` for APIs, service setup,
acceptance scripts and first-version limitations, and the
[canonical build walkthrough](generate-weights.md) for the scientific recipe.
Actual source/static coverage and hardware-epoch compatibility require review;
the proposed date/window is not an automatic certification.

## Implementation and documentation review

The active 8061 checkout is `/home/casm/software/dev/casm_monitor`, branch `main`.
September 25 source revisions: monitor `ed40e44`, scientific review/plotting
helpers `casm_vis_analysis` `8563fcf`, and T3 retirement documentation `c38c44d`.
The paired operational wiki update is `fca42ef`. No changes were pushed.
The earlier isolated preview was `07c39a8` on `observation-preview`.
The owning manuals are `docs/api-science.md`, `docs/api-review.md`,
`docs/api-commissioning.md` and `frontend/README.md`.
Artifacts and the review database are isolated under
`/home/casm/scratch/casm-observation-preview`. Production monitor Store handles
are read-only. Workspace-local rendering, queue persistence and explicitly
confirmed builds are authorized exceptions. The separately authorized SNAP
diagnostic button opens a short-lived handle for the existing atomic `snap_read`
submission after origin, CSRF and confirmation checks. It no longer depends
on a second web service. The existing lease/cooldown and hourly worker remain;
general
operational jobs remain disabled.

This guide supersedes the fixed-baseline preview at `369c34e`, which the
operator rejected as insufficient. The shared solar renderer remains
`casm_vis_analysis` `af8ecd0`. This change affects monitor APIs, defaults,
evidence persistence and build admission; source-local manuals and this guide
are updated together under [documentation maintenance](../maintaining-docs.md).
The preview also corrects a singleton-baseline Sun-delay broadcasting bug in
the monitor adapter. Old singleton Sun-reference views require re-rendering;
the retired legacy web checkout did not receive that fix. Unmocked canonical
transform/render tests cover the corrected time/baseline axes.
The September 22 Calibration workspace adds maintained scientific review
helpers and an optional dynamic-spectrum return in `casm_vis_analysis`.
The central API source snapshot remains historical: its refresh is blocked by
a configured `casm_calibrator/calibration.py` path that no longer exists.
The maintained guide is updated; the Sphinx, local-link and export checks pass.
Historical tutorial figures are preserved without rerunning their jobs.
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
