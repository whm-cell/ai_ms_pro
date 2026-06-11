# Changelog: Task Profile Audit Burn-in Accounting

更新时间：2026-05-24
阶段或版本：stage-00 / stage-01 harness hardening
状态：已确认

## 新增功能

- 扩展 `scripts/check_task_profile_audit.py`，校验 `task-profile-audit-sample/v1` 的 `source_type`、`outcome`、`false_positive`、`process_tax_note` 和 `evidence_refs`。
- 扩展 `docs/ai/standards/task-profile-audit-sample.jsonl`，区分 `synthetic-regression` 与 `real-task`，并登记 1 个 accepted real complex 样本。
- 新增 raw runtime 边界检查，禁止 prompt、transcript、cwd、raw output 或 `.codex/runtime/*` 进入共享 task-profile 样本。

## 修复问题

- 修复 G8 Task Profile Audit 只能校验 profile/read/verification 形状、不能统计真实样本与流程税证据的缺口。

## 行为变化

- `check_task_profile_audit.py` 现在输出 real sample count、accepted real sample count、accepted real profile counts 和 false-positive count。
- 当前新增的 accepted real complex 样本仍不足以支持升级 blocking 或 always-on；后续继续补更多真实样本。

## 边界

- 该检查保持 advisory，不要求用户手动标注每个任务。
- synthetic 样本不计入真实 burn-in；单个 complex real-task 样本不足以支持升级 blocking 或 always-on。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_task_profile_audit.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_task_profile_audit.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_harness_sample_gaps.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Task Profile Audit](../standards/task-profile-audit.md)
