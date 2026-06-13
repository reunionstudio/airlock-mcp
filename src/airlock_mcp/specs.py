from __future__ import annotations

import copy
from typing import Any

from .jsonio import coerce_json_object


def slug_to_snake(value: str) -> str:
    import re

    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return cleaned or "draft_spec"


def spec_name(spec_config: dict[str, Any]) -> str:
    core = spec_config.get("core_config")
    if isinstance(core, dict):
        name = core.get("spec_name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return "draft_spec"


def retitle_spec(spec_config: dict[str, Any], workspace_name: str) -> dict[str, Any]:
    updated = copy.deepcopy(spec_config)
    core = updated.setdefault("core_config", {})
    if isinstance(core, dict):
        new_name = slug_to_snake(workspace_name)
        core["spec_name"] = new_name
        core["spec_alias"] = workspace_name.replace("-", " ").replace("_", " ").title()
    return updated


def extract_spec_config(raw: Any) -> dict[str, Any]:
    """Extract canonical spec config from common Airlock/spec-library shapes."""

    data = coerce_json_object(raw)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object containing a spec config.")

    for key in ("specConfig", "spec_config", "SPEC_CONFIG"):
        if key in data:
            extracted = coerce_json_object(data[key])
            if isinstance(extracted, dict):
                return extracted

    if "core_config" in data or "column_config" in data:
        return data

    specs = data.get("specs")
    if isinstance(specs, list) and specs:
        first = specs[0]
        if isinstance(first, dict):
            config = first.get("config") or first
            if isinstance(config, dict):
                core = {
                    "spec_name": data.get("specName") or data.get("SPEC_NAME") or config.get("spec_name") or "imported_spec",
                    "spec_alias": data.get("specAlias") or data.get("SPEC_ALIAS") or data.get("specName") or "Imported Spec",
                    "description": data.get("summary") or data.get("description") or "",
                    "owner_role": config.get("owner_role") or "app_admin",
                    "is_published": False,
                    "is_archived": False,
                }
                return {
                    "core_config": core,
                    "column_config": config.get("columns") or config.get("column_config") or [],
                    "file_rules": {"file_format": config.get("file_format") or {}},
                    "rules": config.get("rules") or [],
                    "attachment_policy": config.get("attachment_policy") or {},
                    "guest_access": data.get("guest_access") or config.get("guest_access") or {},
                }

    raise ValueError("Could not find specConfig, spec_config, SPEC_CONFIG, or canonical spec keys.")


def sample_value_for_column(column: dict[str, Any]) -> Any:
    column_type = str(column.get("type") or "string").lower()
    name = str(column.get("name") or "field")
    if column_type in {"number", "float", "decimal"}:
        return 1.0
    if column_type == "integer":
        return 1
    if column_type == "boolean":
        return True
    if column_type == "date":
        return "2026-06-13"
    if column_type == "datetime":
        return "2026-06-13 09:00:00"
    if column_type == "variant":
        return {"source": {"system": "manual"}}
    if name.endswith("_id"):
        return f"{name.upper()}-001"
    return f"example {name.replace('_', ' ')}"


def sample_records_for_spec(spec_config: dict[str, Any]) -> dict[str, Any]:
    columns = spec_config.get("column_config")
    if not isinstance(columns, list):
        columns = []
    record: dict[str, Any] = {}
    for column in columns:
        if isinstance(column, dict) and column.get("name"):
            record[str(column["name"])] = sample_value_for_column(column)
    current_spec_name = spec_name(spec_config)
    return {
        "spec_name": current_spec_name,
        "filename": f"{current_spec_name}_001",
        "records": [record],
    }
