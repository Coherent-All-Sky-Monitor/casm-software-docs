# Documentation contributor instructions

Read `/home/casm/software/dev/CLAUDE.md` and the canonical wiki's README and
CLAUDE.md before project work. Read every applicable CLAUDE.md / AGENTS.md in
each source repository before documenting it. Those files remain canonical;
do not maintain divergent copies here.

- Default Python environment: `/home/casm/software/dev/casm_venvs/casm_offline_env`.
- Source repositories are read-only. Write documentation and tooling here only;
  maintain the canonical wiki as separately required by its instructions.
- Approved initial sources: casm_io, casm_vis_analysis, casm_calibrator.
  Do not add repositories based solely on a shared organization name.
- Document the current recorded source snapshot onward. Historical-version
  backfills are not required. Pin revisions and hash inspected files; make
  dirty-tree differences explicit. Refresh only as a deliberate reviewed step.
- Source instructions may contain stale scientific/API claims. Follow their
  work rules, compare factual claims to code and dated evidence, and document
  discrepancies without silently changing upstream files.
- Use existing scientific modules; never create another science implementation
  in the documentation repository. Do not run hardware/observing commands to
  test examples. Mark illustrative examples and verification boundaries.
- Build Sphinx with warnings as errors, run the local link checker, and check
  the browser presentation after layout changes. No scientific-validity claim
  follows merely from a successful docs build.
- Plain local commits as the configured user. No attribution trailers, no
  agent co-authorship, and no pushes without explicit user instruction.
- Write like an experienced scientific software developer: concise prose,
  concrete examples, precise contracts and useful limitations. Avoid filler,
  decorative emoji, repetitive caveats, formulaic conditionals, and marketing
  language. Explain decisions once, where they matter.
- Tutorials are for scientists new to these modules: one task, short code,
  a real figure, and a few sentences on what to notice. Use familiar titles.
  Put hashes, revision audits and extended implementation caveats in developer
  notes linked from the tutorial. Keep action-critical warnings at the action.
  Cyg A calibration validation uses a stationary-beam transit curve; sky imaging
  is a separate tutorial. Preserve scientific captions in Markdown exports too.
- Visual style: conventional technical documentation, restrained typography,
  neutral surfaces and blue links. No promotional cards, numbered feature tiles,
  slogans, decorative hero sections or purple UI/code accents. Scientific figure
  palettes remain tied to the plotted quantity, not the site's theme.
