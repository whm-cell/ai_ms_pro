# Bounded Loop Triage

更新时间：2026-06-16
状态：advisory loop layer

## 定位

`bounded-loop-triage` 是当前 harness 之上的只读 loop 层。它把现有能力摘要、
真实样本队列、task outcome eval 和 guardrail 缺口排序成下一步候选动作。

它不是 agent runtime、scheduler、MCP / A2A runtime、hosted eval/trace、
native sandbox 或 CI agent workflow。

## 当前实现

- `scripts/summarize_loop_triage.py` 读取现有 capability summary 与 sample
  collection queue。
- 输出 markdown 或 JSON 的 `bounded-loop-triage/v1` 报告。
- 报告包含 `next_actions`，每条候选动作都保留 operator-reviewed 边界。
- 默认只建议现有 no-write / capture-card / dry-run 命令，不执行候选动作。

## Loop 层规则

1. 只读 triage 可以默认运行。
2. 任何候选动作都必须由主 Agent 或 reviewer 选择后再执行。
3. 报告不得写 ledger、不得接受样本、不得升级 blocking、不得编辑业务代码。
4. 外部发送、远端验证、destructive 或 externally visible 动作仍需显式确认。
5. 真实样本、升级决策和 canonical 文档发布仍走既有 no-write candidate gate 与主 Agent 语义判断。

## 适用场景

- 需要从多个 advisory / review-required 信号里选择下一步工作。
- 长任务恢复后，需要快速确认当前最值得推进的 loop lane。
- 定期 automation 需要生成只读 triage 报告，但不能自动改仓库或外发。

## 非目标

- 不自动清理 legacy code。
- 不把 task outcome eval 的 warning 自动转成修复提交。
- 不主动制造 PreToolUse / Stop warning 或 red-team incident。
- 不把本地 runtime artifact 当作共享 truth。
- 不声称 `ai_ms_pro` 已具备产品级 autonomous loop runtime。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/summarize_loop_triage.py
.codex/hooks/run_with_repo_python.sh scripts/summarize_loop_triage.py --json
python3 tests/test_summarize_loop_triage.py
.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py
```
