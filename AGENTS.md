# Airlock MCP Guidance

Airlock MCP is the single installed interface for AI agents working with
Airlock. It should cover building specs, using specs, pulling and pushing
governed data, and discovering improvements from real use cases.

Airlock Smith is the spec-building capability inside Airlock MCP, not a second
thing users install.

## Product Boundary

- Keep this repo focused on connector installation, MCP server behavior, agent
  registration, and Airlock-facing tools.
- Keep spec drafting patterns, workspace files, and deterministic Airlock Smith
  checks in `reunionstudio/airlock-smith`.
- The public user command is `npx @airlock/mcp install`.
- For Codex, install should use `codex mcp add airlock -- npx -y @airlock/mcp server`.
- After install, the user creates a blank `<project>-specs` Codex project and
  starts chatting there. They should ask for Airlock, not for a separate Smith
  install.

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
```
