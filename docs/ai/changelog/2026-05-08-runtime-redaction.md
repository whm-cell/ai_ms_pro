# 2026-05-08 Runtime Redaction

更新时间：2026-05-08
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增共用 runtime sanitizer，覆盖 Stop observation、Stop session、SessionStart additional context 和 runtime observation reducer。
- 新增 Agent Harness Security 文档，记录 runtime redaction 已落地的范围，以及 prompt injection / high-impact action guardrails 的后续计划。

## 修复问题

- 修复 `prompt_preview` 只截断不脱敏的问题，避免常见 secret、token、email、phone 在 runtime 文件和 reducer 草稿中扩散。
- 修复 `transcript_path` 记录完整本机路径的问题，新 observation / session 只保留 redacted tail。
- 修复旧 runtime session 被 SessionStart 注入时没有再次脱敏的问题。

## 行为变化

- `.codex/runtime/*` 仍是本地恢复材料，但 runtime 写入和读取路径现在会做 best-effort redaction。
- reducer 从历史 observation 中读取旧 `prompt_preview` 时，会在生成 handoff draft 前重新脱敏。
- 已按人工指令清理本机历史 runtime 文件：删除 49 个旧 observation/session 文件，只保留 README 和 `_template.md`。

## 破坏性变更

- 无

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_runtime_sanitizer tests.test_runtime_stop_hooks tests.test_session_start_runtime_context tests.test_runtime_reducer_metadata`
- `python3 -m py_compile .codex/hooks/runtime_sanitizer.py .codex/hooks/stop_runtime_observation.py .codex/hooks/stop_runtime_session.py .codex/hooks/session_start_runtime_context.py scripts/reduce_runtime_observations.py`
- `find .codex/runtime/sessions .codex/runtime/observations -type f`

## 关联文档

- [Agent Harness Security](../security/agent-harness-security.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [AI 文档入口索引](../index.md)
