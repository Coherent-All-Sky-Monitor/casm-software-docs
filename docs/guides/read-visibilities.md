# Read and inspect visibilities

Load one physical baseline over a bounded interval, verify its axes, and inspect
amplitude and phase. This is a read-only introduction to
[casm_io](../packages/io.md), not a calibration or readiness verdict.

**Prerequisites:** an environment with `casm_io`, NumPy and Matplotlib; a
user-selected visibility directory; a dated antenna layout CSV; and a UTC
interval known to contain data. No telescope connection or hardware operation
is needed.

On the CASM host, activate the shared offline environment first:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
python -B
```

The examples below are illustrative and have not been run against observation
data in this documentation preview. They use the inspected API at revision
`22ef826d9f2ba355388523265081da1468e5a4ff`.

## 1. Supply the observation context

Run the following blocks in order in a Python session or notebook. Enter paths
and times for your own dataset; there are no assumed mounted data directories.

```python
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from casm_io.correlator import AntennaMapping, read_visibilities

data_dir = Path(input("Visibility directory: ")).expanduser().resolve()
layout_csv = Path(input("Dated layout CSV: ")).expanduser().resolve()
time_start = input("Start UTC (YYYY-MM-DD HH:MM:SS): ")
time_end = input("End UTC (YYYY-MM-DD HH:MM:SS): ")
antenna_a = int(input("Reference physical antenna ID: "))
antenna_b = int(input("Target physical antenna ID: "))
if not data_dir.is_dir() or not layout_csv.is_file():
    raise ValueError("Choose an existing data directory and layout CSV")
if antenna_a == antenna_b:
    raise ValueError("Choose distinct antennas for this cross-baseline guide")

mapping = AntennaMapping.load(str(layout_csv))
ref_input = mapping.packet_index(antenna_a)
target_input = mapping.packet_index(antenna_b)
print(mapping.format_antenna(antenna_a))
print(mapping.format_antenna(antenna_b))
```

Physical antenna IDs and correlator inputs are different label spaces. The CSV
provides their correspondence. Preserve its path and contents when saving an
analysis: a mutable `current` symlink is insufficient historical provenance.

## 2. Read a small selection first

This example reads the first 128 native channels and one baseline. Starting with
a short time window makes memory and read duration easy to assess.

```python
result = read_visibilities(
    time_start=time_start,
    time_end=time_end,
    time_tz="UTC",
    data_dir=str(data_dir),
    ref=ref_input,
    targets=[target_input],
    channels=(0, 128),
    freq_order="descending",
    workers=1,
    verbose=True,
)
vis = result.vis
freq_mhz = result.freq_mhz
time_unix = result.time_unix
print("vis:", vis.shape, vis.dtype, "bytes:", vis.nbytes)
print("frequency:", freq_mhz.shape, freq_mhz[[0, -1]], "MHz")
print("timestamps:", time_unix.shape, "Unix seconds UTC")
```

The reader orients the result as `V(reference, target)`, even when the reference
input index is numerically larger. Do not conjugate it a second time.

For header-bearing files, leave `fmt` unset. For headerless files, pass a
`VisibilityFormat` verified for their recording epoch. Do not assume that a
current built-in format describes older observations.

To select a physical band, replace `channels=(0, 128)` with
`freq_range_mhz=(low_mhz, high_mhz)` after checking the observed band. Do not pass
both. Increasing `workers` can improve throughput but raises concurrent I/O and
memory pressure; choose it deliberately on a shared telescope host.

## 3. Verify coverage and metadata

```python
assert vis.ndim == 3 and vis.shape[2] == 1
assert vis.shape[:2] == (time_unix.size, freq_mhz.size)
assert time_unix.size > 0 and freq_mhz.size > 0
assert np.all(np.diff(freq_mhz) < 0), "Unexpected frequency order"
if np.any(np.diff(time_unix) <= 0):
    raise ValueError("Inspect duplicate or non-monotonic timestamps")
for stamp in (time_unix[0], time_unix[-1]):
    print(datetime.fromtimestamp(float(stamp), timezone.utc).isoformat())
print("Integration seconds:", result.metadata.get("dt_raw_s"))
print("Observations:", result.metadata.get("observations"))
print("Gaps:", result.metadata.get("gaps", []))
print("Missing files:", result.metadata.get("missing_files", []))
print("Finite fraction:", np.isfinite(vis).mean())
```

Requested times are selection bounds, not proof of complete coverage. Inspect
warnings, file inventories, and timestamp spacing together. Zero values are not
automatically valid measurements. In file-count mode, `VisibilityReader` can
zero-fill missing files with warnings; time-range reads can instead fail on
missing files. The high-level function also reports gaps between observations.

The timestamp sequence is constructed from the observation start and integration
cadence. Do not silently reinterpret these as midpoint timestamps when aligning
another product; establish its timing convention first.

## 4. Inspect amplitude and phase without averaging away structure

This quick-look plots samples individually, leaving time gaps visible. It keeps
the native descending frequency correspondence and displays phase in radians.

```python
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

baseline = vis[:, :, 0]
dates = [datetime.fromtimestamp(float(t), timezone.utc) for t in time_unix]
x, y = np.meshgrid(mdates.date2num(dates), freq_mhz, indexing="ij")
fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                         constrained_layout=True)
for ax, values, label, cmap, limits in (
    (axes[0], np.abs(baseline), "Amplitude (instrumental units)",
     "viridis", {}),
    (axes[1], np.angle(baseline), "Phase (rad)",
     "twilight", {"vmin": -np.pi, "vmax": np.pi}),
):
    artist = ax.scatter(x.ravel(), y.ravel(), c=values.ravel(),
                        s=8, marker="s", linewidths=0, cmap=cmap, **limits)
    ax.set_ylabel("Frequency (MHz)")
    fig.colorbar(artist, ax=ax, label=label)
axes[0].set_title(f"Ant {antenna_a} → Ant {antenna_b} · raw visibility")
axes[-1].xaxis.set_major_formatter(
    mdates.DateFormatter("%m-%d %H:%M", tz=timezone.utc)
)
axes[-1].set_xlabel("UTC")
plt.show()
```

This is a bounded diagnostic, not the production solar waterfall style. A sparse
or empty interval should remain visibly sparse or empty. For longer runs, use
the existing analysis plotting routines and explicit binning rather than drawing
millions of markers.

Avoid complex averaging across a broad band before accounting for delay: a
phase slope can cancel a strong signal. A wrapped sawtooth phase is not by
itself a fault; baseline geometry, source direction, and instrumental delays
all contribute. Calibration comparison belongs to a controlled analysis with
the same baseline orientation, frequency order, geometry and selected weights.

## 5. Carry the evidence into the next analysis

Retain the requested interval, actual timestamps, frequency selection, antenna
IDs, input indices, layout revision, source files, reader revision, and any gaps.
The in-memory result can then feed visibility-analysis routines; no source
file needs to be rewritten.

For multiple antennas, `inputs=[...]` returns the upper triangle of a sorted,
deduplicated input selection. The reviewed top-level reader omits the subset
labels from its stitched metadata, so keep your own `sorted(set(inputs))` list.
See [package caveats](../packages/io.md#known-discrepancies-in-upstream-documentation)
before adapting older upstream examples.

If a part-file-boundary read raises the documented memory-map `OverflowError`,
record the exact window and traceback. A partial successful read is not evidence
that the requested interval was fully analysed.
