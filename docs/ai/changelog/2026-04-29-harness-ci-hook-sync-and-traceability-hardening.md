# 2026-04-29 Harness CI Hook Sync And Traceability Hardening

更新时间：2026-04-29
阶段或版本：STAGE-00
状态：已确认

## 新增功能

- Added a shared hook-config renderer plus `scripts/sync_hooks_config.py`, so root harness hook entrypoints can be rendered and checked independently from bootstrap.
- Added a repo-level GitHub Actions workflow that runs hook-sync validation, AI governance checks, and the two repo-native browser smoke scripts.
- Extended `scripts/check_ai_governance.py` from field-presence checks into structured traceability alignment checks across AI-side metadata, normalized requirements, workstream docs, and `traceability-matrix.md`.
- Added runtime `REQ/WS` auto-discovery for Stop observation/session based on changed paths, workstream module paths, and the canonical traceability matrix, then covered the same metadata through reducer-draft tests.
- Added `scripts/harness_trace_console_blackbox_smoke.py` so `WS-02` now has a blackbox DOM regression path alongside the existing deterministic smoke.

## 修复问题

- Fixed the current checkout drift where `.codex/hooks.json` still pointed at a PowerShell entrypoint on a non-Windows host.
- Fixed the gap where the current repo still depended on local-only governance/smoke discipline without a committed CI gate.
- Fixed the gap where `REQ/WS` validation only proved “字段存在” and not whether the declared combinations actually matched the canonical matrix.
- Fixed `run_with_repo_python.sh` on macOS `/bin/bash` 3.2, where `set -u` plus an empty `PYTHON_ARGS` array broke Git-hook execution in fresh starter repos.
- Fixed the starter first-commit blocker where `check_code_shape.py --staged` treated every inherited scaffold file as a brand-new addition in unborn `HEAD` repositories.

## 行为变化

- `.codex/hooks.json` now uses the POSIX Python launcher on non-Windows hosts and can be refreshed with `python3 scripts/sync_hooks_config.py`.
- `.codex/harness.toml` now treats stage `status`, `harness-open-items`, and `docs/requirements/index.md` as part of the current repo's required control surface instead of the starter minimum.
- Governance validation now fails when normalized/workstream docs drift away from `traceability-matrix.md`, or when AI-side `Requirement IDs` and `Workstream IDs` do not form a valid matrix-backed combination.
- Stop runtime artifacts now backfill `Requirement IDs` and `Workstream IDs` without explicit environment variables when changed paths can be mapped unambiguously to a workstream or requirement.
- `WS-02` browser verification now has two layers: the existing deterministic test-API smoke and a second blackbox DOM smoke that exercises the default page.
- Starter guidance now states that copied placeholder docs need `bootstrap --force` for immediate project-name replacement, while `AGENTS.md` remains a manual projectization step.

## 破坏性变更

- 无

## 验证范围

- `python3 scripts/sync_hooks_config.py`
- `python3 scripts/sync_hooks_config.py --check`
- `python3 -m unittest discover -s tests -p 'test_hooks_config_sync.py'`
- `python3 -m unittest discover -s tests -p 'test_runtime_*.py'`
- `python3 -m unittest discover -s tests -p 'test_code_shape_initial_commit.py'`
- `python3 scripts/check_ai_governance.py`
- `python3 scripts/threejs_snake_smoke.py`
- `python3 scripts/harness_trace_console_smoke.py`
- `python3 scripts/harness_trace_console_blackbox_smoke.py`
- external starter replay in a temporary repo: `bootstrap --force -> git add -> .githooks/pre-commit`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
