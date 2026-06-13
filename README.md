# Airlock MCP

Airlock MCP is the single installed interface for AI agents working with
Airlock.

It covers the full Airlock loop:

- build specs with the bundled spec-building workbench
- use specs to pull and push governed data with the Airlock Star capability
- validate, create, and revise specs against installed Airlock
- capture real use cases and improvements so specs get better over time

Spec building is not a second thing users install. It is bundled inside
Airlock MCP.

Airlock Star is not a second thing users install either. It is the capability
inside Airlock MCP for working through real Airlock use cases,
pulling and pushing data through specs, reading outputs, and turning experience
back into better specs.

## Install

Dogfood directly from GitHub:

```bash
npx -y github:reunionstudio/airlock-mcp install --package github:reunionstudio/airlock-mcp
```

After the npm package is published, use:

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

The server exposes bootstrap guidance for starting a specs repo and entering
the bundled spec-building workbench or the Airlock Star use-and-improve
capability.

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
- `airlock_init_repo`: bootstrap a blank specs repo.
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
3. Create a blank project repo named for the org or project, such as
   `home-specs`.
4. Ask Codex to use Airlock MCP to help build specs and use specs with
   Airlock Star.
5. Let Airlock MCP bootstrap the project, welcome the user, and offer the next
   useful path before creating the first workspace.

The first workspace should not be created automatically. The spec-building
workbench should offer OODA brainstorming, a known-process draft, or a shared
`posts` feedback loop.
