# 2026-05-23 Stop Runtime Token Pressure Guard

更新时间：2026-05-23
阶段或版本：stage-00 / runtime harness hardening
状态：已确认

## 新增功能

- 新增 warning-only `Stop` hook：`.codex/hooks/stop_runtime_token_pressure.py`。
- hook 读取当前 Stop payload 中的 `transcript_path` / `transcriptPath`，复用 `[runtime_token_budget]` 阈值审计当前 transcript。
- 有压力信号时，hook 通过 `hookSpecificOutput.additionalContext` 输出最多 3 条、总长不超过 1200 字符的提示；无 transcript、无 warning 或异常时静默退出。

## 修复问题

- 修复长 session 已经触发 runtime token pressure 后，下一轮 agent 缺少显式提醒而继续滚大上下文的缺口。
- 降低反复验证、cache miss、大工具输出后继续在同一 session 扩张 transcript 的风险。

## 行为变化

- `.codex/hooks.json` 和 `scripts/hook_config_lib.py` 的 Stop 顺序变为 observation -> session -> token-pressure warning -> AI docs check。
- `check_change_triggered_followups.py` 会把 token-pressure Stop hook 变化路由到 `runtime-token-budget` follow-up。
- 本轮只借鉴 ECC 的 context monitor 提醒模式，不引入 ECC 代码、PostToolUse hook、live monitor 或 shell wrapper。

## 破坏性变更

- 无。该 hook 不输出 `continue: false`，不阻断 Stop，不估算账号费用，不扫描历史 transcript。
- 它只能提醒后续轮次 checkpoint、新开 session 或改用 raw artifact summary，不能挽回第一次已经进入 transcript 的超大输出。

## 验证范围

- `python3 tests/test_runtime_token_budget.py`
- `python3 tests/test_stop_runtime_token_pressure.py`
- `python3 tests/test_hooks_config_sync.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 scripts/sync_hooks_config.py --check`
- `.codex/hooks/run_with_repo_python.sh scripts/check_runtime_token_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`
