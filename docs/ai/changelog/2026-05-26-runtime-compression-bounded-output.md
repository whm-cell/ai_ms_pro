# Runtime Compression And Bounded Tool Output

更新时间：2026-05-26
阶段或版本：stage-00
状态：已完成

## 新增功能

- `scripts/summarize_tool_output.py` 新增 `--max-output-chars` 与 `--max-windows`，markdown / JSON 输出都保持有界，原始 artifact 不被改写。
- 新增 `scripts/capture_tool_output.py`，用于把高风险命令 stdout/stderr 写入 `.codex/runtime/tool-outputs/*.log` 和 `.meta.json`，再只回传 bounded summary。
- 新增 `scripts/build_runtime_compression_draft.py`，Stop token-pressure 触发时写 runtime-only compression draft。
- PreToolUse risk catalog 覆盖更多真实项目大输出命令：`go test -v`、`mvn` / `gradle`、`make`、verbose `pip install`、`tail -f`、`gh api --paginate`、`fd` / `ag` / `ack`。

## 修复问题

- 避免 summary 工具自身因大量 matches、tail 或 windows 再次制造大上下文。
- 避免 Stop token-pressure 把详细 warning 列表注入下一轮上下文；现在只返回 runtime draft 路径和恢复提醒。

## 行为变化

- 仍保持保守强制：PreToolUse warning-only，不阻断、不自动改写命令。
- Runtime compression draft 只写 `.codex/runtime/sessions/`，不是用户指令，也不替代 `docs/ai/*` 或 `docs/requirements/*`。
- Raw tool output 保留为本地 runtime artifact；summary 只是有界视图。

## 破坏性变更

- 无。

## 验证范围

- `pytest tests/test_summarize_tool_output.py tests/test_capture_tool_output.py tests/test_runtime_compression_draft.py tests/test_stop_runtime_token_pressure.py tests/test_pre_tool_use_preflight.py tests/test_runtime_token_budget.py`
- root / starter `ruff check .codex/hooks scripts tests`
- starter `pytest tests`
