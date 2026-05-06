# Requirements Traceability Checklist

Use this checklist when changing PRD imports, normalized requirements, workstreams, or the traceability matrix.

## Source To Requirement

- Keep the source document in `docs/requirements/source/`.
- Preserve source identifiers and enough source location detail for later audit.
- Split large PRD text into normalized `REQ-*` entries only when each entry has a clear acceptance boundary.
- Do not merge unrelated acceptance criteria into one requirement just to reduce document count.

## Requirement To Workstream

- Bind each implementation workstream to one or more normalized requirements.
- Keep `WS-*` docs implementation-sized and projection-oriented.
- Avoid writing current completion status or latest test evidence into `WS-*`; put those in `working-context`, `handoff`, `status`, or the matrix.

## Matrix Integrity

- Update `docs/requirements/traceability-matrix.md` in the same change as new or changed `REQDOC`, `REQ`, or `WS` files.
- Include known `Requirement IDs` and `Workstream IDs` in AI-side artifacts when available.
- Write `未绑定` instead of inventing IDs.
- Treat a matrix mismatch as a governance defect, not as a documentation polish issue.

## Verification Links

- Each active requirement should have a verification method, even if the first value is `manual review`, `smoke`, or `pending`.
- Link automation, smoke tests, review gates, ADRs, or status notes when they exist.
- If the verification method is unknown, state that explicitly and keep it out of accepted architecture facts.

## Skill Boundary

- Keep requirement truth, acceptance criteria, and current implementation status out of skills.
- Put only stable reusable execution patterns into project skills.
- If a skill suggestion conflicts with a current requirement, the requirement wins until an explicit requirement or ADR update changes it.
