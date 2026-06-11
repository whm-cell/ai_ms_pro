# Candidate Skill Eval Samples

更新时间：2026-05-25
状态：收集 with/without 对照实验样本中

## 作用

本文件记录 Candidate repo-local skills 在真实任务中的 eval 证据。

它不替代 `status`、`handoff`、ADR 或 requirements。它只回答一个问题：某个 Candidate skill 是否已经通过真实任务的 with/without 对照证明能减少上下文、减少返工，并且没有给简单任务制造流程税。

## 当前 Candidate Skills

| Skill | 当前有效 accepted eval 样本 | 升级门槛 | 当前判断 |
| --- | ---: | ---: | --- |
| `prd-to-project-skills` | 3 | 2 | SAMPLE-001 / SAMPLE-002 / SAMPLE-005 accepted；建议保持 Candidate 并继续观察，不升级 Stable |
| `progressive-feature-development` | 3 | 2 | SAMPLE-001 / SAMPLE-002 / SAMPLE-005 accepted；建议保持 Candidate 并继续观察，不升级 Stable |

## 协作类 Skill 观察

| Skill | 当前真实多人 / 多 AI accepted 样本 | 观察门槛 | 当前判断 |
| --- | ---: | ---: | --- |
| `team-pr-conflict-control` | 0 accepted / 2 pending | 2 | 不伪造真实多人 PR accepted；PR burn-in 和并行治理整理只能作为 pending，需真实 PR overlap / coordination / merge result 后再 accepted |

## 升级建议

| Skill | 建议 | 理由 | 下一步证据 |
| --- | --- | --- | --- |
| `prd-to-project-skills` | 保持 Candidate；继续观察；不升级 Stable | 现有 accepted 样本证明需求/工作流方法有用，但仍未证明跨模块或实际新 skill 发布后的维护收益。 | 至少再收集 1 个不同 workstream 样本；再收集 1 个明确跳过 skillization 的简单任务负样本或低流程税样本。 |
| `progressive-feature-development` | 保持 Candidate；继续观察；不升级 Stable | 现有 accepted 样本证明非平凡功能适合 plan gate，也证明已有完整计划时可以跳过重复计划；还缺真正简单任务 skip 证据。 | 至少再收集 1 个不同模块的非平凡功能样本；再收集 1 个简单任务明确 skip 的样本，记录没有被完整计划流程拖慢。 |

## 接受为有效 eval 样本的条件

- 任务必须是真实 requirement、真实 workstream、真实功能实现或真实 review，不是纯文档演示。
- 样本必须说明是否使用该 skill，以及为什么触发或跳过。
- 样本必须记录 `baseline_without_skill`、`run_with_skill`、`delta`、`acceptance` 和 `verification`，形成可复查的 with/without 对照。
- `baseline_without_skill` 必须说明不使用 skill 时预计或实际的读取面、步骤、返工风险或流程税。
- `run_with_skill` 必须说明实际触发方式、读取面、产出路径和是否把结果回写到 repo truth surface。
- `delta` 必须说明相对 baseline 的上下文、返工、质量或速度变化；没有收益也要明确记录。
- `acceptance` 必须说明该样本为什么能或不能计入升级证据。
- `verification` 必须记录实际运行的测试、smoke、治理检查或人工复核证据。
- 样本必须有 `Outcome: accepted`，并且没有把当前状态、最新验收证据或临时 TODO 藏进 skill。
- 简单任务若被完整流程拖慢，应记录为负样本。
- 每个 Candidate skill 仍需至少 2 个 accepted real-task eval samples 才能认为完成升级前置证据。
- 多人 / 多 AI PR 样本必须记录 touch-set overlap、high-risk files、coordination action、最终冲突结果和是否降低返工。

## 样本格式

```text
### SAMPLE-XXX short-name

- Date: YYYY-MM-DD
- Skills: prd-to-project-skills, progressive-feature-development
- Evidence Type: real-task
- Outcome: accepted | rejected | pending
- Requirement IDs: REQ-XXX 或 未绑定
- Workstream IDs: WS-XX 或 未绑定
- baseline_without_skill: 不使用 skill 的基线流程、读取面、风险或返工预期
- run_with_skill: 使用 skill 后的实际触发、读取面、输出和治理回写
- delta: 相对 baseline 的上下文、返工、质量或速度变化
- acceptance: 是否计入升级证据及原因
- verification: 实际运行的测试、smoke、治理检查或人工复核
- Doc Promotion: 留在 task、本文件、handoff、status、ADR、requirements 或 check
- Notes: 关键结论
```

更详细的 eval 记录可放在 `docs/ai/skill-evals/`，本文件保留索引级样本摘要。

