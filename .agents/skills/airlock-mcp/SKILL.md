---
name: airlock-mcp
description: Design, draft, review, and iterate Airlock specs in the Airlock MCP spec-building workbench, or help build apps and workflows that use existing Airlock specs safely. Use when Codex is helping a person choose a small starting spec, work through row grain and OODA-loop decisions, import reusable patterns such as posts or guest access setups, validate local draft files, prepare an Airlock spec config before installed Airlock validation, or code an app that reads from and submits through existing specs.
---

# Airlock MCP

Use this skill to help a human develop Airlock specs over multiple sessions.
Also use it when a human wants to build an app or workflow that uses existing
Airlock specs. The specs repo is the durable workbench for spec drafts; an app
repo is the right place for code that reads, orients, decides, and submits
through existing specs. Codex is the conversational interface; the CLI is the
deterministic checker for local spec drafts.

## Default Path

1. Read the target workspace files if they exist:
   `brief.md`, `decisions.md`, `questions.md`, `spec.config.json`,
   `sample.records.json`, and `review.md`.
2. If the current repo is not yet an Airlock MCP specs repo, run or suggest:
   `airlock-mcp init-repo`.
   Exception: if the user asks to build an app, dashboard, approval queue,
   decision UI, agent workflow, or other code that uses existing specs, do not
   bootstrap a specs repo just because the current repo lacks `workspaces/`.
   Treat the current repo as an app repo unless the user asks to create specs.
   Ask for the development mode, available specs, app goal, and read/write
   contract instead. Use `airlock-mcp init-app-context` when the app repo needs
   an `airlock/` folder with spec snapshots and an app manifest.
   When helping create that repo from scratch, ask for the project or
   organization name and suggest `<slug>-specs`; for example, `Home` becomes
   `home-specs`. Reserve `airlock-specs` for the canonical reusable spec
   library.
   Recommend storing the specs project in a real version-controlled repo,
   preferably a GitHub repo when the user already uses GitHub. Before creating
   the directory, ask where the user wants the `<slug>-specs` repo to live. If
   Codex can create the repo, offer to initialize git and create/push a GitHub
   repo; otherwise ask the user to create the repo and open it in Codex before
   running `airlock-mcp init-repo`.
   Public users should normally arrive through the single Airlock MCP install,
   then ask Airlock to help build and use specs. Treat spec-building as a
   capability inside that experience, not a second install.
   If the user is in a blank specs project and provides the public Airlock MCP
   GitHub URL, fetch or install Airlock MCP from that URL, run
   `airlock-mcp init-repo` in the current project, then orient before creating
   any workspace.
   If the user opened the public `airlock-mcp` workbench repo as the entry
   point, help them create a separate `<slug>-specs` project repo beside it.
3. If no workspace exists, welcome the user and ask which mode they want:
   spec-first, app-first from existing specs, or co-development.
   For spec-first or co-development, ask:
   `What process do you want to improve?`
   Explain that Airlock works best when we can identify the loop around that
   process:
   - what information comes in
   - what context helps people or agents understand it
   - what decision needs to be made
   - what action happens after the decision
   Give examples before naming the concept: apps, files, forms, people, emails,
   calls, mail, websites, APIs, data feeds, or physical events. Then call these
   places interfaces: where the process observes from or acts through.
   Ask whether the user already has artifacts for the process, such as CSV or
   Excel files, JSON samples, API docs, schemas, forms, screenshots, PDFs,
   exports, message examples, or other content people already use. A small real
   sample is often better than a long explanation. Remind the user to redact
   secrets before attaching files or pasting content.
   When relevant, look to the reusable `airlock-specs` library for starting
   points, patterns, and ideas. Do not treat those library specs as guaranteed
   descriptions of any third-party system. Prefer current API docs, real data
   exports, samples, and user-provided artifacts when they conflict with the
   library, and record the reason for the divergence.
   Ask for the messy version. Help turn it into a small first Airlock spec and
   a plan for more. Do not create the first workspace until the user chooses a
   path.
4. Create `posts` only when the user chooses a feedback loop, asks for humans
   and agents to provide feedback, or explicitly requests the posts pattern.
   If the user is unsure, continue process discovery before creating files.
5. Create `okf-knowledge-bundle` when the user needs governed Markdown
   knowledge, accepted agent context, policies, runbooks, metric definitions,
   investigations, or other business context organized as an OKF-style bundle.
   The spec must declare `core_config.payload_adapter =
   "okf_knowledge_bundle"`. Installed Airlock loads validated bundles with
   `airlock.admin.load_okf_bundle(...)`, can sync parsed metadata with
   `airlock.admin.sync_okf_bundle_metadata(...)`, and exposes authoritative
   accepted context through `AIRLOCK_DATA.ACTIVE.V_OKF_CONCEPT_METADATA`.
   Draft and rejected bundles are not authoritative agent context.
