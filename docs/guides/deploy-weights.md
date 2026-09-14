# Review and deploy a weights product

`bf_weights_generator.deploy_bf_weights` converts verified CB/IB HDF5 products
to per-stream DADA payloads and can upload them or save restart defaults.
Live upload remains an explicitly approved human operation. This tutorial
documents the interface; no staging, upload, or default replacement was run.

## 1. Establish which product is ready

Start with the [generation report and notebook](generate-weights.md). Confirm
the intended calibration, grid, antenna membership, paired IB mask, and
[independent phase/source checks](check-calibration.md).
Record the product hashes and the rollback product before proposing a change.

Any F-engine `--do_sync` or reflash voids the standing calibration: re-solve
and rebuild the weights before deploying anything that predates it.

Activate the shared environment and inspect the installed interface:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
cd /home/casm
python -m bf_weights_generator.deploy_bf_weights --help
```

Check the current wiki `weights-and-deploy.md`, `weights-verification.md`, and
`correlator-default-weights.md` for live configuration. Numerical examples in
older package documentation are historical. In particular, int8 quantization
scale and the DADA runtime `SCALE` header are different quantities.

**`--scale` and `--ib-scale` must pair with the correlator's `bf_scale_factor`.**
They set only the DADA `SCALE` header (bfcorr's runtime gain), never the int8
values in the HDF5, which are always quantized at `scale_factor=127`. The
pairing changes when the correlator configuration changes, so read the latest
row of the wiki ledger `deployed_weights.csv` and `ib-subtraction.md` before
every deploy and pass exactly what they record. Since 2026-09-02 (Route Z,
`BFCORR_BF_SCALE_FACTOR` 8 on both nodes) that is `--scale 8064 --ib-scale 32`
with `--save-defaults`; a saved CB default without `SCALE 8064` serves a 252x
too-large beam after a restart. The tool defaults of 32/32 belong to
`bf_scale_factor=127`, and `--ib-scale 8` to the `bf_scale_factor=64` era
still quoted in the IB generator's docstring; either one deployed today breaks
CB-IB subtraction.

## 2. Preview without recording a deployment

`--dry-run` never touches the registry: the run returns at the plan printout
before the registry is imported (`deploy_bf_weights.py:546-558`). A staging run
without `--dry-run` and without `--upload` does reach the registry: it records a
product entry with an empty live-event list (L560, 644-650), and it exits 2 if
`casm_t2.weights_registry` is not importable (L561-564). Add `--no-registry` to
staging commands so a rehearsal neither records a product nor fails on a missing
`casm_t2`:

```bash
python -m bf_weights_generator.deploy_bf_weights \
  /path/to/verified-cb.h5 \
  --ib-weights /path/to/verified-ib.h5 \
  --output-dir /path/to/new-staging-directory \
  --dry-run --no-registry
```

`--dry-run` returns the deployment plan before any output directory, payload,
FIFO, defaults, or registry write; `--upload --dry-run` also performs no
upload or registry recording. Check which checkout your environment resolves:

```
python -c "import bf_weights_generator, casm_calibrator; print(bf_weights_generator.__file__); print(casm_calibrator.__file__)"
```

A path under `software/dev/worktrees/` is the audit worktree; a path under
`software/dev/<repo>` is the main checkout.

The preview reads and converts the weight files, so allow memory for that work.
Inspect CB/IB file types, selected streams, header values, sizes, and destinations.
Do not bypass a type or frequency-order error to make the command finish.

## 3. Stage inspectable files

This writes local files, without a live upload or registry event. Take the
pairing from the latest `deployed_weights.csv` row:

```bash
python -m bf_weights_generator.deploy_bf_weights \
  /path/to/verified-cb.h5 \
  --ib-weights /path/to/verified-ib.h5 \
  --output-dir /path/to/new-staging-directory \
  --scale 8064 --ib-scale 32 --save-defaults \
  --no-registry
