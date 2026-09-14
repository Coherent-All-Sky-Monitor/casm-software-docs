# Keeping code and documentation together

Documentation is version-controlled in `casm-software-docs`. A documentation
revision describes a recorded set of software revisions, not whichever packages
happen to be installed when someone reads it.

## Current local workflow

Every source change includes a documentation review. This applies to APIs,
defaults, file formats, scientific behaviour, command-line options, dependencies
and operational procedures. A private refactor may need no prose change; state
why in the handoff. Do not add meaningless documentation edits just to satisfy
a checkbox.

Agents working in source repositories must read this page before changing code.
Update both the owning repository's documentation and the affected pages here.
Do not call a behaviour-changing task complete while its examples describe the
old behaviour. When the docs checkout or required data are unavailable, report
the outstanding documentation work explicitly.

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

Record the source commit and corresponding docs commit in the handoff. Commit
only the files belonging to the task, preserve other working-tree changes, and
do not push. Never add agent attribution trailers. Instruction-only source
commits still require reviewing recorded revision drift, but do not justify
rerunning scientific examples.

The site builds from committed documentation and recorded source copies without
access to the scientific checkouts. Building the site does not execute notebooks,
run calibrations, fold observations or deploy weights.

## Where to update the central docs

The eight approved source repositories carry `AGENTS.md` pointers to this
policy. Existing `CLAUDE.md` instructions also point here on this host; some
repositories ignore that file, so the tracked `AGENTS.md` carries the requirement
for fresh checkouts. Third-party repositories are outside this rollout.

| Changed repository | Review these pages |
| --- | --- |
| `casm_io` | Visibility/voltage tutorials, array shapes and I/O reference |
| `casm_vis_analysis` | Solar plots, phase, imaging and analysis reference |
| `casm_calibrator` | Calibration walkthrough, rank-1 and calibrator reference |
| `bf_weights_generator` | Calibration walkthrough, deployment and weights notes |
| `casm-bf-imaging` | Sky imaging tutorial and imaging notes |
| `casm_t2` | T2/T3 guide, injection recovery and event-storage paths |
| `casm_t3` | T2/T3 guide, event plots, labels and saved products |
| `casm_monitor` | `guides/monitoring.md`, solar prepared-array guidance, injection evidence and artifact links |

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
For the solar figure, run `python scripts/prepare_web_figures.py` after rendering
the PNG to refresh the lightweight WebP preview. This optional command uses
Pillow from the analysis environment; a normal site build needs neither Pillow
nor the source observation.
