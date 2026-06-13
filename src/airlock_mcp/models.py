from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Pattern:
    name: str
    title: str
    summary: str
    directory: Path
    spec_config_path: Path
    sample_records_path: Path
    readme_path: Path | None = None


@dataclass(frozen=True)
class Finding:
    level: str
    path: str
    message: str


@dataclass(frozen=True)
class CheckResult:
    findings: tuple[Finding, ...]

    @property
    def errors(self) -> tuple[Finding, ...]:
        return tuple(finding for finding in self.findings if finding.level == "error")

    @property
    def warnings(self) -> tuple[Finding, ...]:
        return tuple(finding for finding in self.findings if finding.level == "warning")

    @property
    def ok(self) -> bool:
        return not self.errors


JsonObject = dict[str, Any]
