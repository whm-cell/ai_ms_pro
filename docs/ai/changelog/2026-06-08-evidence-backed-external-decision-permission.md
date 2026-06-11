# Evidence-backed External Decision Permission

更新时间：2026-06-08
阶段或版本：stage-00
状态：已确认

## 新增功能

- 为 `external-harness-decision/v1` active records 增加 `default_permission`。
- `scripts/check_external_harness_decisions.py` 现在校验每条 active decision 的 default permission、permitted scope、blocked scope、evidence threshold 和 verification commands。

## 修复问题

- 将“对当前 harness 正向则默认许可”的人工判断转成可审计字段，避免后续会话凭口头授权扩大能力声明。
- 把默认许可限定在 first-party evidence-backed、bounded local/no-effect 小步，避免把外部趋势误写成本地能力完成。

## 行为变化

- 证据充分且对当前 harness 正向时，local/no-effect 的 decision hardening、metadata alignment、comparison-only analysis、advisory contract 和 boundary visibility 改进可默认推进。
- External send、verified remote claim、hosted eval claim、native sandbox claim、MCP/A2A runtime claim、real CI agent workflow creation 和未显式确认的外部副作用仍由 activation gates 阻断。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_external_harness_decisions.py`
- `python3 tests/test_external_harness_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ci_agent_contract.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_remote_trace_interop_report.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_task_outcome_eval_dataset.py`

## 关联文档

- [External Harness Decisions](../standards/external-harness-decisions.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Capability Model](../harness-capability-model.md)
