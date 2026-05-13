# 2026-05-12 Context Budget Gate

## 新增功能

- 新增 context budget gate，用于把默认上下文压缩触发线从人工 warning 升级为默认阻断门禁。

## 修复问题

- 修复长期任务可以持续累积 `working-context` / active `status` 明细而不被治理检查阻断的问题。

## 行为变化

- `scripts/check_context_budget.py` 默认会在默认上下文面达到 90% 压缩触发线、超过硬预算、always-on 文档超行数或 active stage status 触线时返回非零。
- `scripts/check_ai_governance.py` 接入同一 gate；Stop hook 通过治理检查继承该阻断。
- pre-commit 和 GitHub governance job 增加 context budget gate，防止长期状态文档继续膨胀后才被人工发现。

## 影响范围

- 不改变游戏业务代码。
- `scripts/check_context_budget.py --warning-only` 保留审计输出，用于人工查看 warning、重复指令和预算趋势。

## 破坏性变更

- 超过 context budget gate 的后续变更会被 pre-commit、CI 或 Stop hook 阻断，需要先压缩治理文档。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py --warning-only`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `python3 -m unittest tests.test_context_budget`
- `git diff --check`
