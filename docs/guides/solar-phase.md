# See the Sun in baseline phase

A phase waterfall shows how the relative signal phase between two antennas
changes with time and frequency. Compare the measured phase with the geometric
prediction for the Sun, then remove that predicted motion by fringe stopping.

After [reading your first visibilities](read-visibilities.md), select a daytime
window and its matching layout. For new observations use
`/home/casm/software/dev/antenna_layouts/current`. The dated path below belongs
to the historical example. Extend the first tutorial's observation to three
hours, with antenna 9 as the reference and antenna 19 as the target, to see
the phase evolve as the Sun moves.

```python
from casm_io.correlator import AntennaMapping, read_visibilities

ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-07.csv"
)
ant = ant.with_inactive([a for a in ant.active_antennas() if a not in (9, 19)])
target_ids = sorted(a for a in ant.active_antennas() if a != 9)
data = read_visibilities(
    data_root="/mnt/nvme4/data/casm",
    time_start="2026-08-23 19:20:00", time_end="2026-08-23 22:20:00",
    time_tz="UTC", ref=ant.packet_index(9),
    targets=[ant.packet_index(a) for a in target_ids],
    workers=1,
)
print(data.vis.shape)  # time, frequency, reference-to-target baseline
```

This reads only reference-to-target cross-correlations, in the order expected
by fringe stopping. Do not substitute the two-input triangle from the first
tutorial. `with_inactive()` makes an in-memory selection for this example;
it does not change the layout file or the live beamforming set.

The two `iers.conf` settings below let the offline example run against the
installed Earth-orientation tables. Refresh those tables before using this
workflow for calibration.

```python
import matplotlib.pyplot as plt
from astropy.utils import iers
from casm_vis_analysis.fringe_stop import fringe_stop
from casm_vis_analysis.plotting.fringe_diag import plot_fringe_diagnostic

# Offline illustration using the installed Earth-orientation predictions.
with iers.conf.set_temp("auto_download", False), iers.conf.set_temp("auto_max_age", None):
    fs = fringe_stop(data, ant, ref_ant=9, source="sun", sign=-1)
figures = plot_fringe_diagnostic(
    panels=[
        ("Raw phase", fs["vis"]),
        ("Geometric", fs["geometric_phase"]),
        ("Fringe-stopped", fs["vis_stopped"]),
    ],
    time_unix=fs["time_unix"],
    freq_mhz=fs["freq_mhz"],
    target_labels=fs["target_labels"],
    target_snaps=[ant.snap_adc(a)[0] for a in fs["target_aids"]],
    ref_snap=ant.snap_adc(9)[0],
    freq_mask=fs["freq_mask"],
    time_tz="America/Los_Angeles",
)
plt.show()
```

The existing renderer uses **RdBu** with phase fixed to −π…+π radians:

```{figure} ../_static/tutorials/solar/solar-phase-two-antennas.png
:alt: Antenna 9 by antenna 19 phase in three panels: raw, Sun geometric prediction, and fringe-stopped, in red and blue.

Output of the code above: 79 integrations on August 23, 2026,
19:20:31–22:19:11 UTC.
Frequency is vertical and elapsed time is horizontal.
No static background subtraction, calibration or frequency mask is applied.
```

Read across the three panels. The geometric prediction changes with time and
frequency. Fringe stopping removes that predicted phase from the measured
cross-correlation: the raw bands curve with time, while the stopped bands are
more nearly horizontal. Residual structure remains, especially late in the
window. The frequency bands can carry instrumental delay; fringe stopping
alone does not flatten that delay.

Red and blue show phase, not signal strength or “bad” and “good.” The endpoints
−π and +π represent the same phase, so an abrupt red/blue boundary can be a wrap.
Check amplitude or coherence before interpreting noisy phase. A white region can
be masked data or phase near zero, depending on the surrounding pattern.

The header gives the interval in local time; the horizontal axis uses elapsed
hours. With more antennas, the renderer groups baselines by SNAP pair and may
return several figures.

## Score the result with coherence

```{code-block} python
import numpy as np
from casm_vis_analysis.fringe_stop import coherence_metric

coh = coherence_metric(fs["vis_stopped"], fs["freq_mask"])  # (time, baseline)
print(np.nanmean(coh[fs["time_mask"]], axis=0))
```

`coherence_metric` averages unit phasors over frequency, keeping the channels
where `freq_mask` is True. Judge a baseline on the fringe-stopped coherence,
never on raw `|corr|`: the raw-amplitude cut called healthy antenna 30 dead on
2026-08-19 at raw 0.0057 against fringe-stopped 0.978 (casm-wiki
`antenna-health-triage.md`). A good baseline sits near 0.99 once its residual
delay is removed; the delay is still in here, and a phase that wraps across the
band pulls the frequency average down.

Pass `rfi_mask=` to `fringe_stop` to set that mask, for example
`rfi_mask=RFIMask(bad_ranges_mhz=[(465.3, 466.7)])` from
`casm_vis_analysis.rfi` for the satellite emitter.
It populates `fs["freq_mask"]` (True = good) for downstream steps and leaves
`fs["vis_stopped"]` unmodified at flagged channels.

## Extract one baseline's phase

`fs["target_aids"]` holds the antenna IDs in the order of the baseline axis:

```{code-block} python
k = fs["target_aids"].index(19)               # baseline column for antenna 19
phase = np.angle(fs["vis_stopped"][:, :, k])  # (time, frequency), radians
```

Next: [mask RFI and fit per-antenna delays](rfi-and-delay.md) removes the
frequency slope left here, and
[solve a calibration and plot rank-1](rank1-diagnostics.md) turns the
fringe-stopped visibilities into gains. For an independent source, compare
[calibration residuals](check-calibration.md).

## Provenance

Data: `/mnt/nvme4/data/casm`, `visibilities_64ant/2026-08-23-19:18:14.dat.{0,1,2}`,
19:20–22:20 UTC on 2026-08-23 (79 integrations returned, 19:20:31–22:19:11 UTC).
Layout: `casm_antenna_layout_2026-08-07.csv`, matching this recording.
Figure rendered by `scripts/render_solar_phase_tutorial.py`, which executes the
displayed blocks in this page and saves the figure in place of `plt.show()`.
