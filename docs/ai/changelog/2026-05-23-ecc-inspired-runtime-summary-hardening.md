# 2026-05-23 ECC-Inspired Runtime Summary Hardening

## 新增功能

- `summarize_tool_output.py` 采用 streaming 扫描 raw artifact，不再为了生成摘要把完整日志读入内存。
- 摘要工具新增 `--max-line-chars`，默认每条 match、tail 和 line-window 输出最多展示 `800` 字符，并在 Markdown / JSON 中标记截断状态。
- `SessionStart` runtime 恢复上下文新增 stale-by-default guard，明确本地 runtime session 只是历史恢复材料，不是当前用户指令。

## 修复问题

- 修复单行 base64、长 JSONL 或超长错误行绕过“行数限制”重新进入 transcript 的风险。
- 降低大 artifact 摘要时的本地内存压力。
- 降低恢复旧 runtime session 时误把历史任务、命令或工具意图当作当前指令重放的风险。

## 行为变化

- `LineEntry` JSON 增加 `truncated` 和 `original_chars` 字段；top-level summary 字段保持兼容。
- `SessionStart` additionalContext 总长度限制为 `1600` 字符，section 级压缩仍保持 `240` 字符。
- 本轮只借鉴 ECC 的 streaming / tail-based 和 stale-context guard 模式，不引入 ECC 插件、依赖、Claude-specific hooks 或 live context monitor。

## 破坏性变更

- 无。现有摘要工具 top-level JSON 字段、默认 match/tail/window 行为和 hook 注册保持兼容；新增字段只补充截断元数据。

## 验证范围

- `python3 tests/test_summarize_tool_output.py`
- `python3 tests/test_session_start_runtime_context.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_runtime_token_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`
