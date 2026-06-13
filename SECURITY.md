# Security

Airlock MCP is an agent-facing connector. Treat every tool as a governed
operation surface.

## Current Bootstrap Server

- Uses stdio transport only.
- Writes only JSON-RPC messages to stdout.
- Sends diagnostics and install errors to stderr.
- Uses `spawnSync` without a shell for Codex registration.
- Validates MCP server names before passing them to `codex mcp add`.
- Passes npm or GitHub package specs as argv entries, never through a shell.
- Rejects package specs with whitespace or control characters.
- Exposes guidance only; it does not read local secrets, call Snowflake, mutate
  files, or contact network services.

## Production Rules

- Validate all user-supplied paths and identifiers.
- Restrict local file access to the active specs repo unless the user grants
  broader access.
- Treat installed Airlock as the authority for validation, mutation, workflow,
  attachments, and governed data movement.
- Keep Airlock lifecycle state, reviewer state, and approval workflow separate
  from submitted business payloads unless they are true upstream facts.
- For stdio MCP, never log to stdout.
- For future Streamable HTTP MCP, bind local servers to localhost, validate
  `Origin`, and require proper authentication.

Report security issues privately to the Reunion Studio maintainers.
