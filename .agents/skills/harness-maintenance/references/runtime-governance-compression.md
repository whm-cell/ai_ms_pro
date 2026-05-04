# Runtime Governance Compression

Use this reference when changing session promotion, handoff compression, archive candidate handling, or the boundary between local runtime material and shared governance truth.

## Runtime Boundary

- `.codex/runtime/sessions/*.md` and `.codex/runtime/observations/*.jsonl` are local recovery material.
- Runtime files do not replace `docs/ai/*` or `docs/requirements/*`.
- Hooks may write runtime material, but they must not silently rewrite canonical governance documents.
- The main agent owns canonical writes to `working-context`, `handoff`, `status`, `changelog`, `adr`, `plan`, and requirements documents.

## Promote To Handoff When

- A subtask completed and the next agent needs the result.
- A task is paused and must be resumed later.
- Implementation changed in a way future work must understand.
- The session established durable valid or invalid approaches.
- The result should affect `status`, `adr`, `plan`, or requirements tracking.

## Do Not Promote When

- The material is local scratch work.
- The note is personal prompt experimentation.
- Exploration produced no reusable repo-level conclusion.
- The content is already captured in a more authoritative status, ADR, or requirement document.

## Compression Lifecycle

Use this lifecycle:

`handoff -> status -> changelog / ADR -> archive old handoffs`

- Keep active handoffs for live resume value.
- Compress repeated or completed handoff detail into `status` or ADR.
- Move absorbed handoffs to `docs/ai/handoffs/archive/`.
- Keep `docs/ai/index.md` and `docs/ai/working-context.md` aligned after active surface changes.

## Archive Candidate Check

- Run `scripts/check_archive_candidates.py` through the repo-local Python runner when active handoffs reach budget or before stage compression.
- Treat the script as warning-only. It proposes candidates; it does not decide what moves.
- Archive only after confirming the handoff has been absorbed by status, ADR, changelog, plan, or requirements truth.