## 当前样本

### SAMPLE-001 ws01-threejs-snake-first-slice

- Date: 2026-05-25
- Skills: prd-to-project-skills, progressive-feature-development
- Evidence Type: real-task
- Outcome: accepted
- Requirement IDs: REQ-001, REQ-002, REQ-003
- Workstream IDs: WS-01
- baseline_without_skill: 若直接把首个真实需求场景当普通静态页面实现，预计会漏掉 requirement metadata、traceability matrix、runtime promotion 与治理文档回写，导致后续无法证明 harness 闭环。
- run_with_skill: 任务按 requirements/workstream 触发两个 Candidate skills；读取面收敛到 index、working-context、requirements index、traceability、REQ-001/002/003、WS-01 与 smoke；产出限定为 repo-native Three.js slice、smoke、status/handoff/index 回写。
- delta: 相对 baseline，需求、实现、smoke 和 governance truth 被绑定到同一条 WS-01 链路；默认上下文没有携带完整实现细节。
- acceptance: 计入两个 Candidate skills 的 1 个 accepted 样本，因为它是真实 requirement 到真实实现的任务，包含 with/without 对照字段，且没有把最新验收状态藏入 skill。
- verification: `python3 scripts/threejs_snake_smoke.py`；`python3 scripts/threejs_snake_blackbox_smoke.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- Doc Promotion: 本文件登记 accepted 样本；长期业务真相仍留在 requirements、traceability、status 和 handoff。
- Notes: baseline_without_skill 是反事实基线，不是独立重跑；该样本只把两个 Candidate skills 推进到 1/2，不支持升级为 always-on。

### SAMPLE-002 ws02-trace-console-second-slice

- Date: 2026-05-25
- Skills: prd-to-project-skills, progressive-feature-development
- Evidence Type: real-task
- Outcome: accepted
- Requirement IDs: REQ-004, REQ-005, REQ-006
- Workstream IDs: WS-02
- baseline_without_skill: 若直接继续做控制台 UI，容易把 traceability 展示、filter 交互和 smoke 验证当成普通页面功能，遗漏当前 truth source、REQ/WS closure 和 governance check。
- run_with_skill: 本轮按 `$progressive-feature-development` 做最小计划门：只改 governance UI sample 与 smoke；按 `$prd-to-project-skills` 分类后确认业务状态继续留在 requirements、traceability、status、changelog 与 eval 记录。
- delta: 相对 baseline，读取面收敛到 WS-02、REQ-004/005/006、traceability、应用切片和 smoke；新增行为可由 smoke 验证，并提供第二个真实 eval 样本。
- acceptance: 计入两个 Candidate skills 的第 2 个 accepted 样本，因为它是真实 workstream 功能增量，包含 with/without 对照字段，且没有把业务当前状态或最新验证藏入 skill。
- verification: `python3 scripts/harness_trace_console_smoke.py`；`python3 scripts/harness_trace_console_blackbox_smoke.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- Doc Promotion: 本文件登记 accepted 样本；不新增或修改 Candidate skill。
- Notes: 两个 Candidate skills 达到 2/2 只表示升级前置证据满足，不表示自动升级 always-on；仍需单独评估简单任务流程税。

### SAMPLE-003 harness-ci-burn-in-pr

- Date: 2026-05-09
- Skills: team-pr-conflict-control
- Evidence Type: real-task
- Outcome: pending
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs: WS-01, WS-02
- baseline_without_skill: 若直接提交并开 PR，容易只关注本地测试通过，忽略 open dependency PR、workflow / governance / docs high-risk touch-set、private Free 远端门禁 UNKNOWN，以及这次 PR 是否应被当作真实 burn-in 样本。
- run_with_skill: 本轮按 `$team-pr-conflict-control` 分类为 high-risk team touch-set；本地列出 open PR、当前变更文件、高风险文件和验证命令；PR 创建后通过 `check_pr_touch_conflicts.py`、branch hygiene、GitHub Actions 和 PR body 记录 overlap / coordination action。
- delta: 相对 baseline，PR 发布前明确了 high-risk governance / workflow 文件范围，避免把 GitHub Free 远端 UNKNOWN 写成 OK，并把 CI burn-in 与 security evidence 观察留在 PR / docs 证据层。
- acceptance: 暂不计入 accepted；PR 与 main push 远端 CI 已完成，但该样本仍缺真实多人 / 多 AI same-file 或 high-risk overlap、明确协调动作结果和 reviewer / merge sequencing 证据。
- verification: PR / `main` burn-in 证据见 `docs/ai/security/remote-merge-gates.md` 与 `docs/ai/security/security-evidence-triage.md`；local preflight 包括 unit tests、AI governance、code-shape、context budget、requirements shape、workflow YAML parse、workflow SHA pin scan、smoke checks、GitHub guardrails、branch hygiene 和 `git diff --check`。
- Doc Promotion: 本文件保留 pending 样本；远端 CI 证据已提升到 remote merge gates 与 security evidence triage；若后续能回读 PR body / review / overlap 结果，再另行判断是否转 accepted。
- Notes: 该样本用于观察多人 / 多 AI PR collision control，不支持直接升级 blocking，也不计入 0/2 accepted 缺口。

