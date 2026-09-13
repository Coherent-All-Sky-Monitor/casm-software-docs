# Legacy folding implementation notes

These notes describe the existing campaign scripts for maintainers. Start with
the [folding tutorial](../guides/fold-b0329.md) for the scientific workflow and
the [modularization proposal](folding-design.md) for the planned replacement.

Use the existing CASM folding chain to turn a saved, search-rate, single-beam
filterbank into a pulse profile, time/frequency diagnostics, and a constrained
period/DM fit. Read the complete diagnostic figure before interpreting S/N.

This guide documents existing scripts; it introduces no folding implementation.
Its commands write derived products when run, but do not acquire observations,
program SNAPs, or upload weights. No folding commands were executed for this
documentation review on 2026-09-13.

## Start with the right input and script

The canonical operational recipe is
`/home/casm/software/dev/casm-wiki/fold-recipe.md`; the attempt ledger is
`/home/casm/software/dev/casm-wiki/detections.md`.

The shared `/mnt/nvme5/vishnu/b0329_fold/b0329_fold.sh` still omits zero-DM
removal (`-z zdot`) in the inspected copy. Running it unchanged does not implement
the canonical recipe. The audited September 1 campaign copy adds that option:

```text
/mnt/nvme5/vishnu/b0329_20260901/foldkit/b0329_fold.sh
```

Treat this as an available campaign snapshot, not a versioned package release.
It depends on sibling ephemeris, observatory and cleaning files. The higher-level
`b0329_fold_beams.sh` also references a `b0329_plan.py` absent from the inspected
shared kit; this guide starts after conversion rather than relying on that wrapper.

Before folding, establish:

- **Recording identity:** UTC interval, global beam number, deployed weights,
  tracking history if applicable, and the beam's actual on-source interval.
- **Filterbank identity:** a single-beam, search-rate `.fil`, with verified
  frequency order, sample interval, start time and payload length. Visibility
  integrations and slow monitoring products cannot supply this workflow.
- **Conversion provenance:** use the existing `casm-beamdump-to-fil` converter
  in [casm_io](../packages/io.md). The cleaning wrapper documents compatibility
  with `your`/`casm_io` headers and a `sigpyproc`-written-header failure downstream.
  Preserve the original dump and uncleaned filterbank.
- **Software:** `casm_offline_env`, Apptainer, the local `pulsarx_latest.sif` and
  `psrtools_latest.sif` images, and the full foldkit directory. The kit binds
  `/mnt` into the containers: input, output and ephemeris paths must be visible
  there. The `_latest` image names are mutable, so record their hashes for a run.

## What the existing chain does

| Stage | Inspected behaviour | What to record |
|---|---|---|
| `filtool` | `--zapthre -1 --baseline 8 -z kadaneF 8 4 -z zdot`, 32-bit output, zero mean/unit standard deviation | Exact command and cleaning log |
| `dspsr` | OVRO timing, supplied ephemeris, 60-second subintegrations, 256 phase bins | Ephemeris, selected start/duration and archive |
| Time mask | Rejects subintegrations with a combined robust outlier score above 4.5 | Rejected indices and before/after exposure |
| `clfd_local.sh` | Local off-pulse RMS IQR rejection plus `paz -r` channel cleaning | Masked count, archive and errors |
| Optional frequency zap | `-f` enables 432–442 MHz; `-F` selects another band | Whether used and why |
| `pdmp` | Profile, time/frequency panels and period/DM fit; `-D` narrows DM search | S/N, DM/error, width, period/error and PNG |

The time-mask score is absolute deviation divided by MAD without a Gaussian
normalization. Its threshold is not a calibrated 4.5σ detection threshold.
Time masking does not catch a contaminant present in every subintegration.

`clfd_local.sh` is a local approximation, not the upstream `clfd` package. In
this kit a cleaner failure can fall back to the raw archive and still produce
a `pdmp` result. Inspect the full terminal log for `local clfd FAILED` and check
which archive was analysed before accepting a comparison.

## Run the audited single-beam path

