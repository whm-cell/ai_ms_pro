# Check Burn-in Ledger

更新时间：2026-06-15
状态：starter empty ledger

本 ledger 只为 `blocking-candidate` check 提供 starter-safe 记录形状。所有 accepted samples 默认为 `0/2`，不代表新项目已有真实 burn-in evidence。

| Check | Accepted samples | Evidence refs | False positives | Repair path | Cost | Current decision | Next evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `check_agent_trace_schema.py` | 0/2 | - | none recorded | Add bounded trace schema samples and repair notes before promotion. | local checker cost only | keep-candidate | collect two accepted real samples |
| `check_code_shape.py` | 0/2 | - | none recorded | Record false positives and split guidance before tightening. | local checker cost only | keep-candidate | collect two accepted real samples |
| `check_github_guardrails.py` | 0/2 | - | none recorded | Verify remote branch protection/rulesets and document repair path. | manual GitHub verification cost | keep-candidate | collect two accepted real samples |
| `check_pr_touch_conflicts.py` | 0/2 | - | none recorded | Record overlap decisions, merge outcomes, and false positives. | PR review cost only | keep-candidate | collect two accepted real samples |
| `check_requirements_shape.py` | 0/2 | - | none recorded | Record source-boundary and traceability false positives before promotion. | local checker cost only | keep-candidate | collect two accepted real samples |
| `check_tool_contracts.py` | 0/2 | - | none recorded | Record missing contract and high-impact tool repair path before promotion. | local checker cost only | keep-candidate | collect two accepted real samples |
