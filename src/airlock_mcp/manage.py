from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jsonio import read_json, write_json
from .specs import retitle_spec, spec_name
from .summary import workspace_summary
from .validation import check_workspace


ARCHIVE_DIRNAME = "_archive"
WORKSPACE_MARKERS = ("spec.config.json", "sample.records.json")
DECISION_PROMPTS = (
    "One row is:",
    "- Observe:",
    "- Orient:",
    "- Decide:",
    "- Act:",
    "Stable ids and retry-safe keys:",
    "Event, observed, captured, effective, or transaction timestamps:",
    "Fields people will filter, join, audit, aggregate, or report on:",
    "Optional context that may evolve:",
    "Attachments and evidence metadata:",
    "Submitter, reviewer, reader, owner, and delegation model:",
    "States, pushback, due dates, order, or cadence:",
)


@dataclass(frozen=True)
class WorkspaceInfo:
    name: str
    path: Path
    spec_name: str
    spec_alias: str
    records: int
    errors: int
    warnings: int
    archived: bool = False


def is_workspace(path: Path) -> bool:
    return path.is_dir() and all((path / marker).exists() for marker in WORKSPACE_MARKERS)


def _spec_label(spec: Any, key: str, fallback: str) -> str:
    if isinstance(spec, dict):
        core = spec.get("core_config")
        if isinstance(core, dict) and isinstance(core.get(key), str) and core[key]:
            return core[key]
    return fallback


def workspace_info(path: Path, *, archived: bool = False) -> WorkspaceInfo:
    spec = read_json(path / "spec.config.json")
    sample = read_json(path / "sample.records.json")
    records = sample.get("records") if isinstance(sample, dict) else []
    result = check_workspace(path)
    return WorkspaceInfo(
        name=path.name,
        path=path,
        spec_name=_spec_label(spec, "spec_name", "unknown"),
        spec_alias=_spec_label(spec, "spec_alias", "Unknown"),
        records=len(records) if isinstance(records, list) else 0,
        errors=len(result.errors),
        warnings=len(result.warnings),
        archived=archived,
    )


def discover_workspaces(root: Path, *, include_archived: bool = False) -> list[WorkspaceInfo]:
    if not root.exists():
        return []

    infos: list[WorkspaceInfo] = []
    for path in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if path.name.startswith(".") or path.name.startswith("_"):
            continue
        if is_workspace(path):
            infos.append(workspace_info(path))

    archive_root = root / ARCHIVE_DIRNAME
    if include_archived and archive_root.exists():
        for path in sorted(archive_root.iterdir(), key=lambda item: item.name.lower()):
            if is_workspace(path):
                infos.append(workspace_info(path, archived=True))
    return infos


def format_workspace_table(infos: list[WorkspaceInfo]) -> str:
    if not infos:
        return "no workspaces found"
    rows = [
        (
            info.name,
            info.spec_name,
            str(info.records),
            "archived" if info.archived else "active",
            f"{info.errors}/{info.warnings}",
            str(info.path),
        )
        for info in infos
    ]
    headers = ("workspace", "spec", "records", "state", "errors/warnings", "path")
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    lines = [
        "  ".join(headers[index].ljust(widths[index]) for index in range(len(headers))),
        "  ".join("-" * width for width in widths),
    ]
    lines.extend("  ".join(row[index].ljust(widths[index]) for index in range(len(row))) for row in rows)
    return "\n".join(lines)


def format_workspace_paths(infos: list[WorkspaceInfo]) -> str:
    return "\n".join(str(info.path) for info in infos)


def archive_workspace(source: Path, *, archive_root: Path | None = None) -> Path:
    if not is_workspace(source):
        raise FileNotFoundError(source)
    target_root = archive_root or source.parent / ARCHIVE_DIRNAME
    target = target_root / source.name
    if target.exists():
        raise FileExistsError(target)
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    return target


def restore_workspace(source: Path, *, output_root: Path | None = None) -> Path:
    if not is_workspace(source):
        raise FileNotFoundError(source)
    if output_root is None and source.parent.name != ARCHIVE_DIRNAME:
        raise ValueError("restore source must be under _archive or --output must be provided")
    target_root = output_root or source.parent.parent
    target = target_root / source.name
    if target.exists():
        raise FileExistsError(target)
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    return target


