# GitHub 远端配置确认细节

更新时间：2026-04-30
适用仓库：`whm-cell/ai_ms_pro`
适用分支：`main`

## 作用

本文件只整理本地仓库无法单独证明的 GitHub 平台侧配置。

repo 内的 workflow、CODEOWNERS、Dependabot 与 dependency review 文件只能说明“期望规则已经写入代码仓库”。branch protection / ruleset、required checks、review gate、conversation gate 和直推限制是否真的生效，必须到 GitHub 远端配置并确认。

## 已在 repo 内提供的基础

- `.github/workflows/governance-and-smoke.yml`
  - workflow name：`Governance And Smoke`
  - job：`governance`
  - job：`windows-hook-runtime`
  - job：`smoke`
- `.github/workflows/dependency-review.yml`
  - workflow name：`Dependency Review`
  - job：`dependency-review`
- `.github/CODEOWNERS`
  - 当前 owner：`@whm-cell`
- `.github/dependabot.yml`
  - `github-actions`
  - `pip` under `/.codex`
  - `pip` under `/new_pro_standard/.codex`
  - `npm` under `/`

## GitHub 侧必须配置

### 1. Ruleset 或 branch protection

在 GitHub 仓库设置中，对 `main` 配置 ruleset 或 branch protection。

必须启用：

- Require a pull request before merging
- Require approvals
- Require review from Code Owners
- Require conversation resolution before merging
- Require status checks to pass before merging
- Restrict direct pushes to `main`

推荐先等第一轮 PR workflow 跑完，再从 GitHub UI 中选择实际出现的 required check 名称。

当前预期 required checks：

- `governance`
- `windows-hook-runtime`
- `smoke`
- `dependency-review`

注意：GitHub UI 里展示的 check 名称可能带 workflow 前缀或上下文信息。最终以第一轮 PR checks 页面和 branch protection / ruleset 下拉项中实际可选名称为准。

### 2. CODEOWNERS review

确认 `.github/CODEOWNERS` 中的 `@whm-cell` 是实际维护者或团队，并且对仓库有足够权限。

如果不是最终 owner，需要把 `.github/CODEOWNERS` 中的 owner 替换成真实 GitHub 用户或团队，再配置 Code Owners review。

### 3. Dependency Review

确认 GitHub 侧已允许 dependency review 在 PR 上运行。

当前 workflow 使用：

- `actions/dependency-review-action@v4`
- `fail-on-severity: high`

验收方式：

- 新建 PR 后能看到 dependency review job
- 高风险依赖变更会让 PR check 失败
- 该 job 被加入 `main` 的 required checks

### 4. Dependabot

确认 GitHub 仓库的 Dependabot 功能可用，并且能读取 `.github/dependabot.yml`。

注意：

- GitHub Actions 与 pip ecosystem 应能按周检查更新
- root `npm` 配置只有在仓库出现 `package.json`、`package-lock.json`、`npm-shrinkwrap.json` 或同类 npm manifest 后才会产生实际更新 PR
- Dependabot PR 自身也应经过同一套 required checks 和 review gate

## 远端 burn-in 步骤

1. 将当前 harness 变更推到非 `main` 分支并创建 PR。
2. 等待 `Governance And Smoke` 与 `Dependency Review` 两个 workflow 完成。
3. 确认 `governance` job 跑过：
   - `python3 scripts/sync_hooks_config.py --check`
   - `python3 -m unittest discover -s tests`
   - `python3 scripts/check_ai_governance.py`
   - `python3 scripts/check_code_shape.py --all`
4. 确认 `windows-hook-runtime` job 在 `windows-latest` 上跑过：
   - Python resolution unit tests
   - hook sync unit tests
   - PowerShell hook runner governance check
5. 确认 `smoke` job 跑过：
   - `python3 scripts/threejs_snake_smoke.py`
   - `python3 scripts/threejs_snake_blackbox_smoke.py`
   - `python3 scripts/harness_trace_console_smoke.py`
   - `python3 scripts/harness_trace_console_blackbox_smoke.py`
6. 确认 `dependency-review` job 在 PR 上可见。
7. 在 GitHub ruleset / branch protection 中把实际出现的 check 名称加入 required checks。
8. 用失败 PR 或 GitHub 设置页截图 / API 输出确认：未通过 required checks、缺少 review、CODEOWNERS 未批、conversation 未 resolved 时不能 merge。
9. 配置确认后，回写 `docs/ai/harness-open-items.md` 中的 `OPEN-01`。

## 需要人工确认

- `@whm-cell` 是否就是长期 CODEOWNER；如果不是，需要提供真实 GitHub user / team。
- GitHub 远端是否已经对 `main` 配置 ruleset 或 branch protection。
- GitHub UI 中实际 required check 名称是否正好是 `governance`、`windows-hook-runtime`、`smoke`、`dependency-review`。
- Dependency graph / Dependency Review / Dependabot 在当前仓库可见性和账号权限下是否可用。
- 是否额外启用 optional gate：
  - Require branches to be up to date before merging
  - Require linear history
  - Require signed commits
  - Merge queue

## 不要误判为已完成

- 本地存在 `.github/workflows/*.yml` 不等于 GitHub required checks 已启用。
- 本地存在 `.github/CODEOWNERS` 不等于 Code Owners review 已被 branch protection / ruleset 要求。
- 本地测试全绿不等于远端 `ubuntu-latest` / `windows-latest` 已有 green history。
- Dependabot 配置存在不等于 GitHub 平台已经成功创建更新 PR。
- 没有 GitHub 设置页、GitHub API 输出或 PR merge gate 实测证据前，`OPEN-01` 仍应保持开放。

## 官方参考

- [GitHub rulesets available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [GitHub branch protection rule management](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
- [About dependency review](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review)
- [Dependabot options reference](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