6. Use `airlock-mcp import-spec <json-file> <name>` when starting from a
   spec-library file, an exported `SPEC_CONFIG`, or an existing canonical config.
   If the source is from `airlock-specs`, treat it as a reusable draft pattern.
   Check actual API docs, CSV/Excel/JSON samples, schemas, or other artifacts
   before assuming the source fields match a live third-party system.
7. Use `airlock-mcp clone <source-workspace> <name>` when creating a related
   draft from an existing workspace. Treat clone like the old Streamlit UI:
   preserve the shape but deliberately reset spec identity.
8. Keep the draft small. Prefer one useful governed output over a large
   speculative system, then keep a plan for later specs.
9. On later sessions, run `airlock-mcp list-workspaces` when the target draft
   is not obvious.
10. Run `airlock-mcp summary <workspace>` and
   `airlock-mcp next <workspace>` before editing so
   the current shape, sample count, access model, and local check status are
   visible.
   Present the summary back to the user as a structured spec card when useful:
   core, file rules, attachments, guest access, column rules, samples, notes,
   and check status. Do not make the user infer the current spec from file
   links alone.
11. Run `airlock-mcp check <workspace>` after changing draft config or sample
   records.
12. Keep `sample.records.json` as the agent-friendly authoring shape. Use
   `airlock-mcp export-csv <workspace>` when the same examples need to be
   reviewed or loaded through Airlock's CSV path.
13. Use `airlock-mcp rename`, `archive`, and `restore` when organizing
   workspaces so spec identity changes remain deliberate.
14. Use `airlock-mcp render-sql <workspace>` only as a validate-only review
   artifact. Installed Airlock validation remains authoritative.

## Spec Design Questions

Use these as an internal checklist. Do not dump the whole list into chat.
Write resolved answers into `decisions.md` and ask the human only for missing
or risky decisions:

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

## Interfaces

Use interface to mean any place the process observes from or acts through.
Do not lead with the word before examples. Interfaces can be apps, files, forms,
people, emails, calls, mail, websites, APIs, data feeds, physical events,
shared folders, payment tools, bank apps, or other systems.

When a user names a process, map the interfaces both ways:

- Observe: where information enters the loop.
- Act: where a decision writes back to the world.

Spot gaps gently. A user may have one dataset but need additional observations
to orient well, or may rely on hard-to-automate interfaces such as phone calls
or physical mail.

## Artifacts And Libraries

Start from artifacts whenever they exist. Useful design artifacts include CSV
or Excel files, JSON samples, API docs, schemas, forms, screenshots, PDFs,
exports, message examples, and other defined content that already carries the
process shape.

Use design artifacts to infer row grain, field names, durable identifiers,
timestamps, evidence, variants, attachment needs, and edge cases. Distinguish
design artifacts from Airlock attachments: design artifacts help draft the spec;
attachments are evidence files later submitted with governed records.

Use `airlock-specs` as a source of reusable starting points, patterns, and
ideas. Do not promise that Airlock spec-library shapes reflect current
third-party APIs, exports, or business objects. If a library shape looks
outdated, overfit, underfit, or contradicted by current artifacts, override it
with the best current evidence and explain the decision in `decisions.md` or
`review.md`.

## OODA Loop

Use the observe-orient-decide-act loop as the product frame:

- Observe: controlled interface ingestion and observation/reference specs.
- Orient: context, proposals, scoring, exception queues, summaries, and gaps in
  the observation set.
- Decide: governed choices by people or agents, with identity, timestamp,
  rationale, evidence, approval, and separation of duties.
- Act: controlled writes back to interfaces, commitments, follow-ups, outputs,
  and the next observations created by those actions.

## Apps And Workflows Using Existing Specs

Use this path when the user wants to vibe-code an app, dashboard, queue,
decision UI, analysis workflow, or agent workflow that uses specs they already
have access to. This is not spec editing by default.

Use three delivery modes:

- Spec-first: design governed specs, samples, access, and validation before
  building the app surface.
- App-first: use existing specs to build an app, dashboard, queue, or workflow.
- Co-development: develop the app and specs together, keeping the contract and
  experience visible side by side.

Start by identifying:

