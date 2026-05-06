# GitHub 私有仓库 Harness 与完整 CI 配置清单

更新时间：2026-05-06
适用场景：接手公司私有 GitHub 仓库，并希望使用当前 Codex harness、PR 治理和完整 CI 守门。

## 结论先行

对企业私有仓库来说，`main` 必须配置 GitHub branch protection 或 ruleset。repo 内的 workflow、CODEOWNERS、PR template 和检查脚本只能提供“可运行的 CI 与治理证据”，不能从 repo 文件本身阻止任何人直接 push `main`。

当前 harness 已经提供了大部分 repo 内机制层。公司项目要达到完整 CI，需要 GitHub 管理员在远端补齐 `main` 保护、required checks、review gate、CODEOWNERS review、conversation resolution、直接推送限制，以及按套餐能力启用 dependency review / code scanning / Dependabot。

## GitHub 权限前置条件

接手项目前先确认这些条件，否则不能宣称“完整 CI 已强制生效”。

| 项目 | 必需性 | 说明 |
| --- | --- | --- |
| GitHub plan | 必需 | 私有仓库要使用 protected branches，通常需要 GitHub Pro、Team、Enterprise Cloud 或 Enterprise Server。公司组织私有仓库一般应使用 Team / Enterprise 能力。 |
| Repository admin 权限 | 必需 | 配置 branch protection、rulesets、Actions settings、code security settings 通常需要 repo admin 或组织授予的 repository rules 权限。 |
| Actions 可用 | 必需 | 必须允许 GitHub Actions 运行，并允许当前 workflows 使用的 actions。 |
| Dependency graph / GitHub Code Security / GHAS | 依仓库能力 | private repo 的 dependency review、code scanning 能力取决于组织套餐和安全功能开关。没有启用时只能做 advisory artifact，不能作为强制安全 gate。 |
| CODEOWNERS 真实团队 | 必需 | `.github/CODEOWNERS` 里必须换成公司真实团队，例如 `@org/platform-team`，不能保留个人占位 owner。 |

## 当前 Harness 已经带来的 repo 内配置

把当前 harness 或 `new_pro_standard` 同步到公司项目后，repo 内应具备这些文件。

| 文件 | 作用 | 当前策略 |
| --- | --- | --- |
| `.github/workflows/governance-and-smoke.yml` | 主 CI，覆盖 governance、Windows hook runtime、smoke | 作为 required checks 的核心来源 |
| `.github/workflows/dependency-review.yml` | PR 依赖变更审查 | private repo 未启用对应安全能力时先 advisory |
| `.github/workflows/security-evidence.yml` | Scorecard / CodeQL / SBOM 证据 | 单个顺序 `security-evidence` job，产出 artifacts，先不 required |
| `.github/CODEOWNERS` | 控制面和关键目录 owner | 需要替换成公司真实团队 |
| `.github/pull_request_template.md` | PR 中显式填写 REQ/WS、touch set、verification、governance impact | reviewer 检查入口 |
| `.github/dependabot.yml` | GitHub Actions、pip、npm 更新 | 需要结合项目实际 package manifests 和私有 registry 调整 |
| `scripts/check_github_guardrails.py` | 检查本地/远端 GitHub guardrails | 能区分 `OK / WARN / UNKNOWN`，不能把 UNKNOWN 当 OK |
| `scripts/check_pr_touch_conflicts.py` | 比较当前 PR 与同 base open PR 的 changed-file overlap | 默认只阻断已确认 high-risk overlap，GitHub API UNKNOWN 在 burn-in 阶段可见但不阻断 |
| `docs/ai/check-registry.md` | 记录 checks 的 advisory / blocking-candidate / blocking 等级 | 防止所有提示都升级成流程税 |

## GitHub 远端必须配置

### 1. 保护 `main`

优先使用 ruleset；如果组织还未采用 rulesets，可以使用 branch protection rule。两者不要配置成互相冲突的两套规则。

必须启用：

- Require a pull request before merging。
- Require approvals，建议至少 1 个 approval；高风险仓库建议 2 个。
- Require review from Code Owners。
- Dismiss stale pull request approvals when new commits are pushed。
- Require approval of the most recent reviewable push。
- Require conversation resolution before merging。
- Require status checks to pass before merging。
- Restrict direct pushes to `main`，默认不允许普通开发者直接 push。
- Do not allow force pushes。
- Do not allow deletions。
- 不允许绕过规则，或只允许极少数 break-glass 管理员绕过，并要求事后记录。

