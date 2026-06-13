from __future__ import annotations

import copy
import shutil
from pathlib import Path
from typing import Any

from .jsonio import read_json, write_json, write_text
from .models import Pattern
from .patterns import load_pattern_records, load_pattern_spec
from .specs import retitle_spec, sample_records_for_spec, spec_name


WORKSPACE_FILES = (
    "brief.md",
    "decisions.md",
    "questions.md",
    "review.md",
    "spec.config.json",
    "sample.records.json",
)


def workspace_markdown(name: str, source_name: str, summary: str, *, mode: str = "create") -> dict[str, str]:
    if mode == "create":
        goal = f"Start from the `{source_name}` pattern: {summary}"
        source_block = f"Mode: create\n\nPattern: {source_name}"
    else:
        goal = summary
        source_block = f"Mode: {mode}\n\nSource: {source_name}"

    return {
        "brief.md": f"""# Spec Brief

## Goal

{goal}

## Users And Agents

Who submits, reviews, reads, delegates, or acts on this data?

## Systems To Observe

List the systems, files, screenshots, APIs, users, or existing Airlock specs
that inform the decision.

## First Useful Outcome

What should become possible after the first version lands in Airlock?
""",
        "decisions.md": """# Decisions

## Row Grain

One row is:

## OODA Loop

- Observe:
- Orient:
- Decide:
- Act:

## Identifiers

Stable ids and retry-safe keys:

## Business Time

Event, observed, captured, effective, or transaction timestamps:

## Typed Columns

Fields people will filter, join, audit, aggregate, or report on:

## Variant Context

Optional context that may evolve:

## Evidence

Attachments and evidence metadata:

## Access

Submitter, reviewer, reader, owner, and delegation model:

## Workflow And Expectations

States, pushback, due dates, order, or cadence:
""",
        "questions.md": """# Questions

Use this file for decisions that change the model.

- What row grain would be expensive to change later?
- What evidence is required?
- What business timestamp matters?
- Which fields must be typed columns?
- Who can see shared data?
""",
        "review.md": f"""# Review

## Local Check

Run:

```bash
airlock-mcp check .
```

## Source

{source_block}

Adaptations:

## Airlock Validation

Result:

## Remaining Risk

Human decisions still open:
""",
    }


def create_workspace_from_pattern(
    target: Path,
    pattern: Pattern,
    *,
    workspace_name: str,
    force: bool = False,
) -> None:
    if target.exists() and not force:
        raise FileExistsError(target)
    target.mkdir(parents=True, exist_ok=True)

    spec_config = copy.deepcopy(load_pattern_spec(pattern))
    sample_records = copy.deepcopy(load_pattern_records(pattern))
    if pattern.name == "blank":
        spec_config = retitle_spec(spec_config, workspace_name)
        sample_records["spec_name"] = spec_name(spec_config)
        sample_records["filename"] = f"{sample_records['spec_name']}_001"

    for filename, content in workspace_markdown(workspace_name, pattern.name, pattern.summary).items():
        write_text(target / filename, content, force=force)
    write_json(target / "spec.config.json", spec_config, force=force)
    write_json(target / "sample.records.json", sample_records, force=force)


def create_workspace_from_spec_config(
    target: Path,
    spec_config: dict[str, Any],
    *,
    mode: str,
    source: str,
    force: bool = False,
) -> None:
    if target.exists() and not force:
        raise FileExistsError(target)
    target.mkdir(parents=True, exist_ok=True)

    records = sample_records_for_spec(spec_config)
    summary = f"Imported canonical spec config from {source}."
    for filename, content in workspace_markdown(target.name, source, summary, mode=mode).items():
        write_text(target / filename, content, force=force)
    write_json(target / "spec.config.json", spec_config, force=force)
    write_json(target / "sample.records.json", records, force=force)


def clone_workspace(source: Path, target: Path, *, workspace_name: str, force: bool = False) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    if target.exists() and not force:
        raise FileExistsError(target)
    target.mkdir(parents=True, exist_ok=True)

    for filename in WORKSPACE_FILES:
        source_file = source / filename
        if source_file.exists() and filename not in {"spec.config.json", "sample.records.json", "review.md"}:
            shutil.copyfile(source_file, target / filename)

    spec_config = read_json(source / "spec.config.json")
    if not isinstance(spec_config, dict):
        raise ValueError(f"Source workspace has invalid spec.config.json: {source}")

    cloned_config = retitle_spec(spec_config, workspace_name)
    records = sample_records_for_spec(cloned_config)
    write_json(target / "spec.config.json", cloned_config, force=True)
    write_json(target / "sample.records.json", records, force=True)

    review = f"""# Review

## Local Check

Run:

```bash
airlock-mcp check .
```

## Source

Mode: clone

Source workspace: {source}

Original spec: {spec_name(spec_config)}

New spec: {spec_name(cloned_config)}

## Airlock Validation

Result:

## Remaining Risk

Human decisions still open:
"""
    write_text(target / "review.md", review, force=True)
