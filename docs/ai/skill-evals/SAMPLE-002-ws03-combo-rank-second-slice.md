# SAMPLE-002 WS-03 Combo Rank Second Slice Candidate Skill Eval

更新时间：2026-05-08
状态：accepted

## Purpose

记录 WS-03 的第二个 repo-native 薄业务切片：在既有 Godot platformer browser slice 中加入连击计分与评级反馈，并用 smoke 验证。该样本用于评估 `prd-to-project-skills` 与 `progressive-feature-development` 是否继续减少上下文展开和返工。

本文件不是 canonical current-state truth。需求状态、验收和 traceability 仍以 `docs/requirements/*`、`docs/ai/status/*`、`docs/ai/changelog/*` 为准。

## Sample Metadata

- Date: 2026-05-08
- Skills: `prd-to-project-skills`, `progressive-feature-development`
- Evidence Type: real-task
- Outcome: accepted
- Requirement IDs: REQ-007, REQ-008
- Workstream IDs: WS-03
- Implementation Evidence: `apps/godot-platformer-slice/`
- Smoke Evidence: `scripts/godot_platformer_slice_smoke.py`

## Task Classification

- Classification: non-trivial feature increment inside an existing workstream.
- Reason: 该任务改变用户可见玩法反馈、测试 API、smoke 验收和 requirements 证据，不是简单文档修订。
- NOT Building: 不创建 Godot 工程；不新增关卡、素材、本地化、存档、导出或 CI workflow；不把当前业务状态写进 skill。

## Candidate Sources

| Source | Bucket | Reason |
| --- | --- | --- |
| `docs/requirements/workstreams/WS-03-godot-platformer-first-slice.md` | Keep in requirements | 当前 workstream scope 与验收模型。 |
| `docs/requirements/normalized/REQ-007-godot-platformer-core-loop.md` | Keep in requirements | 用户可见玩法反馈需求。 |
| `docs/requirements/normalized/REQ-008-godot-platformer-smoke-verification.md` | Keep in requirements | smoke 验收范围。 |
| `apps/godot-platformer-slice/` | Implementation evidence | 第二个薄业务切片的实际行为。 |
| `scripts/godot_platformer_slice_smoke.py` | Verification evidence | 自动验证 combo/rank 反馈。 |

## baseline_without_skill

若不使用两个 Candidate skills，第二轮“继续业务样本”容易沿完整 PRD 展开：

- 重新读取完整 REQDOC-003 和 Godot 技术方案，导致上下文面明显变大。
- 把 engine spike、关卡表、素材、本地化或导出管线提前拉入当前 PR。
- 没有明确 plan boundary 时，combo/rank 这种小反馈可能演变成完整计分系统和持久化系统。
- 如果把本轮方法结论写进 skill，可能把最新验收和当前状态隐藏到方法层。

## run_with_skill

本轮实际执行：

- `$progressive-feature-development`：作为 plan gate，限定 REQ/WS、改动文件、NOT Building、smoke 和 doc promotion。
- `$prd-to-project-skills`：分类本轮信息，结论是不创建新 skill；业务状态保留在 requirements / traceability / status / changelog / eval。
- 读取面只覆盖当前 status、WS-03、REQ-007/008、traceability、应用切片和 smoke。
- 实现只改浏览器薄切片与 smoke，不引入 Godot 工程。

## delta

- Context: 没有把完整 PRD、完整 diff 或 runtime JSONL 打进任务上下文。
- Scope: 新增行为收敛为 combo/rank 反馈，避免扩展到持久化、排行榜、完整关卡评分体系。
- Rework: smoke 同步覆盖分数、combo、rank 和 reset，避免用户反馈只停留在 UI。
- Quality: requirements、traceability、status、changelog 与 eval 同步记录，防止样本证据与当前 truth surface 分裂。
- Process Tax: 该任务是非平凡功能增量，skill gate 合理；该样本不证明简单命令或窄修复应触发完整流程。

## acceptance

Outcome: accepted。

原因：

- 任务是真实 workstream 的真实功能增量。
- 样本包含 `baseline_without_skill`、`run_with_skill`、`delta`、`acceptance` 和 `verification`。
- 没有新增 skill 内容，也没有把 requirement truth 或最新验证藏进 skill。
- 提供了两个 Candidate workflow skills 的第二个 accepted real-task eval 样本。

限制：

- `baseline_without_skill` 仍是反事实基线，不是独立双跑。
- 达到 2/2 只是升级前置证据满足；是否升级为 stable / default workflow 需要单独评估简单任务流程税和未来样本。

## verification

- `python3 scripts/godot_platformer_slice_smoke.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## Governance Updates Needed

- Done: `docs/ai/skill-usage-samples.md` 登记 SAMPLE-002。
- Done: requirements、traceability、status 和 changelog 同步本轮薄切片。
- Not needed: 不创建或修改 Candidate skill。