推荐启用：

- Require branches to be up to date before merging，或者使用 merge queue。
- Require linear history，如果团队采用 squash/rebase merge。
- Restrict who can push to matching branches，仅保留 release bot 或管理员。

### 2. 配置 required checks

先创建一条测试 PR，让所有 GitHub Actions 跑出真实 check 名称，然后在 ruleset / branch protection 下拉框里选择实际名称。

当前 harness 建议第一批 required checks：

| Check | 来源 workflow | 是否 required | 说明 |
| --- | --- | --- | --- |
| `governance` | `Governance And Smoke` | 是 | 跑 unit tests、AI governance、code shape、PR follow-up summary、PR touch conflict |
| `windows-hook-runtime` | `Governance And Smoke` | 是 | 验证 Windows PowerShell hook runner 和 Python resolution |
| `smoke` | `Governance And Smoke` | 是 | 跑项目 smoke / blackbox smoke |
| `dependency-review` | `Dependency Review` | 条件 required | private repo 只有在 dependency review 能正常运行且误报可控后才 required |

暂不建议第一天就 required：

| Check | 原因 |
| --- | --- |
| `security-evidence` | Scorecard / CodeQL / SBOM 当前是证据层；CodeQL 和 dependency review 在 private repo 中经常受 code scanning / GitHub Code Security / GHAS 开关影响。至少两轮 PR 或 scheduled burn-in 后再决定是否 required。 |
| `check_context_budget.py` | 当前是 advisory，用于控制上下文膨胀，不应阻断普通业务 PR。 |
| `check_skill_usage_samples.py` | 用来评估 skill 是否真的降低返工，不是业务质量 gate。 |

### 3. 配置 CODEOWNERS review

必须完成：

- 把 `.github/CODEOWNERS` 的 owner 改成公司真实团队，例如 `@company/platform-owners`。
- 保护 `.github/CODEOWNERS` 自身，防止普通 PR 绕过 owner 规则。
- 在 branch protection / ruleset 中启用 Require review from Code Owners。
- 对 `AGENTS.md`、`.agents/**`、`.github/**`、`.codex/**`、`docs/ai/**`、`docs/requirements/**`、`scripts/check_*` 保持明确 owner。

注意：CODEOWNERS 文件只会自动请求 reviewer；只有远端 protection / ruleset 开启 code owner review，它才会成为 merge gate。

### 4. 配置 Actions 安全策略

建议设置：

- Repository Settings -> Actions -> General：允许 GitHub Actions，但限制到组织允许的 actions 来源。
- Workflow permissions 默认 `Read repository contents permission`。
- 只有明确需要写权限的 workflow 才在 workflow/job 内声明更高权限。
- 禁止普通 workflow 使用不必要的 secrets。
- 对第三方 actions 做 allowlist；高安全要求下逐步把 `uses:` 从 tag pinning 升级为 commit SHA pinning。

当前 harness workflow 已经做了：

- 显式 `permissions`。
- `timeout-minutes`。
- `concurrency.cancel-in-progress`。
- `pull_request` 与 `merge_group` 触发。

### 5. 配置 Dependency Review / Dependabot

必须完成：

- 启用 dependency graph。
- 启用 Dependabot alerts。
- 启用 Dependabot version updates，并确认 `.github/dependabot.yml` 在默认分支。
- 如果使用私有 npm / pip / container registry，补充 Dependabot registry credentials。
- 确认 dependency review action 在 PR 上可见，并且不是因为平台能力缺失而长期 advisory。

推荐策略：

- dependency-review 初期 `continue-on-error` 或 advisory，直到 private repo 安全功能确认可用。
- 观察两轮依赖变更 PR 后，再把 `dependency-review` 升级为 required check。
- Dependabot PR 也必须经过同一套 required checks 和 CODEOWNERS review。

### 6. 配置 CodeQL / Code scanning

当前 harness 的 CodeQL 策略是 artifact-only：

- `github/codeql-action/analyze@v3`
- `upload: never`
- 上传 `codeql-results` artifact

原因：private repo 如果没有启用 GitHub code scanning，直接上传 CodeQL 结果会让 CI 红叉。公司仓库如果已经启用 code scanning / GitHub Advanced Security，可以把策略改为：

