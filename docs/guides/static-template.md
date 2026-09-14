# Build an off-source static template

The correlator output carries a direction-independent pedestal: cross-talk
between inputs, ground pickup, and broadband correlated RFI. It does not fringe
with hour angle, so time-averaging on a source does not remove it, and it biases
an SVD solve. `casm_vis_analysis.offsource` estimates that pedestal from a quiet
night window and subtracts it.

This tutorial builds the template for the night of 2026-08-23 and compares it
with the template that was actually used for the 2026-08-23 solar calibration.
The layout below is the one matching that recording; for a new observation use
`/home/casm/software/dev/antenna_layouts/current`.

## 1. Choose the quiet window

`find_quiet_windows` scans a time grid for intervals where every named source is
below its altitude cap. Do the geometry first, with no data read.

```python
import numpy as np
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from casm_vis_analysis.offsource import find_quiet_windows, plot_quiet_window_altitudes

TZ = "America/Los_Angeles"
NIGHT = "2026-08-23"          # local date; its evening holds the window

# August caps from the solar recipe: the A-team sources never set, so cap them
# where the primary beam attenuates them instead of demanding they be down.
CAPS_AUGUST = {"sun": 0.0, "tau-a": 0.0, "cyg-a": 47.0, "cas-a": 25.0}
# This night needs the relaxed variant: Cyg A cap 47 -> 64 deg and Cas A
# 25 -> 35 deg (Cas A sits at 30.5-33.9 deg through the window, so the August
# cap alone leaves no window), Sun cap 0 -> -6 deg so the window starts after
# the overlapping recordings end.
CAPS = {"sun": -6.0, "tau-a": 0.0, "cyg-a": 64.0, "cas-a": 35.0}

midnight = datetime.fromisoformat(NIGHT).replace(tzinfo=ZoneInfo(TZ)).timestamp()
grid = midnight + np.arange(0.0, 24 * 3600.0, 60.0)   # 1-min grid over the local day

print(len(find_quiet_windows(grid, altitude_caps=CAPS_AUGUST, min_duration_s=15 * 60)))
window = find_quiet_windows(grid, altitude_caps=CAPS, min_duration_s=15 * 60)[0]
print(datetime.fromtimestamp(window["t_start"], timezone.utc),
      datetime.fromtimestamp(window["t_end"], timezone.utc),
      round(window["duration_s"] / 60))

plot_quiet_window_altitudes(
    {"date": NIGHT, "window_unix": (window["t_start"], window["t_end"])},
    CAPS, time_tz=TZ,
)
plt.show()
```

```
0
2026-08-24 03:02:00+00:00 2026-08-24 03:30:00+00:00 28
  sun     in window:  -11.3 ..   -6.1 deg (cap  -6.0)  OK
  tau-a   in window:  -30.7 ..  -30.6 deg (cap   0.0)  OK
  cyg-a   in window:   58.6 ..   63.9 deg (cap  64.0)  OK
  cas-a   in window:   30.5 ..   33.9 deg (cap  35.0)  OK
```

```{figure} ../_static/tutorials/static/quiet-window-altitudes.png
:alt: Altitude of Sun, Tau A, Cyg A and Cas A over 24 hours on 2026-08-23, with the chosen post-sunset window shaded and each altitude cap drawn as a dashed line.

Altitude tracks for the caps above on 2026-08-23 local time. The shaded band is
the chosen window, 2026-08-24 03:02-03:30 UTC (20:02-20:30 PDT).
```

Read the figure by looking for the interval where every solid track sits under
its own dashed line. It lands just after sunset because Cyg A rises from the
moment the Sun sets and only comes back down after sunrise, while Cas A passes
its lower culmination while the Sun is still up.

The strict August caps return zero windows on this night. That window closed
around 2026-08-11: it drifts about 4 minutes earlier per day, because the sky
returns to the same configuration one sidereal day (23 h 56 m) later while the
Sun's setting time follows the solar day. It was 18 minutes long on Aug 5 and
6 minutes on Aug 9. Re-derive the caps every epoch instead of reusing a window.
After the strict window closes, relax Cyg A to 64 deg and Cas A to 35 deg, move
the Sun cap from 0 to -6 deg, and keep the same post-sunset position. Cas A has
to move with Cyg A: it is at 30.5-33.9 deg over this window, above the 25 deg
August cap. The pre-dawn alternative is worse: Cas A is higher there
and Tau A is rising.

## 2. Build and save the template

`build_static_visibility` repeats that search internally, reads only the window
it finds, and time-averages it to an `(F, n_bl)` array. `max_duration_s` bounds
the read: this 28-minute window is 12 integrations and 2.4 GB of 64-antenna
visibilities.

