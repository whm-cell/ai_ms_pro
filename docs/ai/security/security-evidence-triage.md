# Security Evidence Triage

更新时间：2026-05-10
状态：advisory evidence triage / SLO 已定义；首轮 main push security evidence 已登记

## 作用

定义 Scorecard、CodeQL artifact、SBOM、dependency review 和 secret scanning advisory 的审阅节奏、owner 占位、严重度处理和升级边界。

当前策略不改变 `docs/ai/check-registry.md` 的分级：这些 security evidence 仍是 advisory / review-required 证据，不伪装成 required gate。blocking 升级必须另有 burn-in、误报率、修复路径和 ADR / status 决策支撑。

风险到控制面的总表见 [Agentic Control Matrix](./agentic-control-matrix.md)。安全证据 triage 结束时应能指向对应 control id，或者明确说明该证据暂不属于 agentic harness 控制面。

## Owner 占位

| Role | 当前占位 | 责任 |
| --- | --- | --- |
| Security Owner | `<security-owner>` | 统一 triage 安全证据，决定是否开 issue、是否要求人工 hold。 |
| Repo Admin | `<repo-admin>` | 管理 GitHub plan、secret/settings、私有报告渠道和远端 gate 能力。 |
| Dependency Owner | `<dependency-owner>` | 处理 dependency review、Dependabot、SBOM 依赖和 license / package 风险。 |
| Release Owner | `<release-owner>` | 发布前确认 source revision、digest manifest、SBOM 和未来 attestation 记录。 |

如果 owner 尚未正式任命，默认由仓库管理员代管；不要因为 owner 未填真实人名就跳过 triage。

## Review Cadence

| Evidence | 触发与节奏 | Owner | 审阅内容 | SLO |
| --- | --- | --- | --- | --- |
| OpenSSF Scorecard | `Security Evidence` workflow 的 PR、main push、weekly schedule 和 manual dispatch；每周至少看一次最新 artifact。 | Security Owner | 分数趋势、Dangerous-Workflow、Token-Permissions、Pinned-Dependencies、Branch-Protection 等建议。 | Critical / High 1 个工作日内分类；Medium / Low 7 个工作日内分类。 |
| CodeQL artifact | 同一 `security-evidence` job 产出 artifact-only SARIF；不上传 code scanning。 | Security Owner + 相关代码 owner | SARIF 中的 security severity、path、sink/source、是否真实可达。 | Critical / High 1 个工作日内确认；Medium 7 个工作日内确认；Low / note 可批量复查。 |
| SBOM | `security-evidence` job 生成 CycloneDX JSON；发布前必须取最新可用 SBOM 或重新生成。 | Dependency Owner + Release Owner | 依赖清单、未知组件、重复或过期包、发布 artifact 是否能追到 source revision。 | 发布前完成；非发布阶段每周抽查一次。 |
| Dependency Review | PR 上运行；当前 workflow 使用 `continue-on-error`，结果仍按 advisory evidence 审阅。 | Dependency Owner | 新增 / 升级依赖、已知 CVE、license 风险、transitive dependency 影响。 | High 及以上 1 个工作日内处理；Medium 7 个工作日内处理。 |
| Secret Scanning Advisory | 来自 GitHub secret scanning / push protection / 外部扫描 / reviewer 报告；若当前 GitHub plan 或 setting 不提供 alert，不声明已远端强制。 | Security Owner + Repo Admin | secret 类型、暴露位置、作用域、是否仍有效、是否已轮换；不记录真实 secret 值。 | 立即 triage；疑似有效 secret 当日轮换或禁用。 |

## Severity 处理

| Severity | 默认处理 |
| --- | --- |
| Critical | 立即私有渠道通知 owner；可人工暂停相关 PR / release；确认影响后开脱敏 issue 或修复 PR。 |
| High | 1 个工作日内确认是否真实可利用；影响当前代码、CI、发布或 secret 的，开脱敏 issue 并指定 owner。 |
| Medium | 7 个工作日内分类；若影响 release、认证、供应链或外部接口，提升到 High 路径。 |
| Low / Informational | 可记录在批量 hardening backlog；无需单独阻断，除非同类问题反复出现。 |
| False positive / Not applicable | 在 issue、PR comment 或 triage 记录中写清排除理由和证据位置；不要删除原始 artifact。 |

## 什么时候开 Issue

满足任一条件时开 issue；issue 只记录脱敏信息：

- 确认会影响当前代码、CI、release artifact、依赖链或 secret 安全。
- 需要跨 PR、跨 owner 或超过一个工作日才能修复。
- 同类 advisory 连续两轮 burn-in 出现，说明它不是一次性噪音。
- 发布前 SBOM / digest / source revision 记录缺失。
- 需要 GitHub plan、repository setting 或私有安全渠道管理员介入。

issue 模板内容应包含：evidence source、artifact / run 链接、脱敏影响范围、severity、owner、修复路径、复查时间和验证命令。不要贴 secret 原文、完整 credential、完整 SARIF 大段内容或完整 SBOM。

## 什么时候升级 Blocking

当前阶段不把单次 security evidence 结果自动升级为 blocking。升级必须同时满足：

