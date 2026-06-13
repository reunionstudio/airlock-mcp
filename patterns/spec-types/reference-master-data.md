# Spec Type: Reference Or Master Data

A reference/master-data spec provides controlled data that other specs validate
against or read from.

Good fit:

- projects
- departments
- vendors
- employees
- locations
- chart-of-accounts segments

Design notes:

- Use stable keys and readable aliases.
- Keep lifecycle simple unless changes require review.
- Use references from transactional specs into these keys.
- Consider a read-only reference spec over a materialized table for high-read
  agent workflows.
