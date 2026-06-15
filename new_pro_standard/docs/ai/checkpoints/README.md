# Stage Checkpoints

更新时间：2026-06-15
状态：starter / advisory

## 作用

本目录保存 durable execution state 的最小共享 artifact 形状。

它不是执行引擎，也不替代 `handoff`、`status`、ADR 或 requirements；它只为较长阶段任务提供可恢复、可校验的 checkpoint schema 和 sample ledger 入口。

## 文件

- `stage-checkpoints.jsonl`：当前 checkpoint 记录，每行一个 `stage-checkpoint/v1` JSON object。
- `resume-samples.jsonl`：真实 continuation / resume 样本，每行一个 `stage-checkpoint-resume-sample/v1` JSON object。

Starter 默认只预置一条 `planned` 状态的 schema checkpoint，供 resume sample 模板引用；不预置 accepted resume 样本。新项目应在真实长任务或阶段任务出现后再写入 bounded records。

## 使用规则

- checkpoint 只能引用 bounded shared artifacts，例如 `docs/ai/*`、`docs/requirements/*`、脚本或验证命令。
- 不得把 raw transcript、prompt、cwd、完整工具输出或 `.codex/runtime/*` 路径写入 checkpoint。
- `complete` checkpoint 必须有已经通过或不适用的 evidence；仍有 `pending` / `failed` evidence 时保持 `in_progress` 或 `blocked`。
- 真实 resume 样本积累前，该能力保持 advisory。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_stage_checkpoints.py
```
