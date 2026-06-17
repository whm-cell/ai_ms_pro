# Harness Optimization Decision Defaults

日期：2026-06-17
阶段：STAGE-00 Runtime Harness Foundation

## 新增功能

- 新增 [Harness Optimization Decision Defaults](../standards/harness-optimization-decision-defaults.md)，把 2026-06-17 外部 AI harness 趋势对比后的人工决策收敛为当前阶段默认路线。
- `scripts/run_task_outcome_eval_dataset.py` 现在在结果中输出 `model_usage`、`estimated_model_cost_usd`、`latency_budget_seconds` 和 `measurement_boundary`。
- `agent-run-provenance/v1` 新增必填 `run_metrics`，用于记录模型、token、成本、延迟和测量边界。

## 修复问题

- 避免 task outcome eval 的成本 proxy 只有 timeout 信息，无法机器区分本地 deterministic checks 与未来 model-backed runs。
- 避免 agent-run provenance 只记录 validation 和 claim boundary，却没有稳定位置表达模型、token、成本和延迟边界。

## 行为变化

- 同步 eval README、agent-run provenance 标准、tool contracts、check registry、capability model、working-context、stage status 和 index。
- 当前 deterministic task outcome eval 仍只运行 repo-local checks；默认 `model_usage=none`、estimated model cost 为 0。

## 破坏性变更

- `agent-run-provenance/v1` 样本和 validator 现在要求 `run_metrics`。现有 repo sample 已同步；后续新增 provenance 记录必须带该字段。

## 验证范围

- `run_metrics` 是可审计元数据，不是 hosted eval、生产 SLO、模型质量评分或产品级 agent runtime 证明。
- 本轮不启用外部发送、non-loopback trace probe、native sandbox、MCP / A2A runtime、hosted trace/eval 或真实 CI coding-agent workflow。
- sandbox、CI agent、hosted eval 和 MCP / A2A 方向继续按 comparison-only、task-shape gated 或 explicit-confirmation 路线处理。

```bash
python3 tests/test_task_outcome_eval_dataset.py
python3 tests/test_agent_run_provenance.py
.codex/hooks/run_with_repo_python.sh scripts/check_task_outcome_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/run_task_outcome_eval_dataset.py --dry-run
.codex/hooks/run_with_repo_python.sh scripts/check_agent_run_provenance.py
```

## 关联

- [Harness Capability Model](../harness-capability-model.md)
- [Agent Harness Eval Protocol](../evals/README.md)
- [Agent Run Provenance Standard](../standards/agent-run-provenance.md)
- [Tool Contracts](../tool-contracts/README.md)
