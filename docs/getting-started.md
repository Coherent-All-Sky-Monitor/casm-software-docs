# Getting started

Use the existing **casm_offline_env** environment for Vishnu's CASM software.
The documentation build reads source files without importing the telescope
packages or changing their checkouts.

## On the CASM host

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
cd /home/casm
```

Run analysis outside the shared `software/dev` directory to avoid local
directory names shadowing installed packages. Pass data paths explicitly.

## Choose the right layer

| Task | Package | Input | Result |
|---|---|---|---|
| Read correlator data | `casm_io` | Data directory, time interval, input selection | Complex visibilities with time/frequency axes |
| Inspect spectra or phases | `casm_vis_analysis` | Visibilities, layout, source | Diagnostic arrays and figures |
| Solve a calibration | `casm_calibrator` | Suitable fringe-stopped data and configuration | Gains, weights, flags and quality diagnostics |

For an operational calibration/weights product, use the team's canonical
`bf_weights_generator.make_cal_and_weights` workflow. This preview does not
replace that procedure or authorize deployment.

## Before using a real dataset

1. Identify the observation's format and layout epoch.
2. Select a small time range, frequency interval and baseline subset.
3. Inspect the returned shapes, frequency endpoints and timestamps.
4. Check gaps, flags and configuration before interpreting any statistic.

The [visibility guide](guides/read-visibilities.md) walks through a bounded
read. The [contracts page](guides/contracts.md) collects the conventions most
likely to affect interpretation.

## Rebuild this documentation

From the `casm-software-docs` checkout:

```bash
python -m pip install -r requirements-docs.txt
python -m sphinx -W --keep-going -b html docs _build/html
python scripts/check_site.py
python -m http.server 8070 --bind 127.0.0.1 --directory _build/html
```

The committed documentation snapshot builds without sibling repositories.
Refreshing the snapshot explicitly requires the source checkouts; see the
repository README. The docs dependency installation is for the documentation
toolchain, not a reinstall of the scientific packages.
