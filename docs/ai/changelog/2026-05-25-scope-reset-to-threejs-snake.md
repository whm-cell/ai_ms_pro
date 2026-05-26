# 2026-05-25 Scope Reset To Three.js Snake

更新时间：2026-05-25
阶段或版本：stage-00 scope reset
状态：已确认

## 新增功能

- 无新增业务功能；本次是范围复位与治理面清理。

## 修复问题

- 当前 canonical scope 收敛为 WS-01 Three.js Snake 与 WS-02 Harness Trace Console。
- 删除已退出范围的旧游戏线代码、smoke、需求源、标准化需求、workstream、status、handoff、eval 样本和旧 changelog。
- 清理本地 `.codex/runtime/*` 中会把旧游戏线重新带入上下文的恢复记录。
- 更新 `docs/ai/index.md`、`working-context.md`、`plan.md`、Stage-00 status、requirements index 和 traceability matrix，使默认恢复链路不再指向旧业务范围。

## 行为变化

- 新会话默认从 Stage-00 harness closeout、WS-01 和 WS-02 恢复。
- Runtime recovery 不再携带已退出范围的旧任务记录。

## 破坏性变更

- 已退出范围的旧游戏线文件被删除；当前仓库不再提供对应应用入口或 smoke 命令。

## 验证范围

- 全仓搜索当前工作区和 `.codex/runtime`，旧游戏线关键词无命中。
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`
