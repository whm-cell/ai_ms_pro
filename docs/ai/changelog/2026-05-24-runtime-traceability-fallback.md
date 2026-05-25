# Changelog: Runtime Traceability Fallback

更新时间：2026-05-24
阶段或版本：stage-00 runtime harness hardening
状态：已确认

## 新增功能

- 新增单测覆盖 unknown changed path 不应回退绑定到当前 `working-context` 的 REQ/WS。

## 修复问题

- 修复 `docs/ai/working-context.md` 或未知路径作为 changed path 时会回退绑定到当前 WS-04 的问题。
- Stop runtime traceability 现在只根据显式 payload/env、REQ/WS/REQDOC path 或 module path 做自动发现；无法归因的全局文档和未知路径保持 `unbound`。

## 行为变化

- `working-context-fallback` 不再用于 changed-path 自动归因，避免全局治理文档误带当前业务 WS。

## 破坏性变更

- 无。历史 runtime artifacts 中已有的 `working-context-fallback` 记录仍作为历史 evidence 保留，不自动重写。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_runtime_traceability`
- `.codex/.venv/bin/python -m unittest discover -s tests`

## 关联文档

- [当前工作上下文](../working-context.md)
