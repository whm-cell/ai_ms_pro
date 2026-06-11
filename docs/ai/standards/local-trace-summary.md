# Local Trace Summary Burn-in

更新时间：2026-05-25
状态：v1 / advisory

## 作用

本文件定义 Local Trace Summary 的 burn-in 样本格式，用来记录本地 no-network report 是否有用、是否保持 redaction / bounded 输出边界，以及它是否产生治理 promotion 线索。

它不是完整 trace system，也不证明 OpenAI、OTLP、MCP 或 A2A 互通。

## 证据格式

样本使用 JSONL，每行一个 bounded 记录。默认样本位于 `local-trace-summary-samples.jsonl`。

字段：

- `id`：样本编号，格式为 `TRACE-SUMMARY-SAMPLE-YYYY-MM-DD-*`。
- `gap_id`：采集模板写入 `GAP-TRACE-LOCAL-SUMMARY-BURNIN`；旧样本缺省时由该 ledger 默认归属补齐。
- `sampled_at`：采样日期。
- `source_type`：`real-local-report`、`synthetic-regression` 或 `manual-review`。
- `outcome`：`accepted`、`pending` 或 `rejected`。
- `summary_format`：`markdown` 或 `json`。
- `task_class`：real local report 的任务类别；accepted real report 必须使用非 `TBD` / `unknown` / `none` 的具体类别，升级讨论按 accepted distinct task classes 计数。
- `task_summary`：任务摘要，不记录 raw runtime path、prompt 或 transcript。
- `no_network` / `local_only`：accepted 样本必须为 `true`。
- `observation_count` / `trace_record_count` / `trace_count` / `promotion_needed_count` / `warning_count`：bounded 摘要计数。
- `redaction_states`：`redacted`、`not_applicable`、`unset` 或 `unknown`。
- `key_findings`：本次 report 产生的可复查发现。
- `action_taken`：采样后采取的动作。
- `evidence_refs`：必须指向存在的 repo-relative 共享治理文档、测试或脚本引用；可带 markdown anchor、pytest node id 或 JSONL 行号 selector；不得引用 `.codex/runtime/*`。
- `false_positive`：该 report 是否被判为误报。
- `note`：短说明。

## 当前规则

- raw transcript、prompt、cwd、完整工具输出和 `.codex/runtime/*` 路径不得进入共享样本。
- synthetic 样本只证明 schema、redaction 和 bounded output 回归，不计入真实 burn-in。
- accepted real report 只能证明本地 no-network summary 有用；不能被表述为远端 collector、OpenAI tracing、OTLP、MCP 或 A2A 互通。
- burn-in readiness 按 accepted real local report 的 distinct `task_class` 计数，避免同一任务类别的多条 report 误判为跨任务覆盖。
- 当前 accepted 样本包含 full-history JSON report、current-day focused JSON report 和 rolling two-day JSON report，但都属于 `harness-hardening`，因此当前 accepted task class 仍只有 1/3；rolling two-day 样本只增加同类本地 report 证据，不证明跨任务覆盖。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_local_trace_summary_samples.py
python3 tests/test_local_trace_summary_samples.py
python3 tests/test_summarize_runtime_traces.py
```

## 边界

- 该检查只校验显式记录的样本，不读取本地 runtime，也不重新生成 summary。
- 当前阶段保持 advisory；升级前必须先积累真实 report 样本、误报率、redaction 边界和治理 promotion 修复路径。
