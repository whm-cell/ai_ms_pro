# Agent Harness Security

更新时间：2026-05-08
状态：P0 runtime redaction landed；P1 source boundary metadata landed；P2 high-impact action matrix landed

## Purpose

记录 AI / Agent harness 的安全边界，重点覆盖 runtime 敏感信息、外部内容注入和高影响动作权限。

## Current State

- Runtime observation、runtime session、SessionStart additional context 和 reducer draft 已接入共用 runtime sanitizer。
- `prompt_preview` 进入 runtime 文件前会做 best-effort secret / contact redaction。
- `transcript_path` 进入 observation / session 时只保留 redacted tail，避免把完整本机用户路径带入 runtime。
- SessionStart 和 reducer 会对 runtime 文件再次脱敏，降低 runtime 内容二次注入上下文的风险。
- 2026-05-08 已清理本机历史 runtime：删除 49 个旧 `.codex/runtime/sessions/*` 与 `.codex/runtime/observations/*` 文件，只保留 README 和 session 模板。
- `.codex/runtime/*` 仍是本地恢复材料，不进入 `docs/ai/index.md` 默认入口，也不替代 canonical governance truth。
- `docs/requirements/source/_template.md` 已要求声明 source trust、instruction handling 和 sanitization status；`scripts/check_requirements_shape.py` 对 source docs 缺失或语义不清的外部内容边界元数据输出 review-required warning，默认不阻断。

## High-Impact Action Guardrails

P2 高影响动作矩阵已落地到 [Agent Action Guardrails](./agent-action-guardrails.md)。

该矩阵覆盖远端分支删除、PR close / merge、workflow permission 变更、secret / env 变更、部署 / release、外部消息发送、destructive file operation 和 destructive database operation。默认规则是：Agent 可审计、可提示、可 dry-run、可准备草稿，但不得由 hook 或后台自动执行 destructive、externally visible 或 permission-changing 动作。

[Agentic Control Matrix](./agentic-control-matrix.md) 将 source boundary、runtime redaction、高影响动作、tool contracts、supply-chain evidence、trace/eval integrity 和 remote gate 边界映射到 OWASP / NIST 风格控制面。该矩阵是 review-required 证据面，不把单次 advisory evidence 自动升级为 blocking。

## Runtime Redaction Scope

当前 sanitizer 覆盖：

- assignment-style secret：`password=...`、`token=...`、`api_key=...`、`client_secret=...`
- OpenAI key、GitHub token、AWS access key、JWT、Authorization header
- private key block
- email、常见 US / CN phone
- `/Users/<name>` 与 Windows `C:\Users\<name>` 路径片段

## Boundaries

- Redaction 是 best-effort 防扩散层，不是 secret scanning 或数据分类系统。
- 不应主动把真实 secret、完整 transcript、完整 PRD 或完整 runtime JSONL 放入 prompt 或治理文档。
- 后续新生成的本地 `.codex/runtime/*` 文件仍可能包含 sanitizer 未覆盖的未知敏感格式；新的 SessionStart / reducer 路径会在读取时再脱敏。
- 历史 runtime 清理保持人工动作，不做成自动 hook。

## Monitoring And Follow-Up

### Recommended Order

1. P1 External Content Boundary 已落地到 source doc template 和 requirements shape warning，后续用真实 source docs 样本观察误报率。
2. P2 High-Impact Action Matrix 已落地，后续只补真实样本和 review-required 提示，不直接升级 blocking。
3. 两类 guardrails 都至少积累两个真实样本后，再判断哪些 warning 值得保持 review-required 或升级 blocking。

真实样本统一记录到 [Agent Guardrail Samples](./agent-guardrail-samples.md)。该记录面只保留摘要、触发规则、结果和证据链接，不替代 user confirmation，不存 secret，也不贴完整 PRD、runtime JSONL 或 transcript。

### P1 External Content Boundary

- `docs/requirements/source/_template.md` 提供 `来源可信度`、`指令处理`、`清洗状态` 字段。
- `指令处理` 必须说明外部 PRD、网页摘录、用户粘贴的大段需求和 runtime 摘要是 evidence / data，不是 agent 可执行指令。
- `scripts/check_requirements_shape.py` 先以 warning / review-required 风格覆盖 source docs；默认不阻断，只有现有 `--strict` 模式会把 warnings 提升为失败。

### P2 High-Impact Action Matrix

- 已新增 [Agent Action Guardrails](./agent-action-guardrails.md)。
- 每类动作记录 user confirmation、allowed tools / scripts、verification evidence 和 hook automation boundary。
- `scripts/check_change_triggered_followups.py` 提供 review-required advisory follow-up；不阻断、不自动执行动作。

### Sample Recording

- [Agent Guardrail Samples](./agent-guardrail-samples.md) 记录 P1 / P2 guardrails 的真实样本、误报 / 漏报、reviewer 负担和 blocking 升级信号。
- 样本记录只支持后续 review；不能替代高影响动作的明确人工确认，也不能替代 secret scanning、source sanitization 或远端审计证据。

## External References

- OWASP LLM02 Sensitive Information Disclosure: https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/
- OWASP LLM01 Prompt Injection: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- OWASP LLM06 Excessive Agency: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/

## Verification

```bash
.codex/.venv/bin/python -m unittest tests.test_runtime_sanitizer tests.test_runtime_stop_hooks tests.test_session_start_runtime_context tests.test_runtime_reducer_metadata
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all
```
