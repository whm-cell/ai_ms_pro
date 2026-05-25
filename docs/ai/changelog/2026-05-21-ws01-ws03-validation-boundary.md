# 2026-05-21 WS-01 / WS-03 Validation Boundary

更新时间：2026-05-21
阶段或版本：stage-00 / stage-01 validation boundary
状态：已确认

## 新增功能

- Restored `apps/threejs-snake/` as the active harness capability validation sample.
- `apps/threejs-snake/` now provides a zero-build Three.js game with deterministic `?smoke=1` API and black-box DOM / keyboard behavior.
- Tool contracts now include both Three.js Snake deterministic and black-box smoke commands.
- Added a no-server `check_threejs_snake_contract.py` gate for the Three.js app structure, importmap, smoke API and REQ/WS metadata.
- Added `--url/--no-server` support to the Three.js Snake smoke scripts so restricted runners can use an externally started local server.

## 修复问题

- Fixed the drift where WS-01 smoke scripts existed but `apps/threejs-snake/` was missing from the active worktree.
- Fixed current truth surfaces that still treated the WS-03 Godot browser slice as active validation.

## 行为变化

- Removed the Godot browser slice app and smoke script from active worktree and CI.
- Current blocking browser smoke covers WS-01 Three.js Snake and WS-02 Harness Trace Console.
- Governance job now runs the static Three.js Snake contract check before code-shape checks.
- Default smoke behavior still starts its own local server in CI; `--no-server` is an opt-in local workaround for runners that cannot bind sockets.
- Historical WS-03 changelog / eval / burn-in evidence is not rewritten.
- WS-03 no longer proves current active capability validation.
- Future Godot work must start as a new engine spike with ADR and dedicated verification, not by reusing the removed browser slice.

## 破坏性变更

- `apps/godot-platformer-slice/` and `scripts/godot_platformer_slice_smoke.py` are removed from the active worktree.

## 验证范围

- `node --check apps/threejs-snake/main.js`
- `python3 scripts/check_tool_contracts.py`
- `python3 scripts/check_threejs_snake_contract.py`
- `python3 tests/test_threejs_snake_contract.py`
- `python3 scripts/check_requirements_shape.py`
- `python3 scripts/check_workspace_sandbox.py`
- `python3 scripts/check_context_budget.py`
- `python3 scripts/check_ai_governance.py`
- `python3 scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `python3 scripts/check_agent_eval_dataset.py`
- `python3 scripts/run_agent_eval_dataset.py --dry-run`
- `python3 scripts/collect_harness_sample_gaps.py`
- `python3 scripts/export_agent_trace.py --input docs/ai/standards/agent-trace-sample.jsonl`
- `python3 scripts/check_agent_trace_schema.py`
- `python3 scripts/check_skill_catalog.py`
- `git diff --check`
- Targeted unit tests: `test_tool_contracts.py`, `test_workspace_sandbox.py`, `test_harness_sample_gaps.py`, `test_agent_trace_schema.py`, `test_requirements_shape.py`, `test_context_budget.py`, `test_agent_eval_runner.py`
- Browser smoke attempted but current local sandbox rejects socket bind with `[Errno 1] Operation not permitted`: `python3 scripts/threejs_snake_smoke.py`, `python3 scripts/threejs_snake_blackbox_smoke.py`
- `--no-server` smoke was attempted against user-started `http://127.0.0.1:8000`, but the Codex shell sandbox still rejects outbound localhost access with `[Errno 1] Operation not permitted`.
- Browser-side verification against `http://127.0.0.1:8000` was attempted and blocked by Browser URL policy; the agent must not bypass it through another browser surface.
- Codex Browser local `file://` verification was attempted and blocked by Browser URL policy.
- Full `python3 -m unittest discover -s tests` currently fails with one sandbox socket-bind error in `test_agent_trace_export.py` and one existing runtime traceability fallback failure.
- Known unresolved: `python3 tests/test_runtime_traceability.py` still fails on ambiguous `docs/ai/working-context.md` fallback because `.codex/hooks/runtime_traceability.py` is not writable in this sandbox.
