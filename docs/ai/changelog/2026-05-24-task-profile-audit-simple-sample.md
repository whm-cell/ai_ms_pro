# Changelog: Task Profile Audit Simple Real Sample

更新时间：2026-05-24
阶段或版本：stage-00 / stage-01 harness hardening
状态：已确认

## 新增功能

- 在 `docs/ai/standards/task-profile-audit-sample.jsonl` 登记 1 个 accepted real simple-task 样本，覆盖 EVAL-005 repo Python wrapper 边界修复。
- 将 G8 Task Profile Audit 当前状态更新为 accepted real simple / complex 各 1 个样本。

## 修复问题

- 修复 `EVAL-005-stop-trace-evidence-contract` 直接调用系统 `python3` 导致 runtime Stop hook 测试在 Python 3.9 下失败的问题，改用 repo Python wrapper。

## 行为变化

- `check_task_profile_audit.py` 不再提示缺少 accepted real simple-task profile sample。
- Task Profile Audit 仍保持 advisory；两个真实样本只满足最低 burn-in 面，不支持升级为 blocking。

## 边界

- 新样本不引用 `.codex/runtime/*`、raw transcript、prompt、cwd 或完整工具输出。
- 本次只修 eval command 的解释器边界，不改变 Stop hook、trace schema 或 product requirement mapping。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh tests/test_runtime_stop_hooks.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`
- `.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --id EVAL-005-stop-trace-evidence-contract`
- `python3 tests/test_task_profile_audit.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_task_profile_audit.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Task Profile Audit](../standards/task-profile-audit.md)
