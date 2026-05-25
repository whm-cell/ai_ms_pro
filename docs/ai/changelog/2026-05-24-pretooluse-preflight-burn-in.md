# Changelog: PreToolUse Preflight Burn-in Artifact

更新时间：2026-05-24
阶段或版本：stage-00 runtime harness hardening
状态：已确认

## 新增功能

- 新增 `docs/ai/standards/pre-tool-use-preflight.md`，定义 PreToolUse preflight 的 bounded burn-in 样本格式。
- 新增 `docs/ai/standards/pre-tool-use-preflight-samples.jsonl`，登记 synthetic regression 样本和一个 pending real-tool-call 槽位。
- 新增 `scripts/check_pre_tool_use_preflight_samples.py` 与 `tests/test_pre_tool_use_preflight_samples.py`，校验样本 schema、finding / decision、raw tool 边界、accepted 样本证据和真实 warning 样本计数。
- PreToolUse warning 输出现在带 finding codes 和 placeholder replacement gate，真实 warning 发生后可直接映射到 `triggered_findings` 并先保持 `outcome=pending`。
- `scripts/check_warning_sample_code_alignment.py` 会校验 PreToolUse emitted finding codes、导出常量和样本 checker `FINDING_CODES` 对齐，防止 warning code 漂移后无法进入样本账本。

## 修复问题

- 修复 G1 PreToolUse preflight 只有 hook 与单测、没有可复查 burn-in 样本账本的缺口。

## 行为变化

- governance workflow 会验证 PreToolUse preflight sample artifact；该检查保持 advisory。
- changed-file follow-up 会在 preflight 样本、checker、测试或 roadmap 变更时提示对应验证命令。
- sample gap collector 新增 `GAP-GUARDRAIL-PREFLIGHT-WARNING`，明确当前仍缺真实 accepted preflight warning 样本。

## 边界

- 该检查不读取 raw transcript，不重新运行 PreToolUse hook，不把 raw command 或 `.codex/runtime/*` 写入共享治理面。
- synthetic 样本不计入真实 burn-in；当前 accepted real warning sample 仍为 0。
- PreToolUse preflight 继续 warning-only，不升级 blocking、不等同用户授权。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_pre_tool_use_preflight_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_warning_sample_code_alignment.py`
- `python3 tests/test_pre_tool_use_preflight_samples.py`
- `python3 tests/test_pre_tool_use_preflight.py`
- `python3 tests/test_warning_sample_code_alignment.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_harness_sample_gaps.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [PreToolUse Preflight Burn-in](../standards/pre-tool-use-preflight.md)
