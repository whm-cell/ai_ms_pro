# External Harness Decision Gates

更新时间：2026-06-07
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `external-harness-decision/v1` 标准和 active decision ledger。
- 新增 `scripts/check_external_harness_decisions.py` 和单元测试，用于审计 remote trace pilot、external eval/sandbox、MCP/A2A、CI agent workflow 四类外部 harness 决策。
- 新增 tool contract 与 check registry 记录，使该决策账本进入常规 harness verification surface。
- 将 decision ledger 升级为 source-backed：每条 active decision 必须记录一手 source evidence、positive signal 和 local upgrade scope。
- `run_sandboxed_command.py` 报告现在直接显示 `native sandbox: false`，避免外部 native sandbox 趋势下误读本地 wrapper。

## 修复问题

- 将先前只存在于人工决策列表中的四个外部 harness 方向转为可复核记录，避免后续会话凭口头判断扩大能力声明。
- 把“是否正向提升”的互联网核验结果落在本地可验证字段上；不把 release/doc 趋势误升级为本地 hosted / remote / native runtime 能力。

## 决策结果

- Remote trace pilot：当前不主动发送外部 payload；只在显式 endpoint、`--send` 确认和 operator review 后执行一次 bounded probe。
- External eval / sandbox：先做 comparison-only，不安装新依赖、不声明 native sandbox。
- MCP / A2A：当前只做 contract registry / provenance 元数据，不进入 runtime prototype。
- CI agent workflow：继续保持 advisory contract，不创建真实 GitHub agent workflow。

## 行为变化

- 先前需要人工判断的四个方向现在有可机器复核的 bounded decision record。
- 外部趋势为 positive signal 时，只升级 source-backed 决策质量、comparison-only 口径、contract metadata discipline 或 boundary visibility。
- 该变更不升级 blocking，不声明 hosted trace/eval、verified remote、native sandbox、MCP/A2A runtime 或 CI agent runtime completion。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_external_harness_decisions.py`
- `python3 tests/test_external_harness_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/run_sandboxed_command.py -- python3 --version`
- `python3 -m unittest tests.test_execution_sandbox_wrapper`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `python3 tests/test_tool_contracts.py`

## 关联文档

- [External Harness Decisions](../standards/external-harness-decisions.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Capability Model](../harness-capability-model.md)
