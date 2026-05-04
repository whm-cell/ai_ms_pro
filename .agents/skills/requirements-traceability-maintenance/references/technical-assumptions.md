# Technical Assumptions

Use this reference when a PRD or long requirement document contains technology stack, architecture, integration, deployment, performance, or security claims.

## Status Labels

- `accepted`: supported by an ADR, status decision, implementation fact, verified prototype, or explicit user decision.
- `proposed`: plausible but not yet validated; safe to discuss in a technical plan but not to treat as committed.
- `deferred`: intentionally postponed because the current stage does not need the decision.
- `rejected`: explicitly ruled out by user decision, ADR, evidence, or constraint.
- `unknown`: source text is unclear or incomplete.

## Required Fields

- Source: PRD section, REQDOC, or user statement.
- Claim: the exact stack or technical assertion being classified.
- Status: one of the labels above.
- Verification Method: ADR, spike, smoke, test, benchmark, manual review, or pending confirmation.
- Owner Surface: requirement doc, ADR, status, check script, or project skill candidate.

## Classification Rules

- PRD text can propose a stack; it does not automatically adopt architecture.
- A technology choice that changes long-lived architecture belongs in ADR or status after validation.
- A repeatable implementation method can become a project skill only after it is stable and does not contain current requirement truth.
- If evidence is missing, keep the claim as `proposed`, `deferred`, or `unknown` and list what must be verified.