```python
from pathlib import Path
from casm_io.correlator import load_format
from casm_vis_analysis.offsource import build_static_visibility, save_static_visibility

OUT = Path("/tmp/casm_static_template")
OUT.mkdir(parents=True, exist_ok=True)
fmt = load_format("layout_64ant")

static = build_static_visibility(
    NIGHT, fmt=fmt, data_root="/mnt/nvme4/data/casm", time_tz=TZ,
    altitude_caps=CAPS, min_duration_s=15 * 60, max_duration_s=30 * 60,
)
print("n_integrations", static["data"].vis.shape[0])
print("static_vis", static["static_vis"].shape)

save_static_visibility(
    OUT / "static_2026-08-23_night.npz", static["static_vis"],
    freq_mhz=static["freq_mhz"], window_unix=static["window_unix"],
    altitudes=static["altitudes"],
    notes="layout 2026-08-07, obs 2026-08-24-01:54:29",
)
del static["data"]      # the quiet-window cube is 2.4 GB; the template is 20 MB
```

```
n_integrations 12
static_vis (3072, 8256)
```

The realised window is 03:03:12-03:28:23 UTC, inside the geometric 03:02-03:30.
`static["data"]` holds the full read, so drop it once the average exists. The
altitudes, the frequency axis and the window go into the NPZ with the array;
a template without them cannot be checked against the observation it is
subtracted from.

## 3. Compare with the deployed template

The 2026-08-23 solar calibration used a template from the same night, window
03:00:54-03:28:23 UTC. Compare per-baseline amplitudes on the 16 antennas that
solve used, listed in its `params_aug23_exact512.json`.

```python
from casm_io.correlator import AntennaMapping
from casm_io.correlator.baselines import triu_flat_index
from casm_vis_analysis.offsource import load_static_visibility

DEPLOYED = "/mnt/nvme5/vishnu/cal_build_20260824/static_aug23_exact512_CAL0823N.npz"
SOLVED_ANTS = [9, 10, 15, 19, 22, 23, 24, 26, 30, 32, 36, 38, 40, 42, 44, 45]

ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-07.csv"
)
pk = sorted(ant.packet_index(a) for a in SOLVED_ANTS)
bls = [triu_flat_index(int(fmt.nsig), pk[m], pk[n])
       for m in range(len(pk)) for n in range(m + 1, len(pk))]

old = load_static_visibility(DEPLOYED)
assert np.allclose(old["freq_mhz"], static["freq_mhz"])

amp_new = np.median(np.abs(static["static_vis"][:, bls]), axis=0)  # per baseline
amp_old = np.median(np.abs(old["static_vis"][:, bls]), axis=0)
ratio = amp_new / amp_old
print(len(bls), np.percentile(ratio, [5, 50, 95]).round(3))

bl_9_32 = triu_flat_index(int(fmt.nsig), *sorted((ant.packet_index(9),
                                                  ant.packet_index(32))))
freq = static["freq_mhz"]
fig, (ax_f, ax_r) = plt.subplots(1, 2, figsize=(10.5, 3.6))
ax_f.plot(freq, np.abs(old["static_vis"][:, bl_9_32]), lw=0.6, color="0.55",
          label="deployed template")
ax_f.plot(freq, np.abs(static["static_vis"][:, bl_9_32]), lw=0.6, color="C0",
          label="this build")
ax_f.set_yscale("log")
ax_f.set_xlabel("Frequency (MHz)")
ax_f.set_ylabel("|static| (correlator units)")
ax_f.set_title("Baseline 9-32")
ax_f.legend(fontsize=8, frameon=False)
ax_r.hist(ratio, bins=40, color="C0")
ax_r.set_xlabel("this build / deployed, per-baseline median amplitude")
ax_r.set_ylabel("baselines")
ax_r.set_title("120 cross baselines, 16 antennas")
fig.tight_layout()
plt.show()
```

```
120 [0.971 0.997 1.02 ]
```

```{figure} ../_static/tutorials/static/template-vs-deployed.png
:alt: Left, static amplitude versus frequency for baseline 9-32 from two templates, overlapping. Right, histogram of per-baseline amplitude ratios peaking at one.

Left: `|static|` against frequency on baseline 9-32 for both templates. Right:
ratio of per-baseline median amplitudes over the 120 cross baselines of the
16 solved antennas.
```

