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
Do not copy an old IB scale override. Review current tool defaults against
the actual runtime configuration before proceeding.

## 2. Preview without recording a deployment

```bash
python -m bf_weights_generator.deploy_bf_weights \
  /path/to/verified-cb.h5 \
  --ib-weights /path/to/verified-ib.h5 \
  --output-dir /path/to/new-staging-directory \
  --dry-run --no-registry
```

At the inspected revision, `--dry-run` suppresses payload and FIFO writes but
still creates `--output-dir`. `--no-registry` is deliberate **only for this
offline preview**: the current final registry-recording call is not guarded
by `--dry-run`. Do not combine `--upload` with a registry-enabled dry run;
it can record live-stream events without sending payloads.

The preview reads and converts the weight files, so allow memory for that work.
Inspect CB/IB file types, selected streams, header values, sizes, and destinations.
Do not bypass a type or frequency-order error to make the command finish.

## 3. Stage inspectable files

This writes local files, without a live upload or registry event:

```bash
python -m bf_weights_generator.deploy_bf_weights \
  /path/to/verified-cb.h5 \
  --ib-weights /path/to/verified-ib.h5 \
  --output-dir /path/to/new-staging-directory \
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

After explicit approval for these exact products and targets, the operator uses:

```bash
python -m bf_weights_generator.deploy_bf_weights \
  /path/to/verified-cb.h5 \
  --ib-weights /path/to/verified-ib.h5 \
  --output-dir /path/to/new-staging-directory \
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

Finally assess observation continuity, injection recovery, and the appropriate
calibration/source checks. Update the canonical wiki and deployment ledger with
the date and evidence after a real operation. This tutorial creates no such event.

Implementation details and source versions are in the
[developer notes](../developer/weights-notes.md).
