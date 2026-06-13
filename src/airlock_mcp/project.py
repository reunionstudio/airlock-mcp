from __future__ import annotations

import os
import sysconfig
from pathlib import Path


def repo_root() -> Path:
    """Resolve the Airlock MCP checkout root.

    `AIRLOCK_MCP_HOME` can point the CLI at a different checkout. Otherwise,
    walk upward from this module and the current directory looking for the
    pattern manifest. Editable installs use the module path; direct source runs
    often use the current working directory.
    """

    override = os.environ.get("AIRLOCK_MCP_HOME") or os.environ.get("AIRLOCK_SMITH_HOME")
    if override:
        return Path(override).expanduser().resolve()

    candidates = [Path(__file__).resolve(), Path.cwd().resolve()]
    for start in candidates:
        for parent in [start, *start.parents]:
            if (parent / "patterns" / "manifest.json").exists():
                return parent

    installed_data = Path(sysconfig.get_path("data")) / "airlock_mcp"
    if (installed_data / "patterns" / "manifest.json").exists():
        return installed_data

    return Path(__file__).resolve().parents[2]


def patterns_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "patterns"


def workspace_template_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "workspaces" / "_template"
