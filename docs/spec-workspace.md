# Spec Workspace Files

Every draft workspace should preserve context for future Codex sessions.

- `brief.md`: business goal, users, systems, and first useful outcome.
- `decisions.md`: row grain, evidence, access, workflow, references, and OODA
  decisions.
- `questions.md`: unresolved questions that materially affect the model.
- `spec.config.json`: draft full Airlock admin spec config.
- `sample.records.json`: example records in agent-friendly records JSON.
- `review.md`: local review notes, Airlock validation results, and next steps.

The workspace is intentionally plain files. Diffs are the design history.

Use `airlock-mcp summary <workspace>` to re-enter a draft. Use
`airlock-mcp next <workspace>` to choose the next conservative action. Use
`airlock-mcp export-csv <workspace>` to render `sample.records.json` in the
CSV shape Airlock loading paths commonly expect. Do not treat the CSV as the
source of truth; edit the JSON and regenerate it.

Use `airlock-mcp rename`, `archive`, and `restore` to organize draft folders.
`rename` retitles spec identity by default; pass `--keep-spec-identity` for a
pure folder move.

`review.md` should identify the workspace source mode:

- `create`: started from an Airlock MCP pattern
- `import`: hydrated from an existing spec JSON shape such as `specConfig` or
  exported `SPEC_CONFIG`
- `clone`: copied from another workspace with spec identity reset

For clone and import flows, preserve the source path/name so future sessions can
tell whether changes are deliberate adaptations or accidental drift.
