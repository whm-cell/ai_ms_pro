# Placeholder Replacement Capture Gate Context

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_placeholder_replacement.py` 的 no-write report 现在输出当前 `fill-existing-placeholder` lane 的 `capture_gate`、`capture_gate_detail`、`evidence_needed`、trigger 和 boundary。
- JSON 与文本输出都从当前 collection queue 解析这些字段，而不是依赖候选样本自述。
- replacement gate 现在确认候选 gap 当前仍属于 `fill-existing-placeholder` lane。

## 修复问题

- 避免真实 warning 补全 placeholder 时，复核者只能看到 sample id、schema 和 checker 结果，却看不到 `replace-placeholder-after-real-event` 前置条件。
- 让 placeholder replacement gate 与 append gate 的 current-lane / capture-gate context 输出保持一致。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不改变 readiness 或 upgrade decision。
- 不把模板、candidate 或 report 计为 accepted evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_placeholder_replacement tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action fill-existing-placeholder`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
