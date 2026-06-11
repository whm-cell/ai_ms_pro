# Harness VNext Subagent Slices

更新时间：2026-06-06
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `ci-agent-contract/v1` 样例、标准文档、validator 和测试，用于描述 PR-only / read-only advisory CI-agent boundary。
- 新增 `run_sandboxed_command.py` 本地执行 policy wrapper、标准文档和测试，保留 bounded runtime tool-output artifacts。
- 新增 planner / executor / reviewer trace / provenance / eval sample shape。

## 修复问题

- remote trace interop 现在拒绝把 localhost / loopback evidence 升级为 `verified-remote`。

## 行为变化

- tool contracts、check registry、capability model、working context、verification references 和 changed-file follow-up rules 已登记五个反哺点的 bounded 边界。
- cross-task resume 仍只作为真实样本采集队列项；没有制造 accepted cross-task sample。

## 破坏性变更

- 无。

## 验证范围

- `check_ci_agent_contract.py`、`test_ci_agent_contract.py`
- `run_sandboxed_command.py -- python3 --version`、`test_execution_sandbox_wrapper.py`
- `check_remote_trace_interop_report.py`、`test_remote_trace_interop.py`
- `check_agent_trace_schema.py`、`check_agent_run_provenance.py`、`check_agent_eval_dataset.py`、`run_agent_eval_dataset.py --dry-run`
- `check_tool_contracts.py`、`test_tool_contracts.py`、`test_change_triggered_followups.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Capability Model](../harness-capability-model.md)
