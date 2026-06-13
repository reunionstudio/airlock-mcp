from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import CheckResult


def _core(spec_config: dict[str, Any]) -> dict[str, Any]:
    core = spec_config.get("core_config")
    return core if isinstance(core, dict) else {}


def _columns(spec_config: dict[str, Any]) -> list[dict[str, Any]]:
    columns = spec_config.get("column_config")
    return [column for column in columns if isinstance(column, dict)] if isinstance(columns, list) else []


def _variant_shape_fields(spec_config: dict[str, Any]) -> set[str]:
    rules = spec_config.get("rules")
    if not isinstance(rules, list):
        return set()
    fields: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict) or rule.get("type") != "variant_shape":
            continue
        field = rule.get("field", rule.get("column"))
        if isinstance(field, str) and field:
            fields.add(field)
    return fields


def _guest_access_summary(spec_config: dict[str, Any]) -> str:
    guest_access = spec_config.get("guest_access")
    if not isinstance(guest_access, dict):
        return "not configured"
    if guest_access.get("isolated_directories_enabled") is True:
        return "isolated directories enabled"
    public_folder = guest_access.get("public_folder")
    if not isinstance(public_folder, dict) or public_folder.get("enabled") is not True:
        return "configured without public folder"
    subfolders = public_folder.get("subfolders")
    if not isinstance(subfolders, dict):
        return "shared public folder"
    enabled = [
        name
        for name, value in subfolders.items()
        if isinstance(value, dict) and value.get("enabled") is True
    ]
    return "shared public folder: " + (", ".join(enabled) if enabled else "no enabled subfolders")


def _attachment_summary(spec_config: dict[str, Any]) -> str:
    policy = spec_config.get("attachment_policy")
    if not isinstance(policy, dict):
        return "not configured"
    if policy.get("attachments_enabled") is not True:
        return "disabled"
    return "required" if policy.get("attachment_required") is True else "optional"


def _text_status(workspace: Path, filename: str) -> str:
    path = workspace / filename
    if not path.exists():
        return f"{filename}: missing"
    return f"{filename}: filled" if path.read_text(encoding="utf-8").strip() else f"{filename}: empty"


def workspace_summary(
    workspace: Path,
    spec_config: dict[str, Any],
    sample_records: dict[str, Any],
    result: CheckResult,
) -> str:
    core = _core(spec_config)
    columns = _columns(spec_config)
    required = [
        str(column.get("name"))
        for column in columns
        if isinstance(column.get("tests"), list) and "not_null" in column["tests"]
    ]
    variants = [str(column.get("name")) for column in columns if column.get("type") == "variant"]
    variant_shapes = _variant_shape_fields(spec_config)
    records = sample_records.get("records")
    record_count = len(records) if isinstance(records, list) else 0
    file_rules = spec_config.get("file_rules")
    file_format = file_rules.get("file_format") if isinstance(file_rules, dict) else None
    file_type = file_format.get("file_type") if isinstance(file_format, dict) else "unknown"

    lines = [
        f"workspace: {workspace}",
        f"spec: {core.get('spec_name', 'unknown')} ({core.get('spec_alias', 'no alias')})",
        f"owner_role: {core.get('owner_role', 'unknown')}",
        f"columns: {len(columns)} total, {len(required)} required, {len(variants)} variant",
        "required_fields: " + (", ".join(required) if required else "none"),
        "variant_fields: "
        + (
            ", ".join(
                f"{name}{' shaped' if name in variant_shapes else ' unshaped'}" for name in variants
            )
            if variants
            else "none"
        ),
        f"sample_records: {record_count}",
        f"file_type: {file_type}",
        f"attachments: {_attachment_summary(spec_config)}",
        f"guest_access: {_guest_access_summary(spec_config)}",
        "notes: "
        + "; ".join(
            _text_status(workspace, filename)
            for filename in ("brief.md", "decisions.md", "questions.md", "review.md")
        ),
        f"check: {len(result.errors)} error(s), {len(result.warnings)} warning(s)",
    ]
    return "\n".join(lines)
