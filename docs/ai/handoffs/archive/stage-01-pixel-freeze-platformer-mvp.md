# Stage-01 Pixel Freeze Platformer MVP Handoff

更新时间：2026-05-10
阶段：stage-01
状态：完成

## 需求与工作流标识

- Requirement IDs：REQ-010, REQ-011, REQ-012, REQ-013
- Workstream IDs：WS-04

## 本任务目标

- 依照 REQDOC-003 / `prd_game.md` 和仓库 harness，继续完成 2D 平台闯关游戏的 repo-native 可玩 MVP。
- 不把完整 Godot 工程、正式素材、音频、移动端或发布流水线混入当前 MVP。

## 已完成内容

- 新增 `apps/pixel-freeze-platformer/`：三关房间式平台闯关、移动/跳跃、冻结攻击、投掷连锁、敌人/道具、清场出口、评级、HUD、暂停、重开、localStorage 进度和中英本地化种子。
- 新增 `scripts/pixel_freeze_platformer_smoke.py`：验证 load -> validate content -> controls -> clear level -> next level -> campaign complete -> locale/reset。
- 补齐 REQ-010/011/012/013、WS-04、traceability matrix、REQDOC-003 metadata、Stage-01 status、working-context、index 和 changelog。
- `window.__PIXEL_FREEZE_PLATFORMER_TEST__` 只在 `?smoke=1` 下暴露，普通页面不暴露测试 API。

## 修改文件

- `apps/pixel-freeze-platformer/*`
- `scripts/pixel_freeze_platformer_smoke.py`
- `scripts/check_requirements_shape.py`
- `tests/test_requirements_shape.py`
- `docs/requirements/source/prd_game.md`
- `docs/requirements/source/REQDOC-003-godot-platformer-prd.md`
- `docs/requirements/normalized/REQ-010-platformer-playable-mvp-baseline.md`
- `docs/requirements/normalized/REQ-011-platformer-core-systems-and-levels.md`
- `docs/requirements/normalized/REQ-012-platformer-ui-save-localization.md`
- `docs/requirements/normalized/REQ-013-platformer-production-boundary.md`
- `docs/requirements/workstreams/WS-04-pixel-freeze-platformer-mvp.md`
- `docs/requirements/index.md`
- `docs/requirements/traceability-matrix.md`
- `docs/ai/status/stage-01-game-mvp-development.md`
- `docs/ai/working-context.md`
- `docs/ai/index.md`
- `docs/ai/plan.md`
- `docs/ai/changelog/2026-05-10-pixel-freeze-platformer-mvp.md`

## 关键实现决策

- 当前阶段采纳 browser MVP 作为 harness 验证样本；Godot 仍是后续 engine spike 的 proposed 技术假设。
- 关卡数据先放在 JS module，避免无构建静态应用在本地文件读取上的限制。
- smoke 验证使用 `?smoke=1` 下的测试 API，同时增加固定步进输入模拟，覆盖移动、跳跃和攻击。
- 素材仅使用 canvas 绘制的原创占位视觉，不纳入 AI 图像、音频或最终商用资源。

## 当前未完成项

- Godot 工程、GUT、导出 preset、正式素材、音频、移动端触控、Boss 和发布流水线均未进入本轮。
- WS-04 smoke 尚未接入 CI；若要接入，需要单独处理 workflow touch-set。

## 已知风险与注意事项

- 浏览器 MVP 的通关与 smoke 不等于 Godot 物理、动画、导出或发布质量。
- 当前 venv 没有 `pytest`；本轮 requirements shape 单测使用 `unittest` 路线。
- `scripts/check_requirements_shape.py` 有既有 code-shape 行数 warning。

## 已验证有效的路线

- `node --check apps/pixel-freeze-platformer/main.js`
- `python3 scripts/pixel_freeze_platformer_smoke.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `git diff --check`

## 已验证无效的路线

- `python3 -m pytest tests/test_requirements_shape.py`：当前系统 Python 没有 pytest。
- `.codex/.venv/bin/python -m pytest tests/test_requirements_shape.py`：当前 repo-local venv 也没有 pytest。

## 尚未尝试但建议的路线

- 若要推进真实引擎工程，先做 Godot engine spike 并新增 ADR / REQ / WS。
- 若要继续产品化浏览器 MVP，先拆 Boss、更多关卡、触控输入或资源管线的独立 workstream。
- 后续可把 pixel-freeze smoke 接入 CI，但应先评估 workflow 变更触碰范围。

## 下一位 Agent 的第一步动作

- 先读 `docs/ai/working-context.md` 和 `docs/ai/status/stage-01-game-mvp-development.md`，再跑 `python3 scripts/pixel_freeze_platformer_smoke.py` 确认本地基线。
