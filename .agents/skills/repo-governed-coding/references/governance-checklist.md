# Governance Checklist

Use this checklist when `$repo-governed-coding` is active for a non-trivial change.

## Read First

- `AGENTS.md`
- `docs/ai/index.md`
- `docs/ai/working-context.md`
- `docs/requirements/index.md` when the task is requirement-driven
- `docs/requirements/traceability-matrix.md` when the task already carries `REQ/WS` bindings

## Behavioral Snapshot

- Assumptions: state what is known and what is being assumed.
- Scope Boundary: state what will be changed and what will be left alone.
- Success Criteria: state what observable result proves completion.
- Verification Plan: list the checks, tests, or smoke commands to run.

## Document Impact Check

- Update or create `handoff` when:
  - a subtask is completed
  - a task is paused but should be resumed later
  - implementation changed in a way the next agent must understand
- Update or create `status` when:
  - a stage ends
  - several handoffs have accumulated and need compression
  - current risks or blockers materially changed
- Update or create `changelog` when:
  - a stage is ready for integration
  - externally visible behavior changed
  - release-facing notes are needed
- Update or create `adr` when:
  - a decision remains relevant beyond the current stage
  - architecture, API shape, storage strategy, deployment strategy, or major constraints changed
- Always update `docs/ai/index.md` after changing `plan`, `handoff`, `status`, `changelog`, or `adr`.

## Traceability

- Carry `Requirement IDs` and `Workstream IDs` in `handoff`, `status`, runtime session files, and reducer output when known.
- Write `未绑定` when the mapping is not known.
- Keep the canonical mapping in `docs/requirements/traceability-matrix.md`.
- Update both the AI-side artifact and the requirements-side mapping in the same change when a task becomes newly bound.

## Primary Truth Surface

- Primary truth surfaces:
  - `docs/ai/working-context.md`
  - active `handoff`
  - `status`
  - `adr`
  - `docs/requirements/normalized/*.md`
  - `docs/requirements/traceability-matrix.md`
- Projection surfaces:
  - `docs/ai/plan.md`
  - `docs/requirements/workstreams/*.md`
- Do not write fast-changing completion state, latest validation evidence, or duplicate status summaries into projection surfaces.

## Verification Finish Line

- Run `python3 scripts/check_ai_governance.py`.
- Run `python3 scripts/check_code_shape.py --staged` when implementation or harness code is staged.
- Run any task-specific smoke or test commands needed for the request.
- Confirm that new active docs are present in `docs/ai/index.md`.
- Confirm that `docs/ai/working-context.md` sync metadata reflects new active `handoff` or `status` files when they changed.
