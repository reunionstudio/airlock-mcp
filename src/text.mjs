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
or push a GitHub repo. If I am in an app repo and want to build software that
uses existing specs, or develop the app and specs together, do not bootstrap a
specs repo unless I ask for spec edits.

Welcome me by asking whether I want spec-first, app-first, or co-development:
spec-first designs governed specs before the app, app-first builds from existing
specs, and co-development evolves the app and specs together. For spec-first or
co-development, ask what process I want to improve. Explain that Airlock works
best when we can identify the loop around that process: what information comes
in, what context helps us understand it, what decision needs to be made, and
what action happens after the decision. Information may come from apps, files,
forms, people, emails, calls, mail, websites, APIs, data feeds, or physical
events. Actions may go back through those same places. Ask whether I already
have artifacts: CSV or Excel files, JSON samples, API docs, schemas, forms,
screenshots, PDFs, exports, message examples, or other content people already
use. Treat a small real sample as stronger evidence than a long explanation,
and remind me to redact secrets.

When useful, check the reusable airlock-specs library for starting points,
patterns, and ideas, but do not assume those library specs match current
third-party systems. Prefer current API docs, real exports, samples, and other
artifacts when they conflict with a library shape.

Ask for the messy version, then help turn it into a small first Airlock spec
and a plan for more. Do not create the first workspace until I choose a path.

If I want app-first or co-development, ask for the app goal, the specs I can
access, which specs are read sources, which spec records decisions or actions,
and where the app should run. Teach the installed Airlock procedure split:
\`airlock.observe.*\` is read-only governance observation,
\`airlock.agent.*\` is governed agent work, and \`airlock.admin.*\` is
administrative mutation. Prefer observe payloads such as
\`observe.procedures\`, \`observe.specs\`, \`observe.spec\`,
\`observe.governance_map\`, \`observe.explain_access\`, \`observe.health\`,
\`observe.activity\`, \`observe.admin_activity\`, \`observe.spec_admin_activity\`,
and \`observe.billing_events\` before inventing custom read paths. For \`alter_spec\`
activity, use \`CHANGED_SECTIONS\` and \`CHANGED_FIELDS\` to triage what changed
before fetching version snapshots. Offer to run \`airlock-mcp init-app-context\`
in the app repo to seed \`airlock/specs.manifest.json\`, spec snapshots, sample records, and
generated helper folders. Help code the app using approved Airlock/Snowflake access paths.
When a reference spec declares \`restricted_reference\` or
\`reference_config.restricted_reference\`, do not enumerate values, build a
populated picker, or call broad \`agent.select_reference_data\`. Get the lookup
value from the user's case/work context and call
\`agent.get_reference_record\` for the configured \`object_key\`, purpose, and
role lens. It returns at most one record, applies reference row filters, checks
\`action_limit\` before returning data, and always records the safe
\`REFERENCE_READ\` event used for budgeting. Branch on \`OK\`, \`NOT_FOUND\`,
\`NON_UNIQUE_LOOKUP_KEY\`, \`PURPOSE_REQUIRED\`, \`USAGE_LIMIT_BLOCKED\`, and
\`REFERENCE_READ_EVENT_FAILED\`; report \`USAGE_CONTEXT\` fields such as
\`action_limit_used\` and \`action_time_period\`. Use
\`observe.reference_context\`, \`observe.usage_limits\`, \`observe.usage_limit\`,
and \`observe.explain_access(action => 'get_reference_record', object_key => ...)\`
for read-only planning and audit.

Do not use retired admin read wrappers such as
\`admin.list_specs\`, \`admin.describe_role\`, or \`admin.list_events\`; use
the matching observe procedure. Do not write directly to Airlock-owned tables
or bypass spec workflow.`;
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
  - spec-first, app-first, and co-development planning
  - spec design with the bundled workbench
  - Airlock operating patterns for OODA loops and separation of duties
  - read-only observe procedures for governance maps, health, access explanation, activity, billing events, and context packets
  - app context seeding with spec snapshots and manifests
  - app and workflow coding against existing Airlock specs
  - observe specs for controlled interface ingestion
  - orient specs for proposals, context, scoring, or exception queues
  - decision specs and action specs for governed follow-through
  - OKF-style Markdown knowledge bundles for accepted agent context
  - artifact-grounded drafts from CSV, Excel, JSON, API docs, schemas, forms, screenshots, PDFs, or exports
  - airlock-specs library patterns as starting points, checked against current artifacts`;
}

export function gettingStartedText(project) {
  return `# Airlock MCP

