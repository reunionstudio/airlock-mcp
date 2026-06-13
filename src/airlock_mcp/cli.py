from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .art import about_text
from .bootstrap import bootstrap_repo, format_bootstrap_result
from .jsonio import read_json
from .manage import (
    archive_workspace,
    discover_workspaces,
    format_workspace_paths,
    format_workspace_table,
    next_steps,
    rename_workspace,
    restore_workspace,
)
from .patterns import load_patterns
from .project import repo_root
from .records import records_to_csv
from .specs import extract_spec_config
from .sql import render_admin_sql
from .summary import workspace_summary
from .updater import build_update_plan, format_update_plan, run_update
from .validation import check_workspace
from .workspace import (
    clone_workspace,
    create_workspace_from_pattern,
    create_workspace_from_spec_config,
)


def _workspace_parent(value: str | None) -> Path:
    return Path(value or "workspaces")


def _workspace_root(value: str | None) -> Path:
    return Path(value or "workspaces")


def _print_check_result(result) -> int:
    for finding in result.findings:
        print(f"{finding.level}: {finding.path}: {finding.message}")
    if result.errors:
        print(f"failed: {len(result.errors)} error(s), {len(result.warnings)} warning(s)")
        return 1
    if result.warnings:
        print(f"ok with warnings: {len(result.warnings)} warning(s)")
    else:
        print("ok")
    return 0


def about(_: argparse.Namespace) -> int:
    print(about_text())
    return 0


def init_repo(args: argparse.Namespace) -> int:
    result = bootstrap_repo(Path(args.path), force=args.force)
    print(format_bootstrap_result(result))
    return 0


def init_workspace(args: argparse.Namespace) -> int:
    patterns = load_patterns(repo_root())
    pattern = patterns[args.pattern]
    target = _workspace_parent(args.output) / args.name
    create_workspace_from_pattern(target, pattern, workspace_name=args.name, force=args.force)
    print(f"created {target}")
    print(f"pattern: {pattern.name} - {pattern.summary}")
    print(f"next: airlock-mcp check {target}")
    return 0


def import_spec(args: argparse.Namespace) -> int:
    source = Path(args.source)
    raw = read_json(source)
    if raw is None:
        print(f"error: could not read JSON source: {source}", file=sys.stderr)
        return 2
    try:
        spec_config = extract_spec_config(raw)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    target = _workspace_parent(args.output) / args.name
    create_workspace_from_spec_config(
        target,
        spec_config,
        mode="import",
        source=str(source),
        force=args.force,
    )
    print(f"imported {source} -> {target}")
    print(f"next: airlock-mcp check {target}")
    return 0


def clone(args: argparse.Namespace) -> int:
    source = Path(args.source_workspace)
    target = _workspace_parent(args.output) / args.name
    clone_workspace(source, target, workspace_name=args.name, force=args.force)
    print(f"cloned {source} -> {target}")
    print(f"next: airlock-mcp check {target}")
    return 0


def check(args: argparse.Namespace) -> int:
    return _print_check_result(check_workspace(Path(args.workspace)))


def list_workspaces(args: argparse.Namespace) -> int:
    infos = discover_workspaces(_workspace_root(args.root), include_archived=args.all)
    if args.paths:
        output = format_workspace_paths(infos)
        if output:
            print(output)
    else:
        print(format_workspace_table(infos))
    return 0


def archive(args: argparse.Namespace) -> int:
    target = archive_workspace(
        Path(args.workspace),
        archive_root=Path(args.archive_root) if args.archive_root else None,
    )
    print(f"archived {args.workspace} -> {target}")
    return 0


def restore(args: argparse.Namespace) -> int:
    target = restore_workspace(
        Path(args.archived_workspace),
        output_root=Path(args.output) if args.output else None,
    )
    print(f"restored {args.archived_workspace} -> {target}")
    return 0


def rename(args: argparse.Namespace) -> int:
    target = rename_workspace(
        Path(args.workspace),
        args.name,
        output_root=Path(args.output) if args.output else None,
        retitle=not args.keep_spec_identity,
    )
    print(f"renamed {args.workspace} -> {target}")
    if args.keep_spec_identity:
        print("spec identity preserved")
    else:
        print("spec identity retitled")
    return 0


def summary(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace)
    result = check_workspace(workspace)
    spec = read_json(workspace / "spec.config.json")
    sample = read_json(workspace / "sample.records.json")
    if not isinstance(spec, dict) or not isinstance(sample, dict):
        return _print_check_result(result)
    print(workspace_summary(workspace, spec, sample, result))
    return 1 if result.errors else 0


def next_action(args: argparse.Namespace) -> int:
    print(next_steps(Path(args.workspace)))
    result = check_workspace(Path(args.workspace))
    return 1 if result.errors else 0


