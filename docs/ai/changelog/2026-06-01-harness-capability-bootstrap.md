# Harness Capability Bootstrap

日期：2026-06-01

## 新增功能

- 新增 `runtime-execution-snapshot/v1`，把 runtime session markdown 与 execution snapshot 分离。
- Stop hook 现在会并行写入 `.codex/runtime/execution-snapshots/*.json`。
- SessionStart additional context 现在会带上最近 execution snapshot 的摘要。
- 新增 bounded remote interop report：`verify_remote_trace_interop.py` 与 `check_remote_trace_interop_report.py`。
- 新增 task outcome eval dataset/runner：`task-outcome-evals.jsonl`、`check_task_outcome_eval_dataset.py`、`run_task_outcome_eval_dataset.py`。
- 新增 capability summary：`scripts/summarize_harness_capabilities.py`。

## 修复问题

- 修复了当前 harness 只有 runtime markdown、缺 execution snapshot 的缺口。
- 修复了 local trace / OTLP pilot 只能说明边界、无法输出结构化 remote interop claim level 的缺口。
- 修复了 eval 只有 workflow behavior、没有 task outcome 层的缺口。

## 行为变化

- 当前项目定位从 closeout-only 进一步明确为 `local-first harness control-plane + bounded runtime capability`。
- remote trace 现在可以用 `local-only` / `pilot-remote` / `verified-remote` 三档表述，而不是只靠口头边界说明。
- eval 现在分成两层：workflow behavior 与 task outcome。

## 破坏性变更

- 无。现有 `runtime / governance / verification` 三层结构、WS-01 / WS-02 验证边界和 local-first claim boundary 都保持不变。

## 验证范围

```bash
python3 tests/test_runtime_execution_snapshots.py
python3 tests/test_runtime_stop_hooks.py
python3 tests/test_remote_trace_interop.py
python3 tests/test_task_outcome_eval_dataset.py
python3 tests/test_summarize_harness_capabilities.py
.codex/hooks/run_with_repo_python.sh scripts/check_runtime_execution_snapshots.py
.codex/hooks/run_with_repo_python.sh scripts/check_remote_trace_interop_report.py
.codex/hooks/run_with_repo_python.sh scripts/check_task_outcome_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/run_task_outcome_eval_dataset.py --dry-run
```