Airlock MCP is the single installed interface for AI agents working with
Airlock. It helps a person and their agent improve processes by designing
specs, using specs for governed data movement, planning OODA loops, and building
apps or workflows that read from and submit through existing specs.

Airlock MCP gives agents four kinds of Airlock help:

1. Spec design: draft, check, revise, import, clone, and prepare specs for
   installed Airlock validation.
2. Airlock operating patterns: use specs to organize observations, orientation,
   governed decisions, controlled actions, separation of duties, and feedback
   loops.
3. App and workflow implementation: build dashboards, queues, decision UIs,
   analyses, and agent workflows that use existing specs without bypassing
   Airlock contracts.
4. Governance observation: use installed Airlock's read-only \`observe.*\`
   procedures to inspect setup, access, activity, billing events, health,
   context packets, and governance maps before deciding what an app or agent
   should do.

Start in a Git-backed specs repo such as ${specsRepoName(project)}. GitHub is
the recommended default when the user has it set up, but any normal repository
works. If Codex is creating the repo, ask where the directory should live before
making files. Do not work inside the Airlock MCP implementation repo unless you
are changing the tools themselves.

Use this prompt in the specs repo:

${airlockPrompt(project)}

First ask which delivery mode the user wants:

1. Spec-first: design governed specs before building the app surface.
2. App-first: build an app or workflow from existing specs.
3. Co-development: develop the app and specs together.

For spec-first and co-development work, ask: What process do you want to improve?

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

For governed Markdown knowledge, use the \`okf-knowledge-bundle\` pattern. It
creates a spec with \`core_config.payload_adapter\` set to
\`okf_knowledge_bundle\`. Installed Airlock loads locally validated bundles with
\`airlock.admin.load_okf_bundle(...)\`, can sync parsed metadata with
\`airlock.admin.sync_okf_bundle_metadata(...)\`, and exposes authoritative
accepted context through \`AIRLOCK_DATA.ACTIVE.V_OKF_CONCEPT_METADATA\`.

Give Codex the messy version of the process. Airlock MCP should help turn it
into a small first Airlock spec and a plan for more.

For app-first and co-development work, give Codex the app goal and available
specs. Airlock MCP should identify read specs, write specs, orienting views,
decision capture, and safe Airlock/Snowflake access paths. Installed Airlock
uses \`observe.*\` for read-only governance observation, \`agent.*\` for
governed agent work, and \`admin.*\` for administrative mutation. Start
read-side discovery with observe payloads such as \`observe.procedures\`,
\`observe.specs\`, \`observe.spec\`, \`observe.governance_map\`,
\`observe.explain_access\`, \`observe.health\`, \`observe.activity\`,
\`observe.admin_activity\`, \`observe.spec_admin_activity\`, and \`observe.billing_events\`;
for \`alter_spec\` activity, use \`CHANGED_SECTIONS\` and \`CHANGED_FIELDS\` to
triage what changed before fetching version snapshots. Do not use retired admin
read wrappers such as \`admin.list_specs\`, \`admin.describe_role\`, or
\`admin.list_events\`. If a reference spec declares \`restricted_reference\` or
\`reference_config.restricted_reference\`, do not enumerate the protected
reference; use \`agent.get_reference_record\` for a known lookup value and
\`observe.usage_limits\` / \`observe.usage_limit\` for budget visibility. It can
seed an app repo with \`airlock/specs.manifest.json\`, spec snapshots, sample
records, and generated helper folders. The app should submit decisions,
approvals, actions, comments, or follow-ups through Airlock spec contracts, not
direct table writes.
In co-development mode, keep the spec track and app track visible side by side.`;
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
Airlock MCP can also help build apps and workflows that use existing specs for
approved reads and governed submissions.
`;
}
