# Guest Access: Role Isolation

Use this when groups such as departments, store locations, teams, or external
partners need separate contribution areas.

Good fit:

- location-level operations logs
- department budget packets
- partner submissions
- team-owned weekly reports

Design notes:

- Model the group as an Airlock role.
- Use `managed_by_role` only when a non-admin business role should manage or
  include subordinate roles.
- Keep role membership and assignment outside the submitted payload.
- Prefer reference specs for shared project, location, department, or partner
  catalogs.

Questions to answer:

- Are records owned by the role, by individual contributors, or by both?
- Does a parent role need read or review visibility?
- Do role groups share a public read path after approval?
