# Real Sample Watchlist Sync

更新时间：2026-05-26
阶段或版本：stage-00
状态：已确认

## 新增功能

- 在 `new_pro_standard` 中新增 starter-safe real sample watchlist 模板，只同步 event-driven 观察逻辑，不复制当前项目 gap 计数或 accepted 样本结论。

## 修复问题

- 修正当前项目 real sample watchlist 的快照计数：actionable lane、append lane 和 ready-for-upgrade-discussion 数量与当前脚本输出一致。
- 将 `GAP-WORKFLOW-SIMPLE-SKIP` 从普通 workflow append lane 移到 ready keep-advisory 复核路径，避免已达 2/2 的 gap 被继续当成普通新增样本入口。

## 行为变化

- 新项目模板明确：无法主动验证的真实样本只进入 watchlist；synthetic、placeholder、local-only 和模板草稿不能替代 accepted real evidence。

## 破坏性变更

- 无。

## 验证范围

- `scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- `scripts/check_harness_pending_samples.py`
- `scripts/check_harness_upgrade_decisions.py`

## 关联文档

- [Harness Real Sample Watchlist](../harness-real-sample-watchlist.md)
- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
