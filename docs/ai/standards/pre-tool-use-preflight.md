# PreToolUse Preflight Burn-in

更新时间：2026-05-25
状态：v1 / advisory

## 作用

本文件定义 PreToolUse preflight guard 的 burn-in 样本格式，用来记录动作前 warning 是否有用、是否误报，以及后续动作是否改为 bounded output、draft、显式确认或取消。

它不是新的 blocking gate。PreToolUse hook 仍只输出 warning-only `additionalContext`，不执行、不授权、不阻断工具调用。

## 证据格式

样本使用 JSONL，每行一个 bounded 记录。默认样本位于 `pre-tool-use-preflight-samples.jsonl`。

字段：

- `id`：样本编号，格式为 `PRE-SAMPLE-YYYY-MM-DD-*`。
- `gap_id`：采集模板写入 `GAP-GUARDRAIL-PREFLIGHT-WARNING`；旧样本缺省时由该 ledger 默认归属补齐。
- `sampled_at`：采样日期。
- `source_type`：`real-tool-call`、`synthetic-regression` 或 `manual-review`。
- `task_summary`：任务摘要，不记录 prompt、raw command 或 transcript。
- `risk_summary`：风险摘要，只写类别和处理方式。
- `hook_result`：`warned` 或 `silent`。
- `triggered_findings`：`unbounded-large-output`、`destructive-command`、`externally-visible-command`、`external-tool-send` 或 `none`。
- `operator_decisions`：`bounded-output`、`explicit-confirmation`、`draft-prepared`、`cancelled`、`proceeded-as-is`、`no-action` 或 `none`。
- `outcome`：`accepted`、`pending` 或 `rejected`。
- `false_positive`：该 warning 是否被判为误报。
- `action_taken`：采样后采取的动作；accepted 样本必须填写。
- `evidence_refs`：必须指向存在的 repo-relative 共享治理文档、测试或命令引用；可带 markdown anchor、pytest node id 或 JSONL 行号 selector；不得引用 `.codex/runtime/*`。
- `note`：短说明。

## 当前规则

- raw command、prompt、cwd、完整工具输出、transcript 和 `.codex/runtime/*` 路径不得进入共享样本。
- synthetic 样本只证明 schema 和 regression 覆盖，不计入真实 burn-in。
- accepted real warning sample 才能作为后续阈值、误报率或升级决策证据。
- `silent` 样本必须使用 `triggered_findings: ["none"]`。
- `none` 不能和其他 finding / decision 混用。
- warning `additionalContext` 会显示 finding codes 和 bounded sample capture gate，便于真实 warning 发生后填充 pending placeholder；这些 codes 不是授权、阻断或 accepted evidence。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_pre_tool_use_preflight_samples.py
.codex/hooks/run_with_repo_python.sh scripts/check_warning_sample_code_alignment.py
python3 tests/test_pre_tool_use_preflight_samples.py
python3 tests/test_pre_tool_use_preflight.py
python3 tests/test_warning_sample_code_alignment.py
```

## 边界

- 该检查只校验显式记录的样本，不读取本地 transcript，也不重新运行 PreToolUse hook。
- 当前阶段保持 advisory；升级前必须先积累真实动作前 warning 样本、误报率、用户中断成本和修复路径。
