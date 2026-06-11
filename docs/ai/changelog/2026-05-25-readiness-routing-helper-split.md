# Readiness Routing Helper Split

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `scripts/harness_burn_in_readiness_routing.py`，集中维护 readiness item 的 target artifact、target checker、planner command、intake command 和 lane review command 计算。

## 修复问题

- 修复 `scripts/check_harness_burn_in_readiness.py` 在 next collection commands 落地后超过 code-shape 行数预算的问题。

## 行为变化

- 无对外行为变化。`check_harness_burn_in_readiness.py` 的 CLI、markdown、JSON 字段和 no-write ledger 边界保持不变。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_burn_in_readiness`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Harness Open Items](../harness-open-items.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
