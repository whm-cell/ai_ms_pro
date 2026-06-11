# 2026-05-23 PreToolUse Preflight Guard

更新时间：2026-05-23
阶段或版本：stage-00 / agentic harness hardening
状态：已确认

## 新增功能

- 新增 warning-only `PreToolUse` hook：`.codex/hooks/pre_tool_use_preflight.py`。
- Warning `additionalContext` 现在显式显示 finding codes 和 `check_harness_placeholder_replacement.py <candidate-jsonl>`，便于真实 warning 后填充 bounded pending placeholder；这些 codes 不等同授权、阻断或 accepted evidence。
- hook 会在工具调用前识别 likely large-output shell command、destructive command、externally visible command 和外部发送类工具名。
- 有风险时输出 bounded `hookSpecificOutput.additionalContext`；无风险、payload 缺失或异常时静默退出。

## 修复问题

- 补上 G1 “治理偏事后”的第一个动作前提醒切片。
- 降低第一次 `ps -axo`、完整 `git diff`、未落 artifact 的 broad `rg`、destructive shell 或 external-send 动作无提示进入执行链路的风险。

## 行为变化

- `.codex/hooks.json` 和 `scripts/hook_config_lib.py` 新增 `PreToolUse` preflight hook。
- `check_change_triggered_followups.py` 会把 preflight hook 变化路由到 high-impact action review。
- `Agentic Harness Gap Roadmap` 标记 P0 preflight guard v1 已落地，后续进入真实样本 burn-in。

## 破坏性变更

- 无。该 hook 不执行命令、不写 runtime、不输出 `continue: false`，也不等同用户授权。
- 本轮不做通用 shell wrapper，不自动阻断工具调用，不扩大到外部 collector 或远端策略。

## 验证范围

- `python3 tests/test_pre_tool_use_preflight.py`
- `python3 tests/test_hooks_config_sync.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 scripts/sync_hooks_config.py --check`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`
