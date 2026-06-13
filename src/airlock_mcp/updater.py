from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SOURCE = "git+https://github.com/reunionstudio/airlock-mcp.git"


@dataclass(frozen=True)
class UpdatePlan:
    method: str
    root: Path
    command: tuple[str, ...]
    reason: str


def _is_git_checkout(root: Path) -> bool:
    return (root / ".git").exists()


def build_update_plan(root: Path, *, method: str = "auto", source: str = DEFAULT_SOURCE) -> UpdatePlan:
    if method not in {"auto", "git", "pip"}:
        raise ValueError("method must be auto, git, or pip")

    if method == "git" or (method == "auto" and _is_git_checkout(root)):
        return UpdatePlan(
            method="git",
            root=root,
            command=("git", "-C", str(root), "pull", "--ff-only"),
            reason="update checkout with a fast-forward-only pull",
        )

    return UpdatePlan(
        method="pip",
        root=root,
        command=(sys.executable, "-m", "pip", "install", "--upgrade", source),
        reason="upgrade installed package from source",
    )


def format_update_plan(plan: UpdatePlan, *, dry_run: bool) -> str:
    prefix = "dry-run: " if dry_run else ""
    return "\n".join(
        (
            f"{prefix}self-update method: {plan.method}",
            f"root: {plan.root}",
            f"reason: {plan.reason}",
            "command: " + " ".join(plan.command),
        )
    )


def git_checkout_dirty(root: Path) -> bool:
    result = subprocess.run(
        ("git", "-C", str(root), "status", "--porcelain"),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return True
    return bool(result.stdout.strip())


def run_update(plan: UpdatePlan, *, force: bool = False) -> subprocess.CompletedProcess[str]:
    if plan.method == "git" and git_checkout_dirty(plan.root) and not force:
        return subprocess.CompletedProcess(
            plan.command,
            2,
            "",
            "working tree has uncommitted changes; commit, stash, or pass --force\n",
        )
    return subprocess.run(plan.command, check=False, capture_output=True, text=True)
