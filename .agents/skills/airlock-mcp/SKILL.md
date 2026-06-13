---
name: airlock-mcp
description: Design, draft, review, and iterate Airlock specs in the Airlock MCP spec-building workbench. Use when Codex is helping a person choose a small starting spec, work through row grain and OODA-loop decisions, import reusable patterns such as posts or guest access setups, validate local draft files, or prepare an Airlock spec config before installed Airlock validation.
---

# Airlock MCP Spec Builder

Use this skill to help a human develop Airlock specs over multiple sessions.
The repo is the workbench; Codex is the conversational interface; the CLI is
the deterministic checker.

## Default Path

1. Read the target workspace files if they exist:
   `brief.md`, `decisions.md`, `questions.md`, `spec.config.json`,
   `sample.records.json`, and `review.md`.
2. If the current repo is not yet an Airlock MCP specs repo, run or suggest:
   `airlock-mcp init-repo`.
   When helping create that repo from scratch, ask for the project or
   organization name and suggest `<slug>-specs`; for example, `Home` becomes
   `home-specs`. Reserve `airlock-specs` for the canonical reusable spec
   library.
   Public users should normally arrive through the single Airlock MCP install,
   then ask Airlock to help build and use specs. Treat spec-building as a
   capability inside that experience, not a second install.
   If the user is in a blank specs project and provides the public Airlock MCP
   GitHub URL, fetch or install Airlock MCP from that URL, run
   `airlock-mcp init-repo` in the current project, then orient before creating
   any workspace.
   If the user opened the public `airlock-mcp` workbench repo as the entry
   point, help them create a separate `<slug>-specs` project repo beside it.
3. If no workspace exists, welcome the user and offer three starting paths
   before creating files:
   - brainstorm possible specs using the OODA loop
   - start from a known process and create a blank workspace
   - create a `posts` feedback loop where humans and agents can submit
     requests, observations, and responses
4. Create `posts` only when the user chooses a feedback loop, asks for humans
   and agents to provide feedback, or explicitly requests the posts pattern.
   If the user is unsure, offer OODA brainstorming first.
5. Use `airlock-mcp import-spec <json-file> <name>` when starting from a
   spec-library file, an exported `SPEC_CONFIG`, or an existing canonical config.
6. Use `airlock-mcp clone <source-workspace> <name>` when creating a related
   draft from an existing workspace. Treat clone like the old Streamlit UI:
   preserve the shape but deliberately reset spec identity.
7. Keep the draft small. Prefer one useful governed output over a large
   speculative system.
8. On later sessions, run `airlock-mcp list-workspaces` when the target draft
   is not obvious.
9. Run `airlock-mcp summary <workspace>` and
   `airlock-mcp next <workspace>` before editing so
   the current shape, sample count, access model, and local check status are
   visible.
10. Run `airlock-mcp check <workspace>` after changing draft config or sample
   records.
11. Keep `sample.records.json` as the agent-friendly authoring shape. Use
   `airlock-mcp export-csv <workspace>` when the same examples need to be
   reviewed or loaded through Airlock's CSV path.
12. Use `airlock-mcp rename`, `archive`, and `restore` when organizing
   workspaces so spec identity changes remain deliberate.
13. Use `airlock-mcp render-sql <workspace>` only as a validate-only review
   artifact. Installed Airlock validation remains authoritative.

## Spec Design Questions

Resolve these in order, and write the answers into `decisions.md`:

1. What is one row about?
2. What systems, users, files, events, or reference data must be observed before
   a decision can be made?
3. What decision will the spec support?
4. What action follows that decision?
5. Must the action be human-done, agent-assisted, or automated?
6. What durable identifiers survive retries and reloads?
7. What business event timestamps differ from Airlock load time?
8. What evidence belongs as Airlock attachments?
9. Which facts must be typed columns because people will filter, join, audit,
   aggregate, or report on them?
10. Which optional context can live in a validated `variant` field?
11. Who submits, reviews, reads, delegates, and owns the process?

## OODA Loop

Use the observe-orient-decide-act loop as the product frame:

- Observe: source systems, human signals, files, screenshots, exports, APIs,
  reference specs, and prior Airlock outputs.
- Orient: row grain, field types, access model, evidence, workflow, references,
  expectations, and risk.
- Decide: the smallest governed output worth creating now.
- Act: validate locally, create in Airlock, collect real records, then extend or
  add the next spec based on feedback.

## Pattern Guidance

Read only the relevant pattern files:

- `patterns/starter-posts/` when the user needs a first feedback loop.
- `patterns/guest-access/` when isolation or sharing is the hard part.
- `patterns/spec-types/` when choosing observation, commitment,
  reconciliation, or reference/master-data shape.
- `docs/workflows.md` when the user asks how create, import, clone, check, or
  render-SQL fit together.
- `docs/architecture.md` when changing the CLI architecture.

When adapting a pattern, report the source pattern, what changed, and which
human decisions remain.

## Airlock Boundaries

- Local checks are not Airlock authority.
- Installed Airlock procedures remain the execution contract.
- Do not write directly to Airlock-owned tables, stages, generated views, or
  generated tables.
- Do not put Airlock workflow state, reviewer comments, approval status, or
  pushback notes into submitted payload columns unless they are true upstream
  facts from another system.
- Use attachments for screenshots, receipts, PDFs, exports, and other evidence
  files. Store only evidence metadata in payload fields.
- Airlock MCP is the single installed interface for agents. This workbench helps
  build specs; installed Airlock remains the authority for validating, creating,
  loading, reading, and push/pull workflows through specs.
