# Check a calibration on another day: baseline phase against frequency

A calibration solved on one solar transit should still flatten baseline phase
two days later. Apply the day-A gains to a day-B Sun window, plot phase against
frequency per baseline, and read the residual RMS. The wiki validation battery
(`recipes.md` (d), item 1) puts a passing cross-day residual at roughly
10-19 deg, measured full-band over all 3072 channels including the transmitter
bands. Gate on the full-band RMS; the unflagged RMS below is a diagnostic that
separates source phase from transmitter phase, not the gate.

The check is only meaningful inside one instrument epoch. An F-engine resync or
reflash, or any wiring change, voids the calibration: the per-antenna delays are
redefined and the gains no longer describe the array. Day A here is 2026-08-23
and day B is 2026-08-25, with no resync or layout change between them.

## Load the day-A calibration

```python
import numpy as np
from bf_weights_generator.snap_weights import load_calibration_weights

CAL = "/mnt/nvme5/vishnu/cal_build_20260824/cal_aug23_exact512_CAL0823N.h5"
cal = load_calibration_weights(CAL)
print("antennas:", list(cal.ant_ids))
print("reference antenna:", cal.ref_ant_id, " source:", cal.source)
print("channels:", cal.weights.shape[1],
      f"{cal.frequencies_hz[0]/1e6:.3f}-{cal.frequencies_hz[-1]/1e6:.3f} MHz ascending")
```

`cal.weights` is `conj(gain)` per antenna and channel, stored with frequency
ascending. The visibility read below is descending, so one of the two gets
flipped before they are multiplied.

## Read the day-B Sun window

Use the same window length as a weights build: one hour around the Sun peak.
Compute the peak on a 1-minute grid rather than reusing a previous day's clock
time, because solar transit moves.

```python
from datetime import datetime, timedelta, timezone
from casm_vis_analysis.sources import source_altaz

# 1-min grid over day-B daylight; the peak anchors a 1 h read window.
day_b = datetime(2026, 8, 25, tzinfo=timezone.utc)
grid = np.array([(day_b + timedelta(minutes=m)).timestamp()
                 for m in range(14 * 60, 24 * 60)])
alt_deg, _ = source_altaz("sun", grid)
peak = datetime.fromtimestamp(grid[int(np.argmax(alt_deg))], timezone.utc)
start, end = peak - timedelta(minutes=30), peak + timedelta(minutes=30)
print(f"Sun peak {peak:%Y-%m-%d %H:%M:%S} UTC, altitude {alt_deg.max():.1f} deg")
print(f"window {start:%H:%M:%S}-{end:%H:%M:%S} UTC")
```

```python
from casm_io.correlator import AntennaMapping, read_visibilities

REF = int(cal.ref_ant_id)
ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-07.csv"
)
ant = ant.with_inactive(
    [a for a in ant.active_antennas() if a not in set(int(x) for x in cal.ant_ids)]
)
targets = sorted(a for a in ant.active_antennas() if a != REF)
data = read_visibilities(
    data_root="/mnt/nvme4/data/casm",
    time_start=f"{start:%Y-%m-%d %H:%M:%S}", time_end=f"{end:%Y-%m-%d %H:%M:%S}",
    time_tz="UTC", ref=ant.packet_index(REF),
    targets=[ant.packet_index(a) for a in targets],
    workers=1, verbose=False,
)
print("files:", data.metadata["files"])
print("vis shape (time, freq, baseline):", data.vis.shape)
```

The layout CSV must be the one valid for the day-B recording, and it must be
the same array geometry the calibration was solved on. `with_inactive()` trims
the mapping to the 16 calibrated antennas for this read only; it does not touch
the layout file or the beamforming set.

## Fringe-stop and apply the day-A gains

After fringe stopping toward the Sun, the remaining phase on baseline `i-j` is
instrumental: `V_ij` is approximately `g_i conj(g_j)`. Multiplying by
`w_i conj(w_j)` with `w = conj(g)` cancels it. That is the same convention
`beam_power_vs_time` applies internally, and exactly one conjugation per
antenna pair.

```python
from casm_vis_analysis.fringe_stop import fringe_stop
from casm_vis_analysis.rfi import RFIMask

fs = fringe_stop(data, ant, ref_ant=REF, source="sun", sign=-1)
freq_mhz = np.asarray(fs["freq_mhz"])

# Cal is stored ascending, the read is descending: flip the cal to match.
weights = cal.weights[:, ::-1]
assert np.allclose(cal.frequencies_hz[::-1] / 1e6, freq_mhz)

# cal.ant_ids holds 1-indexed antenna NUMBERS, not row indices. Indexing the
# gain array with an antenna number applies a neighbour's cal to this antenna.
row = {int(a): i for i, a in enumerate(cal.ant_ids)}

vis_raw = np.asarray(fs["vis_for_calibration"])          # (T, F, n_bl)
corr = np.stack([weights[row[REF]] * np.conj(weights[row[t]])
                 for t in fs["target_aids"]], axis=-1)   # (F, n_bl)
vis_cal = vis_raw * corr[None, :, :]

# v1 is the narrowest static mask and keeps 2258 of 3072 channels; v2 keeps
# 390.7-434 MHz and v3 only 405-434 MHz, too narrow for a full-band gate.
good = RFIMask.from_static(version=1)(freq_mhz)          # True = unflagged
# drop channels the solve failed (weight 0 would read as phase 0)
good &= cal.flags[::-1]                                  # cal ascending, read descending
mean_cal = vis_cal.mean(axis=0)
for k, tar in enumerate(fs["target_aids"]):
    residual = np.angle(mean_cal[:, k])                  # wrapped, radians
    full = np.degrees(np.sqrt(np.mean(residual ** 2)))
    masked = np.degrees(np.sqrt(np.mean(residual[good] ** 2)))
    print(f"{REF:>2d}-{tar:<2d}  residual RMS {full:6.1f} deg full band, "
          f"{masked:6.1f} deg unflagged")
```

