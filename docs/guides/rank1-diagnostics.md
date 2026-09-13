# Plot SVD and rank-1 diagnostics

An SVD plot shows whether one coherent component dominates a calibration
solve. Start with the saved result of a solar calibration and plot its rank-1
ratio against frequency.

## Open a saved result

After [activating the environment](../getting-started.md), run this in a notebook.
The example file is an existing solar solve on the CASM host:

```python
import numpy as np
import matplotlib.pyplot as plt

path = "/mnt/nvme5/solar0819/recipe_demo_20260820/rank1_vs_freq_20260820.npz"
with np.load(path, allow_pickle=False) as data:
    frequency = data["freq_mhz"]
    ratio = data["rank1"]

fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(frequency, ratio, linewidth=0.7)
ax.set(xlabel="Frequency (MHz)", ylabel="Rank-1 ratio")
ax.grid(alpha=0.25)
plt.show()
```

The ratio is the largest singular value divided by the second largest.
Higher values mean the leading component is more dominant in this solve.

```{figure} ../_static/tutorials/calibration/rank1_vs_freq_20260820.png
:alt: Solar rank-1 ratio before and after subtraction of a night-time static signal.

The saved August 19 solar analysis, shown with its original comparison curve.
Subtracting a night-time static signal raises the ratio over much of the band.
```

The short code plots the saved primary curve. The original figure above also
includes the comparison without static subtraction. Notice the frequency
structure: a single median would hide narrow dips and changes across the band.

To compare two solves, keep the source window, antennas and frequency mask
the same. A higher ratio alone does not prove that a calibration makes a
better beam. Next, [watch Cyg A cross a fixed beam](check-calibration.md).

See [developer notes](../developer/svd-notes.md) for the plotting API,
matrix preparation and details of these saved figures.
