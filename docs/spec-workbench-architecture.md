# Architecture

Airlock MCP is intentionally small:

- Codex is the conversational interface.
- The repo is the durable workspace.
- The CLI is deterministic local tooling.
- Airlock stored procedures remain the authority for live validation and
  mutation.

## Module Boundaries

- `cli.py`: argument parsing and command dispatch only.
- `art.py`: small terminal identity and about text.
- `bootstrap.py`: specs-repo bootstrap files, including `AGENTS.md` and the
  repo-scoped Codex skill.
- `manage.py`: workspace discovery, archive, restore, rename, and next-action
  helpers.
- `project.py`: checkout discovery and environment override handling.
- `patterns.py`: pattern manifest loading.
- `workspace.py`: create, import, and clone workspace file operations.
- `specs.py`: spec-config extraction, identity retitling, and sample-record
  generation.
- `records.py`: deterministic records JSON to CSV rendering.
- `summary.py`: compact workspace recap for session re-entry.
- `updater.py`: self-update planning and execution.
- `validation.py`: local workspace and records checks.
- `sql.py`: validate-only SQL rendering.
- `jsonio.py`: JSON/text file helpers.

Keep product data in `patterns/`, workspace templates in `workspaces/_template/`,
and Airlock-specific validation rules in `validation.py`. Do not put another
copy of a pattern into Python code.

## Source-Of-Truth Rules

`patterns/manifest.json` lists CLI-visible starter patterns. Each listed
pattern directory must include:

- `README.md`
- `spec.config.json`
- `sample.records.json`

The CLI reads those files directly. That makes pattern edits reviewable as data
changes instead of code changes.

## Create, Import, Clone

The old Airlock Streamlit editor used mode-specific hydration:

- create: start from defaults
- edit: hydrate canonical config and preserve unmodeled sections
- clone: hydrate source config, but blank/reset identity fields

Airlock MCP maps that to files:

- `init-repo`: prepare a separate specs repo for Codex and Airlock MCP
- `init`: create from a pattern
- `import-spec`: edit/import an existing canonical or spec-library config in a
  new workspace
- `clone`: copy a workspace, reset `core_config.spec_name` and
  `core_config.spec_alias`, and regenerate sample records
- `rename`: move a workspace and, by default, retitle its spec identity
- `archive` and `restore`: move drafts in and out of `_archive`
- `list-workspaces`: show active drafts, with archived drafts available via
  `--all`

This repo does not try to be the installed Airlock editor. It gives Codex and
humans a careful drafting surface before Airlock receives the final config.

## Update Boundary

`self-update` supports two intentionally simple paths:

- checkout mode: `git pull --ff-only`
- installed package mode: `pip install --upgrade <source>`

The command prints the selected plan first, supports `--dry-run`, and refuses a
git checkout with uncommitted changes unless `--force` is passed. Keep update
logic in `updater.py`; do not hide network or package-manager side effects in
other commands.

## Validation Boundary

Local checks catch:

- missing workspace files
- invalid JSON
- missing core fields
- duplicate columns
- unsupported column types
- missing date/datetime strftime formats
- `variant_shape` rules pointing at non-variant columns
- variant columns with no `variant_shape` rule
- shared guest-role access levels without matching enabled public subfolders
- sample records with undeclared or missing required fields
- payload fields that look like Airlock workflow/reviewer state

Local checks do not prove that installed Airlock will accept a spec. Always use
installed Airlock validation before mutation.

## Records Boundary

`sample.records.json` is the authoring shape. It supports nested JSON for
variant fields and is easy for Codex to patch over multiple sessions.

`export-csv` is the handoff adapter. It writes fields in `column_config` order,
ignores undeclared extras after validation has reported them, and serializes
objects or arrays as compact JSON strings. Keep other record-format adapters in
`records.py` so the CLI stays thin.

## Install Boundary

The public install surface is expected to be Airlock MCP shaped:

```bash
npx @reunionstudio/airlock-mcp install
```

The connector implementation belongs in `reunionstudio/airlock-mcp`. Airlock
MCP is the single installed interface for agents working with Airlock: building
specs, using specs to pull and push governed data, and capturing improvements
from real use cases. This workbench owns the spec-building implementation:
patterns, bootstrap, workspace files, local checks, and the Codex skill.

That command is the agent connector/setup entry point, not the user's spec
workspace. After installing or registering the connector, the user still creates
or opens a separate Git-backed `<project>-specs` repo in a user-chosen location
and works there with Codex. GitHub is the recommended default when available.
Users should ask for Airlock, not install a separate spec-building tool.

For Codex, the install command should use the platform MCP manager rather than
editing config files directly:

```bash
codex mcp add airlock -- npx -y @reunionstudio/airlock-mcp server
```

The npm package is an installer and launcher. The production MCP server can be
Rust when Airlock MCP grows beyond bootstrap guidance. If implemented with
stdio, stdout must remain protocol-only and all logging must go to stderr.

The current dogfood/development path can install Airlock MCP into the specs
repo before the MCP package is published, then run:

```bash
airlock-mcp init-repo
```

That command writes the Codex-facing repo instructions and skill into the specs
repo. Keep those bootstrap assets as files, not generated prose hidden in the
CLI, so product guidance remains reviewable.

The normal development path for Airlock MCP itself is from a checkout:

```bash
python3 -m pip install -e .
```

The CLI discovers the checkout by walking upward for `patterns/manifest.json`.
Set `AIRLOCK_MCP_HOME=/path/to/airlock-mcp` if the command is launched from
another working directory.
