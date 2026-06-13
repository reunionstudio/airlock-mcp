# Starter Pattern: Posts

Use `posts` when the team does not yet know which larger Airlock spec to build.
It creates a small governed feedback loop:

- a person or agent submits a post, request, observation, or response
- optional structured details are captured in a validated `variant`
- other people or agents can review the feed and decide what spec to build next

This pattern is intentionally humble. It gives the organization a safe place to
observe demand before designing a bigger workflow.

## When To Use

- You are starting from fuzzy process needs.
- You want feedback from users inside Snowflake.
- You want agents to ask for, respond to, or triage requests.
- You need a governed signal stream before committing to specialized specs.

## Adapt Carefully

Keep the core small:

- one row is one post
- `post_id` is stable and retry-safe
- `body` is the human-readable signal
- `tags` supports light routing
- `details` holds optional structured context

Create separate specs later when posts become reimbursements, budget requests,
project issues, support tickets, or outbound commitments with different
validation, evidence, workflow, or ownership.
