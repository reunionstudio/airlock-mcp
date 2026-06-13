from __future__ import annotations

from pathlib import Path
from typing import Any

from .jsonio import read_json
from .models import CheckResult, Finding


ALLOWED_COLUMN_TYPES = {
    "string",
    "number",
    "integer",
    "boolean",
    "date",
    "datetime",
    "variant",
}

BANNED_PAYLOAD_FIELDS = {
    "approval_status",
    "approved_at",
    "approved_by",
    "reviewer_notes",
    "workflow_state",
    "workflow_status",
    "workflow_step",
}

WORKFLOW_FIELD_PREFIXES = (
    "approval_",
    "approved_",
    "reviewer_",
    "workflow_",
    "pushback_",
)

ALLOWED_ACCESS_LEVELS = {"append_access", "read_access", "full_access"}

REQUIRED_TEXT_FILES = ("brief.md", "decisions.md", "questions.md", "review.md")


def require_dict(value: Any, findings: list[Finding], path: str) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        findings.append(Finding("error", path, "Expected object."))
        return None
    return value


def require_list(value: Any, findings: list[Finding], path: str) -> list[Any] | None:
    if not isinstance(value, list):
        findings.append(Finding("error", path, "Expected array."))
        return None
    return value


def _variant_shape_field(rule: dict[str, Any]) -> str | None:
    value = rule.get("field", rule.get("column"))
    return value if isinstance(value, str) and value else None


def _looks_like_workflow_state(name: str) -> bool:
    return name in BANNED_PAYLOAD_FIELDS or name.startswith(WORKFLOW_FIELD_PREFIXES)


def _public_access_enabled(guest_access: dict[str, Any], access_level: str) -> bool:
    public_folder = guest_access.get("public_folder")
    if not isinstance(public_folder, dict) or public_folder.get("enabled") is not True:
        return False
    subfolders = public_folder.get("subfolders")
    if not isinstance(subfolders, dict):
        return False
    target = subfolders.get(access_level)
    return isinstance(target, dict) and target.get("enabled") is True


def validate_guest_access(guest_access: dict[str, Any], findings: list[Finding]) -> None:
    isolated = guest_access.get("isolated_directories_enabled") is True
    guest_roles = guest_access.get("guest_roles")
    if guest_roles is None:
        return

    roles = require_list(guest_roles, findings, "spec.config.json:guest_access.guest_roles")
    if not roles:
        return

    for index, raw_role in enumerate(roles):
        path = f"spec.config.json:guest_access.guest_roles[{index}]"
        if isinstance(raw_role, str):
            continue
        role = require_dict(raw_role, findings, path)
        if not role:
            continue

        role_name = role.get("role_name")
        if not isinstance(role_name, str) or not role_name:
            findings.append(Finding("error", f"{path}.role_name", "Guest role name is required."))

        access_level = role.get("access_level")
        if access_level is None:
            if not isolated:
                findings.append(
                    Finding(
                        "warning",
                        path,
                        "Shared guest role has no access_level; confirm the intended public-folder access.",
                    )
                )
            continue

        if access_level not in ALLOWED_ACCESS_LEVELS:
            findings.append(
                Finding(
                    "error",
                    f"{path}.access_level",
                    "Expected append_access, read_access, or full_access.",
                )
            )
            continue

        if not isolated and not _public_access_enabled(guest_access, str(access_level)):
            findings.append(
                Finding(
                    "error",
                    f"{path}.access_level",
                    f"`{access_level}` requires the matching public_folder subfolder to be enabled.",
                )
            )