def export_csv(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace)
    result = check_workspace(workspace)
    if result.errors and not args.force:
        _print_check_result(result)
        print("error: refusing to export CSV for invalid workspace; pass --force to export anyway", file=sys.stderr)
        return 1

    spec = read_json(workspace / "spec.config.json")
    sample = read_json(workspace / "sample.records.json")
    if not isinstance(spec, dict):
        print(f"error: invalid spec config: {workspace / 'spec.config.json'}", file=sys.stderr)
        return 2
    if not isinstance(sample, dict):
        print(f"error: invalid sample records: {workspace / 'sample.records.json'}", file=sys.stderr)
        return 2

    output = records_to_csv(spec, sample)
    if args.output:
        path = Path(args.output)
        if path.exists() and not args.force:
            print(f"error: {path} already exists; pass --force to overwrite", file=sys.stderr)
            return 2
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
        print(f"exported {path}")
    else:
        print(output, end="")
    return 0


def self_update(args: argparse.Namespace) -> int:
    root = repo_root()
    plan = build_update_plan(root, method=args.method, source=args.source)
    print(format_update_plan(plan, dry_run=args.dry_run))
    if args.dry_run:
        return 0

    result = run_update(plan, force=args.force)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode == 0:
        print("updated")
    return result.returncode


def list_patterns(_: argparse.Namespace) -> int:
    for pattern in load_patterns(repo_root()).values():
        print(f"{pattern.name}\t{pattern.title}\t{pattern.summary}")
    return 0


def show_pattern(args: argparse.Namespace) -> int:
    patterns = load_patterns(repo_root())
    pattern = patterns[args.pattern]
    if args.files:
        for path in (
            pattern.readme_path,
            pattern.spec_config_path,
            pattern.sample_records_path,
        ):
            if path is not None:
                print(path)
        return 0

    if pattern.readme_path and pattern.readme_path.exists():
        print(pattern.readme_path.read_text(encoding="utf-8").rstrip())
    else:
        print(f"{pattern.name}: {pattern.summary}")
    return 0


def render_sql(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace)
    result = check_workspace(workspace)
    if result.errors and not args.force:
        _print_check_result(result)
        print("error: refusing to render SQL for invalid workspace; pass --force to render anyway", file=sys.stderr)
        return 1

    spec = read_json(workspace / "spec.config.json")
    if not isinstance(spec, dict):
        print(f"error: invalid spec config: {workspace / 'spec.config.json'}", file=sys.stderr)
        return 2
    print(render_admin_sql(spec, app_name=args.app, operation=args.operation))
    return 0


