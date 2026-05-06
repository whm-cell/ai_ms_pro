# Candidate Skill Eval Samples

更新时间：YYYY-MM-DD
状态：starter 机制层

## 作用

本文件记录 Candidate repo-local skills 在真实任务中的 eval 证据。

它不替代 `status`、`handoff`、ADR 或 requirements。它只回答一个问题：某个 Candidate skill 是否已经通过真实任务的 with/without 对照证明能减少上下文、减少返工，并且没有给简单任务制造流程税。

## 当前 Candidate Skills

| Skill | 当前有效 accepted eval 样本 | 升级门槛 | 当前判断 |
| --- | ---: | ---: | --- |
| `prd-to-project-skills` | 0 | 2 | 需要真实 PRD / workstream with/without 样本 |
| `progressive-feature-development` | 0 | 2 | 需要非平凡功能或跨模块任务 with/without 样本 |

## 协作类 Skill 观察

| Skill | 当前真实多人 / 多 AI accepted 样本 | 观察门槛 | 当前判断 |
| --- | ---: | ---: | --- |
| `team-pr-conflict-control` | 0 | 2 | 需要真实 PR touch-set overlap 和 coordination action 样本 |

## 接受为有效 eval 样本的条件

- 任务必须是真实 PRD、真实 workstream、真实功能实现、真实 review 或真实多人 / 多 AI PR。
- 样本必须记录 `baseline_without_skill`、`run_with_skill`、`delta`、`acceptance` 和 `verification`。
- `Outcome: accepted` 的样本才能计入升级证据；`rejected` 和 `pending` 应保留为流程税或不确定性证据。
- 简单任务若被完整流程拖慢，应记录为负样本。
- 每个 Candidate skill 仍需至少 2 个 accepted real-task eval samples 才能认为完成升级前置证据。

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

## 当前样本

暂无 accepted real-task eval samples。

## 复查命令

```bash
python3 scripts/check_skill_usage_samples.py
```
