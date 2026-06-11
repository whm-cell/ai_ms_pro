# Intake Upgrade Review Summary

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- `scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary` 现在输出独立的 `Upgrade Decision Review` 表。
- 该表把 ready gap 直接绑定到 `check_harness_upgrade_decisions.py`，避免 upgrade-decision 复核命令只隐含在 Targets 表里。

## 修复问题

- 修复 intake bundle 契约声称 summary 显示 upgrade-decision review command，但 compact summary 缺少专门复核区块的展示漂移。

## 行为变化

- 只有包含 `review-upgrade-decision` entry 的 summary 会显示 `Upgrade Decision Review`。
- 默认 actionable sample intake summary 不会新增该区块。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_intake_bundle.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
