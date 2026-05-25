# Template Capture Gate Filter

日期：2026-05-25

## 新增功能

- `check_harness_sample_templates.py` 支持 `--capture-gate`，可按真实事件前置条件聚焦模板漂移审计。
- 模板审计 text / JSON 输出新增 capture-gate counts。
- 每条 JSON validation entry 现在暴露 `capture_gate` 和 `capture_gate_detail`。

## 修复问题

- 维护者可以单独审计 `requires-approved-remote-interop` 等门槛的草稿，不必在完整模板队列中人工筛选。

## 行为变化

- 该过滤器只影响只读 template drift check 的审计范围，不写 ledger、不采集样本、不接受 evidence。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_harness_sample_templates.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