The following is an illustrative invocation for an operator-selected dataset.
Choose a fresh output directory and explicit source-in-beam window. Seconds are
relative to the input filterbank start. Beam numbers, windows and frequency zaps
from previous campaigns are not defaults for a new observation.

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
fold_kit=/mnt/nvme5/vishnu/b0329_20260901/foldkit
read -r -p 'Absolute input filterbank path under /mnt: ' fold_fil
read -r -p 'New absolute output directory under /mnt: ' fold_out
read -r -p 'Validated ephemeris path under /mnt: ' fold_par
read -r -p 'On-source start offset (seconds): ' fold_start
read -r -p 'On-source duration (seconds): ' fold_duration
bash "$fold_kit/b0329_fold.sh" "$fold_fil" \
    -E "$fold_par" -o "$fold_out" -l b0329_dmcheck \
    -S "$fold_start" -T "$fold_duration" -D -k
```

The kit performs `filtool` cleaning itself. Do not first clean the same input
with `casm-fil-clean` and then inadvertently clean it again. That package command
is the maintained standalone cleaning entry point for workflows that explicitly
continue at the folding stage. It rejects filterbanks with `tsamp > 0.1` seconds.
Zero-DM removal here is a pulsar recipe; it must not be applied to solar products
under the assumption that all broadband signals are interference.

`-D` implements `pdmp -do 0 -dr 1 -ds 0.02` around the archive's reference DM.
It is a constrained search, not a fit at one fixed DM. Verify that the ephemeris
and archive are centred on B0329's expected DM before using this option. The
inspected README advertises different DM steps/range; the script is authoritative
for this snapshot.

`-k` keeps folding archives for inspection. Without it the inspected script
deletes `.ar`, `.wclfd` and `.wfz` outputs; it deletes the temporary cleaned `.fil`
even with `-k`. Record the terminal output separately when launching a real run,
because mask summaries are not all preserved in the individual tool logs.

## Inspect the result

### A detection and a convincing-looking null

These are unchanged, archived `pdmp` figures, visually inspected for this guide.
They illustrate the diagnostic panels, not a matched sensitivity comparison.
Their pointing, calibration and integration lengths differ.

```{figure} ../_static/tutorials/fold/b457-20260904-detection.png
:alt: Archived B0329 fold with a narrow pulse near phase 0.18, a vertical frequency track, and pdmp S/N 20.45.
:width: 850px

**Recorded detection, 2026-09-04, beam 457.** Obs `2026-09-04-08:44:42`,
11:44–13:14 UTC, 90-minute window; 17-antenna late-window calibration cell.
The archived fit reports S/N 20.45, DM 27.044 ± 0.458 pc cm⁻³ and width 8.373 ms.
The narrow peak repeats because the plot extends beyond one rotation. Its phase
is near 0.18 under this corrected ephemeris, illustrating why phase 0.08 is not
universal. The canonical detection classification is in `casm-wiki/detections.md`.
```

```{figure} ../_static/tutorials/fold/b377-20260901-null.png
:alt: Archived beam 377 fold with noisy phase panels, no stable narrow pulse, and a pdmp search maximum of 5.55.
:width: 850px

