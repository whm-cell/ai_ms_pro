# Bounded Loop Triage

更新时间：2026-06-16
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 [Bounded Loop Triage](../standards/bounded-loop-triage.md) 标准，明确 loop engineering 在当前项目中的落点是只读 triage layer。
- 新增 `scripts/summarize_loop_triage.py`，把 capability summary 与 actionable sample collection queue 汇总为 `bounded-loop-triage/v1` next-action candidates。
- 新增 `tests/test_summarize_loop_triage.py`，覆盖 no-write boundary、capability-driven actions 和 queue-driven capture lane actions。
- `docs/ai/tool-contracts/contracts.json` 登记 `summarize_loop_triage` contract。

## 修复问题

- 将“loop engineering 是否落地”的判断从口头建议变成可运行的只读 triage report。
- 避免把 loop 方向误解为自动修复、自动采样或 agent platform claim。

## 行为变化

- `summarize_loop_triage.py` 现在可以输出 markdown 或 JSON 的 operator-reviewed next-action candidates。
- `check-registry`、tool contracts、capability model、working-context、status 和 `$harness-maintenance` references 已同步该 advisory surface。

## 破坏性变更

- 无。

## 边界

- 不自动执行候选动作。
- 不写 ledger、不接受样本、不升级 blocking。
- 不声明 scheduler runtime、planner/executor/reviewer runtime、MCP/A2A runtime、hosted trace/eval、native sandbox 或真实 CI agent workflow。
- 外部发送、destructive、permission-changing 或 externally visible 动作仍需显式确认。

## 验证范围

```bash
python3 tests/test_summarize_loop_triage.py
.codex/hooks/run_with_repo_python.sh scripts/summarize_loop_triage.py --json
.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```

## 关联文档

- [Bounded Loop Triage](../standards/bounded-loop-triage.md)
- [Harness Capability Model](../harness-capability-model.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
