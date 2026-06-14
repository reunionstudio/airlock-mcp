from __future__ import annotations

from . import __version__


MCP_MARK = r"""
      airlock-mcp

          __
     ____/ /__        draft specs
    / __  / _ \       check the shape
   /_/ /_/\___/       forge the handoff

        _________
   ____/_______/ \____
       \_______\_/
"""


def about_text() -> str:
    return f"""{MCP_MARK.rstrip()}

version: {__version__}
commands: init-repo, init-app-context, init, import-spec, clone, rename, archive, restore, list-workspaces, summary, next, check, export-csv, render-sql, self-update
principle: Codex is the conversation; files are memory; Airlock is authority.
"""