- 至少两轮真实 PR / scheduled burn-in 证明信号稳定，误报可解释。
- 有明确修复路径、owner 和回归验证命令。
- CI 成本、runner 配额和私有仓库计划限制可接受。
- `docs/ai/check-registry.md`、相关 status 或 ADR 已同步升级理由。
- 若依赖 GitHub 远端强制力，当前 plan / visibility 已支持 required checks、code scanning、rulesets 或对应功能。

Critical secret 泄漏或可利用漏洞可以由 Security Owner / Repo Admin 人工 hold PR 或 release，但这不是 advisory check 自动变成 required gate。

## Private GitHub Free 边界

当前仓库为 private，且 GitHub Free 下已确认 branch protection / rulesets 属于 plan-limited future gates。因此：

- 不声明 Scorecard、CodeQL、SBOM、dependency review 或 secret scanning advisory 已被远端 required gate 强制。
- CodeQL 保持 artifact-only SARIF；在 private repo 未启用 code scanning 前，不把上传失败当作 blocking 证据。
- Dependency Review 即使配置 `fail-on-severity: high`，当前仍因 workflow `continue-on-error` 和远端 gate 边界按 advisory 处理。
- Secret scanning / push protection 若不可用或未启用，只能作为人工报告或外部扫描 evidence；不写成远端已启用。
- GitHub artifact attestation 在当前 Private + Free 边界下不作为完成条件；发布前先记录 digest manifest、SBOM 和 source revision。

## Burn-in Observations

| 日期 | Evidence | Run / commit | 观察结果 | Triage |
| --- | --- | --- | --- | --- |
| 2026-05-09 | PR #11 security evidence | [run 25598728374](https://github.com/whm-cell/ai_ms_pro/actions/runs/25598728374), head `9b23fd522586bd77126d58ab12c2c3494112cf51` | `security-evidence` job 通过；Scorecard、CodeQL artifact 和 SBOM artifact 均完成。 | 计入首轮 PR burn-in evidence；不升级 blocking。 |
| 2026-05-09 | `main` push security evidence | [run 25599034597](https://github.com/whm-cell/ai_ms_pro/actions/runs/25599034597), merge commit `c1f170faa701885882a0ed7a2105c1054fe956ea` | workflow 成功；Scorecard 完成；CodeQL analysis 完成并上传 `codeql-results` artifact；SBOM 生成并上传 `sbom-cyclonedx` artifact；CodeQL 对 GitHub code scanning / database upload 输出 `Code scanning is not enabled for this repository` 注解。 | 当前按 Private Free / repository setting 边界处理：不是 required gate 失败，不开 issue，不人工 hold；后续继续观察是否重复出现，并仅在启用 code scanning 或升级计划后考虑远端上传/阻断。 |

## Current Executable Next-Step Matrix

| Evidence gap | Current state | Next executable step | Required proof | Still needs external sample |
| --- | --- | --- | --- | --- |
| Scheduled security evidence | 只有 PR #11 和 main push 两类首轮 evidence；缺 scheduled burn-in | 等下一次 schedule 或手动 dispatch 后登记 run、head SHA、artifact names 和 conclusion | `gh run view` / Actions URL；Scorecard、CodeQL artifact、SBOM artifact 可回读 | 需要真实 scheduled 或后续 PR run |
| CodeQL code-scanning annotation | main push 已观察到 private-Free / repository setting 注解；当前不阻断 | 再观察一轮 PR 或 scheduled run 是否重复；若启用 code scanning、升级 plan 或改 public，再重新评估上传失败是否进入 blocking 候选 | run annotation 摘要；repository plan / setting evidence | 需要 plan/setting 变化或第二轮注解样本 |
| Dependency Review advisory | PR workflow 已运行；当前 `continue-on-error`，不作为 required gate | 下一次依赖变更 PR 记录新增/升级依赖、severity、license result 和 triage 结论 | Dependency Review job / PR check link；如有 CVE，记录脱敏 issue 或 owner decision | 需要真实依赖变更 PR |
| SBOM release readiness | 当前只有 CI artifact；无 release / package publish 场景 | 发布前重新生成或引用最新 SBOM，并登记 source revision、artifact digest 和 owner sign-off | SBOM artifact URL/name；digest manifest；source commit | 需要真实 release 或 release-candidate |
| Secret scanning advisory | 当前没有远端 alert evidence；private Free 下不声明 push protection 或 alert gate 已强制 | 若 GitHub、外部扫描或 reviewer 报告疑似 secret，只记录 redacted type/scope、owner、rotation/disable evidence，不写 secret 值 | 脱敏 issue / private triage note；rotation verification | 需要真实 alert 或人工报告 |
| Security owner assignment | owner 仍是占位；triage 可执行但责任人未实名 | 项目方确认 Security / Dependency / Repo Admin / Release Owner 后替换占位，或在 PR 中明确临时代管人 | owner 确认记录；PR / status / issue link | 需要人工确认 |

## Closeout

每次 security evidence triage 结束时至少确认：

- 是否有需要私有渠道处理的 secret 或敏感证据。
- 是否需要开脱敏 issue。
- 是否需要人工 hold PR / release。
- 是否需要更新 `docs/ai/security/supply-chain-provenance-plan.md`、`docs/ai/check-registry.md`、status 或 ADR。

## Verification

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```
