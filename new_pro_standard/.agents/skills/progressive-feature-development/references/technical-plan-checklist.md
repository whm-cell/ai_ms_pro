# Technical Plan Gate Checklist

Use this checklist before implementation when `$progressive-feature-development` is active.

## Classification

- The task is confirmed as non-trivial feature work, architecture-impacting work, or user-requested plan-first work.
- Simple tasks are explicitly allowed to bypass the full workflow.

## Requirements And Scope

- Requirement IDs and Workstream IDs are listed, or `未绑定` is written.
- The plan states what is in scope.
- The plan states `NOT Building` items to prevent scope creep.
- Missing facts that would alter implementation are listed for user confirmation.

## Repo Fit

- Relevant existing implementation patterns have been inspected.
- Interfaces, data flow, module boundaries, or API surfaces are named when they matter.
- Selected skills are listed and each has a clear purpose.
- The plan does not duplicate current-state truth from `working-context`, `status`, or requirements docs.

## Implementation Readiness

- Files or modules likely to change are identified at the right level of detail.
- Tests, smoke checks, or manual verification commands are named.
- Failure modes or risks that could change the implementation are called out.
- The plan can be implemented without a second architecture decision.

## Promotion Decision

- The plan states whether results remain task-local or should be promoted to handoff, status, ADR, changelog, or requirements / traceability.
- If a new reusable pattern is discovered, route it to `$prd-to-project-skills` or the project skill lifecycle template instead of silently embedding it in implementation notes.