Median ratio 0.997, 5th-95th percentile 0.971-1.020, extremes 0.923 and 1.044.
Twelve of the thirteen integrations are shared, so this is a floor on agreement,
not an independent check. The per-baseline complex coherence between the two
templates is 0.9996-0.99999 over the same set. Baselines to inactive inputs are
identically zero in both files; 7101 of 8256 in this format, which is why the
comparison is restricted to a named antenna set.

## 4. Subtract it from a Sun window

```python
from casm_io.correlator import read_visibilities
from casm_vis_analysis.offsource import subtract_static_visibility

sun = read_visibilities(
    "2026-08-23 20:41:30", "2026-08-23 20:51:30", time_tz="UTC",
    data_root="/mnt/nvme4/data/casm", fmt=fmt, workers=1,
)
clean = subtract_static_visibility(sun, static["static_vis"])   # returns a new dict

raw = np.abs(np.mean(sun.vis[:, :, bl_9_32], axis=0))
sub = np.abs(np.mean(clean["vis"][:, :, bl_9_32], axis=0))
peak = int(np.argmax(raw))
print(sun.vis.shape, np.median(sub / raw).round(3))
print(freq[peak].round(1), raw[peak].round(), sub[peak].round())

fig, ax = plt.subplots(figsize=(7.5, 3.6))
ax.plot(freq, raw, lw=0.6, color="0.55", label="raw")
ax.plot(freq, sub, lw=0.6, color="C3", label="static subtracted")
ax.set_yscale("log")
ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel("|V| (correlator units)")
ax.set_title("Baseline 9-32, Sun, 2026-08-23 20:43-20:50 UTC")
ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
plt.show()
```

```
(4, 3072, 8256) 1.137
463.5 1.1908756e+08 8.611369e+06
```

```{figure} ../_static/tutorials/static/sun-baseline-before-after.png
:alt: Visibility amplitude versus frequency on baseline 9-32 for a ten-minute Sun window, raw and after static subtraction, on a logarithmic amplitude axis.

Baseline 9-32 amplitude against frequency, averaged over four integrations,
before and after subtracting the template built above.
```

Three things to notice.

The strongest narrowband line, 463.5 MHz, drops 14x, from 1.19e8 to 8.6e6. It is
correlated across inputs and sits in the template at nearly the same amplitude,
which is what the subtraction is for.

The smooth continuum moves by tens of percent. Over 415-430 MHz the template is
67% of `|V|` on this baseline, and the subtracted amplitude is 1.48x the raw
one: subtraction is a complex vector operation, so a channel where the pedestal
opposes the source gets brighter. Across the 120 cross baselines of the 16
solved antennas the pedestal spans 1.3% to 145% of `|V|` in that band, median
17%; baseline 9-32 is deliberately near the top of that range, at the 88th
percentile.

Eighteen channels end up more than twice their raw amplitude. Those are
narrowband transmitters that were on at night and off during the Sun window, so
the template injects them: 435.9 MHz goes from 2.1e4 to 1.5e6. Pass
`rfi_mask=` to `build_static_visibility` to NaN those channels in the template,
which makes the subtraction a no-op there, or mask them downstream before the
solve.

Feed `clean` into fringe stopping and the SVD solve, as in
[rank-1 diagnostics](rank1-diagnostics.md); the production driver does exactly
this before [generating weights](generate-weights.md).

## What the template is worth, and when it is void

Static subtraction lifts the rank-1 ratio by a few units, which is the
cross-talk pedestal leaving the metric's denominator rather than a beam-quality
gain; the measured lifts are in wiki `recipes.md`. Never rank calibration
variants by rank-1.

Freshness beats duration: a short template from the adjacent night beats a
longer older one on B0329 S/N (numbers in wiki `recipes.md`).

A template is void across an F-engine re-sync or reflash, a wiring change, and
any EQ or gain change, because each moves the amplitudes or whole-sample delays
the template carries; with no matched template, solve without one. Check the
source night against known data incidents too. Cases and numbers: wiki
`recipes.md` and `incidents.md`.

## Provenance

Night: 2026-08-23 local, window 2026-08-24 03:03:12-03:28:23 UTC, 12
integrations, obs `2026-08-24-01:54:29`.
Sun window: 2026-08-23 20:42:59-20:49:51 UTC, 4 integrations, obs
`2026-08-23-19:18:14`.
Data: `/mnt/nvme4/data/casm/visibilities_64ant`, format `layout_64ant`.
Layout: `casm_antenna_layout_2026-08-07.csv`, matching these recordings.
Comparison template:
`/mnt/nvme5/vishnu/cal_build_20260824/static_aug23_exact512_CAL0823N.npz`.
Figures rendered by `scripts/render_static_template_tutorial.py`, which executes
the displayed blocks in this page and saves each figure in place of `plt.show()`.
