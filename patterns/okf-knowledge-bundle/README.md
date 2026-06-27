# Starter Pattern: OKF Knowledge Bundle

Use `okf-knowledge-bundle` when the team wants governed Markdown knowledge for
people and agents to use as accepted business context.

This pattern is for Airlock's `okf_knowledge_bundle` payload adapter. It is
inspired by Google's Open Knowledge Format, but Airlock applies a narrower
profile so accepted bundles can become governed context instead of loose wiki
content.

## Use When

- Policies, runbooks, metrics, definitions, decisions, investigations, or
  operating context need a governed place to land.
- Agents need business context that can be accepted, audited, and queried from
  Snowflake.
- The team has useful Markdown knowledge, but needs Airlock workflow, PDP,
  Expectations, evidence, and acceptance boundaries around it.

## Bundle Shape

- Bundle source is a directory or `.zip` archive of UTF-8 Markdown files.
- Root `index.md` may contain bundle frontmatter such as `okf_version`,
  `bundle_name`, `bundle_version`, `domain`, `owner`, and `purpose`.
- Every non-reserved Markdown file is a concept document with YAML frontmatter.
- Concept documents require `type`.
- Recommended concept fields are `title`, `description`, `resource`, `tags`,
  `timestamp`, and `source_links`.
- `index.md` and `log.md` are reserved at every hierarchy level.

## Airlock Contract

The spec must declare:

```json
{
  "core_config": {
    "payload_adapter": "okf_knowledge_bundle"
  }
}
```

Installed Airlock provides two admin procedures for this adapter:

- `airlock.admin.load_okf_bundle(...)`: load a locally validated bundle into
  Airlock stage storage and `FILE_MANIFEST`, then project concept metadata.
- `airlock.admin.sync_okf_bundle_metadata(...)`: project parsed concept
  metadata for an existing active manifest row.

Use `validate_only => TRUE` before writing. Treat accepted context as
authoritative only from:

```sql
AIRLOCK_DATA.ACTIVE.V_OKF_CONCEPT_METADATA
```

Draft and rejected bundles are not authoritative agent context.

## Local Workbench Notes

`airlock-mcp check` validates the Airlock spec draft and sample metadata. It
does not validate a Markdown bundle. Bundle validation currently lives in the
Airlock source repo's `airlock.okf_knowledge_bundle.validate_okf_bundle`
helper and the installed Airlock OKF procedures.
