from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jsonio import read_json, write_json, write_text
from .specs import extract_spec_config, spec_name


APP_CONTEXT_MODES = ("spec-first", "app-first", "co-development")


APP_README = """# Airlock App Context

This folder is app-local context for building software that uses Airlock specs.

The canonical specs live in the specs repo or installed Airlock. Files here are
snapshots, samples, generated helpers, and planning context for app development.
Refresh them when the canonical spec changes.

Use:

- `specs.manifest.json` to track which specs the app reads from or writes to.
- `spec-snapshots/` for app-local copies of spec configs.
- `sample-records/` for app-local sample records used in UI and test fixtures.
- `generated/types/` for generated application types.
- `generated/sql/` for reviewed SQL helpers or query templates.

Installed Airlock separates procedure intent:

- `observe.*`: read-only governance observation for discovery, health, access
  explanation, activity, admin activity, billing events, governance maps, and
  context packets.
- `agent.*`: governed agent work in the actor's scope.
- `admin.*`: administrative mutation and operational changes.

Prefer `observe.*` for app read-side setup and monitoring questions. Use
`observe.admin_activity` for broad admin mutation and maintenance audit
questions, and `observe.spec_admin_activity` for one spec's definition-change
timeline. For `alter_spec` activity, use `CHANGED_SECTIONS` and
`CHANGED_FIELDS` to triage what changed before fetching version snapshots.
Do not use retired admin read wrappers such as `admin.list_specs`,
`admin.describe_role`, or `admin.list_events`; use the matching observe procedure.

Do not store credentials here. Do not write directly to Airlock-owned tables,
stages, generated views, or generated tables. Use approved Airlock/Snowflake
access paths and submit governed decisions or actions through spec contracts.
"""


APP_AGENTS = """# Airlock App Guidance

This repo may contain application code that uses Airlock specs.

## Modes

- Spec-first: design governed specs before building the app surface.
- App-first: use existing specs to build an app, dashboard, queue, or workflow.
- Co-development: evolve the app and specs together while keeping the contract
  explicit.

## App Context

The `airlock/` folder is app-local. Its spec snapshots are references for
development, not canonical specs. Canonical specs live in the specs repo or
installed Airlock.

Keep two tracks visible during co-development:

- Spec track: row grain, columns, samples, access, validation, and workflow.
- App track: screens, reads, decisions, writes, user actions, and runtime.

Use approved Airlock/Snowflake access paths. Do not bypass spec workflow or
write directly to Airlock-owned tables, stages, generated views, or generated
tables. If the app needs to submit a decision or action and no suitable write
spec exists, propose a small spec-design step.

Installed Airlock procedure grammar:

- `observe.*` is read-only governance observation. Use it for discovery,
  health, access explanation, governance maps, activity, billing events, and
  context packets.
- `agent.*` is governed agent work in the actor's scope.
- `admin.*` is administrative mutation. Do not use retired admin read wrappers;
  use observe list/detail procedures instead.
"""


@dataclass(frozen=True)
class AppContextResult:
    root: Path
    mode: str
    created: tuple[Path, ...]
    updated: tuple[Path, ...]
    kept: tuple[Path, ...]
    specs: tuple[str, ...]


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip())
    cleaned = cleaned.strip("._-").lower()
    return cleaned or "spec"


def _write_text_if_needed(path: Path, text: str, *, force: bool) -> str:
    if path.exists() and not force:
        return "kept"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, text, force=True)
    return "created"


def _write_json_if_needed(path: Path, value: Any, *, force: bool) -> str:
    if path.exists() and not force:
        return "kept"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, value, force=True)
    return "created"


