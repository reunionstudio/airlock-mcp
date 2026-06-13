# Airlock MCP

Airlock MCP is the single installed interface for AI agents working with
Airlock.

It covers the full Airlock loop:

- build specs with the Airlock Smith capability
- use specs to pull and push governed data
- validate, create, and revise specs against installed Airlock
- capture real use cases and improvements so specs get better over time

Airlock Smith is not a second thing users install. It is the spec-building
capability inside Airlock MCP.

## Install

```bash
npx @airlock/mcp install
```

Today this package is a small installer and MCP launcher. For Codex, install
registers a local stdio server with:

```bash
codex mcp add airlock -- npx -y @airlock/mcp server
```

The server exposes bootstrap guidance for starting a specs repo and entering
the Airlock Smith spec-building capability. The current Smith implementation
lives at:

```text
https://github.com/reunionstudio/airlock-smith
```

This install shape uses Node because `npx` runs npm package binaries. MCP itself
does not require Node. Once Airlock MCP does real operational work, such as
validating specs, loading records, handling attachments, reading outputs, and
coordinating push/pull workflows, the production server should likely be Rust
with `rmcp`: single binary, predictable memory and latency, typed tool
contracts, and no Node/Python runtime for the long-running process. The npm
package can remain the friendly installer.

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
4. Ask Codex to use Airlock to help build and use specs.
5. Let Airlock MCP bootstrap the project, welcome the user, and offer the next
   useful path before creating the first workspace.

The first workspace should not be created automatically. Airlock Smith should
offer OODA brainstorming, a known-process draft, or a shared `posts` feedback
loop.
