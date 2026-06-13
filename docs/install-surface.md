# Install Surface

Airlock should offer a familiar agent-connector install surface without making
the implementation more clever than the user journey requires.

## Recommendation

Use an MCP-style public front door:

```bash
npx @reunionstudio/airlock-mcp install
```

Airlock MCP is the single installed interface for agents working with Airlock.
Then the user opens Codex, creates or opens a Git-backed `<project>-specs`
repo, and starts chatting with Airlock. GitHub is the recommended default when
available. If Codex is creating the repo, it should ask where the directory
should live before writing files. Airlock MCP should start by asking what
process the user wants to improve, then help design specs and operating
patterns around observe, orient, decide, and act.

The install command is not the spec workspace. It is the connector/setup entry
point. The specs repo is still the durable memory.

The connector package and MCP server live in `reunionstudio/airlock-mcp`.
This workbench provides the spec-building implementation inside that one
installed Airlock MCP experience.

For Codex, the install command should register a local stdio MCP server using
Codex's built-in MCP manager:

```bash
codex mcp add airlock -- npx -y @reunionstudio/airlock-mcp server
```

## What `npx` Means

`npx` is the npm package runner. It runs a command from a local or remote npm
package. If the requested package is not already available locally, npm can
fetch it into its cache and put that package's executable on `PATH` for the
command.

That means `npx @reunionstudio/airlock-mcp install` requires Node/npm on the
user's machine, but does not require them to clone this workbench, install a
separate spec-building tool, or install a global binary by hand.

It is common in MCP examples because many local MCP servers and installers are
distributed as npm packages, and developers often already have Node tooling.
It is not required by MCP.

## MCP Is Runtime-Agnostic

MCP is a protocol, not a Node framework. The server can be written in Node,
Python, Rust, Go, Java, C#, or another language as long as it speaks the
protocol over a supported transport.

The standard transports to care about first are:

- stdio for local agent-launched servers
- Streamable HTTP for hosted or longer-running servers

## Alternatives

Viable install surfaces include:

- `npx @reunionstudio/airlock-mcp install`: best familiar first impression for agent users
- `uvx airlock-mcp` or `pipx install ...`: useful for workbench development
  and dogfooding, not the public primary path
- Homebrew: good for macOS developer installs
- a signed Rust binary: best for single-file distribution later
- Docker: useful for controlled server deployments, but heavy for spec drafting
- hosted Streamable HTTP MCP: useful when Airlock becomes a remote service

## Runtime Choice

Use Node for the thin public installer and launcher if we want
`npx @reunionstudio/airlock-mcp install`, because `npx` is specifically an npm/Node
distribution path. The Node package should stay small: register the MCP server,
print the next Codex steps, and provide a bootstrap stdio server while the
runtime is still light.

Keep Airlock MCP's drafting CLI in Python for now. The current work is
Markdown, JSON, CSV, pattern loading, and local validation. Product fit and
workflow clarity matter more than raw performance.

Prefer Rust with `rmcp` for the production Airlock MCP server once the server
does real work beyond bootstrap guidance, especially Snowflake/Airlock calls,
workspace scanning, policy checks, loading records, reading outputs, handling
attachments, push/pull workflows, or multi-agent traffic. The Rust guidance we
care about:

- a single signed binary
- stronger local distribution ergonomics
- predictable memory and latency for concurrent agents
- typed tool contracts and generated JSON schemas
- no Node or Python runtime dependency for the long-running server
- stricter supply-chain or runtime constraints

For stdio MCP servers, stdout is the JSON-RPC protocol channel. Logs, tracing,
and diagnostics must go to stderr or the client can disconnect. Integration
tests should send raw JSON-RPC `initialize` and `tools/list` messages to the
server binary and parse the responses.

Do not rewrite the spec-building logic in Rust just to look more performant.
If we want Rust, use it first as a distribution wrapper or future MCP server,
then port core spec-building logic only when real performance, security, or
packaging pressure appears.

The first release should optimize the user journey:

1. install connector
2. create or open a Git-backed `<project>-specs` Codex project
3. ask where the repo directory should live if Codex is creating it
4. ask what process the user wants to improve
5. ask for existing artifacts such as CSV, Excel, JSON, API docs, schemas,
   forms, screenshots, PDFs, exports, or message examples
6. use `airlock-specs` library patterns as starting points when useful, while
   preferring current artifacts over library shapes when they conflict
7. map where information comes in and actions go out
8. create the first workspace only after the user chooses a small first spec
9. keep a plan for later specs that improve the full loop
