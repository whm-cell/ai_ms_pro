# 2026-05-09 Godot Smoke CI

更新时间：2026-05-09
阶段或版本：stage-00
状态：已确认

## 新增功能

- 将 `scripts/godot_platformer_slice_smoke.py` 接入 `.github/workflows/governance-and-smoke.yml` 的 `smoke` job。
- `smoke` job 现在自动覆盖 WS-01 Three.js Snake、WS-02 Harness Trace Console 和 WS-03 Godot Platformer Slice 的 browser smoke。

## 修复问题

- 关闭 WS-03 browser smoke 只停留在本地脚本、未被 CI 自动覆盖的缺口。
- PR #11 远端 burn-in 暴露 GitHub Actions 默认 token 不能读取 `statusCheckRollup.*.workflowRun`；`check_branch_hygiene.py` 现在会在该权限限制下保留 active PR / branch budget 检查，并把 failed-open-PR 审计标记为本次降级说明。

## 行为变化

- 保留 workflow 级 `PLAYWRIGHT_VERSION` 与 `PLAYWRIGHT_CLI_VERSION`，Godot smoke 复用既有 Playwright CLI 固定版本逻辑。
- 不引入完整 Godot engine、GUT、导出 preset、素材、本地化或发布管线。
- branch hygiene 的 failed-open-PR 检查仍会在本地或有足够权限的 `gh` token 下执行；GitHub Actions token 无法读取 check rollup 时不再把 API 权限不足误判为仓库卫生失败。

## 破坏性变更

- 无

## 验证范围

- Workflow YAML parse
- `rg -n "godot_platformer_slice_smoke.py" .github/workflows/governance-and-smoke.yml docs/ai`
- `git diff --check -- .github/workflows/governance-and-smoke.yml docs/ai/index.md docs/ai/working-context.md docs/ai/harness-open-items.md docs/ai/status/stage-00-runtime-harness-foundation.md docs/ai/check-registry.md docs/ai/changelog/2026-05-09-godot-smoke-ci.md`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
