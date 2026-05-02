# 2026-04-30 GitHub Harness Gatekeeping

更新时间：2026-04-30
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added GitHub ownership and supply-chain configuration through CODEOWNERS, Dependabot, and dependency review.
- Added a Windows hook runtime CI job and a WS-01 blackbox browser smoke.
- Added governance stage alignment checks for `working-context` REQ/WS bindings against `traceability-matrix`.

## 修复问题

- GitHub workflow now has least-privilege permissions, concurrency, timeout, code-shape coverage, and a broader smoke gate.
- Runtime session / observation REQ/WS stage drift is now surfaced as warning-only evidence.
- Fixed first PR CI burn-in issues: governance diff detection now uses committed PR/CI diff instead of post-test worktree status, Windows Python resolution tests no longer depend on executable fake `.exe` shell scripts, and dependency review is advisory until GitHub dependency graph / Advanced Security is enabled for the repository.

## 行为变化

- `governance`, `windows-hook-runtime`, `smoke`, and dependency review should become required GitHub checks once branch protection / ruleset is configured remotely.
- Dependency review currently uses `continue-on-error` because GitHub reports dependency review unsupported until repository security analysis features are enabled remotely.
- `WS-01` no longer relies only on the smoke-only internal test API for browser verification.

## 破坏性变更

- 无

## 验证范围

- `scripts/check_ai_governance.py`
- `scripts/check_code_shape.py --all`
- `python3 -m unittest discover -s tests`
- `scripts/threejs_snake_blackbox_smoke.py`
- PR #1 GitHub Actions burn-in logs for `governance`, `windows-hook-runtime`, and `dependency-review`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [ADR-012 GitHub Harness Gatekeeping](../adr/ADR-012-github-harness-gatekeeping.md)
