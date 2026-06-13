# Airlock MCP

Airlock MCP is the public connector front door for AI agents. Airlock Smith is
the guided spec-building mode inside that experience.

## Install

```bash
npx @airlock/mcp install
```

Today this package is a small installer and MCP launcher. For Codex, install
registers a local stdio server with:

```bash
codex mcp add airlock -- npx -y @airlock/mcp server
```

The server exposes bootstrap guidance that points the user to the Codex-first
Airlock Smith workflow and the public tool repo:

```text
https://github.com/reunionstudio/airlock-smith
```

This install shape uses Node because `npx` runs npm package binaries. MCP itself
does not require Node. Once Airlock MCP does real operational work, the
production server should likely be Rust with `rmcp`: single binary, predictable
memory and latency, typed tool contracts, and no Node/Python runtime for the
long-running process. The npm package can remain the friendly installer.

For stdio MCP, stdout is protocol-only. Logs and diagnostics must go to stderr.

## Test

```bash
npm test
```

The smoke test verifies install dry-run output and the stdio MCP handshake for
`initialize`, `tools/list`, `prompts/list`, and `resources/list`.

The intended user flow is:

1. Run `npx @airlock/mcp install` once for the agent environment.
2. Open Codex.
3. Create a blank project repo named for the org or project, such as
   `home-specs`.
4. Ask Codex to use Airlock Smith from the public repo.
5. Let Codex bootstrap the project and welcome the user before creating the
   first workspace.

The first workspace should not be created automatically. Airlock Smith should
offer OODA brainstorming, a known-process draft, or a shared `posts` feedback
loop.
