# Follow an injection through the search

An injection checks whether a known synthetic pulse makes it through the
search. Start with the ledger, then inspect the saved plot. The reading steps
touch nothing live; the commands that fire or replay a shot are in the last
section.

## Read the frozen example

From the documentation checkout root, read the retained record. This record
and the figure below describe the same archived shot; the live ledger may
later be reconciled or its archive paths removed.

```python
import json
from pathlib import Path

from casm_t2.inject_outcome import label

records = json.loads(Path("docs/_static/tutorials/injections/frozen-records.json").read_text())
shot = records["inj_20260913_0023"]
print(shot["file_id"], label(shot["outcome"]))
print(f"S/N: {shot['inject_snr']:.2f} injected, {shot['rec_snr']:.2f} recovered")
```

## Query the live ledger separately

In `casm_offline_env`, open the live ledger read-only:

```python
import sqlite3
from casm_t2.inject_outcome import label

connection = sqlite3.connect(
    "file:/mnt/nvme5/casm_pipeline/db/t2.sqlite?mode=ro", uri=True,
)
connection.row_factory = sqlite3.Row
shot = connection.execute(
    "SELECT file_id, inject_utc, beam, dm, inject_snr, rec_snr, "
    "rec_dm, rec_beam, outcome, fail_reason, replay_png "
    "FROM injections WHERE file_id = ?",
    ("inj_20260913_0023",),
).fetchone()
if shot is None:
    connection.close()
    raise LookupError("This historical shot is no longer in the live ledger")
print(shot["file_id"], label(shot["outcome"]))
print(f"S/N: {shot['inject_snr']:.2f} injected, {shot['rec_snr']:.2f} recovered")
connection.close()
```

For this archived shot, the output is:

```text
inj_20260913_0023 recovered
S/N: 21.93 injected, 25.13 recovered
```

| Quantity | Injected | Recovered |
|---|---:|---:|
| Beam | 141 | 141 |
| DM (pc cm⁻³) | 386.43 | 386.00 |
| S/N | 21.93 | 25.13 |

The search found a matching cluster. This does not mean every pipeline stage
measures S/N identically: the injected estimate, search statistic and offline
plot's boxcar statistic use different calculations.

## Inspect the saved plot

In a notebook, display the retained artifact, independently of the live row:

```python
from IPython.display import Image, display

display(Image(filename="docs/_static/tutorials/injections/inj_20260913_0023.png"))
```

```{figure} ../_static/tutorials/injections/inj_20260913_0023.png
:alt: Injection 0023 replay with a dedispersed pulse, frequency-time waterfall, DM search, candidate context and beam position.

Saved replay for inj_20260913_0023. The pulse is re-added to an upstream dump
for this diagnostic; this is not a recording of the live injected stream.
The matching search event is at 2026-09-13 22:27:02.351 UTC.
```

The dedispersed profile and waterfall put the pulse at zero time. The DM-time
panel shows how its significance changes with the trial dispersion measure.
The bottom panels show the nearby T1 candidates and the detection beam on sky.

The title's `width = 33.6 ms` is the 32-sample trial label, not the injected
pulse's FWHM. This shot's injected FWHM was 23.3 ms; the matching hella kernel
has a FWHM of about 22.0 ms. Use `casm_t2.hella_kernel.kernel_fwhm_ms` when
comparing recovered widths.

Since 2026-09-22, `t3-replay-injection` always dedisperses and quotes the
title at the ledger DM (386.43 here, rounded to 386.00), not a matched
cluster's recovered DM. The injected FWHM, amplitude and S/N, and hella's
recovered S/N and DM, are written as one line to the card JSON's
`injection.summary` field for the Slack thread; they never appear in the
figure title.

The ledger's `inject_utc`, 22:27:24.976 UTC, records when the injection was
sent. The event time in the plot describes the searched samples, which were
already buffered. Do not equate the two timestamps.

## Read a miss before diagnosing it

Shot `inj_20260913_0021` was recorded as `missed_t1`. Its ledger reason says
no matching trial was found in beam 49 or its eight sky neighbours within the
matching time and DM window. Its requested DM was 886.65 pc cm⁻³ and injected
S/N was 20.61. There is no saved replay PNG in that row.

That locates the missing evidence at T1. It does not establish why the search
missed the pulse. Inspect the trial stream and observing conditions before
changing thresholds, beamforming or hardware.

The outcome categories have distinct meanings:

- `recovered`: a matching cluster exists, at any S/N.
- `missed_t1`: no matching raw search trial was found.
- `missed_t2`: matching T1 trials exist, but no matching cluster formed.
- `fire_failed`: the pulse was not sent; do not count it as a search miss.

An unset outcome is unfinished or legacy bookkeeping, not automatically a
miss. `gate_trigger` records trigger eligibility separately; known injections
are excluded from ordinary candidate triggering by design.

For a recovery fraction, count only completed, fired shots. In the ledger
that is

```sql
SELECT outcome, COUNT(*) FROM injections
WHERE outcome IN ('recovered', 'missed_t1', 'missed_t2')
GROUP BY outcome;
```

`fire_failed` rows never reached the stream and a NULL outcome is
unreconciled, so both are excluded from the denominator. Compare like DM,
width, S/N and observing conditions. A single recovery does not establish
full-array sensitivity.

## Fire a shot, or replay one

These commands change live state or write products; run them only under the
approval that covers the operation.

The injection daemon fires scheduled shots. One forced shot, then exit:

```bash
t2-inject --once --beam 22 --dm 400 --fwhm-ms 10 --target-snr 30
```

`--inject-snr` sets the true matched-filter S/N instead; `--target-snr` sets
the S/N hella should report and is converted through the per-width
`rec_per_true` table. The amplitude in stream counts is solved numerically,
not analytically: the daemon reads the beam's live per-channel std from Redis,
divides it by the bandpass factor 1.4, and bisects for the smallest integer
amplitude whose uint8-truncated rendered pulse reaches the target S/N over the
searched channels, with a floor of 4 counts. Keep the target reported S/N
below 40: brighter shots tripped hella's 10000-peak cap on the injected
stream's gulp, while shots at 43 and below did not.

Rerender a shot from its retained dump:

```bash
t3-replay-injection --inject-id 675 \
  --dump /mnt/nvme4/data/casm/cand_beam_dumps/stream_0 \
  --out /tmp/inj_replay.png
```

`--inject-id` is the ledger row id, the database is opened read-only, and
`--no-pulse` renders the same dump untouched for comparison.

Offline, without the live pipeline, the injector writes a filterbank with a
synthetic pulse and runs the searcher over a directory of them:

```bash
inject-frb --output /mnt/nvme3/vishnu/inj_test/shot.fil \
  --dm 400 --fwhm 10 --snr 20
run-hella --input_dir /mnt/nvme3/vishnu/inj_test --gpus 0
```

`--fwhm` is in samples and `--snr` is the target matched-filter S/N.
`run-hella` reads `injections_manifest.csv` from `--input_dir` and matches
candidates against the injected ground truth.

Continue to [T2/T3 and event storage](../packages/t2-t3.md).

## Provenance

Archive: `/mnt/nvme3/T3/EVENTS/inj_20260913_0023/` (PNG and JSON copied
unmodified into `docs/_static/tutorials/injections/`). Ledger: `t2.sqlite`,
`injections` table, rows for `inj_20260913_0023` and `inj_20260913_0021`.
Selected fields for both shots are frozen in
`docs/_static/tutorials/injections/frozen-records.json`; the live ledger can
change or reconcile after this page was written. Source revisions:
`source-snapshot.json` in the repository.
