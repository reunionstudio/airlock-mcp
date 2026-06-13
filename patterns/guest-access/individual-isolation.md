# Guest Access: Individual Isolation

Use this when each person or agent should submit into an isolated path and
should not see another submitter's files.

Good fit:

- reimbursements by employee
- private intake drafts
- delegated assistant work for one principal
- sensitive observations where cross-user visibility is risky

Design notes:

- Enable isolated directories.
- Give each guest role the narrowest useful access level.
- Keep manager, reviewer, or owner visibility in Airlock roles rather than
  payload columns.
- Use delegation when an agent acts for a specific person. Do not impersonate
  the human by reusing their role assignment.

Questions to answer:

- Who owns the submitted record after review?
- Does a reviewer need managed-role visibility across isolated submitters?
- Can the submitter read returned drafts, approved files, or only their own
  working path?
