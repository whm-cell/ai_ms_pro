# 2026-05-24 Default Context Surface Compression

更新时间：2026-05-24
阶段或版本：stage-00 / stage-01 harness hardening
状态：已确认

## 新增功能

- 将 `docs/ai/index.md` 的常用检查长清单压缩为 core / game / harness 三类入口，并把完整命令矩阵留给 `$harness-maintenance` verification commands。
- 将 `docs/ai/working-context.md` 的风险与近期决策压缩为当前仍需继承的 bounded truth，避免重复展开 agentic standards、source-boundary、runtime token 和 sample-gap 细节。

## 修复问题

- 修复默认上下文面达到 80% warning threshold 的问题；`check_context_budget.py` 现在显示 default surface 低于 warning threshold。

## 行为变化

- 默认阅读链路仍是 `AGENTS.md -> working-context -> current status`。
- 详细 harness / sample / security 检查不再复制到默认索引；按 changed-file follow-up、check registry 或 `$harness-maintenance` references 选择。

## 破坏性变更

- 无。该变更只压缩默认路由文档，不改变 check 等级、requirements truth、样本账本或 workstream 状态。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `python3 tests/test_context_budget.py`
- `git diff --check`
