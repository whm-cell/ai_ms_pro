# Team PR Conflict Control Skill

更新时间：2026-05-04
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `.agents/skills/team-pr-conflict-control/`，用于多人 / 多 AI 并行开发时按需评估 PR touch-set overlap、high-risk files、PR template、CODEOWNERS 与 merge queue / `merge_group` readiness。
- 新增 skill references：`control-checklist.md`、`evidence-and-boundaries.md`、`pr-template-minimum.md`。

## 修复问题

- 修复团队并行开发冲突控制只能散落在口头流程或长文档中的问题，改为按需 skill 承载方法层。

## 行为变化

- `AGENTS.md` 和 `docs/ai/index.md` 只增加轻触发入口；团队 PR 冲突控制细则保留在 skill 中，避免把多人协作流程变成简单任务默认流程税。
- 公开 skill 搜索未发现能完整替代该机制的成熟 skill；当前 repo 采用 repo-local skill 承载集成方法，后续真实样本再决定是否升级为 PR template、changed-files overlap check 或 merge queue enforcement。

## 破坏性变更

- 无。

## 验证范围

- `quick_validate.py` 通过 root 与 starter 的 `team-pr-conflict-control` skill。
- `scripts/check_repo_skills.py` 通过 root 与 starter，6 个 repo-local skills 均为 `codex_discoverable=true`、`implicit=false`、`repo-local only`。
- root 与 starter `scripts/check_ai_governance.py` 通过。
- root `scripts/check_context_budget.py` 通过，默认面 `7133 / 8500` 且无 warning。
- starter `scripts/check_context_budget.py` 通过，默认面 `5018 / 6500` 且无 warning。
- `scripts/check_code_shape.py --all` 通过，仅保留既有 legacy size warnings。
- `git diff --check` 通过。
- 新增 [SAMPLE-001 Team PR Conflict Control Validation](../skill-evals/SAMPLE-001-team-pr-conflict-control-validation.md)，记录结构、discoverability、当前 PR、离线场景矩阵、验证结果和治理边界；该样本不计入真实多人 PR accepted 样本。

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [ADR-012 GitHub Harness Gatekeeping](../adr/ADR-012-github-harness-gatekeeping.md)
