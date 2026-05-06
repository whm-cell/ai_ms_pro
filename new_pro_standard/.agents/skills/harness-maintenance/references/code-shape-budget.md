# Code Shape Budget

Use this reference when changing code-shape budgets, code-shape checks, or large harness scripts.

## Rules

- Scope is controlled by `.codex/code_shape.toml`.
- Python file target is `<=300` lines; warning starts above `350`; new files above `500` should be split before landing.
- Function or method target is `<=60` lines; warning starts above `80`; new definitions above `120` should be split.
- Class target is `<=180` lines; warning starts above `250`; new classes above `350` should be split.
- Existing large files are legacy debt and may warn, but new changes should avoid increasing monoliths.
- Keep code-shape checks separate from AI governance checks.

## Check

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged
```

Use `--all` when changing the checker or reviewing existing technical debt.
