# Spec Type: Observation

An observation spec records something a person, agent, export, browser capture,
or API observed.

Use typed columns for:

- observed object id
- source system or URL
- observed or captured timestamp
- status, amount, category, or score used in decisions
- capture method

Use attachments for screenshots, PDFs, exports, receipts, or other evidence.
Use a validated `variant` for optional source payload context.

Avoid:

- using Airlock load time as the event timestamp
- placing raw attachment bytes in payload fields
- mixing observations and commitments in one row unless `record_type` is an
  intentional design choice
