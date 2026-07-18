from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .project import repo_root


AGENTS_MD = """# Airlock Spec Workspace Guidance

This repo is an Airlock MCP workspace for drafting Airlock specs with Codex.

## Product Shape

The public install surface is Airlock MCP, for example
`npx @reunionstudio/airlock-mcp install`. Airlock MCP is the single installed
interface for building specs, using specs, pulling and pushing governed data,
building apps or workflows that use existing specs, and discovering
improvements from real use cases. This project repo remains the durable memory
for the specs being drafted.

## Repo Naming

When helping create a new specs repo, ask for the project or organization name
and suggest `<slug>-specs`: lowercase the name, replace spaces with hyphens,
and append `-specs`. For example, `Home` becomes `home-specs`.

Reserve `airlock-specs` for the canonical reusable Airlock spec library. A
team, customer, domain, or project should use its own scoped repo name such as
`home-specs`, `acme-finance-specs`, or `customer-onboarding-specs`.

Specs work should live in a real version-controlled repo. Prefer GitHub when
the user already uses GitHub, but any normal Git host is acceptable. Before
creating a new `<slug>-specs` directory, ask where it should live. If Codex can
create the repo, offer to initialize git and create or push the GitHub repo. If
not, ask the user to create the repo and open it in Codex before bootstrapping
Airlock MCP files.

Airlock itself does not create this repo. Codex can create it locally while
helping the user start an Airlock MCP project, then Airlock receives the
finished spec later. Start in Codex, not Snowflake Cortex. Snow CLI or Cortex
only matters later when validating, creating, or operating specs against an
installed Airlock app.

## Starting A Spec Project

After bootstrap, welcome the user and orient before creating a workspace. Start
by asking which delivery mode they want:

1. Spec-first: design governed specs before building the app surface.
2. App-first: build from existing specs.
3. Co-development: develop the app and specs together.

For spec-first or co-development work, ask:

What process do you want to improve?

Explain that Airlock works best when we can identify the loop around that
process:

1. what information comes in
2. what context helps people or agents understand it
3. what decision needs to be made
4. what action happens after the decision

Information may come from apps, files, forms, people, emails, calls, mail,
websites, APIs, data feeds, or physical events. Actions may go back through
those same places. After giving examples, call these places interfaces: where
the process observes from or acts through.

Ask whether the user already has artifacts for the process: CSV or Excel files,
JSON samples, API docs, schemas, forms, screenshots, PDFs, exports, message
examples, or other defined content people already use. A small real sample is
often better than a long explanation. Remind the user to redact secrets before
attaching files or pasting content.

Use `airlock-specs` as a reusable library of starting points, patterns, and
ideas when it is available. Do not assume library specs match the current shape
of a third-party API, export, or business object. Prefer current API docs, real
data exports, samples, and user-provided artifacts when they conflict with the
library, and record the reason for the divergence.

Ask for the messy version. Help turn it into a small first Airlock spec and a
plan for more. Do not create the first workspace until the user chooses a path.
Create `posts` only when the user wants a shared feedback loop or explicitly
asks for the posts pattern.

## Building Apps With Existing Specs

Use this path when the user wants to build an app, dashboard, approval queue,
decision UI, analysis workflow, scheduled agent, or other code that uses specs
they already have access to. Treat this as app/workflow implementation, not
spec editing, unless the user explicitly asks to change specs.

Use `airlock-mcp init-app-context` in an app repo when the app needs local
Airlock context. It creates `airlock/specs.manifest.json`,
`airlock/spec-snapshots/`, `airlock/sample-records/`, and generated helper
folders. These files are app-local references, not canonical specs. Canonical
specs live in the specs repo or installed Airlock.

Treat Airlock's built-in Streamlit Native App as a generic operating and
fallback surface. It supports administration, inspection, evidence, workflow,
and safe manual action; it is not a universal domain application builder.
Recommend a purpose-built app when repeated, high-value work benefits from
domain-specific summaries, calculations, evidence layout, terminology, or
controls. Keep those presentation choices in app code. Do not add UI layout or
aggregation fields to a spec merely to improve the generic app.

Identify:

- the app goal and decision the app should support
- read specs such as budgets, expenses, requests, forecasts, observations,
  payouts, or reference data
- write specs such as decisions, approvals, comments, commitments, actions, or
  follow-ups
- where the app should run, such as Streamlit, web app, CLI, notebook,
  scheduled agent, or existing app framework
- the Airlock access path available in this environment
- identity, evidence, timestamp, approval, and separation-of-duties rules

Installed Airlock separates procedure intent:

- `observe.*`: read-only governance observation for discovery, health, access
  explanation, governance maps, activity, billing events, and context packets.
- `agent.*`: governed agent work in the actor's scope.
- `admin.*`: administrative mutation and operational changes.

Use `agent.list_my_work` for the actor's unified current-work inbox,
`observe.work` for account-wide current work, and `observe.activity` for
historical events. The older split workflow/expectation work calls are retired.

For active source links with `min_count > 0`, load the downstream file into
Draft, discover eligible evidence with `agent.list_eligible_source_files`, pin
exact manifest rows with `agent.add_file_reference`, and then advance workflow.
Missing, removed, or wrong-state evidence returns `SOURCE_REFERENCE_REQUIRED`
without moving the file.

For a structural spec change with active files, treat
`SPEC_MIGRATION_REQUIRED` as a governed two-version lifecycle. Create the
immutable revision and migration, validate and approve it, activate the target,
run bounded `admin.run_spec_migration` batches, inspect progress and lineage
with `observe.spec_migration`, and retire the source only after it is drained.
Use `observe.spec_migrations` to discover lifecycle work. Before activation,
`admin.cancel_spec_migration` may release an abandoned `draft`, `planned`,
`validated`, or `approved` migration; it is not rollback after activation. Use
the bounded declarative transform for mechanical changes; semantic
transforms belong in a purpose-built process that reloads through normal
Airlock validation.

For app-first work, use observe payloads such as `observe.procedures`,
`observe.specs`, `observe.spec`, `observe.governance_map`,
`observe.explain_access`, `observe.health`, `observe.activity`,
`observe.admin_activity`, `observe.spec_admin_activity`, and
`observe.billing_events` before inventing custom read paths. For `alter_spec`
activity, use `CHANGED_SECTIONS` and `CHANGED_FIELDS` to triage what changed
before fetching version snapshots. Do not call retired admin read wrappers such as `admin.list_specs`, `admin.describe_role`,
or `admin.list_events`; use the matching observe list/detail procedure.

Restricted references are one-record interaction contracts for read-only
reference specs. If `agent.describe_spec`, `observe.spec_config`, or
`observe.reference_context` shows `restricted_reference` or
`reference_config.restricted_reference`, do not enumerate the protected
reference, build a populated picker, or use broad `agent.select_reference_data`
for that object path. Get the lookup value from the user's case/work context,
then call `agent.get_reference_record` with the configured `object_key`, lookup
value, purpose, and role lens. Use `observe.usage_limits`,
`observe.usage_limit`, and
`observe.explain_access(action => 'get_reference_record', object_key => ...)`
for planning and audit without reading raw reference rows.

Attachments remain governed evidence. Agents should discover and manage them
through installed Airlock procedures, not by reading Airlock-owned stages
directly. The Streamlit Native App can preview images and text inline and can
render bounded page-at-a-time PDF previews for files up to 100 MB and 2,000
pages. PDFs larger than 12 MB require an explicit open action; the selected
page and next two pages warm a private session cache. Successful PDF page
previews emit metadata-only `ATTACHMENT_PREVIEW` activity and do not grant MCP
clients direct attachment bytes.

The app may orient the user with summaries, comparisons, rankings, exception
queues, proposals, or dashboards. It should submit governed choices back
through an Airlock spec contract. Do not write directly to Airlock-owned tables,
stages, generated views, or generated tables. Do not bypass spec workflow just
because the app can connect to Snowflake. If no suitable decision or action spec
exists, explain the gap and propose a small spec-design step.

In co-development mode, keep two tracks visible:

- Spec track: row grain, columns, samples, access, validation, workflow
- App track: screens, reads, decisions, writes, user actions, runtime

## Working Style

- Use the repo-scoped `$airlock-mcp` skill for spec drafting, review, and
  pattern selection, or for app/workflow implementation that uses existing
  Airlock specs.
- Keep drafts small and concrete. Prefer one useful governed output over a
  large speculative process map, then keep a plan for later specs.
- Preserve decisions in workspace files so future Codex sessions can resume
  without relying on chat memory.
- Use `airlock-mcp list-workspaces` before guessing which draft to resume.
- Use `airlock-mcp summary <workspace>` and `airlock-mcp next <workspace>`
  before editing an existing draft.
- Keep `sample.records.json` as the editable authoring shape, then use
  `airlock-mcp export-csv <workspace>` when Airlock-ready CSV examples are
  needed.
- Treat Airlock as the execution authority. Local checks are guardrails, not a
  replacement for installed Airlock validation.

## Spec Design Priorities

Resolve these before final JSON:

- row grain
- durable identifiers
- business event timestamps
- typed columns versus validated variants
- attachment evidence
- guest access and path isolation
- workflow and pushback
- references and expectations
- delegation and agent identity
- interfaces observed from or acted through
- existing artifacts such as CSV, Excel, JSON, API docs, schemas, exports,
  forms, screenshots, PDFs, or message examples
- whether an `airlock-specs` library pattern was used, changed, or rejected
- likely gaps in observations, orientation, decisions, or actions
- observe-orient-decide-act loop

Do not encode Airlock lifecycle state, reviewer notes, approval status, or
workflow transitions as submitted payload fields unless they are true upstream
business facts.
"""


