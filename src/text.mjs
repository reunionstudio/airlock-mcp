export const PACKAGE_NAME = "@reunionstudio/airlock-mcp";
export const DEFAULT_PACKAGE_SPEC = PACKAGE_NAME;
export const DEFAULT_SERVER_NAME = "airlock";
export const PROTOCOL_VERSION = "2025-06-18";

export function slug(value) {
  const cleaned = String(value || "project")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return cleaned || "project";
}

export function specsRepoName(project) {
  const value = slug(project);
  return value.endsWith("-specs") ? value : `${value}-specs`;
}

export function airlockPrompt(project) {
  const repoName = specsRepoName(project);
  return `I want to use Airlock MCP to start working with Airlock specs for ${repoName}.

Set up this project as an Airlock specs repo. If this project is not already a
Git repo, recommend storing it in version control, preferably GitHub if that is
available. If you are creating the repo for me, ask where the ${repoName}
directory should live before making it, then offer to initialize git and create
or push a GitHub repo.

Welcome me by asking what process I want to improve. Explain that Airlock works
best when we can identify the loop around that process: what information comes
in, what context helps us understand it, what decision needs to be made, and
what action happens after the decision. Information may come from apps, files,
forms, people,
emails, calls, mail, websites, APIs, data feeds, or physical events. Actions
may go back through those same places. Ask whether I already have artifacts:
CSV or Excel files, JSON samples, API docs, schemas, forms, screenshots, PDFs,
exports, message examples, or other content people already use. Treat a small
real sample as stronger evidence than a long explanation, and remind me to
redact secrets.

When useful, check the reusable airlock-specs library for starting points,
patterns, and ideas, but do not assume those library specs match current
third-party systems. Prefer current API docs, real exports, samples, and other
artifacts when they conflict with a library shape.

Ask for the messy version, then help turn it into a small first Airlock spec
and a plan for more. Do not create the first workspace until I choose a path.`;
}

export function nextSteps(project) {
  const repoName = specsRepoName(project);
  return `Next:
  1. Open Codex.
  2. Create or open a Git-backed specs repo named ${repoName}. GitHub is the recommended default when available.
  3. If Codex is creating it, ask Codex where the ${repoName} directory should live before it makes files.
  4. Ask Codex:

${airlockPrompt(project)
  .split("\n")
  .map((line) => `     ${line}`)
  .join("\n")}

Airlock MCP will offer:
  - process discovery before choosing a spec pattern
  - spec design with the bundled workbench
  - Airlock operating patterns for OODA loops and separation of duties
  - observe specs for controlled interface ingestion
  - orient specs for proposals, context, scoring, or exception queues
  - decision specs and action specs for governed follow-through
  - artifact-grounded drafts from CSV, Excel, JSON, API docs, schemas, forms, screenshots, PDFs, or exports
  - airlock-specs library patterns as starting points, checked against current artifacts`;
}

export function gettingStartedText(project) {
  return `# Airlock MCP

Airlock MCP is the single installed interface for AI agents working with
Airlock. It helps a person and their agent improve processes by designing
specs, using specs for governed data movement, and planning OODA loops that
can be assisted by people or agents.

Airlock MCP gives agents two kinds of Airlock expertise:

1. Spec design: draft, check, revise, import, clone, and prepare specs for
   installed Airlock validation.
2. Airlock operating patterns: use specs to organize observations, orientation,
   governed decisions, controlled actions, separation of duties, and feedback
   loops.

Start in a Git-backed specs repo such as ${specsRepoName(project)}. GitHub is
the recommended default when the user has it set up, but any normal repository
works. If Codex is creating the repo, ask where the directory should live before
making files. Do not work inside the Airlock MCP implementation repo unless you
are changing the tools themselves.

Use this prompt in the specs repo:

${airlockPrompt(project)}

First ask: What process do you want to improve?

Airlock works best when we can identify the loop around a process:

1. Observe: what information comes in.
2. Orient: what context helps people or agents understand it.
3. Decide: what choice needs to be governed.
4. Act: what happens after the decision.

Information may come from apps, files, forms, people, emails, calls, mail,
websites, APIs, data feeds, or physical events. Actions may go back through
those same places. Airlock calls these places interfaces: where the process
observes from or acts through.

If you already have artifacts, attach or point Codex at them: CSV or Excel
files, JSON samples, API docs, schemas, forms, screenshots, PDFs, exports,
message examples, or other defined content people already use. A small real
sample is often better than a long explanation. Redact secrets before sharing.

Airlock MCP can also use the reusable airlock-specs library for starting
points, patterns, and ideas. Library specs are not guaranteed to match the
current shape of any third-party system. Prefer current API docs, real exports,
samples, and other artifacts when they conflict with the library.

Give Codex the messy version of the process. Airlock MCP should help turn it
into a small first Airlock spec and a plan for more.`;
}

export function helpText() {
  return `airlock-mcp

Usage:
  npx @reunionstudio/airlock-mcp install [--project <name>] [--name <server-name>] [--package <spec>] [--dry-run]
  npx @reunionstudio/airlock-mcp server

Commands:
  install   Register the Airlock MCP server with Codex.
  server    Run the Airlock MCP stdio server.

Options:
  --project <name>      Show next steps using <name>-specs.
  --name <server-name>  Codex MCP server name. Defaults to airlock.
  --package <spec>      npm or GitHub package spec for the registered server.
  --dry-run             Print the Codex registration command without running it.
  --help                Show this help.

Airlock MCP is the single installed interface for agents working with Airlock.
Spec building is bundled inside that experience.
Airlock operating patterns help connect specs into OODA loops, separation of
duties, governed decisions, controlled actions, and feedback loops.
`;
}
