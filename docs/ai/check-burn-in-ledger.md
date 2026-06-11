# Check Burn-in Ledger

更新时间：2026-05-25
状态：v1 / advisory evidence ledger

## 作用

本文件记录 `blocking-candidate` checks 的升级证据，避免只在
`check-registry.md` 写“需要真实样本、误报率和修复路径”，但没有可审计账本。

它不是新的阻断规则；升级为 `blocking` 仍必须进入 `status` 或 `ADR`。

## Candidate Ledger

| Check | Accepted samples | Evidence refs | False positives | Repair path | Cost | Current decision | Next evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `check_code_shape.py` | 2/2 | scripts/check_burn_in_ledger.py, tests/test_check_burn_in_ledger.py, scripts/change_triggered_followup_rules.py, tests/test_change_triggered_followups.py, docs/ai/changelog/2026-05-25-code-shape-burn-in-sample.md, docs/ai/changelog/2026-05-25-code-shape-followup-rule-sample.md | 2 accepted; no false positive in evidence-ref checker/test slice or follow-up rule wiring slice; code-shape surfaced the oversized follow-up rule file and the repair kept the file within budget | split oversized files, compress narrow rule additions, or document scoped exception | low local runtime; reviewer sees shape drift before it becomes harder to split | keep-candidate | upgrade decision review before any ready-for-adr or promote-to-blocking change; collect broader non-harness changed-file samples |
| `check_pr_touch_conflicts.py` | 0/2 | - | 0 accepted; PR #11 remains pending evidence only | coordinate touch-set, split PR, or record explicit reviewer decision | medium reviewer cost for high-risk files | keep-candidate | two real multi-person or multi-agent PR overlap samples |
| `check_requirements_shape.py` | 0/2 | - | 0 accepted | add source trust, instruction handling, sanitization, REQ/WS metadata | medium author cost during PRD import | keep-candidate | two PRD/source-boundary samples with clear repair path |
| `check_agent_trace_schema.py` | 0/2 | - | 0 accepted | fix trace producer, schema, or sample adapter mismatch | low local runtime; medium schema review cost | keep-candidate | two real runtime trace-file batch validations |
| `check_tool_contracts.py` | 2/2 | docs/ai/tool-contracts/contracts.json, tests/test_tool_contracts.py, docs/ai/changelog/2026-05-25-burn-in-ledger-structured-progress.md, docs/ai/changelog/2026-05-25-burn-in-ledger-evidence-refs.md | 2 accepted; no false positives in burn-in ledger structured progress and evidence-ref contract updates | add or correct tool contract fields, side effects, automation mode, and verification commands | low local runtime; medium review for high-impact tools | keep-candidate | upgrade decision review before any ready-for-adr or promote-to-blocking change |
| `check_workspace_sandbox.py` | 0/2 | - | 0 accepted | correct manifest claims, path policy, or rehydration evidence | low local runtime; medium claim-honesty review | keep-candidate | two sandbox/rehydration samples without over-claiming provider support |
| `check_runtime_token_budget.py` | 0/2 | - | 0 accepted | reduce tool output, use raw artifacts, split session, or tune threshold with evidence | low local runtime; medium task-interruption cost if strict | keep-candidate | two real long-session transcript audits with false-positive review |

## 规则

- `Accepted samples` 使用 `N/2` 形式；`N` 不能超过 2，`2/2` 只是进入升级讨论的最低门槛，不自动升级。
- `Evidence refs` 必须指向能审计 accepted 样本的 repo-relative 文件、测试或 changelog；可带 markdown anchor、pytest node id 或 JSONL 行号 selector，但底层路径必须存在；`Accepted samples` 大于 0 时不能为空。
- `False positives` 记录已接受样本中的误报情况；不确定时写 `0 accepted`，不要伪造样本。
- `Repair path` 必须描述实际修复动作，不能只写“fix it”。
- `Cost` 必须同时考虑本地/CI 成本和 reviewer 或任务中断成本。
- `Current decision` 允许值：`keep-candidate`、`ready-for-adr`、`demote-to-advisory`、`promote-to-blocking`。
- `ready-for-adr` 与 `promote-to-blocking` 必须已有 `2/2` accepted samples；低于 `2/2` 时只能保持候选或降级。
- `2/2` 但仍为 `keep-candidate` 的行必须在 `Next evidence` 指向 upgrade decision review；它会进入 `upgrade_review_needed_checks`，但不会自动升级。
- `upgrade_review_needed_checks` 必须在 `docs/ai/standards/check-burn-in-upgrade-decisions.jsonl` 有 bounded 决策行，并由 `scripts/check_burn_in_upgrade_decisions.py` 校验样本快照、当前决策、后续证据和本地 runtime 引用边界。
- 任一升级或降级必须进入 `status` 或 `ADR`，本文件只保存证据账本。
