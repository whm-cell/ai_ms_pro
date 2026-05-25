# 2026-05-24 Future Work Contract Intake Bundle

更新时间：2026-05-24
阶段或版本：stage-00 / agentic harness hardening
状态：已确认

## 新增功能

- `build_harness_sample_intake_bundle.py --ledger-action define-contract-precondition --summary` now emits the two future-work contract precondition entries instead of an empty queue.
- `check_harness_pending_samples.py` next-lane guidance now includes the focused contract intake bundle command before the future-work contract checker.
- `harness-sample-gap-evidence` follow-up coverage now requires that focused contract intake command, so future sample-gap control-plane changes do not only exercise the default bundle.

## 修复问题

- 修复 pending report 指向的 `define-contract-precondition` intake bundle 命令输出空队列的问题；该命令现在与 planner 的 future-work contract lane 对齐。

## 行为变化

- The default intake bundle still excludes future-work contract blockers and local-only accepted gaps, so the normal queue remains focused on real sample capture.
- Focused contract intake output only emits `harness-future-work-contract/v1` drafts with `sample_collection_allowed=false`.

- This change only fixes contract-precondition routing.
- It does not approve remote interop or cascade samples, does not change `sample_collection_allowed`, and does not count contract drafts as accepted evidence.

## 破坏性变更

- 无。该变更只修复 read-only routing，不写 ledger、不批准 future-work sampling、不升级任何 check。

## 验证范围

- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action define-contract-precondition --summary`