1. The app goal: what the user needs to orient around or decide.
2. Read specs: existing specs the app reads from, such as budgets, expenses,
   requests, forecasts, observations, payouts, or reference data.
3. Write specs: existing specs the app submits to, such as decisions,
   approvals, comments, commitments, actions, or follow-ups.
4. The app surface: Streamlit, web app, CLI, notebook, scheduled agent, or
   other runtime.
5. The Airlock access path: installed Airlock procedures, approved MCP tools,
   generated read surfaces, stages, or documented SQL helpers available in the
   user's environment.
6. Identity, evidence, timestamps, approval, and separation-of-duties rules.

Use the current installed Airlock procedure grammar when the app talks to
Airlock:

- `airlock.observe.*` is read-only and is the first-class governance
  observation surface for `app_admin` and `app_observer`.
- `airlock.admin.*` performs administrative changes and operational mutations.
- `airlock.agent.*` performs governed user or agent work in the actor's scope.

For app-first work, prefer `observe.procedures`, `observe.specs`,
`observe.spec`, `observe.governance_map`, `observe.explain_access`,
`observe.health`, `observe.activity`, `observe.admin_activity`,
`observe.spec_admin_activity`, `observe.billing`, `observe.billing_events`, and
the relevant context packets before inventing
custom read paths. Do not tell agents to call retired admin read wrappers such
as `admin.list_specs`, `admin.describe_role`, `admin.get_spec`, or
`admin.list_events`; use the matching observe list/detail procedure instead.
Use `admin.*` only when the app is intentionally changing Airlock setup or
running an admin operation.

Restricted references are one-record interaction contracts for read-only
reference specs. If `agent.describe_spec`, `observe.spec`,
`observe.spec_config`, or `observe.reference_context` shows
`restricted_reference` or `reference_config.restricted_reference`, do not
enumerate the protected reference, build a populated picker, or use broad
`agent.select_reference_data` for that object path. Get the lookup value from
the user's case/work context, then call `agent.get_reference_record` with the
configured `object_key`, lookup value, purpose, and role lens. The procedure
returns at most one `RECORD`, applies reference row filters, checks active
`action_limit` Expectations before returning data, and records the safe
`REFERENCE_READ` event used for usage budgeting. Branch on stable codes such
as `OK`, `NOT_FOUND`, `NON_UNIQUE_LOOKUP_KEY`, `PURPOSE_REQUIRED`,
`USAGE_LIMIT_BLOCKED`, and `REFERENCE_READ_EVENT_FAILED`; expose
`USAGE_CONTEXT` fields such as `action_limit_used` and `action_time_period`.
For read-only planning and audit, use `observe.reference_context`,
`observe.usage_limits`, `observe.usage_limit`, and
`observe.explain_access(action => 'get_reference_record', object_key => ...)`
without querying raw reference rows.

Help the app follow the loop:

- Observe/read: fetch existing governed data through approved Airlock or
  Snowflake surfaces.
- Orient: summarize, compare, rank, flag exceptions, propose options, or build
  dashboards and queues.
- Decide: capture human or agent choices with rationale and evidence.
- Act/write: submit the decision, approval, action, or follow-up through an
  Airlock spec contract.

Keep the boundary clear:

- Do not edit specs unless the user asks for spec changes.
- Do not write directly to Airlock-owned tables, stages, generated views, or
  generated tables.
- Do not treat Snowflake as an unrestricted database just because the app can
  connect to it.
- Prefer existing Airlock contracts for reads and writes. If no suitable write
  spec exists, explain the gap and propose a small decision/action spec as a
  separate spec-design step.
- Keep secrets and credentials out of repo files. Use the app's existing secret
  management pattern.

### App Context Seeding

Use `airlock-mcp init-app-context` in an app repo when the app needs local
Airlock context. The command creates:

```text
airlock/
  AGENTS.md
  README.md
  specs.manifest.json
  spec-snapshots/
  sample-records/
  generated/
    types/
    sql/
```

The manifest and snapshots help the app develop against stable local references.
They are not canonical. Canonical specs live in the specs repo or installed
Airlock. When seeding from draft workspaces, pass `--spec <workspace>` for each
spec to copy `spec.config.json` and `sample.records.json` into the app context.

In co-development mode, keep two tracks visible:

- Spec track: row grain, columns, samples, access, validation, workflow.
- App track: screens, reads, decisions, writes, user actions, runtime.

## Pattern Guidance

Read only the relevant pattern files:

- `patterns/starter-posts/` when the user needs a first feedback loop.
- `patterns/okf-knowledge-bundle/` when the user needs governed Markdown
  business context for people or agents.
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
