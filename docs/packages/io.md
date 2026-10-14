# casm_io

Read CASM data with consistent axes, timestamps, and hardware mapping before
passing it to analysis or calibration. `casm_io` owns binary formats and basic
inspection; fringe-stopping, gain solving, and science interpretation belong
to downstream packages.

**Start here:** [Read and inspect visibilities](../guides/read-visibilities.md)
· [API signatures](io-api.md)

## Package at a glance

| Item | Value |
|---|---|
| Distribution / import | `casm_io` / `casm_io` |
| Python | 3.10 or newer |
| Declared version | 1.0.0 |
| Core dependencies | NumPy, pandas, Astropy, Matplotlib |
| Optional dependency | `sigpyproc`, for filterbank I/O |

Source revisions and file hashes: `source-snapshot.json` in the repository.
Examples are illustrative and need user-supplied data; they are not a claim
of validation on telescope data.

## Choose a reader

| Data product | Entry point | Result / key property |
|---|---|---|
| Correlator `.dat` files across a time window | `casm_io.correlator.read_visibilities` | `VisibilityResult` |
| One known correlator observation | `casm_io.correlator.VisibilityReader` | File inventory and selective reads |
| DADA voltage dumps already on disk | `casm_io.VoltageReader` | `FullBandResult` or `SubbandResult` |
| SIGPROC filterbank | `casm_io.FilterbankFile` | Header first; data loaded on demand |
| Hella T1 candidate list | `casm_io.CandidateReader` | Renamed columns in `.df` |
| Hella RFI flag records and per-event masks (branch `hella-mask`, not deployed) | `casm_io.candidates.hella_mask` | `MaskWindow`; `<event>.mask.npz` |
| T3 event folder, schema 1 or 2 (branch `hella-mask`, not deployed) | `casm_io.candidates.load_event` | `T3Event` |
| Physical antenna to hardware mapping | `casm_io.correlator.AntennaMapping` | CSV-backed input indices and ENU positions |

Voltage dumps and filterbanks are existing package capabilities. Their inclusion
here does not introduce fast-beam processing into the monitor's first release.

## Installation

CASM uses `casm_offline_env` as the default environment for Vishnu's repositories.
Activate it before running the examples:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
python -B -c "import casm_io; print(casm_io.__version__)"
```

This checks the existing installation without writing bytecode. This preview
does not reinstall the package or change its source. Existing environments may
carry a different revision despite the same version string. For a new environment,
install the reviewed revision using the repository's installation instructions
and record the revision independently of the package version.

## Visibility contract

`read_visibilities(time_start, time_end, ...)` discovers and stitches compatible
observations. Prefer an explicit `data_dir` for a bounded read; `data_root`
otherwise scans for `visibilities_*` directories and defaults to `/mnt`.

| Field | Shape | Meaning |
|---|---|---|
| `result.vis` | `(T, F, B)` | Complex64 visibilities; instrumental correlation units |
| `result.freq_mhz` | `(F,)` | Frequency in MHz, descending by default |
| `result.time_unix` | `(T,)` | Unix seconds, UTC |
| `result.metadata` | dictionary | Files, headers, format, observations and gaps |

The reader does not convert correlations to Jy. `B` is the flattened upper
triangle including autos, or the selected baseline count. For `ref`/`targets`,
the last axis follows the target selection and is oriented as `V(ref, target)`.

Selection happens during reading:

- `channels=(start, stop)` uses native channel indices, with exclusive stop.
- `freq_range_mhz=(low, high)` selects by physical frequency instead.
- `ref=p, targets=[q]` reads one directed baseline, conjugating when necessary.
- `inputs=[...]` reads every baseline among the sorted, deduplicated inputs.
- Channel and frequency selections are mutually exclusive. Use either an
  `inputs` subset or a `ref`/`targets` selection.

Channel or baseline subsets use memory mapping; the returned array is still
materialized in memory. `workers=1` bounds concurrent file reads. In the inspected
code an explicit `workers` argument takes precedence over `CASM_IO_WORKERS`;
the default otherwise is at most eight files concurrently.

## Mapping and conventions

Canonical `antenna_id` values are one-based physical labels. Correlator input
indices (`packet_index`) are zero-based. Obtain the latter with
`AntennaMapping.load(csv_path).packet_index(antenna_id)` rather than subtracting
one from an antenna number. For historical data, select the dated layout that
applied to that observation; today's `current` symlink can change.

Positions from `get_positions()` are `[East, North, Up]` in metres. A missing
position column raises an error. Layout flags describe configuration intent;
they do not prove participation in a particular deployed weight product.

The visibility convention is `V[i,j] = <v_i * conj(v_j)>`. For `i < j`, the
geometric baseline is `pos_j - pos_i`; a point source carries positive geometric
phase. Fringe-stopping uses the negative phase sign. Readers do not perform it.

Import baseline utilities from their actual module:

```python
from casm_io.correlator.baselines import triu_flat_index

