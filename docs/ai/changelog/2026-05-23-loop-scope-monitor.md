# 2026-05-23 Loop Scope Monitor

更新时间：2026-05-23
阶段或版本：stage-00 / runtime harness hardening
状态：已确认

## 新增功能

- 新增 warning-only `Stop` hook：`.codex/hooks/stop_loop_scope_monitor.py`。
- Warning `additionalContext` 现在显式显示 finding codes、recommended sample action codes 和 `check_harness_placeholder_replacement.py <candidate-jsonl>`，便于真实长会话 warning 后填充 bounded pending placeholder；这些 codes 不等同自动 checkpoint、阻断或 accepted evidence。
- hook 复用当前 transcript scan，提示 repeated tool commands、repeated failed tool outputs、excessive validation/test loops 和 possible task-scope churn。
- 有循环或范围漂移信号时，hook 通过 bounded `hookSpecificOutput.additionalContext` 提醒下一轮 checkpoint、新开 session 或缩小验证面；无 transcript、无 warning 或异常时静默退出。

## 修复问题

- 补上 G4 “缺 live scope / loop monitor”的第一个 v1 切片。
- 降低同一 session 内反复运行相同工具命令、重复失败、过度验证或任务范围来回漂移但没有显式停顿提示的风险。

## 行为变化

- `Agentic Harness Gap Roadmap` 标记 P1 Loop / Scope Monitor v1 已落地并进入真实长会话 burn-in。
- `check-registry` 将 `stop_loop_scope_monitor.py` 登记为 `advisory`，升级前必须记录真实样本、误报率和任务中断成本。
- `$harness-maintenance` verification reference 增加 loop / scope monitor 对应测试命令。

## 破坏性变更

- 无。该 hook 不输出 `continue: false`，不阻断 Stop，不自动 compact，不自动归档，也不把 loop suspicion 升级为 blocking gate。
- 本轮不引入 PostToolUse hook、通用 shell wrapper、外部 collector 或 durable execution engine。

## 验证范围

- `python3 tests/test_stop_loop_scope_monitor.py`
- `python3 tests/test_runtime_token_budget.py`
- `python3 tests/test_hooks_config_sync.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 scripts/sync_hooks_config.py --check`
- `.codex/hooks/run_with_repo_python.sh scripts/check_runtime_token_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Harness Maintenance Verification Commands](../../../.agents/skills/harness-maintenance/references/verification-commands.md)
