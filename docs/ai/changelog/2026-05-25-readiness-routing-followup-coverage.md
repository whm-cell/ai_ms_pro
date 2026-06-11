# Readiness Routing Follow-up Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_sample_followup_coverage.py` 现在会发现 `scripts/harness_burn_in_readiness_routing.py`。
- `scripts/change_triggered_harness_sample_rules.py` 现在把 readiness routing helper 纳入 `harness-sample-gap-evidence` follow-up pattern。

## 修复问题

- 修复 readiness next-collection routing helper 被拆出后，后续改 target artifact、target checker、planner、intake 或 lane review command 时可能不触发完整 sample-gap follow-up 命令包的问题。

## 行为变化

- coverage audit 的 checked path count 从 58 增加到 59。
- 对外 CLI、JSON、markdown readiness 输出不变；本变更只防 change-triggered follow-up 漂移。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_followup_coverage`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py --json`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
