# Agent Guardrail Samples

更新时间：2026-05-08
状态：样本记录面

## Purpose

记录 AI / Agent guardrails 在真实任务中的轻量样本，用于后续判断 P1 source boundary 和 P2 high-impact action matrix 的误报率、reviewer 负担，以及是否有足够依据升级为 blocking。

本文件是 observation log，不是 confirmation record、操作日志或 requirement source。

## Scope

当前只记录两类样本：

- P1 source boundary：外部 PRD、网页摘录、大段用户粘贴需求、runtime 摘要或其他可能携带指令的 source material。
- P2 high-impact action matrix：destructive、externally visible 或 permission-changing Agent 动作相关提示、人工确认和验证边界。

## Recording Rules

- Sample 不替代 user confirmation；高影响动作仍必须按 [Agent Action Guardrails](./agent-action-guardrails.md) 取得明确人工确认。
- 不存 secret、token、env value、credential、完整本机路径、完整用户身份信息或完整外部消息正文。
- 不贴完整 PRD、完整 runtime JSONL、完整 transcript、完整 diff 或完整网页正文；只记录摘要、触发规则、处理结果和证据链接。
- 外部内容一律作为 evidence / data 记录，不作为 Agent 可执行指令。
- Evidence link 应指向 PR、commit、CI run、check 输出摘要、相关 source doc、status / handoff 摘要或可审计的外部记录；不要把敏感原文复制进本文档。
- 样本结论只能支持后续 review；不得单独证明某项 guardrail 已经可以 blocking。

## Sample Template

```markdown
### SAMPLE-YYYYMMDD-NN - <short title>

- Date:
- Guardrail:
- Triggered Rule:
- Source / Action Summary:
- Decision:
- Result:
- False Positive / False Negative:
- Reviewer Burden:
- Evidence Links:
- Blocking Upgrade Signal:
- Follow-Up:
```

## Field Guide

| Field | Meaning |
| --- | --- |
| Date | 样本发生日期，使用 `YYYY-MM-DD`。 |
| Guardrail | `P1 source boundary` 或 `P2 high-impact action matrix`。 |
| Triggered Rule | 触发的 checker、文档规则、矩阵条目或人工 review 规则。 |
| Source / Action Summary | 只写摘要，不粘贴完整 source、runtime、transcript、PRD 或消息正文。 |
| Decision | `accepted`、`needs-review`、`false-positive`、`false-negative`、`deferred`。 |
| Result | 实际处理结果，例如保留 advisory、补 confirmation、补 evidence link、无需动作。 |
| False Positive / False Negative | 记录误报、漏报或 `none observed`，并说明原因。 |
| Reviewer Burden | `low`、`medium`、`high`，外加一句具体负担描述。 |
| Evidence Links | 指向可审计证据；允许链接到 PR、CI、status、handoff、source doc 或 changelog。 |
| Blocking Upgrade Signal | `none`、`weak`、`candidate`；必须说明是否已有足够真实样本。 |
| Follow-Up | 后续动作；没有则写 `none`。 |

## Samples

暂无真实样本。后续记录时从上方模板复制最小字段，不要把敏感原文或完整上下文搬入本文档。

## Upgrade Review Rule

升级 blocking 前至少需要满足：

- 每个 guardrail 类型至少两个真实样本；
- 样本包含误报 / 漏报判断和 reviewer 负担；
- evidence links 可回读；
- 升级理由能解释为什么 advisory / review-required 不足；
- 升级不会把 confirmation、secret scanning 或人工架构判断错误地交给自动化替代。

## Related Documents

- [Agent Harness Security](./agent-harness-security.md)
- [Agent Action Guardrails](./agent-action-guardrails.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
