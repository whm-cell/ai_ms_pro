# 2026-05-07 REQDOC-003 WS-03 First Slice

更新时间：2026-05-07
阶段或版本：stage-00
状态：已确认

## 新增功能

- 将 REQDOC-003 Godot 2D 单屏平台闯关游戏 PRD 完成首轮标准化，新增 REQ-007、REQ-008、REQ-009 与 WS-03。
- 新增 `apps/godot-platformer-slice/`，作为 repo-native 浏览器垂直切片验证核心玩法闭环。
- 新增 `scripts/godot_platformer_slice_smoke.py`，验证 load -> freeze -> throw -> unlock exit -> complete -> reset。
- 将 Godot Platformer first slice smoke 接入 `.github/workflows/governance-and-smoke.yml` 的 smoke job。

## 修复问题

- 修复 REQDOC-003 source 文件名未携带 `REQDOC-003` 导致 governance catalog 无法按文件名识别 source id 的问题。
- 将新增 smoke 的 Playwright session 名缩短，避免本地 CLI socket 路径冲突。

## 行为变化

- REQDOC-003 不再是 source-only 未绑定状态。
- Godot engine、GUT、导出 preset、素材和本地化管线仍保持 proposed / 待确认；本轮不创建完整 Godot 工程。
- Root repo 继续保持 harness 研究仓定位，业务样本限定为可 smoke 的薄切片。

## 破坏性变更

- 无。

## 验证范围

- `python3 scripts/godot_platformer_slice_smoke.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `git diff --check`

## 关联文档

- [REQDOC-003 Godot 2D 闯关游戏 PRD source](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/source/REQDOC-003-godot-platformer-prd.md)
- [WS-03 Godot Platformer First Slice](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams/WS-03-godot-platformer-first-slice.md)
- [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