```

Use a new staging directory because files of the same names can be overwritten.
CB staging names are `direct.dada.<stream>`; IB names are
`direct_ib.dada.<stream>`. Verify payload bytes, membership, subband ordering,
and headers with the existing verification workflow. A DADA file being present
locally proves staging, not which weights are serving.

The upload command reconverts the HDF5 files; it does not consume these staged
files as an immutable transaction. Reconfirm input hashes and any intentional
activation timestamp before approval.

## 4. Human-approved live upload

After explicit approval for these exact products and targets, take the pairing
from the latest `deployed_weights.csv` row and run:

```bash
python -m bf_weights_generator.deploy_bf_weights \
  /path/to/verified-cb.h5 \
  --ib-weights /path/to/verified-ib.h5 \
  --output-dir /path/to/new-staging-directory \
  --scale 8064 --ib-scale 32 --save-defaults \
  --upload
```

Do **not** use `--no-registry` for a live upload. T2/T3 need the registry to attach
correct beam coordinates to candidates. The tool writes each stream to its
assigned node's FIFO; completion across all selected streams must be checked.
No automatic scientific success or rollback is implied by the command.

`--utc-start` optionally specifies `YYYY-MM-DD-HH:MM:SS` UTC for activation.
Coordinate it with the observation and any beam-tracking process; an elapsed
timestamp or overlapping scheduler changes the operational meaning.

## 5. Decide separately about restart defaults

Adding `--save-defaults` writes restart fallback files on the correlator hosts.
It is a separate persistent change and must be included in the operator's
approval. Without `--ib-weights`, only CB defaults are refreshed.

The IB staging basename is renamed to the runtime default basename during this
operation. Each node serves its assigned streams; inspect the relevant files
on their owning nodes. File ages for another node's streams can be misleading.

## 6. Verify what landed

Check live registry events, per-node serving payload hashes, and the actual
pointings/membership against the approved product. If defaults were requested,
verify their copies too. The registry call happens after FIFO operations:
registry failure can leave weights live but unregistered. Preserve the log and
resolve the partial outcome rather than treating an error exit as “nothing changed.”

Six checks exist, described in wiki `weights-verification.md`:

- **(a) Cal-division pointing fit.** Divide the cal out of the deployed weights
  and fit the residual steering phase per beam against the stated pointings
  (`bf_weights_generator.recipe_verify`). Near-horizon fits are degenerate.
- **(b) Subband decode of the as-deployed payloads.** Decode the
  `direct.dada.N` / `incoh.dada.N` files on each node and compare against the
  dry-run. **This is the only check that proves what is serving.** corr1 serves
  streams 0-2 and corr2 serves 3-5; read each node's own three streams, never
  a cross-copied set.
- **(c) Byte validation.** `bf_weights_generator/tests/validate_recipe.py`
  rebuilds known-good products and compares every HDF5 dataset by md5.
- **(d) Vis-domain achromaticity.** Synthesize a stationary beam from the
  visibilities and measure each channel's transit half-max midpoint. Quote the
  cross-only figure.
- **(e) Bright-source referee.** Form the coherent beam on a bright night
  source with each cal and compare coherence, with an off-beam null as control.
- **(f) Sample-slip delay check.** Difference two cals from matched
  source-altitude windows and fit a delay per antenna. Whole-sample slips show
  up as multiples of 4.00 ns.

Finally assess observation continuity, injection recovery, and the appropriate
calibration/source checks. Update the canonical wiki and deployment ledger with
the date and evidence after a real operation.

## 7. Rollback

There is no rollback subcommand. Take the pairing from the latest
`deployed_weights.csv` row and redeploy the previous product's HDF5 with the
same command:

```bash
python -m bf_weights_generator.deploy_bf_weights \
  /path/to/previous-cb.h5 \
  --ib-weights /path/to/previous-ib.h5 \
  --output-dir /path/to/rollback-staging-directory \
  --scale 8064 --ib-scale 32 --save-defaults \
  --upload
```

Keep `--save-defaults` so the restart fallback matches what is serving. The record of what was live, and of
which cal each product came from, is the wiki ledger `deployed_weights.csv`;
identify the previous row before you deploy, not after.

Implementation details and source versions are in the
[developer notes](../developer/weights-notes.md).
