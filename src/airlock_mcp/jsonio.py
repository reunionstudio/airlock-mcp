from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Finding


def read_json(path: Path, findings: list[Finding] | None = None) -> Any | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        if findings is not None:
            findings.append(Finding("error", str(path), "Missing required JSON file."))
    except json.JSONDecodeError as exc:
        if findings is not None:
            findings.append(
                Finding("error", str(path), f"Invalid JSON at line {exc.lineno}: {exc.msg}.")
            )
    return None


def write_json(path: Path, value: Any, *, force: bool = False) -> None:
    if path.exists() and not force:
        raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, value: str, *, force: bool = False) -> None:
    if path.exists() and not force:
        raise FileExistsError(path)
    path.write_text(value, encoding="utf-8")


def coerce_json_object(value: Any) -> dict[str, Any] | None:
    current = value
    for _ in range(5):
        if isinstance(current, dict):
            return current
        if isinstance(current, str):
            stripped = current.strip()
            if not stripped:
                return None
            try:
                current = json.loads(stripped)
            except json.JSONDecodeError:
                return None
            continue
        return None
    return None
