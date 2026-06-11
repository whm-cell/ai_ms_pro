# Changelog: Stage Checkpoint Artifact

更新时间：2026-05-24
阶段或版本：stage-00 runtime harness hardening
状态：已确认

## 新增功能

- 新增 `docs/ai/checkpoints/stage-checkpoints.jsonl`，作为 `stage-checkpoint/v1` bounded resume artifact。
- 新增 `docs/ai/checkpoints/resume-samples.jsonl`，记录真实 continuation / resume 样本，当前已有 2/2 accepted samples；样本显式标注 `resume_scope`。
- 新增 `docs/ai/checkpoints/README.md`，定义 checkpoint 与 handoff/status/runtime 的边界。
- 新增 `scripts/check_stage_checkpoints.py` 与 `tests/test_stage_checkpoints.py`，校验 checkpoint schema、stage/status、恢复提示、下一步、evidence、REQ/WS、resume samples 和 raw runtime 边界。

## 修复问题

- 修复 Agentic Harness Gap Roadmap G2 只有“定义 checkpoint artifact”目标、没有可复跑 checkpoint artifact 和 checker 的缺口。

## 行为变化

- governance workflow 会验证 checkpoint artifact 的结构；该检查保持 advisory。
- changed-file follow-up 会在 checkpoint artifact、checker 或测试变更时提示对应验证命令。
- checkpoint burn-in 从未来样本推进到 2/2 accepted samples；checker 现在显式报告 accepted cross-task sample 为 0。因两个样本都来自同一 harness-hardening 线程，仍不足以升级 blocking 或 always-on。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_stage_checkpoints.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_stage_checkpoints.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage Checkpoints](../checkpoints/README.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
