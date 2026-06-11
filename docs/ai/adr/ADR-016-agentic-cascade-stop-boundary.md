# Agentic Cascade Stop Sampling Boundary

更新时间：2026-05-24
编号：ADR-016
标题：Agentic cascade stop 真实样本采集边界
状态：已采纳

## 背景

- `GAP-AGENTIC-CASCADE-STOP` 需要真实 incident 样本来判断 cascade autonomy 风险、Stop 建议和人工介入路径是否足够。
- 当前已有 local-replay 样本，但真实 incident 可能涉及子代理、handoff、工具输出、权限声明和长循环上下文。
- 在没有明确 authority、redaction、stop 和 cost 边界前，真实 incident 采样会放大 prompt、transcript、secret 或 raw tool output 泄漏风险。
- 本 ADR 只批准 bounded evidence 采集，不批准自动级联执行、远端 agent 调用、A2A endpoint、MCP interop 或外部发送。

## 决策

- 采纳 `FWC-2026-05-24-agentic-cascade-stop` 作为 `GAP-AGENTIC-CASCADE-STOP` 的采样合同。
- `auth_model`：只有当前主 agent / operator 可以记录 bounded incident summary；任何子代理、worker、handoff 文本或工具输出都不能声明新增权限、扩大文件范围、触发远端动作或替代用户确认。
- `endpoint_or_authority_scope`：采样范围仅限本地 repo harness 和本地运行时可验证事件；不包含远端 agent、A2A endpoint、hosted worker、外部发送、部署、secret 操作或自动 retry loop。
- `redaction_or_boundary_model`：ledger 只能记录 loop trigger、stop condition、open loop 是否存在、owner decision、复核命令和 bounded evidence ref；不得写入 raw transcript、完整 prompt、secret、完整工具输出、`.codex/runtime/*` 原始路径或外部 payload body。
- `cost_or_stop_boundary`：如果 incident 涉及重复失败、重复命令、验证循环或任务漂移，采样记录必须说明停止条件、是否开启新会话 / checkpoint、是否取消动作，以及人工 owner decision；不得把采样过程作为继续级联执行的理由。
- 合同进入 `approved-for-sampling` 后，真实样本仍必须先走 `check_harness_sample_append.py <candidate-jsonl>`，进入 pending review-ready 后再走 `check_harness_sample_outcome.py <candidate-jsonl>`；本 ADR 不直接接受任何样本。

## 备选方案

- 继续保持 `needs-adr`，直到出现真实 incident 后再补 ADR。
- 直接把 cascade-stop 升级为 blocking check。
- 允许远端 agent / A2A / hosted worker incident 一并进入采样。

## 决策理由

- 先定义边界可以让后续真实 incident 立即进入 no-write review gate，而不是在事件发生后临时讨论权限和脱敏规则。
- 采样只记录 bounded evidence，不扩大 agent 权限，也不改变 warning-only / advisory 状态。
- 真实 incident 数量仍为 0；因此当前只能批准采样路径，不能升级 blocking，也不能声称 cascade stop 已被真实验证。
- 远端 agent、A2A 和 hosted interop 与 `GAP-TRACE-REMOTE-INTEROP` 类似，仍需要单独 auth、endpoint、redaction 和 cost 决策。

## 影响

- `GAP-AGENTIC-CASCADE-STOP` 可从 contract-precondition lane 转入真实 red-team incident append lane。
- `docs/ai/standards/harness-future-work-contracts.jsonl` 可以把 `FWC-2026-05-24-agentic-cascade-stop` 标记为 `approved-for-sampling`。
- `scripts/check_harness_future_work_contracts.py` 仍负责验证本 ADR 是否覆盖 `GAP-AGENTIC-CASCADE-STOP`、合同 id、`auth_model`、`endpoint_or_authority_scope`、`redaction_or_boundary_model` 和 `cost_or_stop_boundary`。
- 后续真实样本必须保持 `source_type=real-incident`，并由 red-team sample checker、append gate 和 outcome gate 复核。

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Agentic Control Matrix](../security/agentic-control-matrix.md)
- [Agentic Red-Team Samples](../security/agentic-red-team-samples.md)
- [Harness Future Work Contracts](../standards/harness-future-work-contracts.jsonl)
