from __future__ import annotations

import csv
import json
from io import StringIO
from typing import Any


def column_names(spec_config: dict[str, Any]) -> list[str]:
    columns = spec_config.get("column_config")
    if not isinstance(columns, list):
        return []
    names: list[str] = []
    for column in columns:
        if isinstance(column, dict) and isinstance(column.get("name"), str) and column["name"]:
            names.append(column["name"])
    return names


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), sort_keys=True)
    return value


def records_to_csv(spec_config: dict[str, Any], sample_records: dict[str, Any]) -> str:
    """Render sample.records.json records as CSV in spec column order."""

    fields = column_names(spec_config)
    records = sample_records.get("records")
    if not isinstance(records, list):
        records = []

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for raw_record in records:
        if not isinstance(raw_record, dict):
            continue
        writer.writerow({field: _csv_value(raw_record.get(field)) for field in fields})
    return output.getvalue()
