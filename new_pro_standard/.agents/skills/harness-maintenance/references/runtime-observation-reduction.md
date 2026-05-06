# Runtime Observation Reduction

Use this reference when editing runtime observation/session behavior, reducer logic, or promotion rules.

## Boundaries

- `.codex/runtime/observations/*.jsonl` and `.codex/runtime/sessions/*.md` are local recovery artifacts.
- Runtime artifacts are not canonical shared truth and do not replace `docs/ai/*` or `docs/requirements/*`.
- Reducer output is a candidate artifact. The main agent decides whether to publish handoff, status, ADR, plan, or requirements updates.

## Reduction Flow

1. Review observations through the repo-local Python runner.
2. Produce a handoff draft only when the material has repo-level reuse value.
3. Promote to `status` or ADR only after review and only when the conclusion is stable beyond one local observation batch.
4. Keep runtime stage drift warning-only unless enough real samples justify blocking.

## Command

```bash
.codex/hooks/run_with_repo_python.sh scripts/reduce_runtime_observations.py
```

Use the Windows PowerShell runner with the same script path on Windows.
