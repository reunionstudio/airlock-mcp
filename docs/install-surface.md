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
delivery mode the user wants: spec-first, app-first from existing specs, or
co-development of specs and app together. Then it should help design specs and
operating patterns around observe, orient, decide, and act, or help code an app
that reads and submits through Airlock contracts.

The install command is not the spec workspace. It is the connector/setup entry
point. The specs repo is still the durable memory.

For installed Airlock access, teach the current procedure split:
`airlock.observe.*` is the read-only governance observation surface,
`airlock.agent.*` is governed agent work, and `airlock.admin.*` is
administrative mutation. App-first and audit-style workflows should use
observe payloads for discovery, context, health, access explanation, activity,
billing events, and governance maps before considering custom SQL helpers.
When a read-only reference spec declares `restricted_reference` or
`reference_config.restricted_reference`, agents should avoid broad
`agent.select_reference_data` reads and use `agent.get_reference_record` for a
known lookup value and purpose, with `observe.reference_context`,
`observe.usage_limits`, `observe.usage_limit`, and
`observe.explain_access(action => 'get_reference_record', object_key => ...)`
for planning and audit.

The installed Streamlit Native App also provides governed attachment
inspection: inline image/text previews and bounded, page-at-a-time PDF preview
for documents up to 100 MB and 2,000 pages. The selected PDF page warms the next
two pages in the session cache; large PDFs require explicit open, and full-file
access uses Snowflake download links when available. Successful PDF page
previews emit metadata-only `ATTACHMENT_PREVIEW` activity. This UI capability
does not grant MCP clients direct stage access.

The Native App is deliberately a generic operating and fallback surface. It
should support administration, inspection, evidence, workflow, and safe manual
action without accumulating every domain's presentation rules. Airlock MCP
should recommend app-first or co-development when repeated, high-value work
deserves a purpose-built interface. The custom app owns domain summaries,
calculations, terminology, and controls while Airlock remains the governed
backend. UI layout and aggregation hints should not be added to specs merely to
polish the generic app.

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
7. use the `okf-knowledge-bundle` pattern when the useful artifact is governed
   Markdown knowledge for accepted agent context
8. map where information comes in and actions go out
9. create the first workspace only after the user chooses a small first spec
10. keep a plan for later specs that improve the full loop

For users who already have specs and want to build software, optimize a second
journey:

1. install connector
2. open the app repo in Codex
3. ask for the app goal and available specs
4. identify read specs and write specs
5. seed app-local Airlock context with `airlock-mcp init-app-context` when the
   app needs spec snapshots, samples, generated helpers, and a manifest
6. inspect installed setup with read-only `observe.*` procedures when available
7. build orienting views, dashboards, queues, proposals, or recommendations
8. capture decisions, approvals, actions, comments, or follow-ups through
   Airlock spec contracts
9. avoid direct writes to Airlock-owned tables and avoid bypassing spec workflow

For users who are developing the app and specs together, optimize a third
journey:

1. open the app repo or specs repo in Codex
2. choose co-development explicitly
3. keep a spec track for row grain, columns, access, samples, validation, and
   workflow
4. keep an app track for screens, reads, orienting summaries, decision capture,
   governed writes, runtime, and tests
5. seed the app repo with `airlock/` snapshots and a manifest when the app needs
   local contract context
6. treat app snapshots as development references while canonical specs remain
   in the specs repo or installed Airlock
