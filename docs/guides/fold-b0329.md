# Find a pulsar in a recorded beam

Folding lines up successive rotations of a pulsar and averages them into a
pulse profile. Here we use B0329+54 to see what a detection looks like and
how to distinguish it from a promising-looking fit to noise.

You need a single-beam filterbank (`.fil`) and an ephemeris, the timing model
that predicts the pulsar's rotations. Correlator visibilities are too slowly
sampled for this task.

## Follow the pulse through the plots

```{figure} ../_static/tutorials/fold/b457-20260904-detection.png
:alt: B0329 detection showing a narrow pulse and aligned signal through frequency and time.

B0329+54 detected in beam 457 on September 4, 2026, using a 90-minute interval.
The narrow pulse appears at the same phase across the usable band.
```

Start with the averaged profile, then look for the same pulse in the
frequency and time panels. A detection should make sense in all three views.
The repeated profile peak is the same pulse displayed over multiple rotations.

The dispersion measure (DM) describes the frequency-dependent arrival delay.
B0329's expected DM is about 26.76 pc cm⁻³. Search close to this value and
check the pulse shape, rather than choosing whichever trial has the largest S/N.

## Prepare and fold a recording

The existing workflow has four main steps:

1. Select the interval when the pulsar is inside the beam.
2. Clean interference from the filterbank, including the pulsar recipe's
   zero-DM removal.
3. Fold with `dspsr`, using the ephemeris and short subintegrations.
4. Inspect the archive and refine the period/DM fit with `pdmp`.

The current wrapper is a campaign script, not yet a supported Python module.
Use the complete inspected kit, including its sibling timing and cleaning files.
The [implementation notes](../developer/folding-notes.md) explain its dependencies.

For an existing recording on the CASM host, replace the example paths and
choose the on-source start and duration in seconds:

```bash
source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
fold_kit=/mnt/nvme5/vishnu/b0329_20260901/foldkit
bash "$fold_kit/b0329_fold.sh" /mnt/your-observation/beam.fil \
  -E /mnt/your-observation/B0329.par \
  -o /mnt/your-observation/new-fold -l b0329 \
  -S 0 -T 1800 -D -k
```

This example folds the first 30 minutes; use your observation's actual
on-source window. `-D` restricts the DM search around the ephemeris value,
and `-k` keeps the folding archives. The wrapper performs cleaning itself.
Use a fresh output directory and check the log for a failed cleaning stage
before trusting the result. This example has not been rerun for the docs.

## Recognize a non-detection

```{figure} ../_static/tutorials/fold/b377-20260901-null.png
:alt: B0329 non-detection with noisy panels and no persistent narrow pulse.

Beam 377 on September 1, 2026. The fitter returns a plausible DM, but the
panels do not show a persistent pulse. This observation is a non-detection.
```

A fitted S/N or plausible DM alone is insufficient. Look for a narrow profile
that persists through time and frequency. A sloping pulse track can indicate
an inaccurate timing model; a bright patch in only a few channels can be RFI.
The pulse's absolute phase depends on the ephemeris, so it need not appear at
the same horizontal coordinate in different campaigns.

These two recordings have different observing conditions and integration
lengths. They illustrate recognition of a pulse, not a sensitivity comparison.

Next: [how the folding software should be modularized](../developer/folding-design.md).
Dataset details and script limitations are in the
[implementation notes](../developer/folding-notes.md).
