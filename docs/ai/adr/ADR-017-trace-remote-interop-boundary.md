# Trace Remote Interop Sampling Boundary

更新时间：2026-05-24
编号：ADR-017
标题：Trace remote interop 真实样本采集边界
状态：已采纳

## 背景

- `GAP-TRACE-REMOTE-INTEROP` 需要真实 interop run 样本来判断 OpenAI / OTLP / MCP / A2A 或 hosted collector 相关 trace evidence 是否能在受控边界内采集。
- 当前已有 local capture-server 样本，但它只证明 localhost adapter 路径，不证明外部 collector、hosted service、OpenAI tracing、MCP 或 A2A 互通。
- 远端 interop 可能涉及 credential、endpoint、payload、rate limit、cost 和 redaction 边界；在没有明确合同前，不应把任何外部发送写入样本账本。
- 本 ADR 只批准 bounded evidence 采集路径，不批准默认联网、不批准 secret 使用、不批准自动上传完整 trace，也不把单次 interop run 视为能力完成。

## 决策

- 采纳 `FWC-2026-05-24-trace-remote-interop` 作为 `GAP-TRACE-REMOTE-INTEROP` 的采样合同。
- `auth_model`：每次 remote interop 采样必须由当前 operator 明确确认目标、是否发送、是否使用凭据；默认不使用 secret、personal token、production account 或长期 credential。若必须用凭据，只能记录 credential class 和确认结果，不能写入 token、账号标识或 secret 值。
- `endpoint_or_authority_scope`：允许的采样范围仅限显式传入的 external-test-endpoint、hosted test collector 或用户明确确认的 remote collector；每个样本最多记录一个 endpoint class、一次发送尝试或一次 not-sent/cancelled 结果。MCP / A2A / OpenAI hosted trace 只可按 endpoint class 记录，不得声明超出已验证 endpoint 的互通范围。
- `redaction_or_boundary_model`：ledger 只能记录 endpoint_scope、network_exported、remote_status、failure mode、redaction state、withheld data class、复核命令和 bounded evidence ref；不得写入 raw trace payload、request / response body、prompt、transcript、secret、完整工具输出、`.codex/runtime/*` 原始路径或外部 payload body。
- `cost_or_stop_boundary`：采样必须有 per-run stop boundary：默认一次 probe、不得自动 retry、不得后台持续上传；遇到 auth failure、HTTP error、rate limit、unexpected payload 或 cost uncertainty 时停止并记录 failure mode。任何进一步重试都需要新的人工确认。
- 合同进入 `approved-for-sampling` 后，真实样本仍必须先走 `check_harness_sample_append.py <candidate-jsonl>`，进入 pending review-ready 后再走 `check_harness_sample_outcome.py <candidate-jsonl>`；本 ADR 不直接接受任何样本。

## 备选方案

- 继续保持 `needs-adr`，直到用户指定具体远端 collector 后再补 ADR。
- 只允许 localhost capture-server 样本，不开放 remote interop 采样路径。
- 直接把 remote trace export 接入默认 workflow。

## 决策理由

- 远端 interop 的主要风险不是模板格式，而是 auth、endpoint、payload 和成本边界；先定义合同可以让未来真实事件进入 no-write review gate，而不是临时扩大权限。
- 本 ADR 将 remote interop 采样限制为人工确认、单次 probe、bounded evidence、无 raw payload，因此不会改变默认 no-network / local-only trace summary 路径。
- 当前 accepted remote interop sample 仍为 0；因此只能批准采样路径，不能声明外部 collector、OpenAI hosted trace、MCP 或 A2A 互通已完成，也不能升级 blocking。

## 影响

- `GAP-TRACE-REMOTE-INTEROP` 可从 contract-precondition lane 转入真实 interop sample append lane。
- `docs/ai/standards/harness-future-work-contracts.jsonl` 可以把 `FWC-2026-05-24-trace-remote-interop` 标记为 `approved-for-sampling`。
- `scripts/check_harness_future_work_contracts.py` 仍负责验证本 ADR 是否覆盖 `GAP-TRACE-REMOTE-INTEROP`、合同 id、`auth_model`、`endpoint_or_authority_scope`、`redaction_or_boundary_model` 和 `cost_or_stop_boundary`。
- 后续真实样本必须保持 bounded remote interop summary，并由 generic sample-gap checker、append gate 和 outcome gate 复核。

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Agentic Harness Crosswalk](../standards/agentic-harness-crosswalk.md)
- [Harness Sample Gap Evidence](../standards/harness-sample-gap-evidence.md)
- [Harness Future Work Contracts](../standards/harness-future-work-contracts.jsonl)
