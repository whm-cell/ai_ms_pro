# Pending Review Card Capture Context

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_pending_samples.py --review-cards` 的每张 pending card 现在输出当前 queue 的 ledger action、capture gate、gate detail、trigger 和 evidence checklist。
- JSON `review_cards` 同步携带这些字段，复用 `plan_harness_sample_collection.py` 的当前 queue context。

## 修复问题

- 避免 placeholder pending card 只显示 checker、readiness 和 blockers，却不显示真实事件前置条件。
- 让复核者在 pending card 中直接看到 `replace-placeholder-after-real-event` 与所需 evidence 字段。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不改变 readiness 或 upgrade decision。
- 不把 pending card 或模板计为 accepted evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests/test_harness_pending_samples.py tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --review-cards`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