def _load_spec_source(source: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if source.is_dir():
        raw_spec = read_json(source / "spec.config.json")
        if not isinstance(raw_spec, dict):
            raise ValueError(f"invalid spec workspace: {source}")
        raw_sample = read_json(source / "sample.records.json")
        return raw_spec, raw_sample if isinstance(raw_sample, dict) else None

    raw = read_json(source)
    if raw is None:
        raise FileNotFoundError(source)
    return extract_spec_config(raw), None


def _manifest(mode: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "mode": mode,
        "canonical_source": "specs repo or installed Airlock",
        "snapshot_policy": "Snapshots are app-local development references, not canonical specs.",
        "installed_airlock_contract": {
            "observe": "read-only governance observation, context, activity, health, billing events, and access explanation",
            "agent": "governed agent work in the actor scope",
            "admin": "administrative mutation and operational changes",
        },
        "specs": entries,
        "tracks": {
            "spec_track": "row grain, columns, samples, access, validation, workflow",
            "app_track": "screens, reads, decisions, writes, user actions, runtime",
        },
    }


def _merge_manifest(existing: Any, new_manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(existing, dict):
        return new_manifest

    merged = dict(existing)
    merged.update(
        {
            "schema_version": new_manifest["schema_version"],
            "mode": new_manifest["mode"],
            "canonical_source": new_manifest["canonical_source"],
            "snapshot_policy": new_manifest["snapshot_policy"],
            "installed_airlock_contract": new_manifest["installed_airlock_contract"],
            "tracks": new_manifest["tracks"],
        }
    )

    existing_entries = existing.get("specs")
    by_name: dict[str, dict[str, Any]] = {}
    if isinstance(existing_entries, list):
        for entry in existing_entries:
            if isinstance(entry, dict) and isinstance(entry.get("spec_name"), str):
                by_name[entry["spec_name"]] = dict(entry)

    for entry in new_manifest["specs"]:
        previous = by_name.get(entry["spec_name"], {})
        merged_entry = {**previous, **entry}
        if previous.get("role") and entry.get("role") == "unknown":
            merged_entry["role"] = previous["role"]
        by_name[entry["spec_name"]] = merged_entry

    merged["specs"] = list(by_name.values())
    return merged


def init_app_context(
    target: Path,
    *,
    mode: str = "app-first",
    spec_sources: list[Path] | None = None,
    force: bool = False,
) -> AppContextResult:
    if mode not in APP_CONTEXT_MODES:
        raise ValueError(f"mode must be one of: {', '.join(APP_CONTEXT_MODES)}")

    root = target.expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise NotADirectoryError(str(root))
    root.mkdir(parents=True, exist_ok=True)

    airlock_root = root / "airlock"
    created: list[Path] = []
    updated: list[Path] = []
    kept: list[Path] = []

    for directory in (
        airlock_root,
        airlock_root / "spec-snapshots",
        airlock_root / "sample-records",
        airlock_root / "generated",
        airlock_root / "generated" / "types",
        airlock_root / "generated" / "sql",
    ):
        if directory.exists():
            kept.append(directory)
        else:
            directory.mkdir(parents=True)
            created.append(directory)

    entries: list[dict[str, Any]] = []
    spec_names: list[str] = []
    for source in spec_sources or []:
        spec_config, sample_records = _load_spec_source(source.expanduser())
        name = spec_name(spec_config)
        safe = _safe_name(name)
        snapshot_path = airlock_root / "spec-snapshots" / f"{safe}.spec.config.json"
        bucket = created if _write_json_if_needed(snapshot_path, spec_config, force=force) == "created" else kept
        bucket.append(snapshot_path)

        sample_relative: str | None = None
        if sample_records is not None:
            sample_path = airlock_root / "sample-records" / f"{safe}.sample.records.json"
            bucket = created if _write_json_if_needed(sample_path, sample_records, force=force) == "created" else kept
            bucket.append(sample_path)
            sample_relative = str(sample_path.relative_to(root))

        core = spec_config.get("core_config")
        core = core if isinstance(core, dict) else {}
        entries.append(
            {
                "spec_name": name,
                "spec_alias": core.get("spec_alias"),
                "source": str(source),
                "snapshot": str(snapshot_path.relative_to(root)),
                "sample_records": sample_relative,
                "role": "unknown",
                "snapshot_only": True,
            }
        )
        spec_names.append(name)

    for path, content in (
        (airlock_root / "README.md", APP_README),
        (airlock_root / "AGENTS.md", APP_AGENTS),
        (airlock_root / "generated" / "types" / ".gitkeep", ""),
        (airlock_root / "generated" / "sql" / ".gitkeep", ""),
    ):
        bucket = created if _write_text_if_needed(path, content, force=force) == "created" else kept
        bucket.append(path)

    manifest_path = airlock_root / "specs.manifest.json"
    manifest = _manifest(mode, entries)
    if manifest_path.exists() and not force:
        write_json(manifest_path, _merge_manifest(read_json(manifest_path), manifest), force=True)
        updated.append(manifest_path)
    else:
        bucket = created if _write_json_if_needed(manifest_path, manifest, force=force) == "created" else kept
        bucket.append(manifest_path)

    return AppContextResult(
        root=airlock_root,
        mode=mode,
        created=tuple(created),
        updated=tuple(updated),
        kept=tuple(kept),
        specs=tuple(spec_names),
    )


def format_app_context_result(result: AppContextResult) -> str:
    lines = [f"initialized app context {result.root}", f"mode: {result.mode}"]
    for path in result.created:
        lines.append(f"created {path.relative_to(result.root.parent)}")
    for path in result.updated:
        lines.append(f"updated {path.relative_to(result.root.parent)}")
    for path in result.kept:
        lines.append(f"kept {path.relative_to(result.root.parent)}")
    lines.append("seeded_specs: " + (", ".join(result.specs) if result.specs else "none"))
    lines.extend(
        [
            "",
            "next:",
            "1. Treat spec snapshots as app-local references, not canonical specs.",
            "2. Mark each manifest spec as read, write, or read_write for the app.",
            "3. Use observe.* for read-only governance discovery and agent.* for governed actor work.",
            "4. Build governed submissions through approved Airlock/Snowflake access paths.",
        ]
    )
    return "\n".join(lines)
