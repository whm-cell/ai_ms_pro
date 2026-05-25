# Harness Real Sample Watchlist

更新时间：2026-05-25
状态：event-driven watchlist

## 作用

本文件保存 `agentic-harness-gap-roadmap.md` 中暂时无法主动验证的真实样本缺口。

这些缺口不是每日待办，也不是要求 Agent 反复构造场景补齐的覆盖率任务。只有遇到真实事件时才唤醒对应 lane，并先走 no-write review gate，再决定是否写入样本账本。

## 执行规则

- 不为了补齐 `0/2` 或 `1/3` 人工制造 synthetic evidence。
- 不把 placeholder、template、local-replay、local-only、approved contract 或 no-write candidate 当成 accepted real evidence。
- 不重复运行全量 planner / intake / readiness 来“刷进度”；平时只保留本 watchlist。
- 真实事件发生后，先运行对应 lane review command；通过后再按 checker 输出更新目标 JSONL 或 decision ledger。
- `.codex/runtime/*`、raw transcript 和完整工具输出只作为本地恢复材料；进入共享 docs 前必须压缩成 bounded evidence ref。

## 当前快照

- 来源：`scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- tracked gaps：20
- actionable real-sample lanes：15
- append-new-pending-slot：13
- fill-existing-placeholder：2
- ready-for-upgrade-discussion：4，全部 `keep-advisory`
- local-sample-only：1
- contract / ADR blockers：0

## 唤醒触发器

| Trigger | Gap IDs | What qualifies | First review command |
| --- | --- | --- | --- |
| 真实 PreToolUse warning | `GAP-GUARDRAIL-PREFLIGHT-WARNING` | 高风险、大输出、外发、破坏性或 remote-write 动作前真实触发 warning，并记录 operator decision / action taken / false-positive 结论 | `scripts/check_harness_placeholder_replacement.py <candidate-jsonl>` |
| 真实 Stop loop/scope warning | `GAP-RUNTIME-LOOP-SCOPE-WARNING` | 长 session、重复命令、重复失败、过度验证或 scope churn 真实触发 Stop warning | `scripts/check_harness_placeholder_replacement.py <candidate-jsonl>` |
| 跨任务 checkpoint resume | `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` | 非 harness-hardening 任务中使用 stage checkpoint 恢复，并证明减少重复探索或避免遗漏验证 | `scripts/check_harness_sample_append.py <candidate-jsonl>` |
| 不同 task class 的 local trace report | `GAP-TRACE-LOCAL-SUMMARY-BURNIN` | 非 `harness-hardening` 任务生成 no-network local trace summary，并带 bounded evidence | `scripts/check_harness_sample_append.py <candidate-jsonl>` |
| 真实 security workflow / dependency event | `GAP-SEC-SCHEDULED-RUN`, `GAP-SEC-PR-DEPENDENCY` | scheduled/manual security evidence run、dependency PR、release、CodeQL、SBOM 或 dependency-review 真实事件 | `scripts/check_harness_sample_append.py <candidate-jsonl>` |
| 显式用户确认的高影响动作 | `GAP-GUARDRAIL-CONFIRMATION` | 真实 destructive、externally visible、permission-changing、secret/env、deploy/release 等动作，且用户明确确认 | `scripts/check_harness_sample_append.py <candidate-jsonl>` |
| workflow skill 真实任务 | `GAP-WORKFLOW-CROSS-WS`, `GAP-WORKFLOW-SIMPLE-SKIP`, `GAP-WORKFLOW-PR-OVERLAP` | 跨 workstream 技能加载、简单任务明确跳过技能、多 Agent / 多人 PR touch overlap 的真实样本 | `scripts/check_harness_sample_append.py <candidate-jsonl>` |
| 真实 red-team incident | `GAP-AGENTIC-TOOL-SQUATTING`, `GAP-AGENTIC-MEMORY-POISONING`, `GAP-AGENTIC-A2A-HANDOFF`, `GAP-AGENTIC-CASCADE-STOP` | 工具/skill 冒名、memory poisoning、A2A/handoff 权限混乱、cascade/rogue loop 等真实 incident | `scripts/check_harness_sample_append.py <candidate-jsonl>` |
| 真实 remote interop probe | `GAP-TRACE-REMOTE-INTEROP` | 带真实 auth / endpoint / redaction / cost boundary 的 OpenAI、OTLP、MCP 或 A2A remote interop probe | `scripts/check_harness_sample_append.py <candidate-jsonl>` |

## Ready 但不升级的缺口

这些缺口已经达到升级讨论门槛，但当前决策是 `keep-advisory`。不要继续 append 普通样本来绕过决策；只有出现下列新证据时才复核决策。

| Gap ID | Current decision | Reopen when |
| --- | --- | --- |
| `GAP-GUARDRAIL-SOURCE-BOUNDARY` | `keep-advisory` | 出现 PRD、issue、web、Slack、粘贴 source 等更多来源类型，或有 harmless source-priority correction 的 false-positive 复核 |
| `GAP-SEC-CONTROL-MATRIX-BURNIN` | `keep-advisory` | 出现外部来源类型、多 control mapping 或 reviewer cost evidence |
| `GAP-WORKFLOW-TASK-PROFILE-AUDIT` | `keep-advisory` | 出现 simple / complex / 0-1-stage 之外的真实任务，或 profile selection dispute 的 false-positive 复核 |
| `GAP-AGENTIC-SANDBOX-HONESTY` | `keep-advisory` | 出现 local continuation honesty 之外的真实 incident，或 native sandbox / hosted trace / MCP / A2A / external provider boundary evidence |

复核命令：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py
.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>
```

## Local-only 缺口

`GAP-TRACE-OTLP-PILOT-BURNIN` 当前只有 localhost capture-server local-interop 样本。保持 `local-sample-only`，不要用它声明 external collector、hosted trace、OpenAI、MCP 或 A2A 已互通。

## 唤醒流程

1. 确认事件是真实发生，不是为了补样本专门构造。
2. 从上表找到 gap id、target checker 和 first review command。
3. 生成 bounded candidate JSONL，只保留必要 evidence refs；不要粘贴 raw transcript 或完整工具输出。
4. 先跑 no-write review gate。
5. review gate 通过后，再更新目标样本账本或 upgrade decision ledger。
6. 跑对应全量 checker 和 `scripts/check_ai_governance.py`。

## 不再主动追的事项

- 不主动制造真实 PreToolUse / Stop warning。
- 不为了 cross-task resume 重新开任务。
- 不为了 remote interop 伪造 localhost 或 no-auth probe。
- 不为了 red-team incident 写 synthetic incident 并标成 real。
- 不为了 upgrade discussion 改 decision；保持 `keep-advisory`，直到有新真实证据。
