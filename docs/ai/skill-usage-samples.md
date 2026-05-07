# Candidate Skill Eval Samples

更新时间：2026-05-07
状态：收集 with/without 对照实验样本中

## 作用

本文件记录 Candidate repo-local skills 在真实任务中的 eval 证据。

它不替代 `status`、`handoff`、ADR 或 requirements。它只回答一个问题：某个 Candidate skill 是否已经通过真实任务的 with/without 对照证明能减少上下文、减少返工，并且没有给简单任务制造流程税。

## 当前 Candidate Skills

| Skill | 当前有效 accepted eval 样本 | 升级门槛 | 当前判断 |
| --- | ---: | ---: | --- |
| `prd-to-project-skills` | 1 | 2 | SAMPLE-001 accepted；仍需要至少 1 个真实 PRD / workstream with/without 样本 |
| `progressive-feature-development` | 1 | 2 | SAMPLE-001 accepted；仍需要至少 1 个非平凡功能或跨模块任务 with/without 样本 |

## 协作类 Skill 观察

| Skill | 当前真实多人 / 多 AI accepted 样本 | 观察门槛 | 当前判断 |
| --- | ---: | ---: | --- |
| `team-pr-conflict-control` | 0 | 2 | 已有离线验证样本；仍需要真实 PR touch-set overlap 和 coordination action 样本 |

## 接受为有效 eval 样本的条件

- 任务必须是真实 PRD、真实 workstream、真实功能实现或真实 review，不是纯文档演示。
- 样本必须说明是否使用该 skill，以及为什么触发或跳过。
- 样本必须记录 `baseline_without_skill`、`run_with_skill`、`delta`、`acceptance` 和 `verification`，形成可复查的 with/without 对照。
- `baseline_without_skill` 必须说明不使用 skill 时预计或实际的读取面、步骤、返工风险或流程税。
- `run_with_skill` 必须说明实际触发方式、读取面、产出路径和是否把结果回写到 repo truth surface。
- `delta` 必须说明相对 baseline 的上下文、返工、质量或速度变化；没有收益也要明确记录。
- `acceptance` 必须说明该样本为什么能或不能计入升级证据。
- `verification` 必须记录实际运行的测试、smoke、治理检查或人工复核证据。
- 样本必须有 `Outcome: accepted`，并且没有把 PRD 当前状态、最新验收证据或临时 TODO 藏进 skill。
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

### SAMPLE-001 reqdoc-003-ws03-first-slice

- Date: 2026-05-07
- Skills: prd-to-project-skills, progressive-feature-development
- Evidence Type: real-task
- Outcome: accepted
- Requirement IDs: REQ-007, REQ-008, REQ-009
- Workstream IDs: WS-03
- baseline_without_skill: 若直接把 REQDOC-003 当业务开发入口，预计会反复读取完整 PRD、Godot 技术假设和实现文件，容易把完整游戏工程、素材/导出/GUT 管线一起铺开，并把当前验收状态混入方法层。
- run_with_skill: 任务按 PRD/requirements/workstream 触发两个 Candidate skills；读取面收敛到 index、working-context、requirements index、traceability、REQDOC-003、REQ-007/008/009、WS-03 与相关 smoke/changelog，产出限定为 REQ/WS 绑定、repo-native 薄切片、smoke、status/changelog/index 回写。
- delta: 相对 baseline，业务范围被压缩为首轮可 smoke 垂直切片；完整 Godot 工程保持 proposed / 待确认；默认上下文未把 PRD 原文长期纳入，治理检查发现并修复了 REQDOC source 文件名漂移。
- acceptance: 计入两个 Candidate skills 的 1 个 accepted 样本，因为它是真实 PRD 到真实实现的任务，包含 with/without 对照字段，且没有把 PRD 当前状态、最新验收证据或临时 TODO 藏入 skill。
- verification: `python3 scripts/godot_platformer_slice_smoke.py`；`python3 scripts/threejs_snake_smoke.py`；`python3 scripts/threejs_snake_blackbox_smoke.py`；`python3 scripts/harness_trace_console_smoke.py`；`python3 scripts/harness_trace_console_blackbox_smoke.py`；`python3 -m unittest discover -s tests`；`.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`；`.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`；`.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`；`python3 scripts/check_github_guardrails.py`；`git diff --check`
- Doc Promotion: 本文件登记 accepted 样本；详细 eval 记录在 `docs/ai/skill-evals/SAMPLE-001-reqdoc-003-ws03-first-slice.md`；长期业务真相仍留在 requirements、traceability、status 和 changelog。
- Notes: caveat 是 baseline_without_skill 为反事实基线，不是独立重跑；该样本只把两个 Candidate skills 推进到 1/2，不支持升级为 always-on。这里的 SAMPLE-001 指 workflow Candidate skills 的首个 accepted real-task 样本；既有 team-pr `SAMPLE-001` 文件仍是 validation-task，不计入该 accepted 计数。

## 复查命令

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py
```
