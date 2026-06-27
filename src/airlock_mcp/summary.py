from __future__ import annotations

import json
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


def _format_value(value: Any, *, default: str = "unknown") -> str:
    if value is None:
        return default
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    else:
        text = str(value)
    return text if text else default


def _format_literal(value: Any, *, default: str = "unknown") -> str:
    if value is None:
        return default
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    return str(value)


def _join(values: list[str], *, default: str = "none") -> str:
    cleaned = [value for value in values if value]
    return ", ".join(cleaned) if cleaned else default


def _truncate(value: Any, limit: int = 96) -> str:
    text = _format_value(value, default="")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


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


def _enabled_guest_subfolders(guest_access: dict[str, Any]) -> list[str]:
    public_folder = guest_access.get("public_folder")
    if not isinstance(public_folder, dict):
        return []
    subfolders = public_folder.get("subfolders")
    if not isinstance(subfolders, dict):
        return []
    return [
        str(name)
        for name, value in subfolders.items()
        if isinstance(value, dict) and value.get("enabled") is True
    ]


def _guest_role_lines(guest_access: dict[str, Any]) -> list[str]:
    roles = guest_access.get("guest_roles")
    if not isinstance(roles, list):
        return []
    lines: list[str] = []
    for role in roles:
        if not isinstance(role, dict):
            continue
        role_name = _format_value(role.get("role_name"))
        access_level = _format_value(role.get("access_level"))
        lines.append(f"{role_name} -> {access_level}")
    return lines


def _attachment_summary(spec_config: dict[str, Any]) -> str:
    policy = spec_config.get("attachment_policy")
    if not isinstance(policy, dict):
        return "not configured"
    if policy.get("attachments_enabled") is not True:
        return "disabled"
    return "required" if policy.get("attachment_required") is True else "optional"


def _column_tests(column: dict[str, Any]) -> list[str]:
    tests = column.get("tests")
    return [str(test) for test in tests if isinstance(test, str)] if isinstance(tests, list) else []


def _column_line(column: dict[str, Any], variant_shapes: set[str]) -> str:
    name = _format_value(column.get("name"))
    column_type = _format_value(column.get("type"))
    tests = _column_tests(column)
    attributes: list[str] = []
    if "not_null" in tests:
        attributes.append("required")
    if "unique" in tests:
        attributes.append("unique")
    extra_tests = [test for test in tests if test not in {"not_null", "unique"}]
    if extra_tests:
        attributes.append("tests: " + ", ".join(extra_tests))
    if column.get("type") == "variant":
        attributes.append("variant shaped" if name in variant_shapes else "variant unshaped")
    if column.get("format"):
        attributes.append("format " + _format_value(column.get("format")))
    description = column.get("description")
    suffix = f" - {_truncate(description, 140)}" if isinstance(description, str) and description else ""
    return f"  - {name}: {column_type}; {_join(attributes)}{suffix}"


def _variant_rule_lines(spec_config: dict[str, Any]) -> list[str]:
    rules = spec_config.get("rules")
    if not isinstance(rules, list):
        return []
    lines: list[str] = []
    for rule in rules:
        if not isinstance(rule, dict) or rule.get("type") != "variant_shape":
            continue
        field = rule.get("field", rule.get("column"))
        if not isinstance(field, str) or not field:
            field = "unknown"
        roots = rule.get("allowed_root_keys")
        root_values = [str(value) for value in roots if isinstance(value, str)] if isinstance(roots, list) else []
        paths = rule.get("paths")
        path_count = len(paths) if isinstance(paths, list) else 0
        required_count = (
            len([path for path in paths if isinstance(path, dict) and path.get("required") is True])
            if isinstance(paths, list)
            else 0
        )
        lines.append(
            f"  - {field}: roots {_join(root_values)}; paths {path_count}; required_paths {required_count}"
        )
    return lines


def _ordered_record_fields(columns: list[dict[str, Any]], record: dict[str, Any]) -> list[str]:
    ordered = [
        str(column.get("name"))
        for column in columns
        if isinstance(column.get("name"), str) and column.get("name") in record
    ]
    extras = sorted(str(key) for key in record if str(key) not in ordered)
    return ordered + extras


