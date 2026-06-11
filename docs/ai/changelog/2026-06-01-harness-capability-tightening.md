# Harness Capability Tightening

日期：2026-06-01

## 新增功能

- `verify_remote_trace_interop.py` 在 `--output` 时会自动创建父目录，避免首次 probe 写 runtime artifact 时因目录不存在而失败。
- `run_task_outcome_eval_dataset.py` 在 `--output` 时会自动创建父目录，并在每个 check 结果里记录 `observed_signal`。
- `summarize_harness_capabilities.py` 改为优先按 artifact 内的 `recorded_at` 选择 latest 结果，只有缺少时间戳时才回退到文件 mtime；输出里同时明确 summary boundary 仍是 `artifact-backed-local-runtime`。

## 修复问题

- 修复了首次 `--output` 写入 runtime artifact 需要人工先建目录的首用摩擦。
- 修复了 task outcome eval 会把 exit code 为 `0` 的 warning-bearing check 计为 `pass` 的语义过宽问题。
- 修复了 capability summary 受文件名排序影响、可能把较旧 artifact 当作 latest 的问题。

## 行为变化

- 不改变 `runtime / governance / verification` 三层边界。
- task outcome deterministic grader 现在会把 `WARN:`、`Warnings:`、`review-required` 一类软信号反映到 `warn` / `review-required`，不再把这类命令输出记成 clean pass。
- 不把 bounded remote interop 升格成 verified remote，也不把 task outcome eval 升格成外部模型质量评测。
- 当前 summary 仍然依赖 runtime artifacts 已被落盘，只是 latest 选择和边界表述更准确。

## 破坏性变更

- 无。CLI 更顺、结果语义更严，但不改三层 harness 边界与 claim boundary。

## 验证范围

```bash
python3 tests/test_remote_trace_interop.py
python3 tests/test_task_outcome_eval_dataset.py
python3 tests/test_summarize_harness_capabilities.py
.codex/hooks/run_with_repo_python.sh scripts/check_remote_trace_interop_report.py
.codex/hooks/run_with_repo_python.sh scripts/check_task_outcome_eval_dataset.py
python3 scripts/run_task_outcome_eval_dataset.py --json --output .codex/runtime/task-outcome-evals/manual-tightening.json
python3 scripts/summarize_harness_capabilities.py --json
```
