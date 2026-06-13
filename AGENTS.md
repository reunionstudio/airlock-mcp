# Airlock MCP Guidance

Airlock MCP is the public connector front door for AI agents. Airlock Smith is
the guided spec-building workbench it points users toward.

## Product Boundary

- Keep this repo focused on connector installation, MCP server behavior, and
  agent registration.
- Keep spec drafting patterns, workspace files, and deterministic Airlock Smith
  checks in `reunionstudio/airlock-smith`.
- The public user command is `npx @airlock/mcp install`.
- For Codex, install should use `codex mcp add airlock -- npx -y @airlock/mcp server`.
- After install, the user creates a blank `<project>-specs` Codex project and
  starts chatting there.

## MCP Runtime

- The current Node server is a small bootstrap server.
- Prefer Rust with `rmcp` for the production MCP server once tools do real
  operational work beyond setup guidance.
- For stdio MCP, stdout is protocol-only. Send logs and diagnostics to stderr.
- Test the stdio server with raw JSON-RPC messages for `initialize`,
  `tools/list`, `prompts/list`, and `resources/list`.

## Verification

Run:

```bash
npm test
```