def _sample_key(columns: list[dict[str, Any]], records: list[Any]) -> str:
    if not records or not isinstance(records[0], dict):
        return "none"
    first = records[0]
    preferred: list[str] = []
    for test_name in ("unique", "not_null"):
        preferred.extend(
            str(column.get("name"))
            for column in columns
            if isinstance(column.get("name"), str) and test_name in _column_tests(column)
        )
    preferred.extend(str(column.get("name")) for column in columns if isinstance(column.get("name"), str))
    for field in preferred:
        if field in first and not isinstance(first[field], (dict, list)):
            return f"{field}={_truncate(first[field])}"
    return "none"


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
    record_list = records if isinstance(records, list) else []
    record_count = len(record_list)
    first_record = record_list[0] if record_list and isinstance(record_list[0], dict) else {}
    file_rules = spec_config.get("file_rules")
    file_format = file_rules.get("file_format") if isinstance(file_rules, dict) else None
    file_format = file_format if isinstance(file_format, dict) else {}
    guest_access = spec_config.get("guest_access")
    guest_access = guest_access if isinstance(guest_access, dict) else {}
    attachment_policy = spec_config.get("attachment_policy")
    attachment_policy = attachment_policy if isinstance(attachment_policy, dict) else {}
    variant_rule_lines = _variant_rule_lines(spec_config)

    lines = [
        f"workspace: {workspace}",
        f"spec: {core.get('spec_name', 'unknown')} ({core.get('spec_alias', 'no alias')})",
        "",
        "core:",
        f"  spec_name: {_format_value(core.get('spec_name'))}",
        f"  spec_alias: {_format_value(core.get('spec_alias'), default='none')}",
        f"  owner_role: {_format_value(core.get('owner_role'))}",
        f"  published: {_format_value(core.get('is_published'))}",
        f"  archived: {_format_value(core.get('is_archived'))}",
        f"  payload_adapter: {_format_value(core.get('payload_adapter'), default='default')}",
        f"  description: {_truncate(core.get('description')) or 'none'}",
        "",
        "file_rules:",
        f"  file_type: {_format_value(file_format.get('file_type'))}",
        f"  parse_header: {_format_value(file_format.get('parse_header'))}",
        f"  save_header: {_format_value(file_format.get('save_header'))}",
        f"  field_delimiter: {_format_literal(file_format.get('field_delimiter'))}",
        f"  record_delimiter: {_format_literal(file_format.get('record_delimiter'))}",
        f"  encoding: {_format_value(file_format.get('encoding'))}",
        "",
        "attachments:",
        f"  summary: {_attachment_summary(spec_config)}",
        f"  enabled: {_format_value(attachment_policy.get('attachments_enabled'))}",
        f"  required: {_format_value(attachment_policy.get('attachment_required'))}",
        "",
        "guest_access:",
        f"  summary: {_guest_access_summary(spec_config)}",
        f"  isolated_directories_enabled: {_format_value(guest_access.get('isolated_directories_enabled'))}",
        f"  public_folder_enabled: {_format_value((guest_access.get('public_folder') or {}).get('enabled') if isinstance(guest_access.get('public_folder'), dict) else None)}",
        f"  enabled_subfolders: {_join(_enabled_guest_subfolders(guest_access))}",
        f"  guest_roles: {_join(_guest_role_lines(guest_access))}",
        "",
        "column_rules:",
        f"  total: {len(columns)}",
        f"  required_fields: {_join(required)}",
        f"  variant_fields: {_join([f'{name} shaped' if name in variant_shapes else f'{name} unshaped' for name in variants])}",
        "  columns:",
    ]
    lines.extend(_column_line(column, variant_shapes) for column in columns)
    lines.extend(
        [
            "  variant_shape_rules:",
            *(variant_rule_lines if variant_rule_lines else ["  - none"]),
            "",
            "samples:",
            f"  spec_name: {_format_value(sample_records.get('spec_name'))}",
            f"  filename: {_format_value(sample_records.get('filename'))}",
            f"  records: {record_count}",
            f"  first_record_key: {_sample_key(columns, record_list)}",
            f"  first_record_fields: {_join(_ordered_record_fields(columns, first_record))}",
            "",
            "notes:",
            *(
                f"  {_text_status(workspace, filename)}"
                for filename in ("brief.md", "decisions.md", "questions.md", "review.md")
            ),
            "",
            "check:",
            f"  errors: {len(result.errors)}",
            f"  warnings: {len(result.warnings)}",
        ]
    )
    if result.findings:
        lines.append("  findings:")
        lines.extend(
            f"  - {finding.level}: {finding.path}: {finding.message}" for finding in result.findings
        )
    return "\n".join(lines)