# Full matrix: n is the file's nsig, not the live antenna count.
k = triu_flat_index(128, 0, 1)
```

For an `inputs` subset, use the subset size and ranks within the sorted input
list instead. When reversing a stored pair, conjugate the visibility.

## Frequency and time are data, not constants

Prefer file headers and the returned frequency axis. The shipped `layout_64ant`
configuration has 3072 descending channels starting at 484.375 MHz, with
0.030517578125 MHz spacing. Its last channel is 390.655517578125 MHz; the configured
bottom band edge, 390.625 MHz, is not the last channel frequency.

Pre-shift data have different frequencies. Legacy constants in `constants.py`
must not label current data. The full SNAP diagnostic band and the transmitted
correlator band are different products.

Header `TSAMP` is in microseconds; format `dt_raw_s` is in seconds. The shipped
`layout_64ant` JSON specifies 137.438953472 seconds per integration and 32
integrations per file. Actual headers govern header-bearing observations.
Use `America/Los_Angeles` for local display, never a fixed UTC offset.

## Other data products

`FilterbankFile(path, beam=None, verbose=True)` exposes `nchans`, `nsamples`,
`freq_mhz`, `time_s`, and `backend_used` before loading `.data`. Data are arranged
as `(time, channel)`; `.time_s` is relative seconds, not Unix time. Record the
selected backend when reproducing a result. Accessing `.data` loads the selected
beam, so inspect file size before using it interactively.

`CandidateReader(path)` reads a whitespace-separated Hella table with a header.
Its dataframe exposes `snr`, `sample_index`, `time_start`, `boxcar_width`,
`dm_index`, `dm`, and `beam_index`. DM is in pc cm⁻³. Width is a search index,
not automatically seconds. The reader alone does not establish injection matches
or recovery fractions.

`VoltageReader` reads saved dumps; it does not trigger acquisition. Missing
stream subbands may be zero-filled and are listed in `filled_subbands`.
Inspect those flags before interpreting a spectrum. The package also provides
writers and conversion CLIs; those are outside this read-only walkthrough.

## Hella RFI flags and T3 event folders

Status: `casm_io` branch `hella-mask`, revision `357d3af`. Not deployed; the deploy
needs operator approval. The running pipeline still writes schema-1 event folders
and its hella build writes no flag records, so on the running system `load_event`
reads schema-1 folders only and `hella_mask` has no records to read. Both modules
are documented by hand here and are not in the generated [API reference](io-api.md).
Byte-level specs: casm_io `docs/hella_masks.md` and `docs/t3_events.md` on that
branch. The pipeline side is in [T2, T3 and saved events](t2-t3.md#hella-rfi-flags-and-the-schema-2-event-folder).

### `casm_io.candidates.hella_mask`

hella (the `casm_hella_vishnu` fork) can record, for every beam and every gulp, the
flag decisions its flagging stage made. The module reads those record files (`.hmr`,
and the open `.hmr.part`) and assembles a mask over any sample window at full time
resolution. A record holds hella's flag decisions, not the data hella searched: the
final baseline pass standardises and subtracts a baseline after blanking, and
clipping and uint8 quantisation can create further zeros. Figures built from the
records show "hella RFI flags applied".

| Component | Granularity | Decision in hella |
|---|---|---|
| `static` | channels `[flag1, flag2)` | `FLAG1` / `FLAG2` cfg keys |
| `channel_flags` | channels, with reason bits | blanked by a standardisation pass, or replaced by the `SPEC_MIN`/`SPEC_MAX` rule |
| `sumthreshold` | channel x `mmin`-sample bin | SumThreshold mask after growing |
| `whole_channel` | channels | SumThreshold rows with more than `blank_cnt` flagged bins |

```python
from casm_io.candidates import hella_mask

# Illustrative paths and sample numbers; needs hella records, which exist only
# after the deploy.
win = hella_mask.window_mask(root, utc_start="2026-10-13-18:22:38", beam=285,
                             sample0=4199616, nsamp=9728)
