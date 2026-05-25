# Stage Checkpoints

更新时间：2026-05-25
状态：v1 / advisory

## 作用

本目录保存 G2 durable execution state 的最小共享 artifact。

它不是执行引擎，也不替代 `handoff`、`status`、ADR 或 requirements；它只在较长阶段任务中记录一个可恢复、可校验的 checkpoint：当前目标、恢复提示、下一步、证据和边界。

## 文件

- `stage-checkpoints.jsonl`：当前 checkpoint 记录，每行一个 `stage-checkpoint/v1` JSON object。
- `resume-samples.jsonl`：真实 continuation / resume 样本，每行一个 `stage-checkpoint-resume-sample/v1` JSON object。

## 使用规则

- checkpoint 只能引用 bounded shared artifacts，例如 `docs/ai/*`、`docs/requirements/*`、脚本或验证命令。
- 不得把 raw transcript、prompt、cwd、完整工具输出或 `.codex/runtime/*` 路径写入 checkpoint。
- `complete` checkpoint 必须有已经通过或不适用的 evidence；仍有 `pending` / `failed` evidence 时保持 `in_progress` 或 `blocked`。
- 真实 resume 样本积累前，该能力保持 advisory。
- `accepted` resume sample 必须说明使用了哪个 checkpoint、避免了什么重复探索或遗漏验证，以及仍缺什么字段或证据。
- resume sample 的 `evidence_refs` 必须指向存在的 repo-relative 共享文档、脚本或测试；可带 markdown anchor、pytest node id 或 JSONL 行号 selector，不得引用 raw runtime。
- `resume_scope` 必须标注为 `same-task` 或 `cross-task`；跨任务样本缺失时 checker 会保留 warning。
- 当前 `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` 的新增 pending 采样目标是跨任务 resume；`check_harness_sample_append.py` 会拒绝未把 `resume_scope` 设为 `cross-task`，或仍沿用模板 checkpoint id `CP-2026-05-24-agentic-harness-burnin` 的候选。
- 采集模板会在 resume sample 中写入 `gap_id: GAP-RUNTIME-STAGE-CHECKPOINT-RESUME`；旧样本缺省时由 `resume-samples.jsonl` ledger 默认归属补齐。
- 当前最小 burn-in 已达到 2/2 accepted samples，但两个样本都来自同一 harness-hardening 线程；跨任务样本出现前不升级 blocking 或 always-on。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_stage_checkpoints.py
python3 tests/test_stage_checkpoints.py
```
