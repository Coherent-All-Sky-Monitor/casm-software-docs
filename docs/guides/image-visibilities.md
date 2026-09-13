# Make a sky image from visibilities

A dirty image shows the response obtained by beamforming visibilities toward
many neighbouring directions. Use this optional tutorial to explore the sky
around a source. To check a calibration using a source's rise and fall through
a fixed beam, start with the [Cyg A transit tutorial](check-calibration.md).

## Plot one saved integration

This 165 KB product contains an already computed 241 × 241 all-sky frame.
Run from the documentation checkout root in the offline environment. Loading
and plotting it does not read raw visibilities or apply calibration again.

```python
import numpy as np
import matplotlib.pyplot as plt
from casm_imaging.imaging.allsky import plot_allsky_frame

path = "docs/_static/tutorials/imaging/allsky-saved.npz"
with np.load(path, allow_pickle=False) as saved:
    snapshot = {key: saved[key] for key in ("image", "time_unix", "l_axis", "m_axis")}
    snapshot["time_unix"] = float(snapshot["time_unix"])
    snapshot["sources"] = dict(zip(saved["src_names"], saved["src_lma"]))
assert snapshot["image"].shape == (241, 241)
fig, ax = plt.subplots(figsize=(6, 6))
artist = plot_allsky_frame(ax, snapshot, time_tz="UTC", cmap="viridis")
fig.colorbar(artist, ax=ax, shrink=0.7, label="Saved image value (instrumental)")
plt.show()
```

```{figure} ../_static/tutorials/imaging/allsky-saved.png
:alt: Saved all-sky frame with horizon, altitude rings and source markers, east on the left.

Output of the displayed code for the saved integration at Unix UTC
1789299471. The horizon is the outer circle; zenith is at the centre.
Source markers are the saved predicted positions, not fitted detections.
```

This redraw validates the saved-product plotting path. The product preserves
its configuration fingerprint but not a full calibration/layout manifest, so
it cannot establish that today's source recreates the original image values.
See [bounded example provenance](../developer/bounded-examples.md).

## Historical source-centred image

```{figure} ../_static/tutorials/imaging/cyga-transit-lm.png
:alt: Cyg A dirty image with a central positive peak and alternating red and blue sidelobes.

Cyg A, 2026-06-28, 02:00–04:00 America/Los_Angeles. This saved notebook
output uses 20 antennas, solar calibration, static subtraction and bandpass
normalization. It is an existing observation, not the output of the example below.
```

The source is near the centre. Red and blue show positive and negative
responses: the surrounding pattern includes the sparse array's sidelobes,
so each bright patch need not be another source. The cyan circles select a
background annulus for the displayed image statistic. They are not beam edges.

## Prepare a new image (illustrative, not executed)

Use an existing calibration and dated antenna layout with a short visibility
window. The maintained `casm_imaging` package reads and beamforms the data.
This example assumes `cal`, `ant`, `data_dir`, `time_start` and `time_end`
have been selected and checked using the
[input preparation example](../developer/imaging-notes.md#1-select-a-small-fully-described-input).

```python
from casm_imaging.imaging.pipeline import image_around_source

result = image_around_source(
    "cyg-a", cal_h5=cal, ant=ant,
    data_dir=str(data_dir), time_start=time_start, time_end=time_end,
    time_tz="UTC", fmt=None,
    grid="lm", estimator="real", ang_max_deg=10, npix=41,
    rfi_mask_version=None, normalize_bandpass=True, freq_avg=1,
    subtract_static=None, workers=1, show=True,
)
print(result["image"].shape)  # (41, 41)
```

The `lm` grid follows the source on a tangent plane, avoiding the alt/az
coordinate problem near zenith. `real` preserves the sign. Begin with only a
few integrations: the wrapper reads the full visibility triangle, so a small
image does not imply a small data read. The example applies no RFI mask or
static subtraction; choose those steps for the dataset before drawing conclusions.

## Compare the structure with the array's response

```python
from casm_imaging.imaging import psf_for_result

psf, x_deg, y_deg = psf_for_result(result, workers=1)
print(psf.shape)  # same pixel grid as result["image"]
```

The PSF predicts the image of an ideal point source through the same sampled
geometry. Comparing it with the observed structure helps identify sidelobes.
It does not supply a flux calibration: with bandpass normalization enabled,
the image is dimensionless, not Jy/beam. The displayed image SNR is a
peak/background statistic, not a pulsar detection significance.

The [implementation notes](../developer/imaging-notes.md) contain frequency,
mask and indexing contracts, a second historical image, and source/asset
provenance. The saved-product block was executed with its matching figure;
the new-analysis examples are illustrative. No raw observation was re-imaged.
