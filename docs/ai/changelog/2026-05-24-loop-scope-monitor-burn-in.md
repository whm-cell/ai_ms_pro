# Changelog: Loop / Scope Monitor Burn-in Artifact

更新时间：2026-05-24
阶段或版本：stage-00 runtime harness hardening
状态：已确认

## 新增功能

- 新增 `docs/ai/standards/loop-scope-monitor.md`，定义 Stop loop / scope monitor 的 bounded burn-in 样本格式。
- 新增 `docs/ai/standards/loop-scope-monitor-samples.jsonl`，登记 synthetic regression 样本和一个 pending real-session 槽位。
- 新增 `scripts/check_loop_scope_monitor_samples.py` 与 `tests/test_loop_scope_monitor_samples.py`，校验样本 schema、finding / recommendation、raw runtime 边界、accepted 样本证据和真实 warning 样本计数。
- Stop loop / scope warning 输出现在带 finding codes、recommended sample action codes 和 placeholder replacement gate，真实 warning 发生后可直接映射到 `triggered_findings` / `monitor_recommendations` 并先保持 `outcome=pending`。
- `scripts/check_warning_sample_code_alignment.py` 会校验 Stop loop/scope emitted finding codes、导出常量、样本 checker `FINDING_CODES` 和 recommendation mapping 对齐，防止 warning / action code 漂移后无法进入样本账本。

## 修复问题

- 修复 G4 Loop / Scope Monitor 只有 hook 与单测、没有可复查 burn-in 样本账本的缺口。

## 行为变化

- governance workflow 会验证 loop / scope monitor sample artifact；该检查保持 advisory。
- changed-file follow-up 会在 monitor 样本、checker、测试或 roadmap 变更时提示对应验证命令。
- sample gap collector 新增 `GAP-RUNTIME-LOOP-SCOPE-WARNING`，明确当前仍缺真实 accepted warning 样本。

## 边界

- 该检查不读取 raw transcript，不重新运行 Stop hook，不把 `.codex/runtime/*` 写入共享治理面。
- synthetic 样本不计入真实 burn-in；当前 accepted real warning sample 仍为 0。
- Stop loop / scope monitor 继续 warning-only，不升级 blocking、不自动 compact、不自动归档。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_loop_scope_monitor_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_warning_sample_code_alignment.py`
- `python3 tests/test_loop_scope_monitor_samples.py`
- `python3 tests/test_stop_loop_scope_monitor.py`
- `python3 tests/test_warning_sample_code_alignment.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_harness_sample_gaps.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Loop / Scope Monitor Burn-in](../standards/loop-scope-monitor.md)
