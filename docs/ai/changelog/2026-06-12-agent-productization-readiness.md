# Agent Productization Readiness

日期：2026-06-12
阶段：STAGE-00 Runtime Harness Foundation

## 新增功能

- 新增 `agent-productization-readiness/v1` 标准文档和模型，固定 12 个产品级
  agent 能力域：runtime orchestration、tool/MCP、memory、HITL、
  durable execution、observability/tracing、eval、sandbox/permission、
  multi-agent handoff、structured output、cost/latency、deployment/ops。
- 新增 `agent-productization-assessment/v1` 当前评估，记录
  `ai-ms-pro-harness-control-plane` 的 covered / partial / deferred 状态。
- 新增 `scripts/check_agent_productization_readiness.py` 与单元测试，用于验证
  model / assessment 结构、证据引用和 target coverage，并把短板输出为
  `REVIEW:`。
- 新增 changed-file follow-up 路由，确保 readiness 标准、评估、脚本或测试
  变化时会提示运行对应检查。

## 修复问题

- 修复“构建 agent 时需要人工记得完整产品化清单”的隐性风险，把外部调研结论
  转成 repo-local 可复查缺口雷达。
- 修复 standards 路由过长导致默认上下文预算压力增大的问题，`index` 只保留
  稳定入口，细节从 `standards/` 目录按需进入。
- 修复 runtime execution snapshot 校验在 Windows 路径分隔符下误报
  `working_context_path` 的问题。

## 行为变化

- `check_agent_productization_readiness.py` 默认只在结构错误时失败。
- 当前 partial / deferred 状态会以 `REVIEW:` 输出，提醒后续补设计、证据或
  target-specific assessment。
- `check_change_triggered_followups.py` 会在 readiness 标准、评估、脚本或测试
  变化时建议运行新检查器。

## 破坏性变更

- 无。不新增外部依赖，不接 hosted trace/eval，不创建 MCP/A2A runtime、
  native sandbox、CI agent workflow 或产品 agent 平台。

## 验证范围

```bash
.codex/hooks/run_with_repo_python.ps1 scripts/check_agent_productization_readiness.py
python tests/test_agent_productization_readiness.py
python tests/test_change_triggered_followups.py
python tests/test_runtime_execution_snapshots.py
python -m unittest discover -s tests
```

## 关联文档

- [Agent Productization Readiness](../standards/agent-productization-readiness.md)
- [Check Registry](../check-registry.md)
- [Harness Capability Model](../harness-capability-model.md)