**Recorded non-detection, 2026-09-01, beam 377.** Obs `2026-09-01-15:18:01`,
15:18:01–15:54:00 UTC, 36-minute window. The fit reports S/N 5.55, DM
26.504 ± 0.660 pc cm⁻³ and width 11.164 ms, but no credible persistent pulse.
The acceptable-looking DM and width did not establish a detection. Its use in an
EQ-gain comparison was retracted on September 2: the values were search maxima
on noise. Raw dumps and the original filterbank are recorded as no longer available.
```

Interpretation follows `casm-wiki/detections.md` and
`casm-wiki/incidents-archive-2026-09-02.md`. Full file paths, producing scripts,
hashes and validation boundaries are in the downloadable
[figure provenance](../_static/tutorials/fold/provenance.json).

Open `b0329_dmcheck_pdmp.png` with its matching `_pdmp.log`, `_dspsr.log` and
`_filtool.log`. Confirm the archive named in the `pdmp` log is the intended
cleaned archive. Then inspect these independent pieces of evidence:

1. **DM:** the bundled ephemeris gives 26.76410 pc cm⁻³. The wiki records free-DM
   fits dragged toward low DM by RFI. A large S/N at the wrong DM is not evidence
   of B0329. A constrained fit near the expected DM remains a diagnostic, not
   a sufficient detection criterion by itself.
2. **Profile and width:** inspect a localized pulse and quote its width and DM
   uncertainty. The canonical recipe flags widths around or above 50 ms and DM
   errors around or above 1 pc cm⁻³ as broad-contaminant warnings for the tested
   CASM observations. These are empirical review criteria, not universal cuts.
3. **Phase versus time:** the pulse should remain at a consistent phase after
   timing correction. Isolated bad subintegrations or a continuous slope need
   investigation before comparing sensitivity.
4. **Phase versus frequency:** inspect whether the signal aligns across the
   usable band and whether residual dispersion, narrow-band interference or
   aggressive channel masking dominates the apparent profile.

The wiki's expected phase near 0.08 belongs to its historical ephemeris and
folding convention. Compare against the matching reference archive. A new
ephemeris, phase convention or period correction can shift that coordinate;
do not make 0.08 a universal software acceptance rule.

`pdmp` reports pulse width in bins. Convert using the phase-bin count of the
archive actually analysed and the appropriate period, and state both. This
wrapper folds at 256 bins but passes `-mc 64 -ms 8` to `pdmp`; do not infer the
effective profile resolution from `dspsr -b` alone without checking the product.

## Resolve a tilted phase track

The bundled ephemeris has `PEPOCH 46473.0`, with old spin parameters. The wiki
therefore calls for period feedback when the phase-time track tilts: use the
corrected period from the same observation, refold that observation, and repeat
the DM/profile checks.

The inspected `pdmp` log labels barycentric (BC) and topocentric (TC) periods
and corrections in **milliseconds**, and BC frequency in **Hz**. These are not
interchangeable. Do not paste a topocentric period into an ephemeris `F0`, or
replace an old-epoch frequency with an observation-epoch value without updating
the timing model consistently. Use a validated observation-appropriate ephemeris
with `-E`, preserve the original, and document the timing frame and epoch.

The wrapper has no period-feedback option or automated refold loop. This preview
does not invent one. A reproducible corrected ephemeris remains a prerequisite
for the refold; inspect residual tilt and compare the same interval and masks.

## Provenance and review limits

Keep the input/weights/layout identifiers, source window, ephemeris and image
hashes, script hashes, cleaning settings, masks, archive, PNG and tool logs
together. Quote the chosen trial and any other periods/DMs/windows explored;
selecting the highest fitted S/N after many trials changes its interpretation.
Add accepted results or non-detections to the canonical wiki's attempt ledger,
with dated evidence paths and the tested domain.

This page was checked against wiki revision
`f0ff6d1c95c5ed0a43dcfbb5f4461e43f58948ab`, `casm_io` revision
`22ef826d9f2ba355388523265081da1468e5a4ff`, and the actual campaign files/logs:

| Inspected file | SHA-256 |
|---|---|
| September 1 `foldkit/b0329_fold.sh` | `9e81ee88b6dc038dbf915f188c8dca38ed9fc8fb464bf323fd4a0499d277fb9b` |
| September 1 `foldkit/B0329+54.par` | `e90bd55336091e14672207ed5bd9017c287514927c00a6bd6dacfb1a251fa35d` |
| September 1 `foldkit/clfd_local.sh` | `3efe5c17fff1eabe565a3b21e8383d868571de39b2826345c344458492c361f2` |
| September 1 `foldkit/rfi_time_mask.py` | `bd5e7a985841f0e20705ca24669573b6a6c22d404f31de188c4e833d7026d091` |
| `casm_io/filterbank/clean.py` | `e6ae8c7272131559dbbde4ea86b44623fdd024d688bc2d72bc8d7f9e8f2c0fb8` |

Existing example outputs are under
`/mnt/nvme5/vishnu/b0329_20260901/fold_lock/`, with the terminal log at
`/mnt/nvme5/vishnu/b0329_20260901/fold_lock.log`. Their presence demonstrates the
recorded chain, not a new validation of detection significance. No source scripts,
ephemerides, observations or hardware settings were changed for this guide.