### SAMPLE-004 worker-d-parallel-guardrail-sample-review

- Date: 2026-05-10
- Skills: team-pr-conflict-control
- Evidence Type: real-task
- Outcome: pending
- Requirement IDs: 未绑定
- Workstream IDs: 未绑定
- baseline_without_skill: 当前任务与其他 worker 并行，若不显式限定 touch-set，容易覆盖 code-shape、trace/eval/tool-contract 或 GitHub / script surfaces 的并行改动，并把当前文档整理误记为真实多人 PR accepted 样本。
- run_with_skill: Worker D 只写 `docs/ai/skill-usage-samples.md`、`docs/ai/skill-evals/**` 和 `docs/ai/security/**` 中已有样本/triage 面；不修改 `harness-open-items`、`working-context`、`index`、`.github` 或 `scripts`；现有 dirty worktree 中其他 worker 改动保持只读观察。
- delta: 相对 baseline，当前 touch-set、high-risk governance docs 和不可接受的升级结论被提前分开；team-pr-conflict-control 仍保持 0 accepted，因为本轮没有真实 PR overlap、review coordination 或 merge result。
- acceptance: 暂不计入 accepted；这是真实多 worker 并行整理的可审计 pending 草稿，不是已完成多人 PR 样本。要 accepted，仍需 PR 级 touch-set overlap、high-risk files、coordination action、最终冲突结果和验证链接。
- verification: `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/skill-usage-samples.md docs/ai/skill-evals/2026-05-10-workflow-skill-upgrade-review.md docs/ai/security/agent-guardrail-samples.md docs/ai/security/security-evidence-triage.md`；`.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`；`git diff --check`
- Doc Promotion: 本文件登记 pending；升级建议详见 `docs/ai/skill-evals/2026-05-10-workflow-skill-upgrade-review.md`；不更新 index / working-context，因本轮写入范围明确排除这些文件。
- Notes: 该样本的价值是防止把并行 worker 任务误写成 accepted PR collision 样本；后续仍需要外部 PR / review / overlap 证据。

### SAMPLE-005 agentic-harness-upgrade-approved-plan-control

- Date: 2026-05-10
- Skills: prd-to-project-skills, progressive-feature-development
- Evidence Type: real-task
- Outcome: accepted
- Requirement IDs: 未绑定
- Workstream IDs: 未绑定
- baseline_without_skill: 若把外部一线差距清单直接展开，很容易同时铺 OpenAI trace backend、OTLP、MCP、A2A、hosted eval、GitHub enterprise gates 和更多文档，造成 scope creep；若机械触发完整 Candidate workflow，也会重复已经通过计划模式锁定的实现决策。
- run_with_skill: 本轮没有新增或修改 Candidate skill；把用户已批准的并行计划当作计划门输入，只做 harness / agentic governance 代码与文档落地。`prd-to-project-skills` 的结论是拒绝把当前评级、临时升级目标或最新验收状态写入 skill；`progressive-feature-development` 的结论是沿用已批准计划，不再增加第二套计划文档。
- delta: 相对 baseline，实际落地被收敛为 OTLP pilot、trace-linked eval、security control matrix、workflow evidence intake 和 canonical truth sync；OpenAI hosted trace/eval、MCP/A2A 与 GitHub enterprise gates 继续保持 deferred / blocked。
- acceptance: 计入两个 Candidate skills 的控制样本，因为它是真实 harness 升级任务，包含 with/without 对照字段，并证明“已有完整计划时不把 Candidate workflow 升级成 always-on 或重复计划税”。它不支持把两个 Candidate skills 升级 Stable。
- verification: `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`；`.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --dry-run`；`.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`；`.codex/hooks/run_with_repo_python.sh scripts/collect_harness_sample_gaps.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- Doc Promotion: 本文件登记 accepted control sample；长期结论同步到 status / harness-open-items / index，不写入 skill 作为隐藏 truth。
- Notes: 该样本补的是“已批准计划 / skip duplicated planning”的逃生口，不替代仍缺的简单任务 skip、跨 workstream 或真实 PR overlap 样本。

## 复查命令

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py
```
