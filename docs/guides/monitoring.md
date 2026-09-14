# Monitor the current observation

The observation preview reorganizes the existing `casm_monitor` into three
tabs: Observation, Readiness and Antennas. It runs separately on port 8061;
the existing monitor on 8060, T2/T3 on 8050, scratchpad on 8501 and Medusa
remain available. The preview rejects write requests and reads the production
monitor database without migrating or modifying it.

## Observation

Read the solar-context diagnostic and injection recovery together. The solar
panel uses the existing `casm_vis_analysis.solar_waterfall` rendering style on
the last 24 hours of cached antenna 9 × 19 visibility amplitudes. The baseline
is resolved through the current layout and named in the caption. No raw
visibility recording is opened and no calibration or background subtraction
is applied. The cache contains 8-channel complex averages; their magnitudes
are correlated amplitude, not a recorded beam-power stream or solar flux.
Other sources and interference can contribute.

Each channel is divided by its mean over the displayed interval. The middle
panel preserves the unnormalized spectrum and the lower panel shows light
curves. Gaps remain visible. The nominal integration is about 137 seconds;
these data cannot reproduce the fast structure in the historical filterbank
[solar waterfall](solar-waterfall.md). Stored timestamps are displayed without
claiming an independently validated integration start/centre/end convention.

The injection summary separates completed fired trials from firing failures,
pending and unknown outcomes. Counts cover today in UTC; the trend covers
today and six preceding UTC dates. A 5,000-row limit makes exceptionally busy
windows explicitly incomplete. A missing ledger is unavailable, not zero
recoveries. Compare similar DM, width, S/N and observing conditions before
interpreting a recovery fraction.

Saved replay plots contain a synthetic pulse added to recorded background.
Matched search clusters establish live recovery. A recovered trial can have
no saved plot. The preview serves only existing allowlisted PNG, JSON and
filterbank artifacts; opening it does not generate a replay or trigger a dump.
See [injection recovery](injection-recovery.md) for the full evidence chain.

## Array membership and freshness

The geometry distinguishes current wiring, intended participation and the
recorded product's populated slots. Select a beam to see its membership:
the global HDF5 mask and a filename antenna count are insufficient for mixed
products. Current layout and product coordinates are different evidence and
must not silently replace each other across epochs.

The worker scans at most 400 MiB of uncompressed weights once per changed
product, testing every channel/polarization/beam. It caches by product ID,
resolved path, size and modification time. Latest registry entries for all
six streams must agree before the preview reports a deployed union. This is
recorded deployment evidence, not a fresh audit of running node memory.

Acquisition time, rendering time and last successful check are separate.
An advancing page clock does not make an old figure current. LST is mean
sidereal time from installed offline tables, intended for display.

## Readiness and antenna investigation

Readiness groups existing service/search/events/calibration views. Antennas
groups SNAP and visibility inspection, including interactive time/frequency
cuts, phase and amplitude views. Cached figure manifests refresh every minute;
the page does not request new hardware acquisition. The interactive SNAP
history starts with approximately the last hour. Full-board spectra keep
their actual acquisition ages and existing polling policy.

Cross-day fixed-calibration tools, matched stationary Cyg A model overlays,
layout exclusion persistence and operational controls are later work.
Higher solve rank-1 and solar day-to-day variability are not standalone beam
sensitivity or fault criteria. The [calibration check](check-calibration.md)
explains the independent-source comparison.

## Development and review

Source: `/home/casm/software/dev/casm_monitor/.claude/worktrees/observation-preview`,
branch `observation-preview`, revision `369c34e`, with shared solar renderer
`casm_vis_analysis` revision `af8ecd0`; API and preview instructions are in that
repository's `docs/api-observation.md`. Figures and verification artifacts
are isolated under `/home/casm/scratch/casm-observation-preview`.
The existing production checkout and services are unchanged. Fourier Space
code, including Kafka, is outside this implementation; Grafana is deferred.
This preview has no figure-refresh worker: the saved solar product ages until
an explicitly requested bounded render. The overview polls existing status
and injection records; this does not make the saved image newly acquired.
Source changes follow [documentation maintenance](../maintaining-docs.md).
