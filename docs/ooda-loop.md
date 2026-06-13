# OODA Loop For Airlock Specs

Airlock specs should support a process loop, not just a table.

Airlock works best when we can identify where information comes in and where
actions go out. Those places might be apps, files, forms, people, emails, calls,
mail, websites, APIs, data feeds, physical events, payment tools, bank apps, or
shared folders. After those examples are clear, call them interfaces: where the
process observes from or acts through.

Start from existing artifacts when they exist: CSV or Excel files, JSON samples,
API docs, schemas, forms, screenshots, PDFs, exports, message examples, or other
defined content people already use. A real sample often reveals identifiers,
timestamps, optional fields, and edge cases faster than chat can.

The reusable `airlock-specs` library can provide starting points, patterns, and
ideas. It is not a guarantee of the current shape of any third-party API,
export, or business object. Current docs and actual samples should override the
library when they conflict.

## Observe

Name the interfaces, evidence, and signals that matter:

- human entries
- agent observations
- screenshots, PDFs, receipts, exports, or source files
- CSV, Excel, JSON, API docs, schemas, forms, or message examples
- source APIs or app objects
- existing Airlock specs or reference data
- downstream system state

## Orient

Turn observations into context that can support a decision:

- one row grain
- durable identifiers
- business timestamps
- typed fields
- validated variants
- attachments
- guest access
- workflow
- references
- expectations
- missing observations or quality gaps

## Decide

Capture the governed choice. A decision spec should identify who or what made
the choice, when it happened, which option was selected, what evidence or
rationale mattered, and what separation of duties applies.

## Act

Model the action that follows the decision: send an email, submit payment,
update a website, change a price, open a ticket, trigger outreach, produce a
filing, request more evidence, or create another governed output. The action
creates new observations and the loop spins again.

Start with one small useful spec, then keep a plan for the next specs that
complete or improve the loop.
