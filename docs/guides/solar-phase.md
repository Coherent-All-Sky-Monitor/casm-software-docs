# See the Sun in baseline phase

A phase waterfall shows how the relative signal phase between two antennas
changes with time and frequency. Compare the measured phase with the geometric
prediction for the Sun, then remove that predicted motion by fringe stopping.

After [reading your first visibilities](read-visibilities.md), select a daytime
window and its matching layout. For new observations use
`/home/casm/software/dev/antenna_layouts/current`. The dated path below belongs
to the historical example. This uses the same ten-minute recording as the
first tutorial, with antenna 9 as the reference and antenna 19 as the target.

```python
from casm_io.correlator import AntennaMapping, read_visibilities

ant = AntennaMapping.load(
    "/home/casm/software/dev/antenna_layouts/casm_antenna_layout_2026-08-07.csv"
)
ant = ant.with_inactive([a for a in ant.active_antennas() if a not in (9, 19)])
target_ids = sorted(a for a in ant.active_antennas() if a != 9)
data = read_visibilities(
    data_root="/mnt/nvme4/data/casm",
    time_start="2026-08-23 20:42:00", time_end="2026-08-23 20:52:00",
    time_tz="UTC", ref=ant.packet_index(9),
    targets=[ant.packet_index(a) for a in target_ids],
)
print(data.vis.shape)  # time, frequency, reference-to-target baseline
```

This reads only reference-to-target cross-correlations, in the order expected
by fringe stopping. Do not substitute the two-input triangle from the first
tutorial. `with_inactive()` makes an in-memory selection for this example;
it does not change the layout file or the live beamforming set.

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

These offline settings permit older Earth-orientation predictions for this
illustration. Refresh the IERS tables before using this workflow for calibration.

```{figure} ../_static/tutorials/solar/solar-phase-two-antennas.png
:alt: Antenna 9 by antenna 19 phase in three panels: raw, Sun geometric prediction, and fringe-stopped, in red and blue.

Output of the code above: four integrations on August 23, 2026,
20:42:59–20:49:51 UTC. Frequency is vertical and elapsed time is horizontal.
No static background subtraction, calibration or frequency mask is applied.
```

Read across the three panels. The geometric prediction changes with time and
frequency. Fringe stopping removes that predicted phase from the measured
cross-correlation. The frequency bands that remain can carry instrumental
delay; fringe stopping alone does not flatten that delay. This short window
contains only four integrations, so it is a first look rather than a transit test.

Red and blue show phase, not signal strength or “bad” and “good.” The endpoints
−π and +π represent the same phase, so an abrupt red/blue boundary can be a wrap.
Check amplitude or coherence before interpreting noisy phase. A white region can
be masked data or phase near zero, depending on the surrounding pattern.

The header gives the interval in local time; the horizontal axis uses elapsed
hours. With more antennas, the renderer groups baselines by SNAP pair and may
return several figures.

Next, compare [calibration residuals and an independent source](check-calibration.md).

[Source, data, and verification notes](../developer/solar-example-notes.md).
