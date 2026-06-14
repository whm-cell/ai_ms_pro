# Harness Capability Model

更新时间：2026-06-14
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
   - 新增 task outcome eval，衡量任务完成质量、过度行动、resume 稳定性和 guardrail posture
   - task outcome aggregate counts and blocked reason summary

## 不变边界

- `.codex/runtime/*` 仍是本地恢复材料，不是 canonical shared truth。
- `docs/ai/*`、`docs/requirements/*`、checks、tool contracts 仍是共享真相与约束入口。
- 任何 remote / hosted / MCP / A2A / OpenAI / external OTLP claim 都必须以当前 turn 验证或已接受证据为准。
- 新能力优先以 bounded local-first 方式落地，不先做多租户、分布式或 hosted orchestration。

## 支撑性护栏

2026-06-06 的五个反哺点只把支撑面补齐到 bounded evidence：

- cross-task resume：已有 checkpoint / queue 入口，但 accepted cross-task sample 仍为 0。
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
- Agent Productization Readiness 只作为 review-required 缺口雷达：固定产品 agent 的 12 个能力域，并把当前 harness control-plane 的 partial / deferred 短板显式输出；它不改变三条主线、不声明产品 agent 平台完成。
- Config Contract Boundary 作为 review-required 配置契约机制：`[config_contracts]` 声明 env template、本机 env、typed registry、扫描根、允许 literal path 和 pattern；`check_config_contract.py` 检查配置 key / secret-like key / 模型或 endpoint literal 不散落到未允许路径；`check_env_template_sync.py` 与 SessionStart hook 只比较 env key 集合，不读取、不输出、不覆盖 env 值。
- 该机制不提供生产配置中心、secret manager、Kubernetes / CI secret 或远端部署验证；provider-specific 规则必须由项目配置输入，不写死在通用 checker。

对应审计命令：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_external_harness_decisions.py
.codex/hooks/run_with_repo_python.sh scripts/check_config_contract.py
.codex/hooks/run_with_repo_python.sh scripts/check_env_template_sync.py --warning-only
```

## 运营视图

后续日常关注点收敛成 4 个面：

- durability coverage
- verified interop coverage
- task eval pass rate
- high-impact guardrail confirmation coverage
- config contract / env template drift

对应汇总命令：

```bash
.codex/hooks/run_with_repo_python.sh scripts/summarize_harness_capabilities.py
```
