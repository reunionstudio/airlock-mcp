# Spec Type: Reconciliation

A reconciliation spec compares two or more systems, datasets, or expectations
and records the business difference that needs attention.

Good fit:

- commerce listing gaps
- payment versus invoice matching
- ad spend versus campaign records
- inventory or order discrepancies

Design notes:

- Make the row grain the discrepancy, match group, or reconciliation finding.
- Preserve stable keys from every compared system.
- Use typed fields for match status, amounts, dates, and source identifiers.
- Use a validated `variant` for optional comparison detail.
- Use workflow when a human must resolve or accept the finding.
