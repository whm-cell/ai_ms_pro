# Harness Follow-up Convergence

日期：2026-06-03

## 新增功能

- `.codex/runtime/execution-snapshots/*`、`.codex/runtime/task-outcome-evals/*` 和 `.codex/runtime/trace-interop/*` 现在明确作为本地 runtime artifact ignore，不再作为 canonical shared truth。
- 新增一条 bounded high-impact confirmation real sample，记录本轮用户明确授权的本地 runtime artifact decanonization / governance 收敛动作。
- `summarize_harness_capabilities.py` 的 high-impact confirmation 统计改为读取 red-team ledger 中 `risk_family=human-confirmation` 且 `source_type=real-incident` 的 accepted 样本。

## 修复问题

- 修复 runtime verification artifact 被误纳入 tracked change surface 后容易混淆 canonical truth 与本地恢复材料的问题。
- 修复 capability summary 对 high-impact confirmation 使用不存在的 risk family，导致真实 `human-confirmation` 样本无法计数的问题。
- 将 ADR-002 和 ADR-003 归档到 `docs/ai/adr/archive/`，相关规则已由 AGENTS、runtime governance compression reference、reducer 和 checks 承接。
- 修复 GitHub PR-range CI 暴露的 trailing whitespace 和 sample readiness 测试漂移：`GAP-GUARDRAIL-CONFIRMATION` 已从 `needs-first-real-sample` 转为 `needs-more-real-samples`。
- 修复 task outcome eval dataset validator 在 CI checkout 中误把 repo-local `.codex/.venv/bin/python` 当作必须存在的 committed path。

## 维护降噪

- 压缩 Stage-00 status 和 working-context，只保留当前阶段判断、风险、边界和下一步。
- 把 Stop hook 的 session/payload/git 解析 helper 抽出，降低 `.codex/hooks/stop_runtime_session.py` 行数。
- 把 change-triggered follow-up rule builder 抽出，降低 `scripts/change_triggered_followup_rules.py` 行数。

## 行为变化

- Capability summary 现在能把 accepted real `human-confirmation` 样本计入 high-impact guardrail confirmation coverage。
- `check_context_budget.py` 不再报告 default surface / ADR count warning。
- 本地 runtime probe / eval / snapshot 输出继续生成到 `.codex/runtime/*`，但默认不进入 git change surface。

## 破坏性变更

- 移除此前 tracked 的 `.codex/runtime/*` JSON verification artifacts；稳定样本和标准保留在 docs / standards / tests 中。
- 未改变 runtime hook、checker CLI、eval runner CLI 或 trace interop report schema 的兼容字段。

## 边界保持

- 未新增 hosted runner、OpenAI hosted trace、MCP、A2A、native sandbox 或长期 external collector。
- Cross-task resume 仍缺 accepted real sample；本轮是 harness maintenance，不满足“非 harness-hardening 任务类”的采样条件。
- 本轮 high-impact confirmation 只证明 local repo governance action 的用户授权边界，不证明 remote merge、release、deploy、权限变更或外部发送。

## 验证范围

```bash
python3 tests/test_runtime_stop_hooks.py
python3 tests/test_change_triggered_followups.py
python3 tests/test_harness_pending_samples.py
.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py
.codex/hooks/run_with_repo_python.sh scripts/check_agentic_red_team_samples.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all
python3 -m unittest discover -s tests
git diff --check origin/main...HEAD
```
