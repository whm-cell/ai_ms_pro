# Readiness Gap ID Maps

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_burn_in_readiness.py` 的 report 现在输出 `readiness_gap_ids`。
- 同一 report 也输出 `capture_gate_gap_ids`，把每个真实事件门槛对应的 gap id 直接放在 summary / JSON 层。

## 修复问题

- 修复 readiness summary 只有 readiness / capture-gate counts，人工交接时仍要扫描完整 item 表才能知道具体 gap id 的问题。

## 行为变化

- Markdown text 输出会在 counts 后显示 readiness gap ids 与 capture gate gap ids。
- JSON 输出同步携带同名字段。
- 该变更只改善审计与采集交接；不写 ledger、不生成样本、不接受 evidence、不升级 blocking。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_burn_in_readiness tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
