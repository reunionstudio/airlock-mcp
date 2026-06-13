# Guest Access: Shared Contribution

Use this when many people or agents contribute to the same governed dataset.

Good fit:

- posts and feedback
- general ops issues
- shared observations
- public append-only signal streams

Design notes:

- Enable a public append path for normal contribution.
- Consider a public read path only when contributors may safely see the shared
  data.
- Use workflow for moderation, triage, and pushback.
- Use typed routing fields or tags for simple triage; create specialized specs
  only when lifecycle, evidence, validation, or ownership diverges.

Questions to answer:

- Can contributors read all records, or only append?
- Does moderation happen before records become visible?
- What downstream agent or human watches the shared dataset?
