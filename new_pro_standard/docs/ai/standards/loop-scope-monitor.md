# Loop / Scope Monitor Burn-in

更新时间：2026-05-25
状态：v1 / advisory

## 作用

本文件定义 Stop loop / scope monitor 的 burn-in 样本格式，用来记录真实长会话中 warning 是否有用、是否误报，以及后续动作是否应该是 checkpoint、缩小验证面或开启新 session。

它不是新的 blocking gate。Stop hook 仍只输出 warning-only `additionalContext`，不自动阻断、不自动 compact、不自动归档。

## 证据格式

样本使用 JSONL，每行一个 bounded 记录。默认样本位于 `loop-scope-monitor-samples.jsonl`。

字段：

- `id`：样本编号，格式为 `LOOP-SAMPLE-YYYY-MM-DD-*`。
- `gap_id`：采集模板写入 `GAP-RUNTIME-LOOP-SCOPE-WARNING`；旧样本缺省时由该 ledger 默认归属补齐。
- `sampled_at`：采样日期。
- `source_type`：`real-session`、`synthetic-regression` 或 `manual-review`。
- `task_summary`：任务摘要，不记录 prompt 或 transcript。
- `triggered_findings`：`repeated-command`、`repeated-failure`、`validation-loop`、`prompt-churn` 或 `none`。
- `monitor_recommendations`：`checkpoint`、`inspect-repeated-command`、`narrow-task`、`new-session`、`shrink-validation` 或 `none`。
- `outcome`：`accepted`、`pending` 或 `rejected`。
- `false_positive`：该 warning 是否被判为误报。
- `action_taken`：采样后采取的动作；accepted 样本必须填写。
- `evidence_refs`：必须指向存在的 repo-relative 共享治理文档、测试或命令引用；可带 markdown anchor、pytest node id 或 JSONL 行号 selector；不得引用 `.codex/runtime/*`。
- `note`：短说明。

## 当前规则

- raw transcript、prompt、cwd、完整工具输出和 `.codex/runtime/*` 路径不得进入共享样本。
- synthetic 样本只证明 schema 和 regression 覆盖，不计入真实 burn-in。
- accepted real warning sample 才能作为后续阈值、误报率或升级决策证据。
- `none` 不能和其他 finding / recommendation 混用。
- Stop warning `additionalContext` 会显示 finding codes、推荐 sample action codes 和 bounded sample capture gate，便于真实长会话 warning 发生后填充 pending placeholder；这些 codes 不是自动 checkpoint、阻断或 accepted evidence。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_loop_scope_monitor_samples.py
.codex/hooks/run_with_repo_python.sh scripts/check_warning_sample_code_alignment.py
python3 tests/test_loop_scope_monitor_samples.py
python3 tests/test_stop_loop_scope_monitor.py
python3 tests/test_warning_sample_code_alignment.py
```

## 边界

- 该检查只校验显式记录的样本，不读取本地 transcript，也不重新运行 Stop hook。
- 当前阶段保持 advisory；升级前必须先有真实长会话样本、误报率、用户中断成本和修复路径记录。
