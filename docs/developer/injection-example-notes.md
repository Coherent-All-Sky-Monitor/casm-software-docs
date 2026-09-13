# Injection example verification

Inspected on 2026-09-13 with read-only SQLite queries and saved image/JSON
inspection. No injection, service action, dump request, Slack call, replay
render or bulk filterbank read was performed.

## Recorded result

Database: `/mnt/nvme5/casm_pipeline/db/t2.sqlite`, `injections` rows 748 and
746. The tutorial query used `sqlite3.connect(...?mode=ro, uri=True)` and was
executed against the existing records. The output was checked against the
saved replay card and PNG.

Row 748, `inj_20260913_0023`:

- Injection sent: `2026-09-13T22:27:24.976+00:00`.
- Matching cluster: 5364944; saved event UTC `2026-09-13T22:27:02.351+00:00`.
- Beam 141; DM 386.4305139731968; injected S/N 21.9322909938559.
- Recovered beam 141, DM 386.0, S/N 25.1319, width trial 5.
- `gate_t1=1`, `gate_t2=1`, `gate_trigger=1`, `outcome=recovered`.
- `sigma_ms=9.901979617616888`; the injected Gaussian FWHM is about 23.3 ms.
- `replay_posted=1` is the ledger's posting flag. Slack itself was not queried.

The image labels width as `2**5 * 1.048576 = 33.554432` ms. The search kernel
FWHM at trial 5 is 22.020096 ms in `casm_t2.hella_kernel`, and the tutorial
explicitly distinguishes these. The offline plot's boxcar S/N 24.9 is a
separate statistic from the ledger's hella S/N 25.1319.

Row 746, `inj_20260913_0021`: sent at
`2026-09-13T20:28:48.740+00:00`, beam 49, DM 886.6518146806226,
injected S/N 20.6101667637822; `outcome=missed_t1`, `n_t1_trials=0`,
all three gates zero, no matching cluster and no replay PNG. Recorded reason:

```text
lost at T1: no matching trial in beam 49 or its 8 sky neighbours within the window at DM 887 (+-133)
```

This tutorial reports the ledger classification without asserting a physical
cause. It does not recompute reconciliation or validate the matching window.

## Figure and archive

Originals under `/mnt/nvme3/T3/EVENTS/inj_20260913_0023/`:

| File | Bytes | SHA256 |
|---|---:|---|
| `inj_20260913_0023.png` | 299928 | `33d762b9cdf9b57ebeb92f4b4d4c50ba6eef6777b7a72bed9aabdfa9687faf2d` |
| `inj_20260913_0023.json` | 18799 | `524ca4be1f975d1da2dcb72d0a6cecb6e4346621bfc5f3a9ca7c0a66075c845b` |

The PNG was copied byte-for-byte to
`docs/_static/tutorials/injections/inj_20260913_0023.png`; no palette, crop or
pixel changes. Its title names this injection and its event timestamp matches
the JSON. The archive also contains a 231,211,291-byte filterbank, not read for
this tutorial. The full source JSON and live database were not copied.

The plot is a replay because intensity dumps tap the stream before injection
merging. Its pulse has been synthesized again over the recorded background.
The live recovery claim comes from the ledger and matched cluster, not the
visual existence of a replay pulse. Background and injected-pulse timing are
different from the time of the FIFO write.

## Source audit

- casm_t2: `2215ed13b8aa7d64c003a5f5a2edbff0dace6144`.
- casm_t3: `20f5bca3f19f52d291aba9d355e197bc79f178cf`.

Inspected source: both READMEs and operations guides, `casm_t2/db.py`,
`inject_outcome.py`, `hella_kernel.py`, `apps/inject_report.py`, and T3's
read-only web connection. `db.connect` creates directories, enables WAL and
runs schema migrations; `t2-inject-report` calls it and writes a report.
Neither is advertised as a no-write inspection command in this tutorial.

Historical context: `/home/casm/software/dev/casm-wiki/injection-bot.md`,
`storage-map.md`, and `dump-stream-content.md`. Existing operational documents
describe differing Slack layouts and cadences from earlier dates, so no
current cadence or exact Slack-card format is promised here. These manually
documented source revisions are outside the generated API snapshot's scope.

Return to [the injection tutorial](../guides/injection-recovery.md).
