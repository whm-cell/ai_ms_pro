# Harness Sample Gap Evidence Record Template

更新时间：YYYY-MM-DD

用途：为 `docs/ai/standards/harness-sample-gap-evidence.jsonl` 准备单条候选记录。

本模板不是 evidence。生成的候选记录必须先通过 no-write review gate，人工确认后才可写入 ledger；写入后仍不能自动变成 accepted evidence，除非 `outcome=accepted` 且 checker 通过。

## 边界

- 不接受 synthetic、placeholder、local-only、dry-run、localhost-only 或模板草稿作为 accepted real evidence。
- 不记录 prompt、raw transcript、完整 tool output、secret、account id、runtime JSONL 路径或旧项目 ledger row。
- `evidence_refs` 必须是新项目仓库内的 bounded 证据路径。
- starter 默认 ledger 为空；不要从旧项目复制 accepted、pending 或 rejected rows。

## 生成命令

```bash
.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --sample-template
```

## 复核命令

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py --samples <candidate-jsonl>
```

## JSONL 形状

```json
{"schema_version":"harness-sample-gap-evidence/v1","id":"GAP-SAMPLE-YYYY-MM-DD-replace-me","gap_id":"GAP-GUARDRAIL-CONFIRMATION","sampled_at":"YYYY-MM-DD","source_type":"real-user-action","outcome":"pending","local_only":true,"no_external_claim":true,"false_positive":false,"network_exported":false,"endpoint_scope":"none","remote_status":"none","sample_summary":"Replace with a bounded real-event summary.","decision":"Pending review; do not count as accepted evidence.","boundary_note":"Use bounded project evidence only; no raw transcript or runtime material.","action_taken":["replace with operator action"],"evidence_refs":["docs/ai/harness-real-sample-watchlist.md"],"checker_refs":["scripts/check_harness_sample_gap_evidence.py"]}
```