- 允许 CodeQL 上传到 GitHub Code Scanning。
- 把 CodeQL alerts 接入安全 review 流程。
- 至少两轮 burn-in 后，再决定 `security-evidence` 或专门的 `codeql` check 是否 required。

### 7. 配置 merge queue

团队多人并行、PR 高频时建议启用 merge queue。

必要条件：

- Branch protection / ruleset 中启用 Require merge queue。
- Required check 对应 workflow 必须支持 `merge_group` 事件。
- 当前 harness 的 `governance-and-smoke.yml` 和 `dependency-review.yml` 已包含 `merge_group` trigger。

注意：

- merge queue 不替代 branch protection。
- 如果 required checks 没有在 `merge_group` 上运行，GitHub merge queue 会因为拿不到 required status 而失败。
- 初期可以先不启用 merge queue，等 PR 量和冲突样本证明需要后再启用。

## 接手公司项目时的推荐执行顺序

1. 拉取项目，确认默认分支是 `main` 或明确目标保护分支。
2. 同步 harness 机制层，确保 `.github/`、`.codex/`、`.agents/skills/`、`scripts/check_*`、`docs/ai/`、`docs/requirements/` 存在。
3. 把 `.github/CODEOWNERS` 改成公司真实团队。
4. 推一个非 `main` 分支并创建 PR。
5. 等第一轮 CI 跑完，记录真实 check 名称。
6. 配置 ruleset / branch protection，要求 PR、review、CODEOWNERS、conversation resolution、required checks。
7. 尝试直接 push `main`，应失败；不能用“我不会直推”替代远端验证。
8. 创建一个故意失败的 PR，确认 required checks 失败时不能 merge。
9. 创建一个缺少 CODEOWNER approval 的 PR，确认不能 merge。
10. 运行 `scripts/check_github_guardrails.py`，确认本地/远端状态不是 `UNKNOWN`。
11. 把配置结果写回项目 `docs/ai/status` 或 `docs/ai/harness-open-items.md`。

## 验收命令

本地验证：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py
.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all
git diff --check
```

远端验证：

```bash
gh pr checks <PR_NUMBER> --repo <OWNER>/<REPO>
gh api repos/<OWNER>/<REPO>/branches/main/protection
gh api 'repos/<OWNER>/<REPO>/rulesets?targets=branch'
```

验收标准：

- `check_github_guardrails.py` 至少本地 workflow、CODEOWNERS、Dependabot、PR template、remote workflows 为 `OK`。
- branch protection 或 rulesets 不能是 `UNKNOWN`。
- `governance`、`windows-hook-runtime`、`smoke` 至少一轮远端 PR 绿。
- `dependency-review` 在 private repo 能正常运行后再 required。
- `security-evidence` 至少两轮 PR 或 scheduled 运行成功后，再讨论升级。

## 当前 ai_ms_pro 仓库对照

| 项目 | 当前状态 |
| --- | --- |
| repo 内 workflows | 已有 |
| CODEOWNERS | 已有，但 owner 是 `@whm-cell`，公司项目需替换 |
| PR template | 已有 |
| Dependabot config | 已有 |
| PR touch conflict checker | 已有 |
| Security evidence | 已有，单 job 顺序 evidence |
| remote workflows 可见 | 已确认 |
| branch protection / rulesets | 当前 GitHub API 返回 403，仍是 `UNKNOWN` |
| main 直推禁止 | 不能宣称已生效 |

## 常见误判

- 有 `.github/workflows/*.yml` 不等于 required checks 已启用。
- 有 `.github/CODEOWNERS` 不等于 Code Owners review 会阻断 merge。
- 有 `dependency-review.yml` 不等于 private repo dependency review 可用。
- 有 CodeQL workflow 不等于 code scanning 已启用。
- PR checks 全绿不等于 `main` 禁止直推。
- `security-evidence` 通过不等于供应链 gate 已 blocking。
- `UNKNOWN` 不是 OK；只能说明当前权限或套餐无法证明远端状态。

## 官方参考

- [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub branch protection settings](https://docs.github.com/articles/about-required-reviews-for-pull-requests)
- [GitHub merge queue and `merge_group`](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/using-a-merge-queue)
- [GitHub CODEOWNERS](https://docs.github.com/articles/about-code-owners)
- [GitHub Dependency Review](https://docs.github.com/en/code-security/concepts/supply-chain-security/about-dependency-review)
- [GitHub Dependabot configuration](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [GitHub Actions security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
