# GitHub Harness Gatekeeping

更新时间：2026-05-05
编号：ADR-012
标题：GitHub ownership、CI required checks 与 supply-chain 守门
状态：已采纳

## 背景

- Stage-00 已把 governance、hook sync 与 repo-native smoke 接入 GitHub Actions，但远端 required checks、CODEOWNERS 和 supply-chain 守门仍缺少 repo 内配置。
- 本仓库的 harness 控制面包含 `.codex/`、`.github/`、`scripts/check_*`、`docs/ai/` 与 `docs/requirements/`，这些路径变更应被明确 review。
- Branch protection / ruleset 属于 GitHub 远端设置，不能仅靠 repo 文件证明已经生效。

## 决策

- 新增 `.github/CODEOWNERS`，由 `@whm-cell` 默认拥有 harness 控制面与治理文档路径。
- GitHub Actions workflow 采用最小默认权限、concurrency 和 job timeout，并将 code-shape、Windows hook runtime 与 WS-01 黑盒 smoke 纳入守门。
- 新增 Dependabot 与 dependency review workflow；dependency review 在 PR 上阻断 high severity 依赖风险。
- CodeQL 暂不纳入本轮 P0，等业务代码进入 release / CI maturity 阶段再评估。
- GitHub branch protection / ruleset 需要人工或 API 配置，并且只有远端确认后才能把 OPEN-01 标记完成。
- 多人 / 多 AI PR touch-set 冲突控制先作为 repo-local `$team-pr-conflict-control` skill 落地，用于按需评估 open PR overlap、high-risk files、PR template、CODEOWNERS 与 merge queue / `merge_group` readiness；是否升级为阻断式 PR check 需要真实样本证明。
- 新增 `.github/pull_request_template.md` 与 `scripts/check_pr_touch_conflicts.py`，并在 PR workflow 中对 high-risk changed-file overlap 做阻断检查。
- GitHub Actions workflow 增加 `merge_group` 触发；PR touch conflict check 只在 `pull_request` 事件运行。

## 备选方案

- 方案 A：只保留本地 hooks 和单个 governance workflow，不引入 GitHub ownership 或 supply-chain 守门。
- 方案 B：直接把 CodeQL、发布和多平台浏览器矩阵全部接入本轮。
- 方案 C：在 docs 中记录 GitHub 建议，但不落 repo 内配置文件。

## 决策理由

- CODEOWNERS、required checks 和 dependency review 是当前最小有效的 GitHub 强制力组合。
- Windows hook runtime job 验证跨平台 harness 入口，但不承担浏览器 smoke，避免扩大 CI 成本。
- CodeQL 当前收益低于 CI burn-in、dependency review 和 branch protection；延后能保持 Stage-00 hardening 聚焦。

## 影响

- PR 上应出现 `governance`、`windows-hook-runtime`、`smoke` 和 dependency review job。
- GitHub 远端 ruleset 应要求 required checks、PR review、CODEOWNERS review、conversation resolved，并禁止直接 push 到 `main`。
- 团队并行开发任务应通过 `$team-pr-conflict-control` 显式记录 touch-set overlap 与协调动作；`scripts/check_pr_touch_conflicts.py` 在 PR 上补充 high-risk overlap 阻断，但不替代 GitHub branch protection 或 CODEOWNERS review。
- 2026-05-05 曾遇到 GitHub API 403；2026-05-08 当前 guardrails check 显示 `main` branch protection 404 且 branch rulesets 为空，因此当前不能宣称远端已禁止直推 `main`。
- CI 中 `check_code_shape.py --all` 作为 warning-aware gate 运行；当前 legacy warning 不阻断。
- `WS-01` 与 `WS-02` 都具备黑盒浏览器回归路径。

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
