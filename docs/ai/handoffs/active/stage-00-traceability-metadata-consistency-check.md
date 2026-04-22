# Traceability Metadata Consistency Check Handoff

更新时间：2026-04-22
阶段：stage-00
任务：traceability-metadata-consistency-check
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务为治理脚本补齐 AI-side `REQ/WS` 元数据一致性校验，不新增 requirements canonical mapping

## 本任务目标

- 给 `scripts/check_ai_governance.py` 增加 active `handoff` 与 `status` 的 `Requirement IDs / Workstream IDs` 字段级校验
- 让治理检查至少能拦住“AI-side 文档写了不存在于 traceability matrix 的 ID”这类基础漂移
- 用这个最小实现作为 `$repo-governed-coding` 的首个真实任务样本，验证 assumptions、最小 diff、verification 与 doc impact check 的约束是否顺畅

## 已完成内容

- 更新 [scripts/check_ai_governance.py](../../../../scripts/check_ai_governance.py)，新增对 active `handoff` / `status` 的 `## 需求与工作流标识` 解析
- 新增 active `handoff` / `status` 的 `Requirement IDs`、`Workstream IDs` 必填校验
- 新增 active `handoff` / `status` 的 ID 格式校验与 “是否存在于 [traceability-matrix.md](../../../requirements/traceability-matrix.md)” 校验
- 保留 `未绑定` 作为合法占位，避免把未映射任务误判为错误
- 已用 `python scripts/check_ai_governance.py` 验证当前仓库继续通过
- 已用临时文件导入脚本函数做一轮 smoke，确认 checker 会拦住不存在于 traceability matrix 的 `REQ-999 / WS-999`
- 已显式按 `$repo-governed-coding` 的方式完成这次任务：先收窄范围为“字段存在性校验”，不扩到更复杂的 cross-doc 语义推断

## 修改文件

- [scripts/check_ai_governance.py](../../../../scripts/check_ai_governance.py)
- [docs/ai/handoffs/active/stage-00-traceability-metadata-consistency-check.md](./stage-00-traceability-metadata-consistency-check.md)
- [docs/ai/handoffs/active/stage-00-repo-governed-coding-skill.md](./stage-00-repo-governed-coding-skill.md)
- [docs/ai/working-context.md](../../working-context.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](../../status/stage-00-runtime-harness-foundation.md)
- [docs/ai/harness-open-items.md](../../harness-open-items.md)
- [docs/ai/index.md](../../index.md)

## 关键实现决策

- 这一轮只做 “active handoff/status 中的 ID 必须存在于 traceability matrix” 的最小校验，不做 reducer output、runtime 产物或更复杂的交叉语义检查
- 复用现有 `validate_identifier_field` 能力，并把错误文案参数化，避免为 handoff/status 再造第二套 ID 校验逻辑
- 对 active `handoff` / `status` 不在 `未绑定` 时发 warning，而只在 ID 非法或不存在时报错，避免把合法未绑定任务误伤
- 把这次实现视为 `$repo-governed-coding` 的首个真实样本，而不是直接据此升级为 starter / ADR

## 已验证有效的路线

- 先落字段级存在性校验，再考虑更复杂的一致性检查，能在小 diff 内提高治理脚本的实际约束力
- 复用已有 metadata 解析与 ID 校验逻辑，比单独为 handoff/status 写一套新规则更稳
- 用临时文件导入函数做 smoke，可以证明新增校验逻辑真的会拦住未知 ID，而不需要污染 repo 内文档

## 已验证无效的路线

- 一上来就做跨 `handoff / status / reducer / traceability matrix` 的全量语义匹配，会把本次前向验证变成过大的实现
- 把 active `handoff` / `status` 的 `未绑定` 直接当 warning，会和当前仓库“未绑定是合法占位”的规则冲突

## 尚未尝试但建议的路线

- 下一轮可把同样的存在性校验扩到 reducer 输出或 runtime promotion 草稿
- 若后续 drift 仍高频，可继续补 `REQ` 与 `WS` 的组合关系、stage 关系或 workstream 覆盖关系校验
- 可在 `WS-02 Harness Trace Console` 中补一层 drift 可视化，让 metadata mismatch 不只被脚本拦下，也能被界面看见

## 当前未完成项

- 尚未校验 reducer output 与 runtime artifact 的 `REQ/WS` 一致性
- 尚未做更细的 `REQ <-> WS <-> STAGE` 交叉约束
- 尚未决定这类 consistency check 是否需要进入 starter 或 ADR

## 已知风险与注意事项

- 当前新增规则只能证明 ID 存在于 traceability matrix，不能证明该 handoff/status 绑定到了“正确的一组关系”
- 若将来 active 文档的 `## 需求与工作流标识` 结构发生变化，checker 需要同步调整
- 这次实现会提高 active handoff/status 的刚性约束，后续编辑这些文档时需要更注意 `REQ/WS` 字段同步

## 下一位 Agent 的第一步动作

- 若要继续推进 OPEN-06，先从 reducer output 或 `REQ <-> WS` 组合关系校验里再选一小块，而不是直接跳到全量语义一致性

## 建议同步更新

- 已同步 `working-context`
- 已同步 `stage status`
- 已同步 `harness-open-items`
- 检查 [AI 文档入口索引](../../index.md)
