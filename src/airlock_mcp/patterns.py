from __future__ import annotations

from pathlib import Path

from .jsonio import read_json
from .models import Pattern
from .project import patterns_dir


def load_patterns(root: Path | None = None) -> dict[str, Pattern]:
    base = patterns_dir(root)
    manifest = read_json(base / "manifest.json")
    if not isinstance(manifest, dict):
        raise RuntimeError(f"Pattern manifest not found or invalid: {base / 'manifest.json'}")

    patterns: dict[str, Pattern] = {}
    for raw in manifest.get("patterns", []):
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "").strip()
        directory_name = str(raw.get("directory") or name).strip()
        if not name:
            continue
        directory = base / directory_name
        pattern = Pattern(
            name=name,
            title=str(raw.get("title") or name),
            summary=str(raw.get("summary") or ""),
            directory=directory,
            spec_config_path=directory / "spec.config.json",
            sample_records_path=directory / "sample.records.json",
            readme_path=(directory / "README.md") if (directory / "README.md").exists() else None,
        )
        patterns[name] = pattern
    return patterns


def load_pattern_spec(pattern: Pattern) -> dict:
    spec = read_json(pattern.spec_config_path)
    if not isinstance(spec, dict):
        raise RuntimeError(f"Pattern spec config is missing or invalid: {pattern.spec_config_path}")
    return spec


def load_pattern_records(pattern: Pattern) -> dict:
    records = read_json(pattern.sample_records_path)
    if not isinstance(records, dict):
        raise RuntimeError(f"Pattern sample records are missing or invalid: {pattern.sample_records_path}")
    return records
