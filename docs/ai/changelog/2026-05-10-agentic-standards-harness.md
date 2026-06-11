# 2026-05-10 Agentic Standards Harness

更新时间：2026-05-10
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 standard agent trace schema、JSON Schema、JSONL sample 和 `scripts/check_agent_trace_schema.py`，为后续 runtime observation / trace export 提供 dependency-free contract。
- 新增 agent harness eval dataset 与 `scripts/check_agent_eval_dataset.py`，把 simple code、requirements traceability、high-impact guardrail 和 resume/runtime reduction 做成可校验样本。
- 新增 tool contract registry 与 `scripts/check_tool_contracts.py`，记录 repo tools 的 side effects、permissions、timeout、automation mode、destructive / externally-visible 边界。
- 新增 P0 Python linter 层：`pyproject.toml` 配置 Ruff，`.codex/requirements.txt` 固定 Ruff 版本，governance workflow 安装依赖并运行 Ruff。
- 新增 Stop hook trace producer：在保留 `.codex/runtime/observations/*.jsonl` 的同时，输出本地 `agent-trace/v1` JSONL 到 `.codex/runtime/observations/agent-traces/`。
- 新增 external standards crosswalk，映射 OpenAI Agents SDK、Anthropic agent patterns、MCP、W3C Trace Context、OpenTelemetry GenAI、OWASP、NIST AI RMF / GenAI profile 和 A2A deferred gap。
- 新增 eval `trace_expectations` 字段校验，把 Stop trace producer、eval dataset 和 tool contract registry 串成 shape-level 闭环。
- 新增 `scripts/run_agent_eval_dataset.py`，对 eval dataset 的 `expected_checks` 做本地执行或 `--dry-run`，并用确定性规则输出 `pass` / `warn` / `review-required` / `fail`；执行模式会绑定声明的 trace id、artifact 和 redaction state。
- 新增 `scripts/export_agent_trace.py`，把 `agent-trace/v1` JSONL 转为本地 `local-otel-json` adapter payload，并新增 no-network `otlp-http-json` pilot；只有显式 `--send --endpoint` 才会 POST 并记录 `network_exported=true`。
- 新增 `scripts/collect_harness_sample_gaps.py` 和 `--使用细节/真实场景覆盖缺口待确认.md`，集中列出 security evidence、AI guardrail、workflow skills 与远端互通的真实样本缺口。
- 新增 [Agentic Control Matrix](../security/agentic-control-matrix.md)，把 OWASP / NIST 风格风险映射到 repo 控制面、证据面和 blocking 升级边界。

## 修复问题

- 补齐此前缺少的标准 trace、标准 eval dataset 和标准 tool contract 三类可校验 contract，避免这些 agentic harness 能力只停留在说明文档或口头约定。
- 补齐此前缺少的传统 linter / whitespace gate，避免 Python harness 只能靠 code-shape 和 unit tests 发现基础语法与导入类问题。
- 补齐此前 `agent-trace/v1` 只有 schema/sample、没有 runtime producer 的缺口。
- 关闭 OPEN-14 主 code-shape 债务：拆分 `check_ai_governance.py`、`bootstrap_harness.py` 与 `check_agent_eval_dataset.py`，当前 code-shape 无 warning。

## 行为变化

- `Governance And Smoke` workflow 现在运行 agent trace schema、agent eval dataset 和 tool contract checks。
- `Governance And Smoke` workflow 现在安装 `.codex/requirements.txt`，运行 `git diff --check` 和 `python3 -m ruff check .codex/hooks scripts tests`。
- `check_change_triggered_followups.py` 会在 trace standard、eval dataset 或 tool contract registry 改动时提示对应 follow-up check。
- `check_change_triggered_followups.py` 会在 linter config、dependency 或 CI entrypoint 改动时提示 Ruff / whitespace follow-up。
- `Governance And Smoke` workflow 现在运行 eval runner `--dry-run`、trace sample local export 和 harness sample gap collector；OTLP pilot 保持显式命令 / 单测验证，不默认上传网络。
- `docs/ai/index.md` 和 verification reference 增加三个 standard surface 的入口与常用命令。
- `docs/ai/index.md` 现在路由 external standards crosswalk。
- Candidate workflow skills 虽达到 2/2 accepted 样本，但 2026-05-10 复核结论是继续保持 Candidate，不升级 Stable / always-on。

## 破坏性变更

- 无。现有 `.codex/runtime/*` 文件不迁移；新增 trace producer 只追加本地 runtime trace 原料。

## 后续观察

- Stop trace producer 已输出 `agent-trace/v1` 本地 trace；后续如需跨系统互通，再单独评估 W3C Trace Context、OpenTelemetry/OpenAI exporter、MCP 或 A2A。
- 本地 trace export adapter 和 OTLP HTTP JSON pilot 只证明转换层与显式 endpoint 证据链，不证明 OpenAI hosted traces、MCP、A2A 或外部 collector 已纳入生产互通。
- Ruff 当前覆盖 `E9` 与 Pyflakes `F`；semantic standards honesty、tool contract completeness 和 security policy 仍由 governance docs / checks / review 承担。
- Agent eval dataset 已有本地 runner 和 deterministic grader；CI 默认只跑 `--dry-run`，真实执行和升级 blocking 仍需要更多样本。
- Eval `trace_expectations` 当前由 checker 校验字段与 contract 引用；runner 执行模式会读取声明的本地 trace evidence，但仍不调用 hosted eval、不判断模型质量。
- Tool contract registry 当前覆盖核心 harness tools；新增 MCP-like tool 或高影响命令时，应先补 contract 再决定 hook / CI / manual automation mode。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_trace_schema.py`
- `.codex/hooks/run_with_repo_python.sh scripts/export_agent_trace.py --input docs/ai/standards/agent-trace-sample.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/export_agent_trace.py --input docs/ai/standards/agent-trace-sample.jsonl --format otlp-http-json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`
- `.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --dry-run`
- `.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --id EVAL-005-stop-trace-evidence-contract`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/collect_harness_sample_gaps.py`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `python3 -m unittest discover -s tests -p 'test_runtime_stop_hooks.py'`
- `.codex/.venv/bin/python -m unittest tests.test_agent_trace_schema tests.test_agent_trace_export tests.test_agent_eval_dataset tests.test_agent_eval_runner tests.test_tool_contracts tests.test_harness_sample_gaps tests.test_change_triggered_followups`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/standards/agent-trace-schema.md docs/ai/evals/agent-harness-evals.jsonl docs/ai/tool-contracts/contracts.json --markdown`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `git diff --check`

## 关联文档

- [Agent Trace Standard](../standards/agent-trace-schema.md)
- [Agent Harness Evals](../evals/README.md)
- [Tool Contracts](../tool-contracts/README.md)
- [Agentic Control Matrix](../security/agentic-control-matrix.md)
- [External Standards Crosswalk](../standards/agentic-harness-crosswalk.md)
- [Check Registry](../check-registry.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
