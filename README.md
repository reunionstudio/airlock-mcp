# Airlock MCP

Airlock MCP is the single installed interface for AI agents working with
Airlock.

It covers the full Airlock loop:

- design specs with the bundled spec-building workbench
- map the process a person wants to improve into observe, orient, decide, and act
- use specs for governed data movement, decisions, actions, and feedback loops
- build apps and workflows that read from and submit through existing specs
- validate, create, and revise specs against installed Airlock

Spec building and spec-using app guidance are not second things users install.
They are bundled inside Airlock MCP.

Airlock MCP gives agents four kinds of Airlock help:

1. Spec design: draft, check, revise, import, clone, and prepare specs for
   installed Airlock validation.
2. Airlock operating patterns: use specs to organize observations, orientation,
   governed decisions, controlled actions, separation of duties, and feedback
   loops.
3. App and workflow implementation: build dashboards, queues, decision UIs,
   analyses, and agent workflows that use existing specs through Airlock
   contracts.
4. Governance observation: use installed Airlock's read-only `observe.*`
   procedures to inspect setup, access, activity, billing events, health,
   context packets, and governance maps before deciding what an app or agent
   should do.

## Installed Airlock Contract

Current Airlock separates procedure intent:

- `airlock.observe.*` is the read-only governance observation surface. It is
  available to `app_admin` and `app_observer` and is the preferred path for
  discovery, health checks, access explanation, governance maps, activity,
  billing event context, and list/detail context packets.
- `airlock.admin.*` is for admin changes and operational actions such as
  creating specs, changing roles, loading OKF bundles, rerunning setup, or
  deleting purge candidates.
- `airlock.agent.*` is for governed agent work such as listing my
  specs, validating/loading data, workflow actions, attachments, delegations,
  and references.

When building an app or workflow, prefer `observe.*` for read-only setup and
monitoring questions, `agent.*` for governed submissions in the actor's scope,
and `admin.*` only for intentional administrative mutation. Do not use retired
admin read wrappers such as `admin.list_specs`, `admin.describe_role`, or
`admin.list_events`; use the matching observe procedures instead.

## Install

Dogfood directly from GitHub:

```bash
npx -y github:reunionstudio/airlock-mcp install --package github:reunionstudio/airlock-mcp
```

Install from npm:

```bash
npx @reunionstudio/airlock-mcp install
```

Today this package is a small installer and MCP launcher. For Codex, install
registers a local stdio server with:

```bash
codex mcp add airlock -- npx -y @reunionstudio/airlock-mcp server
```

The GitHub dogfood command registers:

```bash
codex mcp add airlock -- npx -y github:reunionstudio/airlock-mcp server
```

The server exposes bootstrap guidance for starting a specs repo, coaching a
person through process discovery, and entering the bundled spec-building
workbench when a first spec is ready to draft. It also guides agents building
apps or workflows that use specs the user already has access to.

Workspace summaries are structured spec cards. They present the current spec
core, file rules, attachment policy, guest access, column rules, sample record
shape, note-file status, and local check status so Codex can reflect the draft
back to the user before asking for decisions.

This install shape uses Node because `npx` runs npm package binaries. MCP itself
does not require Node. Once Airlock MCP does real operational work, such as
validating specs, loading records, handling attachments, reading outputs, and
coordinating push/pull workflows, the production server should likely be Rust
with `rmcp`: single binary, predictable memory and latency, typed tool
contracts, and no Node/Python runtime for the long-running process. The npm
package can remain the friendly installer.

For stdio MCP, stdout is protocol-only. Logs and diagnostics must go to stderr.

## Test

```bash
npm test
node -c bin/airlock-mcp.mjs
python3 -m json.tool package.json
PYTHONPATH=src python3 -m unittest discover
PYTHONPATH=src python3 -m airlock_mcp doctor
```

The smoke test verifies install dry-run output and the stdio MCP handshake for
`initialize`, `tools/list`, `prompts/list`, `resources/list`, prompt reads,
tool calls, resource reads, unknown methods, malformed input, and install
argument validation. It also exercises the bundled Python workbench through MCP
tool calls against a temporary specs repo.

## MCP Tools

The server exposes orientation plus local spec-building tools:

- `airlock_start`: return setup guidance for a project.
- `airlock_doctor`: verify bundled workbench assets.
- `airlock_init_repo`: bootstrap a Git-backed specs repo.
- `airlock_init_app_context`: seed an app repo with spec snapshots, sample
  records, generated helper folders, and an app manifest.
- `airlock_list_patterns` and `airlock_show_pattern`: inspect starter patterns.
- `airlock_init_workspace`: create a workspace from `blank`, `posts`, or
  `okf-knowledge-bundle`.
- `airlock_list_workspaces`: inspect active or archived drafts.
- `airlock_check_workspace`, `airlock_summary`, and `airlock_next`: validate and re-enter a draft.
- `airlock_export_csv`: render `sample.records.json` as Airlock-ready CSV.
- `airlock_render_sql`: render validate-only Airlock admin SQL.

