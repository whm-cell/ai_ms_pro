# 2026-05-23 Runtime Tool Output Summary

更新时间：2026-05-23
阶段或版本：stage-01 / harness hardening
状态：已确认

## 新增功能

- 新增 `.codex/runtime/tool-outputs/` 作为本地 raw tool-output artifact 目录；原始大日志、完整 diff 或长工具输出留在本地 runtime 层。
- 新增 `scripts/summarize_tool_output.py`，从 raw artifact 输出 bounded summary：artifact path、bytes、line count、estimated tokens、错误匹配、tail 和可选 line windows。
- `check_change_triggered_followups.py` 现在会把摘要工具和 runtime tool-output 路径变化路由到 `runtime-token-budget` follow-up。

## 修复问题

- 修复“大输出压缩省 token 但可能丢证据”的缺口：raw artifact 保留完整证据，transcript 只带摘要和定点扩窗。
- 修复 runtime state 防 staged 边界未覆盖 tool output artifact 的问题。

## 行为变化

- `AGENTS.md` 只新增触发句：大工具输出必须作为本地 runtime artifact 保留，进入对话的是 bounded summary 或 line window。
- `$harness-maintenance` `runtime-token-budget.md` 记录完整使用协议：先落 `.codex/runtime/tool-outputs/<timestamp>-<slug>.log`，再用 `summarize_tool_output.py` 摘要，修复时用 `--around <line>` 扩窗。

## 破坏性变更

- 无。v1 不拦截工具调用，不执行 shell wrapper，不改变现有 runtime transcript audit 阈值。

## 验证范围

- `python3 tests/test_summarize_tool_output.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_runtime_token_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`
