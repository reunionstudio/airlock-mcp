# Spec Type: Commitment

A commitment spec records a decision or promise the business intends to honor or
send downstream.

Good fit:

- approved budget requests
- payment commitments
- outbound product updates
- accepted offers or invitations

Design notes:

- Distinguish the observed inputs from the committed output.
- Use workflow for approval and pushback.
- Use references to link back to source observations, requests, projects, or
  counterparties.
- Use expectations when commitments must happen in order or by a due date.

Avoid:

- copying every upstream observation field into the commitment
- hiding approval state in payload columns instead of Airlock workflow