def rename_workspace(
    source: Path,
    new_name: str,
    *,
    output_root: Path | None = None,
    retitle: bool = True,
) -> Path:
    if not is_workspace(source):
        raise FileNotFoundError(source)
    target_root = output_root or source.parent
    target = target_root / new_name
    if target.exists():
        raise FileExistsError(target)

    spec = read_json(source / "spec.config.json")
    sample = read_json(source / "sample.records.json")
    old_spec_name = spec_name(spec) if isinstance(spec, dict) else None

    target_root.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))

    if retitle and isinstance(spec, dict):
        updated = retitle_spec(spec, new_name)
        new_spec_name = spec_name(updated)
        write_json(target / "spec.config.json", updated, force=True)
        if isinstance(sample, dict):
            sample["spec_name"] = new_spec_name
            if sample.get("filename") in {None, "", f"{old_spec_name}_001"}:
                sample["filename"] = f"{new_spec_name}_001"
            write_json(target / "sample.records.json", sample, force=True)
    return target


def _line_answers_prompt(line: str, prompt: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(prompt) and stripped != prompt


def _is_prompt_line(line: str) -> bool:
    stripped = line.strip()
    return any(stripped.startswith(prompt) for prompt in DECISION_PROMPTS)


def _has_following_answer(lines: list[str], index: int) -> bool:
    for line in lines[index + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("## ") or _is_prompt_line(stripped):
            return False
        return True
    return False


def _text_has_open_placeholders(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return True
    lines = text.splitlines()
    seen_prompt = False
    for index, line in enumerate(lines):
        for prompt in DECISION_PROMPTS:
            if line.strip().startswith(prompt):
                seen_prompt = True
                if not _line_answers_prompt(line, prompt) and not _has_following_answer(lines, index):
                    return True
    return not seen_prompt


def next_steps(workspace: Path) -> str:
    spec = read_json(workspace / "spec.config.json")
    sample = read_json(workspace / "sample.records.json")
    result = check_workspace(workspace)
    lines = [workspace_summary(workspace, spec if isinstance(spec, dict) else {}, sample if isinstance(sample, dict) else {}, result)]
    lines.append("")
    lines.append("next:")
    if result.errors:
        lines.append("1. Fix local check errors before exporting CSV or rendering SQL.")
        lines.append(f"2. Run `airlock-mcp check {workspace}` again.")
        return "\n".join(lines)
    if result.warnings:
        lines.append("1. Review local warnings and either fix them or record the deliberate exception in review.md.")
        lines.append(f"2. Run `airlock-mcp summary {workspace}` to confirm the shape.")
        return "\n".join(lines)
    if _text_has_open_placeholders(workspace / "decisions.md"):
        spec_name = ""
        if isinstance(spec, dict):
            core_config = spec.get("core_config")
            if isinstance(core_config, dict):
                spec_name = str(core_config.get("spec_name") or "")
        if spec_name == "posts":
            lines.append("1. Record the starter assumptions in decisions.md, or change only what is wrong.")
            lines.append(
                "2. Defaults: one row is one post/request/observation/response; "
                "submitters are the owner and approved agents; evidence is optional; "
                "posted_at is authored or captured time."
            )
            lines.append("3. Use posts to collect messy process feedback, then plan the first observe, orient, decide, or act spec.")
        else:
            lines.append("1. Record the messy process goal and first-loop assumptions in decisions.md.")
            lines.append("2. Identify what is observed, what helps orient, what decision is governed, and what action follows.")
            lines.append("3. Keep the first spec small and note later specs in review.md.")
        lines.append(f"4. Run `airlock-mcp next {workspace}` when the design notes are current.")
        return "\n".join(lines)
    records = sample.get("records") if isinstance(sample, dict) else []
    if not records:
        lines.append("1. Add at least one realistic sample record.")
        lines.append(f"2. Run `airlock-mcp check {workspace}`.")
        return "\n".join(lines)
    lines.append(f"1. Export sample CSV: `airlock-mcp export-csv {workspace}`.")
    lines.append(f"2. Render validate-only SQL: `airlock-mcp render-sql {workspace}`.")
    lines.append("3. Run installed Airlock validation before any mutating create or alter call.")
    return "\n".join(lines)
