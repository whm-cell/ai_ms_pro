# Check Registry

更新时间：2026-05-08
状态：已确认

## 作用

本文件记录 harness checks 的治理等级，避免把所有提醒都升级为 blocking，也避免只靠口头约定判断哪些检查必须跑。

## 等级定义

- `advisory`：只提示风险或压缩机会，不阻断。
- `review-required`：需要 PR 作者或 reviewer 明确看过；是否阻断由当前阶段决定。
- `blocking-candidate`：具备升级为 blocking 的候选条件，但必须先满足真实样本、误报率和修复路径要求。
- `blocking`：CI、hook 或远端规则已经强制；失败必须修复或显式记录例外。

## 当前分级

| Check | Level | CI coverage | 升级条件 |
| --- | --- | --- | --- |
| `check_ai_governance.py` | `blocking` | governance job / Stop hook | 已强制，继续保持 |
| `check_code_shape.py` | `blocking-candidate` | governance job uses `--all`; hooks use `--staged` | 新增大文件误报可控后保持或收紧 |
| `check_pr_touch_conflicts.py` | `blocking-candidate` | PR job blocks confirmed high-risk overlap; GitHub API `UNKNOWN` stays visible but non-blocking during burn-in | 两次真实多人 PR 样本证明收益后收紧 |
| `check_github_guardrails.py` | `blocking-candidate` | manual / PR review evidence | 远端 branch protection / rulesets 可读取后再考虑阻断 |
| `check_branch_hygiene.py` | `blocking` | PR summary runs `--strict --current-pr`; main push summary runs `--strict`; manual cleanup commands remain explicit | active PR 预算、failed open PR、stale branch 持续稳定后再考虑调整阈值 |
| `check_requirements_shape.py` | `blocking-candidate` | manual / follow-up summary | PRD 导入样本证明误报可控后升级 |
| `check_change_triggered_followups.py` | `advisory` | PR / main push summary | 不直接升级；只驱动其他 checks |
| `check_context_budget.py` | `advisory` | manual | 80/90、ADR 到达预算或 stage status 触线持续出现且可自动修复前不阻断 |
| `check_archive_candidates.py` | `advisory` | manual | 不自动归档；保持主 Agent 语义判断 |
| `check_skill_usage_samples.py` | `advisory` | manual | 只证明 skill 样本是否足够，不阻断业务 |
| `check_repo_skills.py` | `review-required` | manual / starter validation | skill 结构频繁变更后再考虑 CI |
| Scorecard / CodeQL / SBOM | `advisory` | single `security-evidence` job with artifacts | burn-in 后按严重度和误报率逐项升级 |

## 升级规则

- 一个 advisory 或 review-required check 不能直接升为 blocking。
- 升级前必须至少有两次真实样本，且记录误报、修复路径、CI 成本和 reviewer 负担。
- 升级决策进入 `status` 或 `ADR`；`AGENTS.md` 只补触发句，不展开完整执行细节。
