# Visibility analysis

`casm_vis_analysis` turns correlator visibilities into baseline diagnostics,
fringe-stopped data, delay estimates, and synthesized-beam checks. Start here
when investigating an antenna, a phase change, or whether calibration transfers
to another source or observing day.

Source revisions and file hashes: `source-snapshot.json` in the repository.
Examples are illustrative and were checked against source signatures; they
have not been executed against telescope data for this preview.

## Choose a task

| Question | Existing interface |
|---|---|
| What does each input's spectrum look like? | `run_autocorr`, `casm-autocorr` |
| Are fringes or interference visible? | `run_waterfall`, `casm-waterfall` |
| Does removing source geometry stabilize phase? | `fringe_stop`, `run_fringe_stop` |
| Does a calibration produce a source response? | `beam_power_vs_time` |
| Does a source cross the proposed beam grid? | `validate_source`, `plot_source_validation` |
| Is a static visibility floor affecting the result? | `build_static_visibility`, `subtract_static_visibility` |

The [calibration-check guide](../guides/check-calibration.md) connects these
measurements. The [API inventory](vis-analysis-api.md) lists source signatures.

## Installation and dependencies

The default environment for Vishnu's repositories is `casm_offline_env`:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
python -c "import casm_io, casm_vis_analysis; print(casm_vis_analysis.__file__)"
```

Use the installed modules first. If preparing a new environment, upstream
supports `python -m pip install -e /path/to/casm_io` followed by the same command
for `casm_vis_analysis`; installation changes that environment. Layout
synchronization has additional CAsMan and network dependencies. Ordinary
visibility plotting does not require a sync.

## Read a bounded observation window

Use `casm_io` for loading. Supply the observation's layout explicitly when
replaying history; the current layout may describe different wiring.

```python
from casm_io.correlator import AntennaMapping, load_format, read_visibilities
from casm_vis_analysis.fringe_stop import fringe_stop

ant = AntennaMapping.load("/path/to/observation-layout.csv")
data = read_visibilities(
    time_start="2026-09-01 19:00:00",
    time_end="2026-09-01 19:30:00",
    time_tz="UTC",
    data_root="/path/to/data-root",
    fmt=load_format("layout_64ant"),
)
print(data["vis"].shape, data["freq_mhz"][[0, -1]])
print(data["time_unix"][[0, -1]])

# Choose an active reference appropriate for this observation.
reference_id = 9
fs = fringe_stop(data, ant, ref_ant=reference_id, source="sun", sign=-1)
```

The timestamps and reference above are examples, not a recommended calibration
window. Auto-discovery can cross observation boundaries; inspect gaps and the
actual returned times. RFI masks must be chosen explicitly for the analysis.

## Plot baseline phase versus frequency

```python
from casm_vis_analysis.plotting.phase_freq import plot_phase_vs_freq

figures = plot_phase_vs_freq(
    [("Fringe stopped", fs["vis_stopped"])],
    fs["freq_mhz"],
    baseline_labels=fs["target_labels"],
    time_unix=fs["time_unix"],
    time_mask=fs["time_mask"],
    freq_mask=fs.get("freq_mask"),
    unwrap=False,
    output_path=None,
)
```

Wrapped phase exposes the familiar sawtooth. Unwrapped phase can help inspect
delay slopes, but bad channels and low coherence can make unwrapping misleading.
The function averages complex visibilities before taking phase and always
returns a list of figures, including when there is just one figure.

## Shapes, axes, and masks

| Quantity | Convention |
|---|---|
| Visibility data | Complex `(time, frequency, baseline)` |
| Frequency | MHz; native reader order is descending |
| Time | Unix seconds; display timezone is a separate choice |
| Antenna position / baseline | East, north, up in metres |
| Geometric delay | Seconds |
| `freq_mask` | `True` means include / good |
| `RFIMask.flag_bins()` | `True` means contaminated / bad |

Antenna IDs, packet indices, SNAP ADC indices, and baseline-array indices are
different namespaces. Use `AntennaMapping` and `casm_io` baseline helpers.
The fringe-stop function handles reference/target ordering and conjugation.

`fringe_stop` intersects `valid_integrations` with input and transit time masks;
an empty valid selection raises. It rejects unsupported input-subset triangles
before baseline indexing and validates labeled reference/target ordering.
Use the full native triangle for the fringe-stop/calibration workflow rather
than treating a plotting subset as a relabeled full observation.

`run_waterfall` reads a subset triangle for the selected inputs. Its returned
`inputs` and `nsig` describe that subset; indices from the full correlator
triangle cannot be reused directly. `run_autocorr` and `run_fringe_stop` do not
share that memory-saving reader path. Start with a short interval.

## Interpretation and boundaries

Fringe stopping removes predicted geometric phase. Diagnostic delay correction
is an additional operation; do not silently substitute delay-corrected arrays
for the calibration pipeline's inputs. `casm_calibrator.svd_calibrate` requires
both fringe-stop metadata and the original full-triangle `data=`.

`beam_power_vs_time` returns the cross-baseline contribution, excluding autos.
It is a directional diagnostic, not calibrated flux density, SEFD, or a fast
beam recording. A stationary pointing produces a transit; a source-name
pointing tracks the source and answers a different question.

## Source documentation discrepancies

The older `CLAUDE.md` array signature for `fringe_stop` belongs to the current
`fringe_stop_array` primitive. Use `fringe_stop(data, ant, ...)` for the composed
API. The old claim that phase plotting returns one figure is also superseded.
Mask policy requires an explicit choice; `RFIMask.from_static()` loads a
versioned configuration but is not evidence that it suits every observation.

Layout `status`/`diff` can refresh a local CAsMan snapshot over the network even
though they do not apply layout changes. Layout synchronization is outside the
read-only diagnostic examples here.

## Upstream reading

- [README](https://github.com/Coherent-All-Sky-Monitor/casm_vis_analysis/blob/main/README.md)
- [Fringe stopping](https://github.com/Coherent-All-Sky-Monitor/casm_vis_analysis/blob/main/docs/fringe_stop.md)
- [Beam validation](https://github.com/Coherent-All-Sky-Monitor/casm_vis_analysis/blob/main/docs/beam_validation.md)
