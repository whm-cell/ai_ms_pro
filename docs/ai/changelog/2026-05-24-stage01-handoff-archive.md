# 2026-05-24 Stage-01 Handoff Archive

更新时间：2026-05-24
阶段或版本：stage-01 context compression
状态：已确认

## 新增功能

- 将 `docs/ai/handoffs/active/stage-01-pixel-freeze-platformer-mvp.md` 归档到 `docs/ai/handoffs/archive/stage-01-pixel-freeze-platformer-mvp.md`。

## 修复问题

- 清理 `docs/ai/working-context.md` 的默认接力入口，避免已完成的 WS-04 browser MVP handoff 继续占用 active handoff surface。
- 保留 Stage-01 status 与 traceability matrix 作为默认恢复入口；Godot spike、浏览器 MVP 产品化和 WS-04 CI 接入仍在 status / working-context 的活跃队列与风险中承接。

## 行为变化

- `Active Handoff Sources` 现在只列 runtime-stop 与 observation-reducer 两条仍需活跃恢复的 handoff。
- Stage-01 Pixel Freeze Platformer MVP 仍可从 archive 追溯，但不再作为下一次会话默认先读文档。

## 破坏性变更

- 无。该变更只调整 handoff 生命周期与默认上下文入口，不改变 REQ/WS、实现代码、smoke 或 roadmap gap 状态。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_archive_candidates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `python3 tests/test_context_budget.py`
- `git diff --check`
