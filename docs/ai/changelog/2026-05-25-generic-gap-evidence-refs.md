# Generic Gap Evidence Refs

更新时间：2026-05-25
阶段或版本：STAGE-01
状态：已确认

## 新增功能

- `check_harness_sample_gap_evidence.py` 现在校验通用 gap evidence ledger 的 `evidence_refs` 必须解析到存在的 repo-relative 路径。

## 修复问题

- 过去通用 sample-gap 账本只要求 `evidence_refs` 是非空字符串列表并且不包含 runtime 路径；拼错、缺失或逃出仓库的证据引用可能进入 pending / accepted 样本。

## 行为变化

- `evidence_refs` 可继续使用 markdown anchor、pytest node id 或 JSONL 行号 selector，但底层 repo 文件必须存在。
- 本次不新增真实样本、不接受 pending row、不改 readiness 或 check level。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_gap_evidence.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --json`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `check_code_shape.py --all`
- `unittest discover`
- `ruff`
- `check_ai_governance.py`
- `git diff --check`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
