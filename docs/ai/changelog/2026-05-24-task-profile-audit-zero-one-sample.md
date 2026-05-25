# 2026-05-24 Task Profile Audit 0-1 Stage Sample

更新时间：2026-05-24
阶段或版本：stage-00 / stage-01 harness hardening
状态：已确认

## 新增功能

- 在 `docs/ai/standards/task-profile-audit-sample.jsonl` 登记 1 个 accepted real `0-1-stage` 样本，复用 Stage-01 Pixel Freeze Platformer MVP 的 handoff、status、REQ/WS 和 smoke 证据。

## 修复问题

- 补齐 `GAP-WORKFLOW-TASK-PROFILE-AUDIT` 的第三类真实 profile 覆盖：simple、complex、0-1-stage 现在各有 1 个 accepted real 样本。

## 行为变化

- `check_harness_burn_in_readiness.py` 会把 `GAP-WORKFLOW-TASK-PROFILE-AUDIT` 评为 `ready-for-upgrade-discussion`。
- Task Profile Audit 仍保持 advisory；达到样本门槛只允许进入升级讨论，不自动升级 blocking。

## 破坏性变更

- 无。该变更只增加 bounded sample metadata，不写 raw runtime、transcript、prompt 或完整工具输出。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_task_profile_audit.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted --json`
- `python3 tests/test_task_profile_audit.py`
- `python3 tests/test_harness_burn_in_readiness.py`
