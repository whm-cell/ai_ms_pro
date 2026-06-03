# Runtime Execution Snapshot

更新时间：2026-06-03
状态：local-first bounded checkpoint

## Purpose

`runtime-execution-snapshot/v1` 是当前 harness 的最小 execution snapshot。

它用于：

- 记录本地任务的执行状态
- 为下一次 resume 提供 bounded checkpoint
- 区分 execution snapshot 与 runtime session markdown
- 表达本地 resume readiness 和阻塞原因

它不用于：

- 替代 canonical governance truth
- 声称已经具备通用 execution engine
- 作为远端恢复、跨机器恢复或 hosted orchestration 证明

## Files

- runtime artifacts: `.codex/runtime/execution-snapshots/*.json`
- sample shape: `docs/ai/standards/runtime-execution-snapshot.sample.json`
- hook producer: `.codex/hooks/stop_runtime_session.py`
- builder helpers: `.codex/hooks/runtime_execution_snapshot.py`
- validator: `scripts/check_runtime_execution_snapshots.py`
- tests: `tests/test_runtime_execution_snapshots.py`, `tests/test_runtime_stop_hooks.py`

## Record Shape

Required fields:

- `schema_version`: `runtime-execution-snapshot/v1`
- `session_id`
- `recorded_at`
- `stage`
- `branch_or_thread`
- `session_type`
- `state`
- `state_reason`
- `state_source`
- `agent`
- `authority`
- `task_summary`
- `requirement_ids`
- `workstream_ids`
- `traceability_source`
- `tool_contracts`
- `claim_boundary`
- `changed_paths`
- `changed_path_count`
- `resume_ready`
- `resume_blockers`
- `last_validation_refs`
- `run_identity`
- `state_transition`
- `resume_context`
- `artifacts`

Allowed `state` values:

- `created`
- `running`
- `paused`
- `resumable`
- `completed`
- `failed`
- `cancelled`

当前 Stop hook 默认写入 `resumable`，除非 payload 明确给出更具体的 state。

Allowed `state_source` values:

- `payload`
- `payload-task-complete`
- `default-stop-hook`

`resume_ready=true` 只表示本地恢复材料足够继续下一次 continuation；
它不表示任务已完成，也不表示 canonical governance docs 已同步。
`resume_blockers` 记录本地 continuation 的阻塞原因，例如 terminal state、
failed state、缺少 task summary 或缺少 transcript reference。

## Boundary

- execution snapshot 是 runtime artifact，不是 handoff/status/ADR/requirements。
- snapshot 记录的是“下一次本地 continuation 需要的最小状态”，不是完整 transcript。
- `task_summary` 必须保持 bounded；不得把 raw prompt、完整 transcript、secret 或 `.codex/runtime/*` 路径提升到共享治理层。
- `artifacts` 不得包含 raw local transcript path、`.codex/runtime/*` 原始路径或用户主目录路径；需要使用 redacted path 或 bounded repo-relative path。
- `tool_contracts` 只记录当前本地执行面引用的 contract 名称，不声明 remote interoperability。

## Validation

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_runtime_execution_snapshots.py
python3 tests/test_runtime_execution_snapshots.py
python3 tests/test_runtime_stop_hooks.py
```
