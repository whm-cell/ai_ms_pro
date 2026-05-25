# 2026-05-21 Runtime Token Budget

更新时间：2026-05-21
阶段或版本：stage-01 / harness hardening
状态：已确认

## 新增功能

- 新增 `scripts/check_runtime_token_budget.py`，用于按需审计 Codex rollout JSONL transcript 的 runtime token pressure。
- 新增 `.codex/harness.toml` `[runtime_token_budget]` 阈值：单次 tool output、last input、fresh input/cache miss、task_complete、token snapshot 和 elapsed minutes。
- governance workflow 增加 no-transcript wiring check，确保脚本在 CI 可运行；真实 transcript audit 仍需手动传 `--transcript <rollout-jsonl>`。

## 修复问题

- 修复只用静态 default context budget 判断 token 风险的盲点；长会话、工具输出和 cache miss 现在有单独审计面。
- 修复 changed-file follow-up 无法提示 runtime transcript / token budget 策略变更的缺口。

## 治理依据

- 外部依据记录在 [ADR-014 Context Budget Audit](../adr/ADR-014-context-budget-audit.md) 和 `$harness-maintenance` [Runtime Token Budget](../../../.agents/skills/harness-maintenance/references/runtime-token-budget.md)。
- 本次改造把静态 context budget 与运行时 transcript/token budget 分离：前者继续 blocking，后者先作为 `blocking-candidate` 收集真实样本。

## 行为变化

- `AGENTS.md` 增加一条 always-on 触发：运行时 token pressure 需要 bounded tool output 和 transcript audit，而不是把完整 runtime JSONL 或工具输出直接塞进上下文。
- `check_change_triggered_followups.py` 会在 `.codex/harness.toml`、runtime artifact 或 runtime token checker 变化时建议 `runtime-token-budget` follow-up。

## 破坏性变更

- 无。`check_runtime_token_budget.py` 无 `--transcript` 时只做 CI wiring check；真实 transcript warning 默认不阻断，除非显式加 `--strict`。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_runtime_token_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_runtime_token_budget.py --transcript /Users/coolm/.codex/sessions/2026/05/21/rollout-2026-05-21T11-08-45-019e4881-c70f-7b21-afa1-aa93905e914b.jsonl`
- `python3 -m unittest tests.test_runtime_token_budget`
- `python3 -m unittest tests.test_change_triggered_followups`