win.combined.shape      # (3072, 9728) bool, True = flagged
win.coverage.mean()     # fraction of samples with a usable record
hella_mask.save_event_mask("261013nnuclj.mask.npz", win)
win2 = hella_mask.load_event_mask("261013nnuclj.mask.npz")
```

| Function | Returns |
|---|---|
| `read_file(path, *, beams=None, sample_range=None)` | `HmrFile` for one `.hmr` or `.hmr.part`; `HmrFormatError` on a bad file header |
| `read_records(root, utc_start, beam, sample_range=None)` | `list[GulpRecord]` for one global beam, ascending `first_sample` |
| `window_mask(root, utc_start, beam, sample0, nsamp, *, fch1=484.375, foff=-125/4096)` | `MaskWindow` over `[sample0, sample0 + nsamp)` |
| `summarize(win)` | dict for the event summary: `coverage`, `searched`, `flagged_fraction`, `channels_fully_flagged`, `static_channels`, `gulps` |
| `save_event_mask(path, win)`, `load_event_mask(path)` | write (through a temporary name, then rename) and read the `mask.npz` |

The spec also lists the file-header parser, `scrunch_could_fire` and a reference
encoder (`write_record_file`) that tests use to build record files.

Reading rules that change how a mask is interpreted:

- Align by sample index, never by time. `tstart` in the event's `.fil` derives from
  corr1's system clock (about 15 s fast on 2026-10-13, casm-wiki `incidents.md`).
- Where `coverage` is False every component is False and the flags are unknown, not
  "unflagged". A window no record covers returns all-False arrays and no gulps.
- A record with a bad CRC, no end magic, a payload that does not parse, or
  `alignment_ok` other than 1 is skipped and counted in `HmrFile.skipped`.
- SCRUNCH stages are not recorded. hella refuses to record when a configured SCRUNCH
  stage could fire (threshold below 1e5 sigma; the deployed stage is 1e6 and never
  fires), and the reader warns when a header's cfg shows one.
- `searched` says whether the search step that ran right after flagging a gulp reached
  the beam. It is not per-sample search coverage: an event hella reported can sit in a
  gulp with `searched` 0.

`<event>.mask.npz` sits next to `<event>.fil` and covers exactly the fil: channel 0 is
484.375 MHz (descending) and the first sample is the same. It holds the packed boolean
arrays `combined` (union of the components), `static`, `channel_flags`, `sumthreshold`,
`whole_channel` (True = flagged), `channel_reasons` (uint8, reason bits per channel per
gulp), `coverage`, `searched`, and a JSON `meta` string with the shape, `sample0`,
`tsamp`, the gulps, the record headers used and the cfg sha256.

### `casm_io.candidates.load_event`

Every candidate T3 dumps gets a folder `/mnt/nvme3/T3/EVENTS/<candname>/`. `load_event`
reads schema 1 (one monolithic card JSON, the layout the running system writes) and
schema 2 (summary JSON, CSV tables, `mask.npz` and a manifest, the layout the branch
writes) into one `T3Event`.

```python
from casm_io.candidates import load_event

ev = load_event("/mnt/nvme3/T3/EVENTS/261013nnuclj")   # illustrative folder name
ev.schema            # 1 or 2
ev.summary           # dict; for schema 1, built from the card
ev.trials            # DataFrame: the deduplicated T1 table
ev.clusters, ev.beams
ev.mask              # hella_mask.MaskWindow or None
ev.slack             # list of dicts parsed from .slack
ev.fil, ev.png, ev.raw_png   # paths or None
ev.complete          # manifest present and every file in it checks out
ev.problems          # why not, one string per finding
```

`load_event(event_dir, *, verify=False, load_mask=True)` raises `FileNotFoundError` when
`<candname>.json` is absent and `ValueError` for a `schema` above 2. A missing CSV reads
as an empty table with the right columns and a line in `problems`. `complete` means the
manifest exists and the files it lists are intact, not that every optional product
exists: an event whose `.fil` failed to write is complete with `ev.fil` None.
`verify=True` also re-hashes every listed file. A schema-1 folder has no manifest, so
`complete` is True when its PNG exists, and `ev.mask` is None. The folder layout,
summary keys, CSV columns and `.slack` marker format are in casm_io `docs/t3_events.md`.

## Known discrepancies in upstream documentation

These findings are documented here without modifying the source repository:

- The correlator guide's format table understates integration and file duration.
  Use header-derived values; the shipped JSON values are described above.
- Some examples import `triu_flat_index` from `casm_io.correlator`. It is exported
  from `casm_io.correlator.baselines`, not from the package initializer.
- `read_visibilities` preserves `metadata['inputs']`, `nsig_subset`, validity and
  missing-file evidence through top-level stitching. Earlier revisions dropped
  the selection fields; keep the sorted selection when reading old saved results.
- Upstream documents a part-file-boundary `OverflowError` from memory mapping.
  The current reader reproduces a truncated-file cause on a tiny fixture and
  rejects it descriptively. The original historical boundary incident remains
  unverified. Preserve the window, filenames, format and traceback if encountered.

Upstream reference: [README and detailed guides](https://github.com/Coherent-All-Sky-Monitor/casm_io).
