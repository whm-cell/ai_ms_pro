# Append Replacement Readiness Context

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_sample_append.py` 的 no-write report 现在输出当前 append lane 的 readiness、source metric 和 current / target。
- `check_harness_placeholder_replacement.py` 的 no-write report 现在输出当前 `fill-existing-placeholder` lane 的 readiness、source metric 和 current / target。
- JSON 与文本输出都复用当前 collection queue，不依赖候选样本自述。

## 修复问题

- 避免 append / replacement 复核者只看 accepted real 粗计数，而漏看 cross-task resume、distinct task class report 或 real warning 等精确 burn-in 指标。
- 让 append / replacement gate 与 outcome、upgrade-decision、future-work contract candidate gate 的 current-lane context 输出保持一致。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不改变 readiness 或 upgrade decision。
- 不把模板、candidate 或 report 计为 accepted evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_append tests.test_harness_placeholder_replacement tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action append-new-pending-slot`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action fill-existing-placeholder`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
