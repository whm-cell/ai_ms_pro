# Governance Checklist

Use this checklist when `$repo-governed-coding` is active for a non-trivial change.

## Read First

- `AGENTS.md`
- `docs/ai/index.md`
- `docs/ai/working-context.md`
- `docs/requirements/index.md` when the task is requirement-driven
- `docs/requirements/traceability-matrix.md` when the task already carries `REQ/WS` bindings
- relevant active `handoff`, `status`, or `ADR` when the change touches current stage truth

## Behavioral Snapshot

- Assumptions: state what is known and what is being assumed.
- Scope Boundary: state what will be changed and what will be left alone.
- Success Criteria: state what observable result proves completion.
- Verification Plan: list the checks, tests, or smoke commands to run.

## Document Impact Check

- Update or create `handoff` when a subtask completes, pauses, or changes implementation in a way the next agent must understand.
- Update or create `status` when a stage ends, several handoffs need compression, or risks materially change.
- Update or create `changelog` when a stage is ready for integration, behavior changed externally, or release-facing notes are needed.
- Update or create `ADR` when a decision remains relevant beyond the current stage.
- Always update `docs/ai/index.md` after changing `plan`, `handoff`, `status`, `changelog`, or `ADR`.

## Traceability

- Carry `Requirement IDs` and `Workstream IDs` in `handoff`, `status`, runtime session files, and reducer output when known.
- Write `未绑定` when the mapping is not known.
- Keep the canonical mapping in `docs/requirements/traceability-matrix.md`.
- Update both AI-side artifacts and requirements-side mapping when a task becomes newly bound.
- Use `$requirements-traceability-maintenance` for PRD import, `REQDOC / REQ / WS` edits, matrix changes, or technical assumption checks.

## Primary Truth Surface

- Primary truth surfaces: `working-context`, active `handoff`, `status`, `ADR`, normalized requirements, and `traceability-matrix.md`.
- Projection surfaces: `plan` and workstream docs.
- Do not write fast-changing completion state, latest validation evidence, or duplicate status summaries into projection surfaces.

## Verification Finish Line

- Run `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`.
- Run `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged` when implementation or harness code is staged.
- Run any task-specific smoke or test commands needed for the request.
- Confirm `docs/ai/working-context.md` sync metadata reflects changed active `handoff` or `status` files.
- Use `$harness-maintenance` `references/verification-commands.md` when selecting specialized harness checks.
