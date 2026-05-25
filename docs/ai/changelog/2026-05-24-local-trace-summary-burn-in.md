# Changelog: Local Trace Summary Burn-in Artifact

更新时间：2026-05-24
阶段或版本：stage-00 runtime harness hardening
状态：已确认

## 新增功能

- 新增 `docs/ai/standards/local-trace-summary.md`，定义 Local Trace Summary 的 bounded burn-in 样本格式。
- 新增 `docs/ai/standards/local-trace-summary-samples.jsonl`，登记 synthetic redaction regression 和 3 个 accepted real local JSON report 样本；real report 样本现在显式记录 `task_class`。
- 新增 `scripts/check_local_trace_summary_samples.py` 与 `tests/test_local_trace_summary_samples.py`，校验 no-network/local-only、task_class、计数、redaction state、evidence refs 和 raw runtime 边界。

## 修复问题

- 修复 G3 Local Trace Summary 只有 report 脚本和单测、没有可复查 no-network burn-in 样本账本的缺口。

## 行为变化

- governance workflow 会验证 Local Trace Summary sample artifact；该检查保持 advisory。
- changed-file follow-up 会在 local trace summary 样本、checker、测试或 roadmap 变更时提示对应验证命令。
- 第二个 real report 使用 current-day focused JSON summary，只证明近期本地摘要保持 bounded / redacted，不证明跨任务覆盖或远端互通。
- rolling two-day report 使用 `--max-files 2` 的本地 JSON summary；2026-05-24 复核后已接受为同类 real local report 样本，但不提升跨任务覆盖。
- burn-in readiness 现在按 accepted distinct task classes 计数；当前 3 个 accepted real report 都属于 `harness-hardening`，因此 Local Trace Summary 仍是 1/3，不能进入升级讨论。

## 边界

- 该检查不读取 raw runtime，不重新生成 summary，不上传、不阻断。
- accepted real report 只证明本地 no-network summary 可用，不证明 OpenAI、OTLP、MCP 或 A2A 互通。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_local_trace_summary_samples.py`
- `python3 tests/test_local_trace_summary_samples.py`
- `python3 tests/test_summarize_runtime_traces.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Local Trace Summary Burn-in](../standards/local-trace-summary.md)
