# 2026-05-10 Pixel Freeze Platformer MVP

## 新增功能

- 新增 `apps/pixel-freeze-platformer/` repo-native 浏览器 MVP，覆盖三关平台闯关、冻结攻击、投掷连锁、敌人/道具、清场出口、评级、HUD、暂停、重开、localStorage 进度和中英本地化种子。
- 新增 `scripts/pixel_freeze_platformer_smoke.py`，覆盖 load -> validate content -> controls -> clear level -> next level -> campaign complete -> locale/reset。
- 新增 REQ-010/011/012/013 与 WS-04，承接 REQDOC-003 / `prd_game.md` 的游戏 MVP 开发范围。

## 修复问题

- `scripts/check_requirements_shape.py` 支持 raw PRD evidence attachment，避免把 `prd_game.md` 误判为第二份 canonical REQDOC。
- 四个新 normalized requirement 补齐标准章节 `## 依赖与前置条件`。

## 行为变化

- WS-04 从“进行中”更新为已完成 repo-native MVP 验证。
- `window.__PIXEL_FREEZE_PLATFORMER_TEST__` 只在 `?smoke=1` 暴露；普通页面不暴露测试 API。

## 破坏性变更

- 无。

## 验证范围

- `node --check apps/pixel-freeze-platformer/main.js`
- `python3 scripts/pixel_freeze_platformer_smoke.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `git diff --check`
