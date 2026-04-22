# Repo-Governed Coding Skill Handoff

更新时间：2026-04-22
阶段：stage-00
任务：repo-governed-coding-skill
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务为当前仓库引入显式调用的 repo-local coding skill，不新增 requirements canonical mapping

## 本任务目标

- 在当前仓库新增一个显式调用的 repo-local skill `$repo-governed-coding`
- 保留 Karpathy-style 的四条行为原则，并补入本仓库的文档同步、traceability、verification 与 projection boundary 约束
- 把这次 skill 引入同步进当前 stage 的 `working-context`、`status` 与 `index`，但不改 starter、不做全局安装

## 已完成内容

- 新增 [repo-governed-coding SKILL](../../../../.codex/skills/repo-governed-coding/SKILL.md)，将四条行为原则与 repo-specific 治理规则组合为显式调用能力
- 新增 [governance-checklist.md](../../../../.codex/skills/repo-governed-coding/references/governance-checklist.md)，把 doc impact check、traceability、verification 与 primary truth surface 边界拆到 reference 文件
- 更新 [agents/openai.yaml](../../../../.codex/skills/repo-governed-coding/agents/openai.yaml)，提供最小 UI 元数据，并显式关闭隐式触发
- 在 [AGENTS.md](../../../../AGENTS.md) 补充 repo-local skill 说明，明确它是可选方法层能力，不替代仓库规则
- 同步更新 [working-context.md](../../working-context.md)、[stage status](../../status/stage-00-runtime-harness-foundation.md) 与 [index.md](../../index.md)，让这次 skill 引入进入当前共享入口
- 已用 `python -X utf8 C:\\Users\\Administrator\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py .codex/skills/repo-governed-coding` 验证 skill 结构通过
- 已运行 `python scripts/check_ai_governance.py`，确认新增 handoff / status / index / working-context 同步后治理检查继续通过
- 已做一轮轻量静态 smoke，确认 skill 文案显式覆盖 assumptions、最小 diff、doc impact check、`REQ/WS` traceability、verification finish line 与 projection boundary
- 已在 [Traceability Metadata Consistency Check Handoff](./stage-00-traceability-metadata-consistency-check.md) 中完成首个真实实现任务样本，验证该 skill 能把任务收敛到“小范围 assumptions + 最小 diff + 明确 verification + 文档收尾”

## 修改文件

- [AGENTS.md](../../../../AGENTS.md)
- [.codex/skills/repo-governed-coding/SKILL.md](../../../../.codex/skills/repo-governed-coding/SKILL.md)
- [.codex/skills/repo-governed-coding/agents/openai.yaml](../../../../.codex/skills/repo-governed-coding/agents/openai.yaml)
- [.codex/skills/repo-governed-coding/references/governance-checklist.md](../../../../.codex/skills/repo-governed-coding/references/governance-checklist.md)
- [docs/ai/working-context.md](../../working-context.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](../../status/stage-00-runtime-harness-foundation.md)
- [docs/ai/index.md](../../index.md)

## 关键实现决策

- 把 skill 放在 `.codex/skills/repo-governed-coding/`，按 repo-contained + 显式调用理解“可插拔”，不安装到 `~/.codex/skills`
- 让 `SKILL.md` 保持行为层约束，把 repo-specific closeout 细节放进 `references/governance-checklist.md`，避免 skill 正文膨胀
- 在 `agents/openai.yaml` 中设置 `allow_implicit_invocation: false`，防止这次 repo-local skill 被误当成默认常驻规则
- 不为这次引入创建 `ADR`，先把它记录为当前 stage 的策略补强，待真实任务样本累积后再判断是否升级

## 已验证有效的路线

- 用 repo-local skill 承载行为层约束，同时继续由 `AGENTS.md + docs/ai/* + verification scripts` 承载主治理面，能保持职责清晰
- 把 repo-specific checklist 下沉到 `references/`，可以在不增大触发上下文的前提下保留可操作细节
- 显式关闭隐式触发，能保持“可选 skill”与“always-on 仓库规则”的边界

## 已验证无效的路线

- 保留初始化骨架里的默认隐式触发配置会冲掉本次“显式调用”边界，因此已弃用
- 把所有 repo-specific 治理细节都塞进 `SKILL.md` 会让 skill 过胖，不利于后续稳定复用，因此已拆到 reference 文件

## 尚未尝试但建议的路线

- 在几个真实实现任务中显式调用 `$repo-governed-coding`，收集它是否真能改善 assumptions、diff discipline 与 closeout 质量
- 若后续多个任务都依赖这个 skill，再评估是否同步进入 `new_pro_standard` 或升级到 `ADR`
- 若将来引入更多 repo-local skills，可复用这次 “repo-contained + explicit-only + stage doc sync” 的接入模式

## 当前未完成项

- 已完成首个真实实现任务样本，但尚未在多个不同类型任务上累计前向使用样本
- 尚未决定是否将该 skill 提升为 starter 资产或长期决策

## 已知风险与注意事项

- 该 skill 当前只在本仓库内生效，且只按显式调用设计；不要把它误解为默认自动发现能力
- 若未来仓库规则发生变化，需优先更新 `AGENTS.md` 和 stage docs，再同步 skill 内容
- 该 skill 提供的是“怎么做”的约束，不应替代“何时必须更新文档”的仓库规则

## 下一位 Agent 的第一步动作

- 在下一个不同类型的真实任务里继续显式调用 `$repo-governed-coding`，判断它是否不只对治理脚本类改动有效，也能稳定收紧实现类任务的 assumptions、diff 和治理收尾质量

## 建议同步更新

- 已同步 `working-context`
- 已同步 `stage status`
- 检查 [AI 文档入口索引](../../index.md)
