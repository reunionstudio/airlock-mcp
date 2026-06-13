export const PACKAGE_NAME = "@airlock/mcp";
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

Set up this project as an Airlock specs repo. Use the Airlock Smith
spec-building capability when we need to draft or revise specs. Welcome me,
help me think through real Airlock use cases, and ask only for the missing
decisions. Do not create the first workspace until I choose a path.`;
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
  - spec-building with Airlock Smith
  - spec use and improvement loops with Airlock Star
  - guidance for pulling and pushing governed data through specs
  - OODA brainstorming for possible specs
  - a blank workspace for a known process
  - a posts feedback loop for shared human/agent feedback`;
}

export function gettingStartedText(project) {
  return `# Airlock MCP

Airlock MCP is the single installed interface for AI agents working with
Airlock. It helps a person and their agent build specs, pull and push governed data
through specs, and improve Airlock workflows from real use cases.

Airlock Smith is the spec-building capability inside Airlock MCP. Use it when a
spec needs to be drafted, checked, revised, imported, cloned, or prepared for
installed Airlock validation.

Airlock Star is the use-and-improve capability inside Airlock MCP. Use it when
someone wants to pull or push governed data through specs, exercise real
Airlock workflows, inspect outputs, or turn field experience into spec
improvements.

Start in a blank project specs repo such as ${specsRepoName(project)}. Do not
work inside the Airlock MCP or Airlock Smith implementation repos unless you
are changing the tools themselves.

Use this prompt in the blank specs repo:

${airlockPrompt(project)}

After bootstrap, choose the next useful path:

1. Brainstorm possible specs using the OODA loop.
2. Start from a known process and create a blank workspace.
3. Create a posts feedback loop for humans and agents to submit requests,
   observations, and responses.
4. Use Airlock Star with an installed Airlock app to validate specs, load data,
   read outputs, plan push/pull workflows, and capture improvements.

Create posts only when the user chooses the feedback-loop path.`;
}

export function helpText() {
  return `airlock-mcp

Usage:
  npx @airlock/mcp install [--project <name>] [--name <server-name>] [--package <spec>] [--dry-run]
  npx @airlock/mcp server

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
Airlock Smith is the spec-building capability inside that experience.
Airlock Star is the use-and-improve capability inside that experience.
`;
}
