# Harness Capability Model

更新时间：2026-06-15
状态：starter capability direction

## 定位

本 starter 只提供 local-first agent harness 的公共机制层：

- runtime / governance / verification 三层边界
- bounded runtime recovery and evidence capture
- starter-safe checks, templates, and contract registries

它不声明新项目已经具备通用云端 agent platform、hosted orchestration、MCP/A2A runtime、native sandbox 或生产配置中心能力。

## 三条主线

新项目可按需启用以下能力方向：

1. `runtime durability`
   - execution snapshot
   - bounded checkpoint / resume
   - local execution state summary
2. `bounded observability / interop`
   - local traces and provenance samples
   - explicit local / remote claim boundary
   - remote interop contract only after project ADR or equivalent decision
3. `task-quality eval`
   - deterministic local eval dataset
   - task outcome dry-run checks
   - guardrail and workflow regression coverage

## 不变边界

- `.codex/runtime/*` 是本地恢复材料，不是 shared canonical truth。
- `docs/ai/*`、`docs/requirements/*`、checks、tool contracts 是共享真相与约束入口。
- Remote / hosted / MCP / A2A / external collector claims must be backed by project-specific accepted evidence.
- Starter ledger files are empty or synthetic unless a new project records its own bounded real samples.

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/summarize_harness_capabilities.py
.codex/hooks/run_with_repo_python.sh scripts/check_agent_productization_readiness.py
```
