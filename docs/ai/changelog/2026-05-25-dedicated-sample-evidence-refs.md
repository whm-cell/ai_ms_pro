# Dedicated Sample Evidence Refs

更新时间：2026-05-25
阶段或版本：STAGE-01
状态：已确认

## 新增功能

- Red-team、PreToolUse preflight、loop/scope monitor、Local Trace Summary、Task Profile Audit 和 Stage Checkpoint resume sample checker 现在都复用 `evidence_ref_utils.validate_existing_repo_relative_refs` 校验 `evidence_refs`。
- 共享 evidence-ref helper 变更现在会触发这些独立样本 checker 的 change-triggered follow-up route。

## 修复问题

- 过去这些独立样本账本只要求 `evidence_refs` 是非空列表并拒绝 raw runtime；缺失文件、绝对路径或逃出仓库的引用可能进入样本账本。
- 修正 red-team skill-squatting 样本里已经不存在的 `.codex/skills.catalog.json` 引用，改为当前存在的 skill lifecycle ADR 证据。

## 行为变化

- `evidence_refs` 必须指向存在的 repo-relative 文件。
- markdown anchor、pytest node id 和 JSONL 行号 selector 可以保留，但底层路径必须存在。
- 本次不新增真实样本、不接受 pending row、不改变 readiness、upgrade decision 或 check level。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_agentic_red_team_samples.py`
- `python3 tests/test_pre_tool_use_preflight_samples.py`
- `python3 tests/test_loop_scope_monitor_samples.py`
- `python3 tests/test_local_trace_summary_samples.py`
- `python3 tests/test_task_profile_audit.py`
- `python3 tests/test_stage_checkpoints.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agentic_red_team_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_pre_tool_use_preflight_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_loop_scope_monitor_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_local_trace_summary_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_task_profile_audit.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_stage_checkpoints.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_warning_sample_code_alignment.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `check_code_shape.py --all`
- `unittest discover`
- `ruff`
- `check_ai_governance.py`
- `git diff --check`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Agentic Red-Team Samples](../security/agentic-red-team-samples.md)
