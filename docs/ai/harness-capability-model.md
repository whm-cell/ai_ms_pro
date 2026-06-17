# Harness Capability Model

更新时间：2026-06-17
状态：active capability direction

## 定位

`ai_ms_pro` 当前目标不是演进成通用云端 agent platform，而是继续保持：

- local-first agent harness control-plane
- bounded runtime capability
- strong governance / verification / claim-boundary discipline

它保留 `runtime / governance / verification` 三层结构，但后续建设面从
“burn-in closeout”切到“能力增量建设”。

## 三条主线

后续新增能力只集中在以下 3 条主线：

1. `runtime durability`
   - execution snapshot
   - bounded checkpoint / resume
   - local execution state model
   - resume readiness / blocker summary
2. `bounded observability / interop`
   - local trace + bounded remote interop report
   - OTLP pilot evidence
   - future MCP/A2A/OpenAI-friendly contract shape
   - local-only / pilot-remote / verified-remote count and endpoint failure mode
3. `task-quality eval`
   - workflow/guardrail/tooling eval 继续保留
   - 新增 task outcome eval，衡量任务完成质量、过度行动、resume 稳定性、guardrail posture 和本地 model / cost / latency metadata
   - task outcome aggregate counts and blocked reason summary

## Bounded Loop Layer

2026-06-16 新增的 bounded loop triage 是三条主线之上的只读排序层：

- `scripts/summarize_loop_triage.py` 读取 capability summary 与 sample collection queue。
- 输出 `bounded-loop-triage/v1` markdown / JSON，列出 operator-reviewed `next_actions`。
- 默认候选动作指向现有 no-write / capture-card / dry-run 命令。
- 不写 ledger、不接受样本、不升级 blocking、不执行修复、不外发 payload。
- 不声明 scheduler runtime、planner/executor/reviewer runtime、MCP/A2A runtime、hosted eval/trace、native sandbox 或 CI agent workflow。

## 不变边界

- `.codex/runtime/*` 仍是本地恢复材料，不是 canonical shared truth。
- `docs/ai/*`、`docs/requirements/*`、checks、tool contracts 仍是共享真相与约束入口。
- 任何 remote / hosted / MCP / A2A / OpenAI / external OTLP claim 都必须以当前 turn 验证或已接受证据为准。
- 新能力优先以 bounded local-first 方式落地，不先做多租户、分布式或 hosted orchestration。

## 支撑性护栏

2026-06-06 的五个反哺点只把支撑面补齐到 bounded evidence：

- cross-task resume：已有 checkpoint / queue 入口，但 accepted cross-task sample 仍为 0。
- PreToolUse preflight：已有 2/2 accepted real warning samples（含 1 个 false positive），升级讨论结论为 `keep-advisory`，只支持 warning tuning，不支持 blocking。
- remote trace interop：loopback / localhost evidence 不能升级为 `verified-remote`。
- execution policy：`run_sandboxed_command.py` 是 local wrapper，metadata 明示 `native_sandbox=false`。
- multi-agent：planner / executor / reviewer 只作为 trace / provenance / eval 样例，不是 runtime scheduler。
- CI agent：`ci-agent-contract/v1` 是 PR-only / read-only advisory contract，不创建真实 GitHub agent workflow。

2026-06-07 已把四个外部 harness 方向转成 source-backed active bounded decisions；
2026-06-08 增加 evidence-backed default permission：