def validate_spec_config(spec: dict[str, Any], findings: list[Finding]) -> set[str]:
    core = require_dict(spec.get("core_config"), findings, "spec.config.json:core_config")
    if core:
        for key in ("spec_name", "spec_alias", "description", "owner_role"):
            if not core.get(key):
                findings.append(
                    Finding("error", f"spec.config.json:core_config.{key}", "Required value is missing.")
                )

    columns = require_list(spec.get("column_config"), findings, "spec.config.json:column_config")
    column_names: set[str] = set()
    variant_columns: set[str] = set()
    variant_shape_fields: set[str] = set()
    if columns:
        seen: set[str] = set()
        for index, raw_column in enumerate(columns):
            path = f"spec.config.json:column_config[{index}]"
            column = require_dict(raw_column, findings, path)
            if not column:
                continue

            name = column.get("name")
            column_type = column.get("type")
            tests = column.get("tests")

            if not isinstance(name, str) or not name:
                findings.append(Finding("error", f"{path}.name", "Column name is required."))
                continue
            if name in seen:
                findings.append(Finding("error", f"{path}.name", f"Duplicate column `{name}`."))
            seen.add(name)
            column_names.add(name)

            if _looks_like_workflow_state(name):
                findings.append(
                    Finding(
                        "warning",
                        f"{path}.name",
                        f"`{name}` looks like Airlock workflow or review state; keep it only if it is an upstream fact.",
                    )
                )

            if column_type not in ALLOWED_COLUMN_TYPES:
                findings.append(Finding("error", f"{path}.type", f"Unsupported column type `{column_type}`."))
            if column_type == "variant":
                variant_columns.add(name)
            if column_type in {"date", "datetime"}:
                fmt = column.get("format")
                if not isinstance(fmt, str) or "%" not in fmt:
                    findings.append(
                        Finding(
                            "error",
                            f"{path}.format",
                            "Date and datetime formats must use strftime tokens such as %Y-%m-%d.",
                        )
                    )
            if not isinstance(column.get("description"), str) or not column.get("description"):
                findings.append(Finding("error", f"{path}.description", "Column description is required."))
            if not isinstance(tests, list):
                findings.append(Finding("error", f"{path}.tests", "Column tests must be an array."))

    rules = spec.get("rules", [])
    if rules is not None:
        rules_list = require_list(rules, findings, "spec.config.json:rules")
        if rules_list:
            for index, raw_rule in enumerate(rules_list):
                path = f"spec.config.json:rules[{index}]"
                rule = require_dict(raw_rule, findings, path)
                if not rule:
                    continue
                if rule.get("type") == "variant_shape":
                    field = _variant_shape_field(rule)
                    if not field:
                        findings.append(
                            Finding("error", f"{path}.field", "variant_shape needs `field` or `column`.")
                        )
                    elif field not in variant_columns:
                        findings.append(
                            Finding(
                                "error",
                                f"{path}.field",
                                "variant_shape field must reference a declared variant column.",
                            )
                        )
                    else:
                        variant_shape_fields.add(field)
                    allowed = rule.get("allowed_root_keys")
                    if allowed is not None and not isinstance(allowed, list):
                        findings.append(Finding("error", f"{path}.allowed_root_keys", "Expected array."))
                    paths = rule.get("paths")
                    optional_paths = rule.get("optional_paths")
                    required_paths = rule.get("required_paths")
                    if paths is not None and not isinstance(paths, list):
                        findings.append(Finding("error", f"{path}.paths", "Expected array."))
                    if optional_paths is not None and not isinstance(optional_paths, list):
                        findings.append(Finding("error", f"{path}.optional_paths", "Expected array."))
                    if required_paths is not None and not isinstance(required_paths, list):
                        findings.append(Finding("error", f"{path}.required_paths", "Expected array."))

    for name in sorted(variant_columns - variant_shape_fields):
        findings.append(
            Finding(
                "warning",
                "spec.config.json:rules",
                f"Variant column `{name}` has no variant_shape rule.",
            )
        )

    file_rules = require_dict(spec.get("file_rules"), findings, "spec.config.json:file_rules")
    if file_rules:
        file_format = require_dict(
            file_rules.get("file_format"), findings, "spec.config.json:file_rules.file_format"
        )
        if file_format and file_format.get("file_type") not in {"csv", "excel"}:
            findings.append(
                Finding(
                    "warning",
                    "spec.config.json:file_rules.file_format.file_type",
                    "Local records adapter currently checks CSV and Excel-shaped specs best.",
                )
            )

    guest_access = spec.get("guest_access")
    if guest_access is not None and not isinstance(guest_access, dict):
        findings.append(Finding("error", "spec.config.json:guest_access", "Expected object."))
    elif isinstance(guest_access, dict):
        validate_guest_access(guest_access, findings)

    return column_names


def validate_sample_records(
    sample: dict[str, Any], spec: dict[str, Any], columns: set[str], findings: list[Finding]
) -> None:
    core = spec.get("core_config") if isinstance(spec.get("core_config"), dict) else {}
    expected_spec_name = core.get("spec_name")
    if sample.get("spec_name") != expected_spec_name:
        findings.append(
            Finding(
                "error",
                "sample.records.json:spec_name",
                f"Expected `{expected_spec_name}` to match spec.config.json.",
            )
        )
    if not sample.get("filename"):
        findings.append(Finding("error", "sample.records.json:filename", "Filename is required."))

    records = require_list(sample.get("records"), findings, "sample.records.json:records")
    if not records:
        return

    required_fields = {
        column["name"]
        for column in spec.get("column_config", [])
        if isinstance(column, dict)
        and isinstance(column.get("tests"), list)
        and "not_null" in column["tests"]
    }
    variant_fields = {
        column["name"]
        for column in spec.get("column_config", [])
        if isinstance(column, dict) and column.get("type") == "variant"
    }

    for index, raw_record in enumerate(records):
        path = f"sample.records.json:records[{index}]"
        record = require_dict(raw_record, findings, path)
        if not record:
            continue
        extra = set(record) - columns
        missing = {field for field in required_fields if record.get(field) in (None, "")}
        for field in sorted(extra):
            findings.append(
                Finding("error", f"{path}.{field}", "Record field is not declared in column_config.")
            )
        for field in sorted(missing):
            findings.append(Finding("error", f"{path}.{field}", "Required sample value is missing."))
        for field in sorted(variant_fields & set(record)):
            if record[field] not in (None, "") and not isinstance(record[field], (dict, list)):
                findings.append(
                    Finding("error", f"{path}.{field}", "Variant sample values should be objects or arrays.")
                )


def check_workspace(workspace: Path) -> CheckResult:
    findings: list[Finding] = []
    if not workspace.exists():
        return CheckResult((Finding("error", str(workspace), "Workspace not found."),))

    for filename in REQUIRED_TEXT_FILES:
        path = workspace / filename
        if not path.exists():
            findings.append(Finding("error", filename, "Missing workspace file."))
        elif not path.read_text(encoding="utf-8").strip():
            findings.append(Finding("warning", filename, "Workspace file is empty."))

    spec = read_json(workspace / "spec.config.json", findings)
    sample = read_json(workspace / "sample.records.json", findings)
    if isinstance(spec, dict):
        columns = validate_spec_config(spec, findings)
        if isinstance(sample, dict):
            validate_sample_records(sample, spec, columns, findings)

    return CheckResult(tuple(findings))
