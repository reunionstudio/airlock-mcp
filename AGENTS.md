# Airlock MCP Guidance

Airlock MCP is the single installed interface for AI agents working with
Airlock. It should cover building specs, using specs, pulling and pushing
governed data, and discovering improvements from real use cases.

Spec building is bundled inside Airlock MCP, not a second thing users install.

## Product Boundary

- Keep this repo focused on connector installation, MCP server behavior, agent
  registration, Airlock-facing tools, spec drafting patterns, workspace files,
  and deterministic spec-building checks.
- The public user command is `npx @reunionstudio/airlock-mcp install`.
- For Codex, install should use `codex mcp add airlock -- npx -y @reunionstudio/airlock-mcp server`.
- After install, the user creates a blank `<project>-specs` Codex project and
  starts chatting there. They should ask for Airlock, not for a separate
  spec-building install.
- Current installed Airlock separates procedure intent: `observe.*` is the
  read-only governance observation surface, `agent.*` is governed actor work,
  and `admin.*` is administrative mutation. App and audit guidance should
  prefer observe payloads for discovery, health, access explanation, activity,
  billing events, governance maps, and context packets.

## MCP Runtime

- The current Node server is a small bootstrap server for the one-install
  Airlock MCP experience.
- Prefer Rust with `rmcp` for the production MCP server once tools do real
  operational work beyond setup guidance, such as validating specs, loading
  records, reading outputs, handling attachments, or coordinating push/pull
  workflows.
- For stdio MCP, stdout is protocol-only. Send logs and diagnostics to stderr.
- Test the stdio server with raw JSON-RPC messages for `initialize`,
  `tools/list`, `prompts/list`, and `resources/list`.

## Verification

Run:

```bash
npm test
node -c bin/airlock-mcp.mjs
python3 -m json.tool package.json
PYTHONPATH=src python3 -m unittest discover
PYTHONPATH=src python3 -m airlock_mcp doctor
```
