# 2026-05-23 Local Trace Summary

更新时间：2026-05-23
阶段或版本：stage-00 / runtime harness hardening
状态：已确认

## 新增功能

- 新增本地 no-network trace summary 切片：`scripts/summarize_runtime_traces.py`。
- v1 读取 `.codex/runtime/observations/*.jsonl` 与 `agent-traces/*.agent-trace.jsonl`，输出 Markdown / JSON 摘要。
- 摘要面向 burn-in 观察：session 数量、agent / trace 事件分布、changed paths、REQ / WS 覆盖、`needs_governance_promotion`、失败 / warning 线索和最近会话趋势。

## 修复问题

- 补上 G3 “observability 仍是本地证据，不是完整 trace system”的第一个 P1 切片。
- 降低本地 runtime / trace artifact 分散导致无法快速判断失败来源、治理 promotion 候选和最近会话趋势的风险。

## 行为变化

- `Agentic Harness Gap Roadmap` 标记 P1 Local Trace Summary v1 已落地并进入 advisory burn-in。
- `check-registry` 将 `summarize_runtime_traces.py` 登记为 `advisory`；2026-05-24 已将 no-network summary smoke 接入 governance job，但升级前仍必须记录真实样本、误报率、redaction 边界和治理 promotion 修复路径。
- `$harness-maintenance` verification reference 增加 Local Trace Summary 对应单测和本地 smoke 命令。

## 破坏性变更

- 无。该脚本只读本地 runtime / trace artifact，不上传、不阻断 CI 或 hooks。
- 本轮不声明 OpenAI hosted trace、OTLP collector、MCP 或 A2A 互通；外部 trace / collector 仍需单独 contract、ADR 和可复跑证据。

## 验证范围

- `python3 tests/test_summarize_runtime_traces.py`
- `.codex/hooks/run_with_repo_python.sh scripts/summarize_runtime_traces.py --runtime-dir .codex/runtime/observations`
- `.codex/hooks/run_with_repo_python.sh scripts/summarize_runtime_traces.py --runtime-dir .codex/runtime/observations --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `git diff --check`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Harness Maintenance Verification Commands](../../../.agents/skills/harness-maintenance/references/verification-commands.md)
