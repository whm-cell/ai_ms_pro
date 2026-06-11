# Append Replacement Report Shape Split

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `scripts/harness_sample_review_context.py`，集中承载 append / placeholder replacement no-write review gate 共享的 queue context 和 candidate review report helper。
- `harness_sample_review_context.py` 已纳入 sample-gap follow-up coverage，后续改动会触发 append / replacement gate 相关复核命令。

## 修复问题

- 消除了 `scripts/check_harness_sample_append.py` 与 `scripts/check_harness_placeholder_replacement.py` 中 `build_report` 过长导致的 code-shape warning。
- 避免报告组装拆分后把函数级 warning 转成文件级 warning。

## 行为变化

- 不改 CLI 参数。
- 不移除或重命名既有 JSON report 字段；后续新增 focused planner / intake command 字段见同日 focused routing changelog。
- 不写 ledger。
- 不接受或拒绝任何样本。
- append / replacement review 仍从当前 queue 回显 readiness、source metric、current / target、capture gate、evidence checklist、trigger 和 boundary。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests/test_harness_sample_append.py tests/test_harness_placeholder_replacement.py tests/test_tool_contracts.py`
- `.codex/.venv/bin/ruff check scripts/check_harness_sample_append.py scripts/check_harness_placeholder_replacement.py scripts/harness_sample_review_context.py tests/test_harness_sample_append.py tests/test_harness_placeholder_replacement.py tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [AI 文档入口索引](../index.md)
