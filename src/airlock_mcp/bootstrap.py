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
and discovering improvements from real use cases. This project repo remains
the durable memory for the specs being drafted.

## Repo Naming

When helping create a new specs repo, ask for the project or organization name
and suggest `<slug>-specs`: lowercase the name, replace spaces with hyphens,
and append `-specs`. For example, `Home` becomes `home-specs`.

Reserve `airlock-specs` for the canonical reusable Airlock spec library. A
team, customer, domain, or project should use its own scoped repo name such as
`home-specs`, `acme-finance-specs`, or `customer-onboarding-specs`.

Airlock itself does not create this repo. Codex can create it locally while
helping the user start an Airlock MCP project, then Airlock receives the
finished spec later. Start in Codex, not Snowflake Cortex. Snow CLI or Cortex
only matters later when validating, creating, or operating specs against an
installed Airlock app.

## Starting A Spec Project

After bootstrap, welcome the user and orient before creating a workspace. Ask
whether they want to:

- brainstorm possible specs with the OODA loop
- start from a known process they already have in mind
- create a shared `posts` feedback loop for humans and agents to submit
  requests, observations, and responses

Create `posts` only when the user chooses a feedback loop or explicitly asks
for the posts pattern.

## Working Style

- Use the repo-scoped `$airlock-mcp` skill for spec drafting, review, and
  pattern selection.
- Keep drafts small and concrete. Prefer one useful governed output over a
  large speculative process map.
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
            "2. Ask: Use Airlock to help me build and use specs.",
            "3. Choose OODA brainstorming, a known process, or a posts feedback loop.",
        ]
    )
    return "\n".join(lines)
