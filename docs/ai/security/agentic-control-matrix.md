# Agentic Control Matrix

更新时间：2026-05-10
状态：review-required control matrix

## Purpose

把 OWASP / NIST / agentic guardrail 风险映射到当前 repo harness 的可复查控制面。

本文件不是 blocking policy。它只说明当前有哪些控制、证据在哪里、还缺什么真实样本，以及什么时候才允许把 advisory / review-required 升级为 blocking。

## Control Matrix

| Control ID | Risk family | Current control | Evidence surface | Current level | Upgrade condition |
| --- | --- | --- | --- | --- | --- |
| AC-01 | prompt injection / external instruction confusion | requirement source trust、instruction handling、sanitization status；外部内容只作为 evidence / data | `docs/requirements/source/*`、`check_requirements_shape.py`、guardrail samples | review-required | 至少 2 个外部来源真实样本证明误报可控，并能定位 reviewer action |
| AC-02 | sensitive disclosure | runtime sanitizer；禁止把完整 prompt、transcript、secret、PRD、runtime JSONL 推入共享 truth | `.codex/hooks/runtime_sanitizer.py`、`agent-harness-security.md`、Stop trace redaction state | review-required | 新增敏感格式覆盖测试，并有真实脱敏样本确认无泄露 |
| AC-03 | excessive agency / unsafe automation | 高影响动作矩阵；destructive、externally visible、permission-changing 动作必须人工确认 | `agent-action-guardrails.md`、`check_change_triggered_followups.py`、tool contracts | review-required | 两轮真实高影响动作样本证明确认链可靠，再考虑对特定动作 blocking |
| AC-04 | insecure tool / plugin design | tool contract registry 声明 side effects、permissions、automation mode、dangerous flags | `docs/ai/tool-contracts/contracts.json`、`check_tool_contracts.py` | blocking-candidate | 高影响工具 contract 增多且误报率可控后升级 |
| AC-05 | supply chain / CI evidence | Scorecard、CodeQL artifact、SBOM、dependency review、workflow SHA pinning | `security-evidence-triage.md`、remote merge gates、GitHub runs | advisory | 至少两轮 PR / scheduled evidence、owner、修复路径和 supported GitHub gate 后逐项升级 |
| AC-06 | trace and eval integrity | `agent-trace/v1` schema、Stop producer、trace-linked eval、local / OTLP pilot exporter | trace schema、eval dataset、tool contracts、runner report | blocking-candidate | 真实 trace-file batch validation 稳定后升级 schema；远端 exporter 另需 ADR |
| AC-07 | remote merge bypass | local CI/process evidence；private Free 下 remote required gates 保持 UNKNOWN / plan-limited | `remote-merge-gates.md`、`check_github_guardrails.py` | review-required | 升级 GitHub plan 或改 public 后重新验证 branch protection / rulesets |
| AC-08 | risk governance / ownership | security evidence triage SLO、owner 占位、severity handling | `security-evidence-triage.md`、check registry、status | advisory | 项目方确认 owner 后替换占位，并在真实 issue / PR 中验证 SLO |

## NIST-Style Evidence View

| RMF function | Repo evidence | Gap |
| --- | --- | --- |
| Govern | `AGENTS.md`、check registry、ADR/status、tool contracts | owner 仍是占位；正式风险 owner 需人工确认 |
| Map | requirements traceability、source boundary、sample gap collector | 外部来源样本不足 |
| Measure | smoke、eval runner、trace schema checker、security evidence workflow | hosted eval / trace grading 未接入 |
| Manage | high-impact action matrix、triage SLO、branch hygiene、remote gate evidence | remote enforcement 受 private Free plan 限制 |

## Blocking Upgrade Rule

任何 security / guardrail / evidence 项从 advisory 或 review-required 升级 blocking 前，必须同时满足：

- 至少两轮真实样本，不用演示样本替代。
- 误报、漏报、reviewer 负担和修复路径已记录。
- 有明确 owner 或临时代管人。
- CI 成本和 GitHub plan / repository setting 支持。
- `docs/ai/check-registry.md` 与当前 status 或 ADR 同步升级理由。

## Current Non-Goals

- 不把单次 Scorecard、CodeQL、SBOM 或 dependency review 结果升级为 required gate。
- 不声称 private Free 下 branch protection、rulesets、required checks 或 CODEOWNERS review 已远端强制。
- 不把 OTLP pilot、local trace adapter 或 eval runner 等同于 OpenAI hosted trace / hosted eval。
