# A maintainable folding workflow

Status: design proposal. The existing campaign scripts remain unchanged.

The folding workflow should be a tested Python package with a small command-line
interface. B0329+54 is a worked configuration of that package, not a special
pipeline whose steps live in a sequence of copied shell scripts.

## Boundaries

Reuse `casm_io` for filterbank inspection and existing cleaning functionality.
Keep `dspsr`, `pdmp` and the established archive tools as scientific backends;
there is no reason to reimplement their algorithms here.

Separate input selection, cleaning, folding, archive inspection and report
generation into callable stages. A Python API and the CLI should call the same
stage implementations. Each stage accepts explicit inputs and returns named
outputs; none should depend on the caller's current directory.

## Behaviour to fix first

- Put the source, ephemeris, time window and cleaning settings in one validated
  configuration. Check units, file availability and container bind paths before
  running an expensive step.
- Use checked subprocess calls and retain stdout/stderr. A failed cleaner must
  stop the run, not silently substitute the uncleaned archive.
- Preserve intermediate archives by default. Cleanup is a separate explicit
  action; repeated runs must not overwrite earlier results silently.
- Record tool versions and processing settings automatically in a run manifest.
  The human report leads with the profile, time/frequency plots and conclusions.
- Keep period refinement explicit, with timing frame, epoch and units validated.
  Do not automatically optimize a detection claim by repeatedly maximizing S/N.

## Implementation order

1. Collect the existing scripts, dependency requirements and known-good test
   recordings. Choose the owning repository after checking the existing inventory.
2. Capture the current intended commands in tests, including failure and retention
   behaviour. Exclude known accidental fallbacks from the desired behaviour.
3. Extract the stages behind a single Python API and CLI. Keep a compatibility
   wrapper for existing campaign invocations during migration.
4. Compare both paths on one recorded detection and one non-detection, using
   identical data, masks, ephemerides and tool versions.
5. Publish the short tutorial against the tested interface and retire duplicate
   scripts after operator review.

Unit tests should use small fixtures and mocked process execution. Scientific
regression tests should run separately on approved recorded data, never as part
of an ordinary documentation build. Repository selection and source-code changes
need a separate implementation step from this documentation revision.
