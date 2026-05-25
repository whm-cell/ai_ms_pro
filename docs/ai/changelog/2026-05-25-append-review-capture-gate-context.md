# Append Review Capture Gate Context

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_sample_append.py` 的 no-write report 现在输出当前 append lane 的 `capture_gate`、`capture_gate_detail`、`evidence_needed`、trigger 和 boundary。
- JSON 与文本输出都从当前 collection queue 解析这些字段，而不是依赖候选样本自述。
- 同步测试、tool contract、check registry、roadmap 和 open-items 说明。

## 修复问题

- 剩余 roadmap 缺口主要等待真实事件；真实样本候选到来时，append gate 应直接显示当前真实事件前置条件和 bounded evidence checklist。
- 避免候选只因 schema/source_type 通过而让复核者漏看 capture-gate 边界。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不改变 readiness 或 upgrade decision。
- 不把模板、candidate 或 report 计为 accepted evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_append tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action append-new-pending-slot`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
