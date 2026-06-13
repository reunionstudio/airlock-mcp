# OODA Loop For Airlock Specs

Airlock specs should support a process loop, not just a table.

Airlock works best when we can identify where information comes in and where
actions go out. Those places might be apps, files, forms, people, emails, calls,
mail, websites, APIs, data feeds, physical events, payment tools, bank apps, or
shared folders. After those examples are clear, call them interfaces: where the
process observes from or acts through.

## Observe

Name the interfaces, evidence, and signals that matter:

- human entries
- agent observations
- screenshots, PDFs, receipts, exports, or source files
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