- remote trace pilot：当前不发送外部 payload；等待显式 endpoint、`--send` 确认和 operator review。
- external eval / sandbox：先做 comparison-only，不新增依赖、不声明 native sandbox。
- MCP / A2A：只保留 tool-contract / provenance 元数据方向，不进入 runtime prototype。
- CI agent workflow：继续 advisory contract，不创建真实 GitHub agent workflow。
- 每条 decision 都必须记录一手 `source_evidence`、positive signal 和 local upgrade scope；source 只提升决策质量、比较口径、metadata discipline 或边界可见性，不提升 hosted / remote / native runtime claim。
- 每条 active decision 也必须记录 `default_permission`：证据充分且对当前 harness 正向时，允许 bounded local/no-effect 小步默认推进；external send、verified remote、hosted eval、native sandbox、MCP/A2A runtime、真实 CI agent workflow 和外部副作用仍按 activation gates 阻断。
- 2026-06-16 已新增 Coding Agent / Browser Harness Selection：当前 coding-agent 对照物默认优先 `mini-swe-agent`，SWE-agent 主仓库保留为历史 / SWE-bench / trajectory 参考；deterministic browser smoke、CI gate 和 local static checks 默认优先 repo script + CLI / skills，MCP 只在 persistent state、rich introspection、exploratory automation 或显式 MCP interop 需要时进入评估。
- Agent Productization Readiness 只作为 review-required 缺口雷达：固定产品 agent 的 12 个能力域，并把当前 harness control-plane 的 partial / deferred 短板显式输出；它不改变三条主线、不声明产品 agent 平台完成。
- Config Contract Boundary 作为 review-required 配置契约机制：`[config_contracts]` 声明 env template、本机 env、typed registry、扫描根、允许 literal path 和 pattern；`check_config_contract.py` 检查配置 key / secret-like key / 模型或 endpoint literal 不散落到未允许路径；`check_env_template_sync.py` 与 SessionStart hook 只比较 env key 集合，不读取、不输出、不覆盖 env 值。
- 该机制不提供生产配置中心、secret manager、Kubernetes / CI secret 或远端部署验证；provider-specific 规则必须由项目配置输入，不写死在通用 checker。
- Bounded Loop Triage 只提升“下一步该看什么”的选择质量；它不把任何 advisory / review-required signal 自动变成执行、修复、样本接受或 blocking 升级。
- Mock Data Boundary 只提升产品页面/组件里大型 mock 数据的早期可见性；它不自动清理旧代码、不移动 fixture、不创建 API、不证明生产数据集成，也不默认阻断开发。
- Harness Optimization Decision Defaults 把 2026-06-17 趋势对比后的人工决策转成 bounded 默认路线：保持 STAGE-00 local-first，优先补真实 cross-task resume、remote pilot 和 model/cost/latency metadata；sandbox、CI agent、hosted eval 与 MCP/A2A 默认仍是 comparison-only 或 task-shape gated。
- `agent-run-provenance/v1` 的 `run_metrics` 和 task outcome runner 的 `model_usage` / `estimated_model_cost_usd` / `latency_budget_seconds` 只记录本地可审计边界；当前 deterministic 本地检查默认 `model_usage=none`，不声明 hosted eval、生产 SLO 或模型质量结论。

对应审计命令：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_task_outcome_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/run_task_outcome_eval_dataset.py --dry-run
.codex/hooks/run_with_repo_python.sh scripts/check_agent_run_provenance.py
.codex/hooks/run_with_repo_python.sh scripts/check_external_harness_decisions.py
.codex/hooks/run_with_repo_python.sh scripts/check_config_contract.py
.codex/hooks/run_with_repo_python.sh scripts/check_env_template_sync.py --warning-only
.codex/hooks/run_with_repo_python.sh scripts/summarize_loop_triage.py
.codex/hooks/run_with_repo_python.sh scripts/check_mock_data_boundary.py
```

## 运营视图

后续日常关注点收敛成 6 个面：

- durability coverage
- verified interop coverage
- task eval pass rate
- high-impact guardrail confirmation coverage
- config contract / env template drift
- mock data boundary review queue
- bounded loop next-action queue

对应汇总命令：

```bash
.codex/hooks/run_with_repo_python.sh scripts/summarize_harness_capabilities.py
.codex/hooks/run_with_repo_python.sh scripts/summarize_loop_triage.py
```
