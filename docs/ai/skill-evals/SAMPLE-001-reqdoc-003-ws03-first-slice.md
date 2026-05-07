# SAMPLE-001 REQDOC-003 WS-03 First Slice Candidate Skill Eval

更新时间：2026-05-07
状态：accepted

## Purpose

记录 REQDOC-003 Godot 2D 闯关游戏 PRD 首轮标准化与 WS-03 repo-native 薄切片任务，作为 `prd-to-project-skills` 与 `progressive-feature-development` 的第一个 accepted real-task eval 样本。

本文件不是 canonical current-state truth。需求状态、验收和 traceability 仍以 `docs/requirements/*`、`docs/ai/status/*`、`docs/ai/changelog/*` 为准。

## Sample Metadata

- Date: 2026-05-07
- Skills: `prd-to-project-skills`, `progressive-feature-development`
- Evidence Type: real-task
- Outcome: accepted
- Requirement IDs: REQ-007, REQ-008, REQ-009
- Workstream IDs: WS-03
- Implementation Evidence: `apps/godot-platformer-slice/`
- Smoke Evidence: `scripts/godot_platformer_slice_smoke.py`

## Task Classification

- Classification: 0-1 / complex governed task.
- Reason: 该任务从一个 PRD source 进入 requirements normalization、workstream 拆分、traceability、首轮实现、smoke 和治理文档回写，不是简单文档登记。
- NOT Building: 不创建完整 Godot 工程；不采纳 Godot engine、GUT、导出 preset、素材、本地化或发布管线；不把业务长期状态写入 skill。

## Candidate Sources

| Source | Bucket | Reason |
| --- | --- | --- |
| `docs/requirements/source/REQDOC-003-godot-platformer-prd.md` | Keep in requirements | 原始产品意图和业务验收来源，不进入 skill。 |
| `docs/requirements/normalized/REQ-007-godot-platformer-core-loop.md` | Keep in requirements | 用户可见玩法闭环需求。 |
| `docs/requirements/normalized/REQ-008-godot-platformer-smoke-verification.md` | Keep in requirements | 首轮 smoke 验收要求。 |
| `docs/requirements/normalized/REQ-009-godot-platformer-technical-boundary.md` | Keep in requirements | 技术假设状态和边界。 |
| `docs/requirements/workstreams/WS-03-godot-platformer-first-slice.md` | Keep in requirements | 当前 workstream scope 和验收模型。 |
| `apps/godot-platformer-slice/` | Implementation evidence | 证明首轮 repo-native 薄切片可执行。 |
| `scripts/godot_platformer_slice_smoke.py` | Verification evidence | 证明玩法闭环可自动验证。 |

## baseline_without_skill

如果不触发两个 Candidate skills，最可能的路径是直接围绕完整 PRD 展开业务开发：

- 读取面会长期包含完整 PRD、业务实现、Godot 技术假设、导出和素材管线讨论。
- 需求、实现、验收和当前状态容易混在同一任务上下文中，增加压缩难度。
- 完整 Godot 工程、GUT、导出 preset 和素材/本地化管线可能提前进入 root repo，削弱 harness 研究仓定位。
- 没有明确 plan gate 时，首轮切片可能从“验证 harness 可压缩 PRD”漂移成“开始做完整游戏”。

## run_with_skill

实际运行把 `progressive-feature-development` 作为 plan / boundary gate，把 `prd-to-project-skills` 作为 PRD truth 与 reusable method 分离规则：

- 先把 REQDOC-003 标准化为 REQ-007 / REQ-008 / REQ-009。
- 再拆出 WS-03，只承载首轮 repo-native 垂直切片。
- 实现限定在 `apps/godot-platformer-slice/` 与 `scripts/godot_platformer_slice_smoke.py`。
- 当前业务真相回写到 requirements、traceability、stage status 和 changelog。
- skill eval 只记录方法效果，不把需求状态提升为 skill truth。

## delta

- Context: 默认上下文仍通过 `index -> working-context -> status` 进入，PRD 原文只在 requirement-driven 阶段按需读取。
- Scope: 完整 Godot 工程保持 proposed / 待确认，首轮只验证 `move/jump -> freeze -> throw -> clear enemies -> unlock exit -> complete`。
- Rework: governance check 发现 REQDOC source 文件名未携带 `REQDOC-003` 的漂移，任务内完成修复，避免 traceability catalog 继续失配。
- Quality: smoke 与 governance checks 共同验证 `REQDOC -> REQ -> WS -> implementation -> verification` 链路。
- Process Tax: 本任务本身为 PRD 到实现的非平凡任务，skill overhead 合理；该样本不证明简单任务也应触发这两个 skills。

## acceptance

Outcome: accepted。

原因：

- 任务是真实 PRD 到真实 repo-native implementation 的任务，不是纯文档演示。
- 样本记录了 `baseline_without_skill`、`run_with_skill`、`delta`、`acceptance` 和 `verification`。
- 产品行为、验收状态、traceability 和最新验证留在 requirements / status / changelog。
- 没有新建或修改 skill 内容，也没有把临时业务状态藏进 skill。

限制：

- `baseline_without_skill` 是反事实基线，不是独立重跑。
- 该样本只让 `prd-to-project-skills` 与 `progressive-feature-development` 达到 1/2 accepted samples，不支持升级为 always-on。
- 本 SAMPLE-001 是 workflow Candidate skills 的首个 accepted real-task 样本；`SAMPLE-001-team-pr-conflict-control-validation.md` 是另一条 validation-task 记录，不计入这里的 accepted real-task 计数。
- 完整 Godot engine spike 仍未执行，不能把该样本解释为 Godot 技术方案已成立。

## verification

REQDOC-003 / WS-03 落地任务已报告通过：

- `python3 scripts/godot_platformer_slice_smoke.py`
- `python3 scripts/threejs_snake_smoke.py`
- `python3 scripts/threejs_snake_blackbox_smoke.py`
- `python3 scripts/harness_trace_console_smoke.py`
- `python3 scripts/harness_trace_console_blackbox_smoke.py`
- `python3 -m unittest discover -s tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `python3 scripts/check_github_guardrails.py`
- `git diff --check`

本 eval 登记任务补跑：

- `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## Governance Updates Needed

- Done: `docs/ai/skill-usage-samples.md` 登记 SAMPLE-001。
- Done: 本详细 eval 文件记录对照字段和 caveats。
- Done: 主 Agent 同步 `working-context`、stage status、changelog 和 `docs/ai/index.md`，避免 0/2 旧事实继续留在当前 truth surface。
- Not needed: 不更新 requirements、app code、smoke scripts 或 ADR。