@dataclass(frozen=True)
class BootstrapResult:
    root: Path
    created: tuple[Path, ...]
    kept: tuple[Path, ...]


def _write_text_if_needed(path: Path, text: str, *, force: bool) -> str:
    if path.exists() and not force:
        return "kept"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return "created"


def _copy_file_if_needed(source: Path, target: Path, *, force: bool) -> str:
    if target.exists() and not force:
        return "kept"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return "created"


def bootstrap_repo(target: Path, *, force: bool = False) -> BootstrapResult:
    root = target.expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise NotADirectoryError(str(root))

    created: list[Path] = []
    kept: list[Path] = []
    root.mkdir(parents=True, exist_ok=True)

    workspace_root = root / "workspaces"
    if workspace_root.exists():
        kept.append(workspace_root)
    else:
        workspace_root.mkdir()
        created.append(workspace_root)

    agents_path = root / "AGENTS.md"
    bucket = created if _write_text_if_needed(agents_path, AGENTS_MD, force=force) == "created" else kept
    bucket.append(agents_path)

    source_skill = repo_root() / ".agents" / "skills" / "airlock-mcp"
    if not source_skill.exists():
        raise FileNotFoundError(str(source_skill))

    target_skill = root / ".agents" / "skills" / "airlock-mcp"
    for source_file in sorted(path for path in source_skill.rglob("*") if path.is_file()):
        relative = source_file.relative_to(source_skill)
        target_file = target_skill / relative
        bucket = created if _copy_file_if_needed(source_file, target_file, force=force) == "created" else kept
        bucket.append(target_file)

    return BootstrapResult(root=root, created=tuple(created), kept=tuple(kept))


def format_bootstrap_result(result: BootstrapResult) -> str:
    lines = [f"initialized {result.root}"]
    for path in result.created:
        lines.append(f"created {path.relative_to(result.root)}")
    for path in result.kept:
        lines.append(f"kept {path.relative_to(result.root)}")
    lines.extend(
        [
            "",
            "next:",
            "1. Open this repo in Codex.",
            "2. Keep this specs project in git; GitHub is recommended when available.",
            "3. Ask: Use Airlock to help me build and use specs.",
            "4. Start with: What process do you want to improve?",
        ]
    )
    return "\n".join(lines)
