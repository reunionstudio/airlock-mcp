# Airlock MCP

Airlock MCP is the single installed interface for AI agents working with
Airlock.

It covers the full Airlock loop:

- design specs with the bundled spec-building workbench
- map the process a person wants to improve into observe, orient, decide, and act
- use specs for governed data movement, decisions, actions, and feedback loops
- validate, create, and revise specs against installed Airlock

Spec building is not a second thing users install. It is bundled inside
Airlock MCP.

Airlock MCP gives agents two kinds of Airlock expertise:

1. Spec design: draft, check, revise, import, clone, and prepare specs for
   installed Airlock validation.
2. Airlock operating patterns: use specs to organize observations, orientation,
   governed decisions, controlled actions, separation of duties, and feedback
   loops.

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
workbench when a first spec is ready to draft.

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
- `airlock_list_patterns` and `airlock_show_pattern`: inspect starter patterns.
- `airlock_init_workspace`: create a workspace from `blank` or `posts`.
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
6. Let Airlock MCP bootstrap the project, ask what process the user wants to
   improve, and propose a small first spec plus a plan for more.

The first workspace should not be created automatically. The spec-building
workbench should first ask for the messy process, identify where information
comes in and actions go out, then choose a small observation, orient, decision,
or action spec.

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
