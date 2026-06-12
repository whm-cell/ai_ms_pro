# Code Shape Budget

Use this reference when changing code-shape budgets, code-shape checks, or large harness scripts.

## Rules

- Scope is controlled by `.codex/code_shape.toml`.
- Python file target is `<=300` lines; warning starts above `350`; new files above `500` should be split before landing.
- Function or method target is `<=60` lines; warning starts above `80`; new definitions above `120` should be split.
- Class target is `<=180` lines; warning starts above `250`; new classes above `350` should be split.
- TypeScript and JavaScript file target is `<=350` lines; warning starts above `450`; new files above `800` should be split before landing.
- Stylesheet file target is `<=500` lines; warning starts above `700`; new files above `1200` should be split before landing.
- SQL file target is `<=180` lines; warning starts above `250`; new files above `500` should be split before landing.
- Shell and PowerShell file target is `<=80` lines; warning starts above `120`; new files above `200` should be split before landing.
- Rust file target is `<=350` lines; warning starts above `450`; new files above `800` should be split.
- Test files use a path-specific single-file budget: warning starts above `800`; new files above `1500` should be split. Python test functions and classes still use the global function/class budgets.
- Fixture/cases/mock data files use a path-specific single-file budget: warning starts above `900`; new files above `1800` should be split. This is for data-shaped samples, not hidden business logic.
- Next-style `app/`, `components/`, and `lib/` source trees are in scope, along with `scripts/`, `services/`, `tests/`, `.codex/hooks/`, and skill script directories.
- Existing large files are legacy debt and may warn, but new changes should avoid increasing monoliths.
- Keep code-shape checks separate from AI governance checks.

## Check

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged
```

Use `--all` when changing the checker or reviewing existing technical debt.