def doctor(_: argparse.Namespace) -> int:
    root = repo_root()
    print(f"root: {root}")
    patterns = load_patterns(root)
    print(f"patterns: {', '.join(patterns)}")
    exit_code = 0
    for pattern in patterns.values():
        missing = [
            str(path)
            for path in (pattern.spec_config_path, pattern.sample_records_path)
            if not path.exists()
        ]
        if missing:
            exit_code = 1
            for path in missing:
                print(f"error: missing pattern file: {path}")
    template = root / "workspaces" / "_template"
    print(f"workspace template: {template}")
    if not template.exists():
        print(f"error: missing workspace template: {template}")
        exit_code = 1
    if exit_code == 0:
        print("ok")
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="airlock-mcp",
        description="Draft, clone, import, and check Airlock spec workspaces.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    patterns = load_patterns(repo_root())

    about_parser = subparsers.add_parser("about", help="Show the Airlock MCP mark and command map.")
    about_parser.set_defaults(func=about)

    init_repo_parser = subparsers.add_parser("init-repo", help="Prepare a specs repo for Codex and Airlock MCP.")
    init_repo_parser.add_argument("path", nargs="?", default=".", help="Specs repo path. Defaults to current directory.")
    init_repo_parser.add_argument("--force", action="store_true", help="Overwrite AGENTS.md and the repo-scoped skill.")
    init_repo_parser.set_defaults(func=init_repo)

    init_parser = subparsers.add_parser("init", help="Create a spec workspace.")
    init_parser.add_argument("name", help="Workspace folder name.")
    init_parser.add_argument(
        "--pattern",
        choices=sorted(patterns),
        default="blank",
        help="Starting pattern. Defaults to blank for a known process.",
    )
    init_parser.add_argument("--output", help="Parent directory. Defaults to ./workspaces.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite files.")
    init_parser.set_defaults(func=init_workspace)

    import_parser = subparsers.add_parser("import-spec", help="Create a workspace from a spec JSON file.")
    import_parser.add_argument("source", help="JSON file with specConfig, spec_config, SPEC_CONFIG, or canonical config.")
    import_parser.add_argument("name", help="Workspace folder name.")
    import_parser.add_argument("--output", help="Parent directory. Defaults to ./workspaces.")
    import_parser.add_argument("--force", action="store_true", help="Overwrite files.")
    import_parser.set_defaults(func=import_spec)

    clone_parser = subparsers.add_parser("clone", help="Clone an existing workspace under a new spec name.")
    clone_parser.add_argument("source_workspace", help="Existing workspace directory.")
    clone_parser.add_argument("name", help="New workspace folder name.")
    clone_parser.add_argument("--output", help="Parent directory. Defaults to ./workspaces.")
    clone_parser.add_argument("--force", action="store_true", help="Overwrite files.")
    clone_parser.set_defaults(func=clone)

    check_parser = subparsers.add_parser("check", help="Check a spec workspace.")
    check_parser.add_argument("workspace", help="Workspace directory.")
    check_parser.set_defaults(func=check)

    list_workspaces_parser = subparsers.add_parser("list-workspaces", help="List local spec workspaces.")
    list_workspaces_parser.add_argument("--root", help="Workspace root. Defaults to ./workspaces.")
    list_workspaces_parser.add_argument("--all", action="store_true", help="Include archived workspaces.")
    list_workspaces_parser.add_argument("--paths", action="store_true", help="Print only workspace paths.")
    list_workspaces_parser.set_defaults(func=list_workspaces)

    archive_parser = subparsers.add_parser("archive", help="Move a workspace into _archive.")
    archive_parser.add_argument("workspace", help="Workspace directory to archive.")
    archive_parser.add_argument("--archive-root", help="Archive directory. Defaults to <workspace-parent>/_archive.")
    archive_parser.set_defaults(func=archive)

    restore_parser = subparsers.add_parser("restore", help="Restore a workspace from _archive.")
    restore_parser.add_argument("archived_workspace", help="Archived workspace directory to restore.")
    restore_parser.add_argument("--output", help="Restore parent directory. Defaults to archive parent.")
    restore_parser.set_defaults(func=restore)

    rename_parser = subparsers.add_parser("rename", help="Rename a workspace and retitle its spec identity.")
    rename_parser.add_argument("workspace", help="Workspace directory to rename.")
    rename_parser.add_argument("name", help="New workspace folder name.")
    rename_parser.add_argument("--output", help="Target parent directory. Defaults to the current parent.")
    rename_parser.add_argument(
        "--keep-spec-identity",
        action="store_true",
        help="Move the folder without changing spec_name, spec_alias, or sample spec_name.",
    )
    rename_parser.set_defaults(func=rename)

    summary_parser = subparsers.add_parser("summary", help="Summarize a spec workspace for session re-entry.")
    summary_parser.add_argument("workspace", help="Workspace directory.")
    summary_parser.set_defaults(func=summary)

    next_parser = subparsers.add_parser("next", help="Show the next safe action for a workspace.")
    next_parser.add_argument("workspace", help="Workspace directory.")
    next_parser.set_defaults(func=next_action)

    export_parser = subparsers.add_parser("export-csv", help="Render sample records as Airlock-ready CSV.")
    export_parser.add_argument("workspace", help="Workspace directory.")
    export_parser.add_argument("--output", help="Write CSV to a file instead of stdout.")
    export_parser.add_argument("--force", action="store_true", help="Export despite local errors or overwrite output.")
    export_parser.set_defaults(func=export_csv)

    list_parser = subparsers.add_parser("list-patterns", help="List bundled patterns.")
    list_parser.set_defaults(func=list_patterns)

    show_parser = subparsers.add_parser("show-pattern", help="Show a pattern README or file paths.")
    show_parser.add_argument("pattern", choices=sorted(patterns))
    show_parser.add_argument("--files", action="store_true", help="Print pattern file paths instead of README.")
    show_parser.set_defaults(func=show_pattern)

    update_parser = subparsers.add_parser("self-update", help="Update Airlock MCP from git or pip.")
    update_parser.add_argument(
        "--method",
        choices=("auto", "git", "pip"),
        default="auto",
        help="Update method. Defaults to git for checkouts and pip otherwise.",
    )
    update_parser.add_argument(
        "--source",
        default="git+https://github.com/reunionstudio/airlock-mcp.git",
        help="pip source used for package installs.",
    )
    update_parser.add_argument("--dry-run", action="store_true", help="Print the update command without running it.")
    update_parser.add_argument("--force", action="store_true", help="Run git update despite uncommitted changes.")
    update_parser.set_defaults(func=self_update)

    sql_parser = subparsers.add_parser("render-sql", help="Render validate-only admin SQL for a workspace.")
    sql_parser.add_argument("workspace", help="Workspace directory.")
    sql_parser.add_argument("--app", default="airlock", help="Installed app name. Defaults to airlock.")
    sql_parser.add_argument(
        "--operation",
        choices=("create", "alter"),
        default="create",
        help="Procedure shape to render. Defaults to create.",
    )
    sql_parser.add_argument("--force", action="store_true", help="Render even if local check has errors.")
    sql_parser.set_defaults(func=render_sql)

    doctor_parser = subparsers.add_parser("doctor", help="Check repo-level Airlock MCP assets.")
    doctor_parser.set_defaults(func=doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileExistsError as exc:
        target = exc.filename or (exc.args[0] if exc.args else "unknown")
        print(f"error: {target} already exists; pass --force to overwrite", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        target = exc.filename or (exc.args[0] if exc.args else "unknown")
        print(f"error: not found: {target}", file=sys.stderr)
        return 2
    except NotADirectoryError as exc:
        target = exc.filename or (exc.args[0] if exc.args else "unknown")
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
