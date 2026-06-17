# Check Registry

更新时间：YYYY-MM-DD
状态：starter 机制层

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
| `check_requirements_shape.py` | `blocking-candidate` | manual / follow-up summary | PRD 导入、raw evidence / source quarantine、`pending` source boundary 和 external-web / third-party / unknown 样本证明误报可控后升级；`source-evidence/raw-prd-evidence` 不作为 canonical REQDOC |
| `check_change_triggered_followups.py` | `advisory` | PR / main push summary | 不直接升级；只驱动其他 checks |
| `check_agent_eval_dataset.py` | `advisory` | manual / starter validation | starter eval dataset 积累真实样本后再评估升级 |
| `run_agent_eval_dataset.py` | `advisory` | manual / dry-run validation | 只运行 repo-local declared checks；真实模型质量结论需要单独样本 |
| `check_agent_trace_schema.py` | `blocking-candidate` | manual / starter validation | trace schema 和 sample 扩大到真实 runtime batch 后再考虑升级 |
| `export_agent_trace.py` | `advisory` | manual / starter validation | starter 只证明 local adapter；远端 exporter 需要项目级 ADR |
| `check_tool_contracts.py` | `blocking-candidate` | manual / starter validation | MCP-like tools 或高影响工具 contract 增多后再考虑升级 |
| `check_mock_data_boundary.py` | `review-required` | manual / starter validation | 校验 `[mock_data_boundary]` 的 fixture、manifest、runtime import 和 inline mock 边界；默认只输出 `REVIEW:`，不自动清理 mock、不创建 API、不证明真实数据集成 |
| `check_data_activation.py` | `review-required` | manual / starter validation | 校验 `[data_activation]` 的 `smoke / shadow-real / real` 切换信号；只把 smoke/mock 退场变成审计提示，不自动迁移数据、不删除 fixture、不证明真实数据质量 |
| `check_context_budget.py` | `blocking` | manual; use `--warning-only` for non-blocking audits | 默认面、skill catalog、raw source、static task packet 达到 hard budget 或 90% compression trigger 时阻断；starter 默认 token budget 仍保持 6500 |
| `check_archive_candidates.py` | `advisory` | manual | 不自动归档；保持主 Agent 语义判断 |
| `check_skill_usage_samples.py` | `advisory` | manual | 只证明 skill 样本是否足够，不阻断业务 |
| `collect_harness_sample_gaps.py` | `advisory` | manual / starter validation | 只列出 starter-safe generic `GAP-*` 观察目录；新项目可沿用或替换为项目 gap id |
| `plan_harness_sample_collection.py` | `advisory` | manual / starter validation | 只生成采集计划或 pending candidate 模板；不写 ledger、不接受 evidence |
| `check_harness_sample_gap_evidence.py` | `advisory` | manual / starter validation | 校验空账本或 candidate JSONL；拒绝 synthetic accepted evidence、raw runtime 和旧项目 ledger 迁移 |
| `check_repo_skills.py` | `review-required` | manual / starter validation | skill 结构频繁变更后再考虑 CI |
| `check_skill_catalog.py` | `review-required` | governance job / starter validation | `.codex/skills` vendor/proxy/lock 与 `--check-output` 样本证明误报可控后再考虑升级为 blocking |
| Scorecard / CodeQL / SBOM | `advisory` | single `security-evidence` job with artifacts | burn-in 后按严重度和误报率逐项升级 |

## 升级规则

- 一个 advisory 或 review-required check 不能直接升为 blocking。
- 升级前必须至少有两次真实样本，且记录误报、修复路径、CI 成本和 reviewer 负担。
- 暂时无法主动验证的真实样本进入 `docs/ai/harness-real-sample-watchlist.md`，不要用 synthetic、placeholder、local-only 或模板草稿代替 accepted real evidence。
- 升级决策进入 `status` 或 `ADR`；`AGENTS.md` 只补触发句，不展开完整执行细节。
