# Harness Real Sample Watchlist

更新时间：YYYY-MM-DD
状态：starter template

## 作用

本文件保存暂时无法主动验证、只能等真实事件发生后再采集的 harness 样本缺口。

它不是每日待办，也不是要求 Agent 构造场景补齐覆盖率。真实事件发生后，先走 no-write review gate，再决定是否写入样本账本、status、ADR 或 check registry。

## 执行规则

- 不为了补齐 `0/2`、`1/3` 或其他门槛人工制造 synthetic evidence。
- 不把 placeholder、template、local-replay、local-only、approved contract 或 no-write candidate 当成 accepted real evidence。
- 不重复运行全量 planner / intake / readiness 来“刷进度”；平时只保留本 watchlist。
- 真实事件发生后，先运行项目定义的 review command；通过后再更新目标 JSONL、decision ledger、status 或 ADR。
- `.codex/runtime/*`、raw transcript 和完整工具输出只作为本地恢复材料；进入共享 docs 前必须压缩成 bounded evidence ref。

## 初始化方式

新项目不要复制旧项目的 gap id、样本计数或 accepted 结论。

初始化本文件时：

1. 从当前项目的 `docs/ai/check-registry.md` 找到 `advisory`、`review-required`、`blocking-candidate` 检查。
2. 对每个暂时缺真实样本的检查，补一行触发器。
3. 对已经达到讨论门槛但暂不升级的检查，补到 “Ready 但不升级” 表。
4. 若项目引入 sample ledger / intake 脚本，再把 `First review command` 改成真实命令；否则写 `人工复核：<文档或检查名>`。
5. 保持本文件为观察入口，不把它变成当前状态总表。

## 当前快照

- 来源：未绑定
- tracked gaps：未绑定
- actionable real-sample lanes：未绑定
- append-new-pending-slot：未绑定
- fill-existing-placeholder：未绑定
- ready-for-upgrade-discussion：未绑定
- local-sample-only：未绑定
- contract / ADR blockers：未绑定

若项目没有 sample-gap checker，上述字段保持 `未绑定`，不要编造计数。

## 唤醒触发器

| Trigger | Gap IDs | What qualifies | First review command |
| --- | --- | --- | --- |
| 真实动作前风险 warning | `未绑定` | 高风险、大输出、外发、破坏性或 remote-write 动作前真实触发 warning，并记录 operator decision / action taken / false-positive 结论 | `人工复核：check-registry / guardrail doc` |
| 真实长会话或 scope warning | `未绑定` | 长 session、重复命令、重复失败、过度验证或 scope churn 真实触发 warning | `人工复核：runtime / context budget doc` |
| 跨任务 resume | `未绑定` | 非 harness 维护任务中使用 checkpoint / handoff 恢复，并证明减少重复探索或避免遗漏验证 | `人工复核：status / handoff / checkpoint doc` |
| 不同任务类 trace summary | `未绑定` | 非默认任务类生成 no-network local trace summary，并带 bounded evidence | `人工复核：trace docs` |
| 真实 security workflow / dependency event | `未绑定` | scheduled/manual security evidence run、dependency PR、release、CodeQL、SBOM 或 dependency-review 真实事件 | `人工复核：security evidence / PR evidence` |
| 显式用户确认的高影响动作 | `未绑定` | 真实 destructive、externally visible、permission-changing、secret/env、deploy/release 等动作，且用户明确确认 | `人工复核：guardrail doc` |
| workflow skill 真实任务 | `未绑定` | 跨 workstream 技能加载、简单任务明确跳过技能、多 Agent / 多人 PR touch overlap 的真实样本 | `人工复核：skill eval / PR evidence` |
| 真实 red-team incident | `未绑定` | 工具或 skill 冒名、memory poisoning、A2A/handoff 权限混乱、cascade/rogue loop 等真实 incident | `人工复核：security / red-team doc` |
| 真实 remote interop probe | `未绑定` | 带真实 auth / endpoint / redaction / cost boundary 的 OpenAI、OTLP、MCP、A2A 或其他 remote interop probe | `人工复核：ADR / trace evidence` |

## Ready 但不升级的缺口

这些缺口已经达到升级讨论门槛，但当前决策是 `keep-advisory`、`keep-candidate` 或 `defer`。不要继续 append 普通样本来绕过决策；只有出现新证据时才复核决策。

| Gap ID | Current decision | Reopen when |
| --- | --- | --- |
| `未绑定` | `未绑定` | 出现新的来源类型、false-positive、process tax、reviewer cost、外部集成证据或 owner 决策 |

## Local-only 缺口

本地 smoke、localhost capture server、dry-run、no-network adapter、synthetic fixture 只能证明本地机制。

不要用 local-only evidence 声称：

- remote collector / hosted trace 已互通
- OpenAI hosted eval / trace 已接入
- MCP / A2A / external provider 已验证
- native sandbox 或远端权限审计已生效

## 唤醒流程

1. 确认事件是真实发生，不是为了补样本专门构造。
2. 从上表找到 gap id、target checker 或人工复核入口。
3. 生成 bounded candidate，只保留必要 evidence refs；不要粘贴 raw transcript、secret、完整 payload 或完整工具输出。
4. 先跑 no-write review gate 或人工复核。
5. review 通过后，再更新目标样本账本、status、ADR 或 check registry。
6. 跑对应全量 checker 和 `scripts/check_ai_governance.py`。

## 不再主动追的事项

- 不主动制造 warning、事故、远端互通或多人冲突。
- 不为了 cross-task resume 重新开任务。
- 不为了 remote interop 伪造 localhost 或 no-auth probe。
- 不为了 red-team incident 写 synthetic incident 并标成 real。
- 不为了 upgrade discussion 改 decision；保持当前决策，直到有新真实证据。
