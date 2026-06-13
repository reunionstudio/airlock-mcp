# Architecture

Airlock MCP is the single installed interface for agents working with Airlock.
The public command should stay simple:

```bash
npx @airlock/mcp install
```

Before npm publication, the same shape can run from GitHub:

```bash
npx -y github:reunionstudio/airlock-mcp install --package github:reunionstudio/airlock-mcp
```

The current package is a dependency-light Node installer and bootstrap stdio MCP
server. It gives agents a standard way to start the Airlock loop while the
heavier operational tools mature.

## Boundaries

- `bin/airlock-mcp.mjs`: executable entry point only.
- `src/cli.mjs`: argument parsing and command dispatch.
- `src/install.mjs`: Codex MCP registration command construction and execution.
- `src/mcp.mjs`: JSON-RPC request handling and stdio transport loop.
- `src/text.mjs`: product language, prompts, repo naming, and guidance text.
- `test/smoke.mjs`: executable smoke and protocol tests.

The Smith implementation lives in `reunionstudio/airlock-smith`. Airlock Smith
is the spec-building capability inside Airlock MCP, not a second install.

## MCP Surface

The bootstrap server exposes:

- tool: `airlock_start`
- prompt: `airlock-start`
- resource: `airlock://getting-started`

These give the agent enough context to start a blank `<project>-specs` repo,
enter Smith when specs need drafting, and avoid creating a first workspace until
the user chooses a path.

## Stdio Rules

MCP stdio messages are newline-delimited JSON-RPC. The server must write only
valid MCP messages to stdout. Logs and diagnostics belong on stderr.

## Install Rules

For Codex, install registers:

```bash
codex mcp add airlock -- npx -y @airlock/mcp server
```

The installer uses argument arrays, not shell strings, for execution. Server
names are allowlisted to letters, numbers, dot, underscore, and hyphen. Package
specs are passed as argv entries, never through a shell, and are rejected if they
contain control characters.

## Runtime Direction

Keep the Node package as the friendly installer and bootstrap launcher.

Prefer Rust with `rmcp` for the production Airlock MCP server once tools do
real operational work: validating specs, loading records, reading outputs,
handling attachments, coordinating push/pull workflows, or serving multiple
agents concurrently.
