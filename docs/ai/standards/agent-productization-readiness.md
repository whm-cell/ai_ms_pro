# Agent Productization Readiness

更新时间：2026-06-12
状态：review-required standard

## 定位

本标准把“成熟产品级 agent 应具备的能力”沉淀为 repo-local readiness
模型，用于发现当前 harness-governed agent 或未来产品 agent 的短板。

它不是新的平台目标，也不是 blocking gate。当前项目仍保持
local-first harness control-plane；本标准只把外部调研、已有 harness
能力和当前 gap 转成可复查的检查面，避免后续构建 agent 时遗漏关键措施。

## 输入来源

- 2026-06-12 的外部 agent 产品化调研线程
  `019eb959-9194-7ed3-92be-e4be2661babf`。
- 当前 repo 的 `harness-capability-model`、agentic control matrix、eval
  protocol、tool contracts、runtime snapshot、local execution policy wrapper
  和 external harness decisions。

外部调研只作为 source-backed design input。任何 OpenAI hosted trace/eval、
MCP/A2A runtime、native sandbox、CI agent workflow 或外部执行能力仍必须走
现有 activation gates，不能由本标准自动声明完成。

## 能力域

模型文件 `agent-productization-readiness-model.json` 固定 12 个能力域：

1. runtime orchestration
2. tool and MCP boundary
3. memory and context governance
4. human-in-the-loop checkpoints
5. durable execution and resume
6. observability and tracing
7. eval harness
8. sandbox and permission model
9. multi-agent handoff
10. structured output contracts
11. cost and latency control
12. deployment and operations

评估文件 `agent-productization-readiness-assessment.jsonl` 记录当前
`ai-ms-pro-harness-control-plane` 对这些能力域的状态。`partial`、`missing`
或 `deferred` 都是 review findings，不是失败；它们用于提醒后续 agent
建设需要补齐对应设计、证据或边界说明。

## 检查命令

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_agent_productization_readiness.py
```

默认检查只在结构错误时失败。`partial`、`missing` 和 `deferred` 输出为
`REVIEW:`，便于 PR 作者或下一位 agent 看见缺口。只有将来有真实样本、误报率、
修复路径、CI 成本和 reviewer 负担记录后，才允许讨论 `--strict` 或 blocking
升级。

## 当前边界

- 不新增外部依赖。
- 不接 OpenAI hosted eval/trace、LangSmith、OTLP collector、MCP/A2A runtime
  或 CI agent workflow。
- 不把本地 trace、schema sample、advisory wrapper 或调研结论等同于产品
  agent 完成证明。
- 未来如果项目真的新增产品 agent，应新增对应 target assessment，而不是覆盖
  当前 harness control-plane 评估。
