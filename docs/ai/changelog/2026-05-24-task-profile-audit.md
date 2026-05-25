# Changelog: Task Profile Audit

更新时间：2026-05-24
阶段或版本：stage-00 / stage-01 harness hardening
状态：已确认

## 新增功能

- 新增 `scripts/check_task_profile_audit.py`，以 advisory 方式校验 task profile、实际读取面、改动文件、验证命令和 traceability closure。
- 新增 `docs/ai/standards/task-profile-audit.md` 与 `task-profile-audit-sample.jsonl`，记录 P2 Task Profile Audit v1 的证据格式和样本。
- 新增 `tests/test_task_profile_audit.py`，覆盖 simple profile 不拉重治理面、complex profile 保留 traceability、governance/requirements 变更验证和 0-1 stage 读取面。

## 修复问题

- 修复 P2 Task Profile Audit 只有 roadmap 目标、没有可复跑 audit artifact 和 checker 的缺口。

## 行为变化

- 将 task profile audit 接入 check registry、AI index、harness open items、roadmap、changed-file follow-up routing 和 governance workflow 样本校验。

## 边界

- 该能力不要求用户手动标注每个任务。
- 默认 CI 只验证样本和规则可运行；真实任务样本仍需 burn-in。
- 该能力保持 advisory，不升级 blocking。

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
