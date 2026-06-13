# Workflows

## Start A New Specs Repo

Use this when a person opens a blank Codex project and wants to start working
with real Airlock specs. The project repo is where they work. Public users
should come through the single Airlock MCP install; this repo provides the
spec-building capability behind that experience.

Ask for the project or organization name first, then lowercase it, replace
spaces with hyphens, and append `-specs`. For example, `Home` becomes
`home-specs`. Reserve `airlock-specs` for the canonical reusable spec library.
Airlock itself does not create this repo; Codex can create it locally while
helping the user start an Airlock specs project.
Start in Codex, not Snowflake Cortex. Snow CLI or Cortex only matters later when
validating, creating, or operating specs against an installed Airlock app.

The preferred Codex prompt is:

```text
I want to use Airlock MCP to start working with Airlock specs for Home.

Set up this project as an Airlock specs repo. Use the Airlock MCP
spec-building capability when we need to draft or revise specs. Welcome me,
help me think through real Airlock use cases, and ask only for the missing
decisions. Do not create the first workspace until I choose a path.
```

When dogfooding this implementation repo before the MCP package is published,
Codex can install the spec-building workbench from GitHub:

```bash
git init
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install git+https://github.com/reunionstudio/airlock-mcp.git
airlock-mcp init-repo
```

This does not require a PyPI release. `pip` installs the package directly from
GitHub. It is a dogfood/developer path, not the public primary install.

The target public install shape should be:

```bash
npx @reunionstudio/airlock-mcp install
```

The connector implementation lives in `reunionstudio/airlock-mcp`; this
workbench keeps the Airlock MCP spec-building capability.

That should install or register the Airlock MCP connector for the user's agent
environment. After that, the user still creates a blank `<slug>-specs` project
and starts chatting there. Airlock MCP covers building specs, using specs to
pull and push governed data, and improving specs from real use cases.

For Codex, the install command should register the server with:

```bash
codex mcp add airlock -- npx -y @reunionstudio/airlock-mcp server
```

The MCP-style flow should be:

1. Run `npx @reunionstudio/airlock-mcp install` once for the agent environment.
2. Open Codex.
3. Create a new blank project named for the org or project, such as
   `home-specs`.
4. Tell Codex: `Use Airlock to help me build and use specs.`
5. Airlock MCP welcomes, offers OODA brainstorming, a known-process draft, a
   `posts` feedback loop, or installed-Airlock validation/use.

`init-repo` creates `AGENTS.md`, `.agents/skills/airlock-mcp/SKILL.md`, and
`workspaces/`. That is what lets Codex understand prompts such as
`Use $airlock-mcp` inside the specs repo.

After bootstrap, offer three paths before creating a workspace:

- brainstorm possible specs using the OODA loop
- start from a known process and create a blank workspace
- create a `posts` feedback loop for humans and agents to submit requests,
  observations, and responses

## Start From Feedback

Use this when the user chooses a shared feedback loop for humans and agents.
If they are not sure what to model yet, offer OODA brainstorming before creating
this workspace.

```bash
airlock-mcp init feedback-loop --pattern posts
airlock-mcp check workspaces/feedback-loop
```

Then ask Codex to help decide what the posts should observe, who responds, and
what next spec should grow from the feedback.

## Start From A Known Process

Use this when the process is known but the data shape is not.

```bash
airlock-mcp init weekly-timesheets --pattern blank
```

Replace the draft columns once row grain, event timestamps, typed fields,
evidence, access, and workflow are clear.

## Import An Existing Spec

Use this for an Airlock spec-library file, exported `SPEC_CONFIG`, or a canonical
config from another repo.

```bash
airlock-mcp import-spec ../airlock-specs/specs/internal/posts.json imported-posts
airlock-mcp check workspaces/imported-posts
```

Supported input shapes:

- `{"specConfig": {...}}`
- `{"spec_config": {...}}`
- `{"SPEC_CONFIG": "{...}"}`
- a raw canonical object with `core_config` or `column_config`
- a legacy `{"specs": [{"config": ...}]}`

## Clone A Workspace

Use this when a related spec should preserve most design choices but needs a new
identity.

```bash
airlock-mcp clone workspaces/imported-posts team-posts
airlock-mcp check workspaces/team-posts
```

Clone resets `core_config.spec_name`, `core_config.spec_alias`, and sample
records. It keeps the surrounding brief and decisions so Codex can adapt them.

## Organize Workspaces

Use this when a workbench has more than one draft in motion.

```bash
airlock-mcp list-workspaces
airlock-mcp list-workspaces --all
airlock-mcp rename workspaces/weekly-timesheets weekly-time-entries
airlock-mcp archive workspaces/old-draft
airlock-mcp restore workspaces/_archive/old-draft
```

`rename` retitles `core_config.spec_name`, `core_config.spec_alias`, and sample
record spec names by default so the folder and spec identity stay together. Use
`--keep-spec-identity` when the move is purely organizational.

`archive` moves a workspace under `_archive`. `list-workspaces` hides internal
underscore directories by default and shows archived drafts with `--all`.

## Resume A Session

Use this at the start of a later Codex session before changing JSON.

```bash
airlock-mcp summary workspaces/team-posts
airlock-mcp next workspaces/team-posts
```

The summary shows the current spec identity, required fields, variant fields,
attachment posture, guest access model, sample record count, note-file status,
and local check counts.

`next` prints the same recap plus a conservative next action: fix local errors,
review warnings, fill open design prompts in `decisions.md`, add sample records,
or prepare export and validate-only SQL. Inline answers such as
`One row is: a submitted receipt` count as filled.

## Export Sample Records

Use this when the JSON examples should be reviewed or loaded through an
Airlock CSV-oriented path.

```bash
airlock-mcp export-csv workspaces/team-posts
airlock-mcp export-csv workspaces/team-posts --output /tmp/team-posts.csv
```

`sample.records.json` remains the authoring shape because it is easier for
Codex and humans to edit. `export-csv` writes columns in `column_config` order
and serializes `variant` values as compact JSON strings.

## Render Validate-Only SQL

Use this as a handoff artifact for an admin or agent with Snowflake access.

```bash
airlock-mcp render-sql workspaces/team-posts
airlock-mcp render-sql workspaces/team-posts --operation alter
```

The rendered SQL uses `validate_only => TRUE` positionally. Review installed
Airlock documentation before changing it to a mutating call.

## Update The Workbench

Use dry-run first so the command is visible before anything changes.

```bash
airlock-mcp self-update --dry-run
airlock-mcp self-update
```

From a checkout, `self-update` uses `git pull --ff-only` and refuses to run with
uncommitted changes unless `--force` is passed. From an installed package, it
uses `pip install --upgrade` with the configured source.

## Session Rhythm

1. Run `airlock-mcp check <workspace>`.
2. Run `airlock-mcp summary <workspace>` and `airlock-mcp next <workspace>`
   to re-enter the draft.
3. Use `airlock-mcp list-workspaces` when choosing which draft to resume.
4. Ask Codex to read the workspace and continue the draft.
5. Update `decisions.md` before changing `spec.config.json` when a decision
   affects row grain, evidence, business time, access, workflow, or references.
6. Keep `questions.md` for decisions that need the human.
7. Use `review.md` for local check results, Airlock validation results, and the
   next safe action.
8. Export CSV only after the local checker is clean or the exception is
   deliberate and recorded.
