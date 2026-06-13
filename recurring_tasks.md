# Airlock MCP Recurring Tasks

Airlock MCP is a Codex-first workbench for drafting Airlock specs. Use this
file to keep small maintenance passes repeatable without turning the repo into
the main Airlock maintenance program.

## Tracked Variables

- last_improve_dependency_sync_at: 2026-06-13
- last_improve_cleanup_pass_at: 2026-06-13
- last_improve_coverage_pass_at: null
- unit_test_priority_below_percent: 80
- improve_coverage_target_delta_percent: 0.5

## Start Here

For each `/improve` pass:

1. Inspect `git status -sb` and preserve any existing user or agent changes.
2. Check whether Airlock source docs changed in ways that should affect this
   repo's patterns, spec guidance, or CLI examples.
3. Choose one small substantive cleanup or coverage improvement in the current
   worktree.
4. Review touched CLI output for deterministic, flat, safe messages.
5. Run focused tests:

```bash
PYTHONPATH=src python3 -m unittest discover
PYTHONPATH=src python3 -m airlock_mcp doctor
```

6. Update this file and `cleanup.md` when the pass leaves a durable follow-up or
   completes a tracked cleanup/coverage/sync item.
