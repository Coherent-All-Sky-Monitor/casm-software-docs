# Keeping code and documentation together

Documentation is version-controlled in `casm-software-docs`. A documentation
revision describes a recorded set of software revisions, not whichever packages
happen to be installed when someone reads it.

## Current local workflow

1. Make and test the software change in its owning repository. Record the
   behaviour change, including shapes, units, defaults and compatibility.
2. Review the affected tutorial, package guide and examples in this repository.
   Update their explanation and expected outputs alongside the code change.
3. Refresh the reference snapshot deliberately:

   ```bash
   source /home/casm/software/dev/casm_venvs/casm_offline_env/bin/activate
   python scripts/snapshot_sources.py --source-root /home/casm/software/dev
   ```

4. Review the generated diff. Signatures, docstrings, source views and upstream
   manual copies update automatically. Tutorial explanations and scientific
   interpretations require an author and reviewer.
5. Build and check the site, then make a local documentation commit:

   ```bash
   python scripts/snapshot_sources.py --source-root /home/casm/software/dev --check
   python -m sphinx -W --keep-going -b html docs _build/html
   python scripts/check_site.py
   python scripts/check_exports.py
   ```

`source-snapshot.json` records the three API packages' Git revisions and source
hashes. Additional tutorial dependencies and historical figures carry provenance
on their own pages. These are not yet included in the automatic drift check.
Untracked files are excluded from the API snapshot. Tracked working-tree changes
are disclosed; a release should use reviewed, committed source revisions.

The site builds from committed documentation and recorded source copies without
access to the scientific checkouts. Building the site does not execute notebooks,
run calibrations, fold observations or deploy weights.

## Automation to add after review

No cross-repository CI or automatic publishing is configured yet. The intended
release process is:

- A software pull request identifies affected documentation. Its tests and
  documentation checks must pass before merge.
- A source-revision change opens a documentation update for review. It does not
  publish regenerated API text as a substitute for reviewing the tutorials.
- Documentation CI checks the recorded revisions, builds with warnings treated
  as errors, checks links and runs bounded, offline example tests.
- A reviewed documentation release is tagged and published at an immutable
  version URL. The release manifest identifies every covered software revision;
  `latest` points to the newest reviewed build.

The repositories can release independently. The documentation release manifest
records the tested combination; matching version numbers across all packages
are unnecessary. Archive previous published versions from this point onward,
without reconstructing old releases.

Repository workflows, branch protection and hosting need a separate approved
configuration change. Until then, the local commands above are the operating
procedure, and Vishnu reviews and pushes the commits.

## Scientific figures

Reuse an existing result with its observation date, input selection, generating
script or notebook, software provenance and limitations. Keep a copy of the
figure in the documentation so a scratch-directory cleanup cannot break it.
A historical figure illustrates the recorded experiment; it does not establish
the present array state or prove that a newer code version reproduces it.

Re-run a tutorial only as an explicit analysis task with an agreed data and
resource budget. Review changed outputs before updating the published result.
