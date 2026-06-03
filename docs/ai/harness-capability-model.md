# Harness Capability Model

更新时间：2026-06-03
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

## 运营视图

后续日常关注点收敛成 4 个面：

- durability coverage
- verified interop coverage
- task eval pass rate
- high-impact guardrail confirmation coverage

对应汇总命令：

```bash
.codex/hooks/run_with_repo_python.sh scripts/summarize_harness_capabilities.py
```
