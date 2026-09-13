# Generate calibration and beam weights

The calibration driver reads visibilities, solves antenna gains and writes
beamforming weights with a diagnostic notebook. It does not upload them.
Use this guide after working through the [solar phase](solar-phase.md) and
[SVD](rank1-diagnostics.md) tutorials.

## Choose the observation

Start from the configuration saved with a recent reviewed product. In your
copy, set the solar or bright-source time window, dated antenna layout,
participating antennas and a new output directory. Keep the diagnostics and
notebook enabled, and select `grid_mode="exact"` for beam placement.

The solve window must contain a useful source signal. A longer interval is
not automatically better; changing solar structure and interference can affect
the result. The [configuration reference](../developer/weights-notes.md)
describes the available fields.

## Preview the settings

Activate the [shared environment](../getting-started.md), then inspect your
configuration without starting a solve:

```bash
python -m bf_weights_generator.make_cal_and_weights \
  --config /path/to/reviewed-recipe.json --print-params
```

Check the printed source window, antennas, output directory and grid mode.
This command displays settings; it does not check the recording's contents.

## Build the products

Once the configuration and analysis resources are agreed, run:

```bash
python -m bf_weights_generator.make_cal_and_weights \
  --config /path/to/reviewed-recipe.json
```

The run reads observation data and writes a calibration, beam weights,
report and notebook. Use a fresh output directory to avoid overwriting a
previous product. No solve was rerun to prepare this documentation.

## Open the diagnostic notebook

Start with the phase panels, then inspect the rank-1 plot:

```{figure} ../_static/tutorials/calibration/rank1_vs_freq_20260820.png
:alt: Rank-1 diagnostic from a saved solar calibration.

An existing solar solve's rank-1 curves. Use the frequency structure to find
channels that deserve a closer look; the ratio alone does not validate a beam.
```

Look for missing or **SKIPPED** notebook sections and errors in the report.
Confirm that the weight file contains the intended antennas, then
[check a Cyg A transit](check-calibration.md) and compare phase residuals
with the previous calibration.

The coherent-beam file also needs a matching incoherent-beam mask. Review the
pair together before following the separate [deployment guide](deploy-weights.md).
Creating files does not change the telescope's active weights.

The [developer notes](../developer/weights-notes.md) contain the Python API,
complete output list and details of the saved example.
