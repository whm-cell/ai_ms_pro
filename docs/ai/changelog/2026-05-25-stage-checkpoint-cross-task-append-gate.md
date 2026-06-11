# Stage Checkpoint Cross-Task Append Gate

日期：2026-05-25

## 新增功能

- `scripts/harness_sample_boundary.py` 现在把 Stage Checkpoint resume pending candidate 的 cross-task 约束纳入 review-state blocker。
- `check_harness_sample_append.py` 会拒绝新增 checkpoint resume candidate 仍沿用模板 checkpoint id `CP-2026-05-24-agentic-harness-burnin`，或未设置 `resume_scope=cross-task`。

## 修复问题

- 防止跨任务 resume 草稿在字段补全后仍引用同一 harness-hardening burn-in checkpoint，从而被误当作可进入 outcome review 的真实跨任务样本。

## 行为变化

- 采集模板仍可作为草稿输出；写入新增 pending 行前，候选必须替换成真实跨任务 checkpoint id，并保留 bounded evidence。
- 现有 accepted same-task burn-in 样本不受影响。

## 破坏性变更

- 无。该 gate 只影响新增 pending candidate 的 no-write append review。

## 验证范围

- `python3 tests/test_harness_sample_append.py`

## 关联文档

- `docs/ai/checkpoints/README.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
