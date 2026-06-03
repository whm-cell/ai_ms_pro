# Harness Capability State Evidence Aggregates

日期：2026-06-03

## 新增功能

- `runtime-execution-snapshot/v1` 新增轻量 local execution state model：`state_source`、`resume_ready`、`resume_blockers`、`last_validation_refs`、`run_identity`、`state_transition` 和 `resume_context`。
- `trace-remote-interop-report/v1` 新增结构化 evidence 面：`export_attempt`、`endpoint_evidence`、`claim_evidence` 和 `withheld_payloads`。
- `task-outcome-evals.jsonl` 新增 4 类 benchmark slice：`resume-durability`、`trace-interop-boundary`、`warning-review-signal`、`overreach-prevention`。
- `run_task_outcome_eval_dataset.py` 新增 aggregate output：`pass_count`、`warn_count`、`review_required_count`、`fail_count`、`not_run_count`、`blocked_by_resume`、`blocked_by_guardrail`。
- `summarize_harness_capabilities.py` 现在汇总 resume readiness、blocked resume、latest blockers、local-only / pilot / verified interop count、endpoint failure mode、task outcome breakdown 和 blocked reason。

## 修复问题

- 修复 execution snapshot 只能表达 latest state、不能机器可读地区分 resume-ready 与 blocked-resume 的缺口。
- 修复 remote interop report 只有顶层 claim 字段、缺少 export / endpoint / operator-review / withheld-payload evidence 的缺口。
- 修复 task outcome eval 结果缺少 aggregate counts 和 blocked reason summary 的缺口。

## 行为变化

- 新 Stop snapshot 会写入结构化 state / resume context；旧 runtime artifact 仍可被 checker 容忍。
- `verified-remote` report 需要显式 operator review evidence；local capture 或普通 pilot 不会自动升级。
- task outcome execute-mode JSON 会输出 aggregate counts；dry-run 仍保持 local-only，不执行 checks。

## 破坏性变更

- 无。新增字段向后兼容，现有 runtime artifact、top-level interop report 字段和 eval runner CLI 保持可读。

## 边界保持

- 不引入 hosted orchestration、多租户 runtime、native sandbox provider、OpenAI hosted trace、MCP、A2A 或长期 external collector。
- `.codex/runtime/*` 仍是本地恢复材料，不是 canonical shared truth。
- `verified-remote` 仍需要成功 bounded probe、非 local capture endpoint scope 和显式 operator review evidence。
- task outcome eval 仍是 deterministic repo-local runner，不是模型质量评测服务。

## 验证范围

```bash
python3 tests/test_runtime_execution_snapshots.py
python3 tests/test_runtime_stop_hooks.py
.codex/hooks/run_with_repo_python.sh scripts/check_runtime_execution_snapshots.py
python3 tests/test_remote_trace_interop.py
.codex/hooks/run_with_repo_python.sh scripts/check_remote_trace_interop_report.py
python3 tests/test_task_outcome_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/check_task_outcome_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/run_task_outcome_eval_dataset.py --dry-run
python3 tests/test_summarize_harness_capabilities.py
.codex/hooks/run_with_repo_python.sh scripts/summarize_harness_capabilities.py
.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all
git diff --check
```
