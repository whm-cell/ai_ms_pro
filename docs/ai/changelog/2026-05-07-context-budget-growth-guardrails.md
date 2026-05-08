# 2026-05-07 Context Budget Growth Guardrails

更新时间：2026-05-07
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_context_budget.py` 新增默认上下文面 `80%` / `90%` 高水位 warning。
- 新增 ADR 到达预算 warning，使 `15/15` 不再被视为仍有余量。
- 新增 active stage `status` 行数预算，触线时提示 stage compression。
- `new_pro_standard` 同步相同 context budget 机制层。

## 修复问题

- 修复默认上下文只在超过硬 token budget 后才 warning 的滞后问题。
- 修复 ADR count 到达预算边界但不报警的问题。
- 拆出 `context_budget_warnings.py`，避免本次改动把 `check_context_budget.py` 推成新的 code-shape 债务。

## 行为变化

- `AGENTS.md` 明确 subagent 默认使用精简任务包，不默认 `fork_context=true`。
- `AGENTS.md` 明确禁止把完整 PRD、完整 diff、完整 transcript 或完整 runtime JSONL 直接打进对话或治理文档；应先摘要、筛选或结构化抽取。
- `90%` 默认面 warning、ADR 到达预算和 stage status 触线仍是 warning-only，但应优先触发压缩判断。

## 破坏性变更

- 无。检查脚本退出码仍只在配置解析失败等硬错误时返回非零。

## 验证范围

- `python3 tests/test_context_budget.py`
- `python3 tests/test_harness_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [ADR-014 Context Budget Audit](../adr/ADR-014-context-budget-audit.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [上下文预算 OPEN-10 使用细节](../../../--使用细节/上下文预算OPEN-10使用细节.md)