Workbench tools default to the MCP server working directory and accept an
optional `cwd` when an agent needs to target a specific specs repo. They launch
the bundled Python workbench by argv array, not through a shell. Python 3 is
required for those workbench tools; `airlock_start`, prompts, resources, and
installer behavior remain pure Node.

## Repo Layout

- `bin/airlock-mcp.mjs`: executable entry point.
- `src/cli.mjs`: argument parsing and command dispatch.
- `src/install.mjs`: Codex MCP registration.
- `src/mcp.mjs`: JSON-RPC handlers and stdio loop.
- `src/text.mjs`: prompts and user-facing guidance.
- `src/airlock_mcp/`: Python spec-building workbench and local checker.
- `.agents/skills/airlock-mcp/`: repo-scoped Codex skill for spec drafting.
- `patterns/`: reusable spec and access patterns.
- `workspaces/`: spec workspace template files.
- `schemas/`: documented draft shapes.
- `docs/architecture.md`: architecture and runtime boundaries.
- `SECURITY.md`: security rules for current and future tools.

The intended user flow is:

1. Run `npx @reunionstudio/airlock-mcp install` once for the agent environment.
2. Open Codex.
3. Create or open a Git-backed specs repo named for the org or project, such as
   `home-specs`. GitHub is the recommended default when available.
4. If Codex is creating the repo, choose where the `home-specs` directory should
   live before files are written.
5. Ask Codex to use Airlock MCP to help improve a process with Airlock specs.
6. Choose a delivery mode: spec-first, app-first from existing specs, or
   co-development of specs and app together.
7. Let Airlock MCP bootstrap the project, ask what process the user wants to
   improve when specs are involved, and propose a small first spec plus a plan
   for more.

The first workspace should not be created automatically. Airlock MCP should
first ask whether the user wants spec-first, app-first from existing specs, or
co-development of specs and app together. For spec-building work, it should ask
for the messy process, identify where information comes in and actions go out,
then choose a small observation, orient, decision, or action spec.

For app-building work, Airlock MCP should identify the app goal, read specs,
write specs, orienting views, decision capture, and approved Airlock/Snowflake
access paths. The app should submit decisions, approvals, actions, comments, or
follow-ups through Airlock spec contracts. It should not write directly to
Airlock-owned tables or bypass spec workflow.

When an app repo needs local Airlock context, use:

```bash
airlock-mcp init-app-context . --mode app-first --spec ../home-specs/workspaces/expenses
```

That creates:

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

The snapshots are for coding, tests, and UI planning. They are not canonical.
Canonical specs live in the specs repo or installed Airlock. In
co-development, keep a visible spec track and app track so changes to row
grain, access, workflow, screens, reads, and governed writes stay aligned.

When the user already has artifacts, Airlock MCP should ask for them early:
CSV or Excel files, JSON samples, API docs, schemas, forms, screenshots, PDFs,
exports, message examples, or other defined content people already use. These
are design artifacts for drafting the spec; later Airlock attachments are
evidence files submitted with governed records.

Airlock MCP can also consult the reusable `airlock-specs` library for starting
points, patterns, and ideas. Those library specs are not guaranteed to reflect
the current shape of any third-party system. Current API docs, real exports,
samples, schemas, and user-provided artifacts should override library shapes
when they conflict.

For app-first work against installed Airlock, start with `observe.procedures`,
`observe.specs`, `observe.spec`, `observe.governance_map`,
`observe.explain_access`, `observe.health`, and the relevant context packet
before designing direct SQL helpers. These payloads are intended to be useful
to agents as well as humans.

Restricted references are one-record interaction contracts. When
`observe.reference_context`, `observe.spec_config`, or `agent.describe_spec`
shows `restricted_reference` or `reference_config.restricted_reference`, agents
must not call broad
`agent.select_reference_data` for that object path and must not enumerate values
or build a populated picker from the protected reference. The agent should get
the lookup value from the user's case/work context, then call
`agent.get_reference_record` with the configured `object_key`, lookup value,
purpose, and role lens. The procedure applies configured reference row filters,
checks active `action_limit` Expectations before returning a record, always
records the safe `REFERENCE_READ` event used for budgeting, and returns at most
one `RECORD`. Branch on codes such as `OK`, `NOT_FOUND`,
`NON_UNIQUE_LOOKUP_KEY`, `PURPOSE_REQUIRED`, `USAGE_LIMIT_BLOCKED`, and
`REFERENCE_READ_EVENT_FAILED`, and report `USAGE_CONTEXT` fields such as
`action_limit_used` and `action_time_period`. Auditors and planning agents can
inspect `observe.usage_limits`, `observe.usage_limit`, and
`observe.explain_access(action => 'get_reference_record', object_key => ...)`
without reading raw reference rows.

For governed Markdown knowledge, use the `okf-knowledge-bundle` pattern. It
sets `core_config.payload_adapter` to `okf_knowledge_bundle` so installed
Airlock can load locally validated bundles through
`airlock.admin.load_okf_bundle(...)`, sync parsed metadata through
`airlock.admin.sync_okf_bundle_metadata(...)`, and expose accepted concept
metadata from `AIRLOCK_DATA.ACTIVE.V_OKF_CONCEPT_METADATA`. Draft and rejected
bundles are not authoritative agent context.
