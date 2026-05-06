# PR Template Minimum

Use this reference when creating or reviewing a PR template for multi-person or multi-agent development.

## Required Fields

```markdown
## Requirement / Workstream

- Requirement IDs:
- Workstream IDs:

## Touch Set

- Expected changed areas:
- High-risk files:

## Parallel PR Conflict Check

- Checked open PR overlap:
- Overlapping PRs:
- Coordination action:

## Verification

- Commands run:
- Screenshots / smoke evidence:

## Governance Impact

- Docs updated:
- ADR / status / traceability impact:
```

## Review Guidance

- Missing `REQ/WS` is acceptable only when marked `未绑定`; do not invent mappings.
- High-risk file changes should identify an owner or reviewer.
- Overlap checks should be explicit, even when the result is `none`.
- If merge queue is enabled, required workflows should run on `merge_group`.
- If the PR changes governance or requirements truth, the PR body should name the updated truth surface.
