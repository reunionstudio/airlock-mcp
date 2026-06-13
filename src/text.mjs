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

Set up this project as an Airlock specs repo. Welcome me by asking what
process I want to improve. Explain that Airlock works best when we can
identify the loop around that process: what information comes in, what context
helps us understand it, what decision needs to be made, and what action happens
after the decision. Information may come from apps, files, forms, people,
emails, calls, mail, websites, APIs, data feeds, or physical events. Actions
may go back through those same places. Ask for the messy version, then help
turn it into a small first Airlock spec and a plan for more. Do not create the
first workspace until I choose a path.`;
}

export function nextSteps(project) {
  const repoName = specsRepoName(project);
  return `Next:
  1. Open Codex.
  2. Create a new blank project named ${repoName}.
  3. Ask Codex:

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
  - decision specs and action specs for governed follow-through`;
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

Start in a blank project specs repo such as ${specsRepoName(project)}. Do not
work inside the Airlock MCP implementation repo unless you are changing the
tools themselves.

Use this prompt in the blank specs repo:

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
