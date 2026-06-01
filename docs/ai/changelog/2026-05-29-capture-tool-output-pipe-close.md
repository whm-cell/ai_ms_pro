# Capture Tool Output Pipe Close

更新时间：2026-05-29
阶段或版本：stage-00
状态：已完成

## 新增功能

- 无。

## 修复问题

- `scripts/capture_tool_output.py` 现在显式关闭 `subprocess.PIPE` 返回的 stdout，避免 bounded tool-output capture 在全量 unittest 中产生 `ResourceWarning: unclosed file`。

## 行为变化

- capture 输出、metadata 和 exit code 行为不变；只收紧子进程 stdout 资源释放。

## 文档同步

- `index`、`working-context`、stage status 和 active closeout handoff 已同步到 2026-05-29；旧长 session 的大批量 dirty worktree 拆分不再作为当前待办，后续只处理独立小切片，真实样本继续走 event-driven watchlist。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_capture_tool_output.py`
- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_archive_candidates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged`
- `.codex/.venv/bin/ruff check .codex/hooks scripts tests`
- `git diff --check`
