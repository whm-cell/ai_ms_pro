# Harness Optimization Decision Defaults

更新时间：2026-06-17
状态：active decision defaults

## 定位

本文件把 2026-06-17 AI harness 趋势对比后的人工决策点转成
`ai_ms_pro` 当前阶段的默认选择。

当前默认目标仍是：

- local-first agent harness control-plane
- bounded runtime capability
- strong governance / verification / claim-boundary discipline

本文件不把项目切换为通用云端 agent platform，也不创建 hosted trace/eval、
native sandbox、MCP / A2A runtime、真实 CI coding-agent workflow 或外部副作用。

## 默认路线

| 决策面 | 当前默认 | 何时升级 |
| --- | --- | --- |
| Stage direction | 保持 STAGE-00 bounded capability，不整体 pivot 到产品级 autonomous runtime | 出现明确产品 agent workstream、部署目标和 owner |
| Cross-task resume | 优先采集非 harness 任务 accepted sample | 真实跨任务恢复证明减少重复探索或避免漏验证 |
| Remote trace interop | 只允许 ADR-017 下的 non-loopback `pilot-remote`，且需要 operator review | 有 endpoint、auth class、redaction、status、cost/stop boundary 和复核证据 |
| Cost / latency / model metadata | 默认记录为本地 deterministic：`model_usage=none`、cost=0；真实 agent run 必须显式记录 `run_metrics` | 进入 hosted/local model eval、产品 agent 或长任务趋势分析 |
| Native sandbox | comparison-only，不引入 provider 依赖，不声明 native sandbox | ADR 覆盖 mounted inputs/outputs、secrets、network、tool access、cost 和 isolation tests |
| CI / PR coding agent | 保持 advisory contract，不创建真实 workflow | 人工确认 permissions、secrets、PR write scope、rollback 和 GitHub plan 边界 |
| MCP / A2A runtime | task-shape gated；deterministic smoke 和 CI 默认继续 CLI / scripts / skills-first | 需要 persistent state、rich introspection、explicit interop 或跨系统 agent 协议 |
| Hosted / model-assisted eval | 可做 report-only comparison，不进入 blocking | 有真实运行样本、数据边界、成本预算和 reviewer workflow |
| GitHub remote gates | remote `UNKNOWN` 继续显式保留 | GitHub plan / repo setting 允许验证 branch protection / rulesets |

## 执行规则

1. 默认先补真实 evidence，不先补大 runtime。
2. 所有外部发送、远端验证、destructive、externally visible 或 permission-changing
   动作继续需要显式确认。
3. comparison-only ADR 可以默认推进；runtime dependency、external effect 和
   blocking 升级不能默认推进。
4. 本地 deterministic eval 和 provenance 必须把模型、成本、延迟边界写清楚；
   没有模型调用时写 `model_usage=none`，不得暗示 hosted eval 或模型质量结论。
5. 所有新增能力仍按 sample、误报率、修复路径、CI 成本和 owner evidence
   决定是否升级；不从趋势报告直接升级 blocking。

## 验证

相关变更至少运行：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_task_outcome_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/run_task_outcome_eval_dataset.py --dry-run
.codex/hooks/run_with_repo_python.sh scripts/check_agent_run_provenance.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```