```text
 9-10  residual RMS   63.4 deg full band,   45.0 deg unflagged
 9-15  residual RMS   18.6 deg full band,   13.5 deg unflagged
 9-19  residual RMS   21.5 deg full band,   15.8 deg unflagged
 9-22  residual RMS   17.6 deg full band,   14.9 deg unflagged
 9-23  residual RMS   16.3 deg full band,   10.6 deg unflagged
 9-24  residual RMS   29.6 deg full band,   28.2 deg unflagged
 9-26  residual RMS   24.2 deg full band,   22.8 deg unflagged
 9-30  residual RMS   24.4 deg full band,   18.8 deg unflagged
 9-32  residual RMS   43.2 deg full band,   43.3 deg unflagged
 9-36  residual RMS   27.0 deg full band,   15.0 deg unflagged
 9-38  residual RMS   23.7 deg full band,   21.2 deg unflagged
 9-40  residual RMS   21.1 deg full band,   19.2 deg unflagged
 9-42  residual RMS   28.9 deg full band,   27.8 deg unflagged
 9-44  residual RMS   37.3 deg full band,   37.4 deg unflagged
 9-45  residual RMS   20.1 deg full band,   17.1 deg unflagged
```

For this cal `cal.flags` is True on all 3072 channels, so the intersection
drops nothing here. That is expected: the production driver solves with no RFI
mask, so every channel comes back "solved". Keep the intersection anyway, a
cal built with a mask carries zeros that would read as phase 0.

## Plot a few baselines

```python
import matplotlib.pyplot as plt
from casm_vis_analysis.plotting.phase_freq import plot_phase_vs_freq

show = [23, 19, 10, 44]          # flat, flat, residual slope, residual structure
sel = [list(fs["target_aids"]).index(t) for t in show]
figs = plot_phase_vs_freq(
    panels=[("Fringe-stopped", vis_raw[:, :, sel]),
            ("After day-A gains", vis_cal[:, :, sel])],
    freq_mhz=freq_mhz,
    baseline_labels=[f"{REF}-{t}" for t in show],
    unwrap=False, freq_mask=good,
    time_unix=fs["time_unix"], time_tz="UTC",
)
plt.show()
```

```{figure} ../_static/tutorials/phase/cross-day-phase.png
:alt: Four rows of baseline phase against frequency, fringe-stopped on the left and calibrated on the right; the left column shows a sawtooth ramp and the right column is flat for the first two baselines.

Output of the code above. Sun window 2026-08-25 19:25-20:25 UTC, 26
integrations, gains from the 2026-08-23 calibration. Unflagged channels only
(static RFI mask v1, 2258 of 3072 channels); flagged bands appear as gaps.
```

## What to read off the plot

A **sawtooth** in the left column is an uncorrected delay. Phase wraps linearly
with frequency at rate `2 pi tau`, so the wrap spacing gives the delay: 9-23
wraps every 5.6 MHz, which is 180 ns of cable and electronics.

A **flat residual** in the right column means the day-A gains still describe
day B on that baseline. Baselines 9-23 and 9-19 sit at 16.3 and
21.5 deg full band (10.6 and 15.8 unflagged) against the wiki 10-19 deg
full-band gate: 9-23 passes, 9-19 sits just above it. The fitted
residual delay on 9-23 is 0.0 ns.

A **slope** left in the residual is a delay that drifted between the two days.
Baseline 9-10 does this: the fringe-stopped phase was already nearly flat (5 ns
of delay, so no visible sawtooth), and after the gains a 4 ns ramp remains that
walks the phase by 2.4 rad across the 93.75 MHz band (2 pi tau B). Its 63.4 deg
full-band RMS is the worst of the 15 baselines. A drift like this re-solves away.

**Structure that is neither flat nor a ramp**, as on 9-44 at 37.3 deg full band,
points at
one antenna's signal path: a swapped cable, a moved antenna, or a position
error in the layout. The discriminator is whether every baseline to that
antenna carries the same shape and no other baseline does, which needs the full
triangle rather than the reference-to-target read above. Do not re-solve first.
Check the position with
`casm-fit-positions`, sweeping more than one reference antenna, because a
target that lands on the reference's own baseline direction is coupling rather
than position. A wrong position re-solves into a direction-dependent
calibration that beamforms worse while the solve metrics improve
(wiki `rank1-metric-caveat.md`).

Gate on the full-band number, which is the basis of the wiki 10-19 deg band.
The unflagged number printed alongside it drops the transmitter bands, whose
phase has nothing to do with the source, so it runs tens of degrees lower and
is the right number for judging which baseline carries a real defect.

## Provenance

Calibration: `/mnt/nvme5/vishnu/cal_build_20260824/cal_aug23_exact512_CAL0823N.h5`
(Sun, 2026-08-23 20:41:30-21:41:30 UTC, ref antenna 9, 16 antennas).
Day-B data: `/mnt/nvme4/data/casm/visibilities_64ant/2026-08-25-04:38:03.dat.12`,
2026-08-25 19:25:00-20:25:00 UTC requested, 19:26:49-20:24:05 UTC returned,
26 integrations.
Layout: `casm_antenna_layout_2026-08-07.csv`, matching both recordings.
Figure rendered by `scripts/render_cross_day_phase_tutorial.py`, which executes
the displayed blocks on this page and saves the figure in place of `plt.show()`.
