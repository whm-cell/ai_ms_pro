# 2026-04-30 Karpathy Guardrails Harness Upgrade

更新时间：2026-04-30
阶段或版本：stage-00
状态：已确认

## 新增功能

- Reviewed the current `forrestchang/andrej-karpathy-skills` repo and adopted the reusable behavior layer as a harness-compatible optional skill pattern.
- Added `repo-governed-coding` to `new_pro_standard` so new repositories can copy the behavior guardrails as part of the starter mechanism layer.
- Added a runtime session `行为护栏快照` section for assumptions, scope boundary, success criteria, and verification plan.
- Added a handoff template `行为护栏摘要` section so reusable behavioral decisions can be promoted into shared governance docs.
- Recorded the long-lived workflow decision in `ADR-009`.

## 修复问题

- Fixed a starter portability gap where the root repository had `$repo-governed-coding` but the reusable starter did not.
- Fixed a runtime/handoff template gap where behavior-level assumptions and verification criteria had no stable promotion field.

## 行为变化

- The harness now carries a reusable method-level guardrail without making it an always-on replacement for `AGENTS.md` or governance checks.
- Stop session snapshots now preserve a clear place for the main agent to promote behavioral decisions into handoff/status when they matter.
- Starter docs now explain when to invoke `$repo-governed-coding` and how skill usage should be escalated.

## 破坏性变更

- 无

## 验证范围

- `python3 -m unittest tests/test_runtime_stop_hooks.py`
- `python3 scripts/check_ai_governance.py`
- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/.venv/bin/python scripts/check_ai_governance.py`
- `.codex/.venv/bin/python scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m py_compile .codex/hooks/stop_runtime_session.py new_pro_standard/.codex/hooks/stop_runtime_session.py scripts/bootstrap_harness.py new_pro_standard/scripts/bootstrap_harness.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [ADR-009 Behavioral Guardrails Skill And Session Snapshot](../adr/ADR-009-behavioral-guardrails-skill-and-session-snapshot.md)
