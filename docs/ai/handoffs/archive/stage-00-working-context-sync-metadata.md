# Working Context Sync Metadata Handoff

更新时间：2026-04-20
阶段：stage-00
任务：working-context-sync-metadata
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务处理的是治理层 `working-context` 的轻结构化同步元数据与显式字段校验，不新增 requirements canonical mapping

## 本任务目标

- 给 `working-context.md` 增加最小可校验的同步元数据头
- 保持 `working-context` 正文仍以人读为主，不把它改造成第二份 `status` 或 `traceability` 数据表
- 在 governance check 中新增字段级校验，验证显式 stage/status/handoff/REQ/WS 引用，而不是做自由文本推断

## 已完成内容

- 为主仓 [working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md) 增加 `## 同步元数据` 头部，显式记录 `Current Stage`、`Active Status Source`、`Active Handoff Sources`、`Requirement IDs`、`Workstream IDs`、`Last Synced From` 和 `Last Synced At`
- 同步更新 starter 版 [new_pro_standard/docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/docs/ai/working-context.md) 与 `bootstrap_harness.py` 的生成模板，保持新项目首轮 bootstrap 产物一致
- 更新 [scripts/check_ai_doc_quality.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_doc_quality.py)，把 `## 同步元数据` 纳入 `working-context` 的必需 section
- 更新 [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)，开始校验 `working-context` 同步元数据中的显式字段
- 同步更新 [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md) 与 stage status，使这次治理增强进入默认入口

## 修改文件

- [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [new_pro_standard/docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/docs/ai/working-context.md)
- [scripts/check_ai_doc_quality.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_doc_quality.py)
- [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)
- [scripts/bootstrap_harness.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/bootstrap_harness.py)
- [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)

## 关键实现决策

- 只给 `working-context` 增加轻结构化元数据头，不把正文改造成表格式状态数据库
- checker 只验证显式字段，不推断自由文本语义，避免把 `working-context` 再变成另一套 projection drift 误报源
- 对 starter/bootstrapped 初始状态保留 `未绑定` 与 `YYYY-MM-DD` 的模板容忍度，但对真实 repo 中已绑定的 stage/status/handoff/REQ/WS 引用执行存在性与一致性检查
- 继续保留 runtime hooks 不自动改写 `working-context` 的边界；canonical 写入仍由主 Agent 在语义节点完成

## 当前未完成项

- 尚未对 `working-context` 与 `traceability-matrix` 的所有跨文档 metadata 做更强的一致性闭环
- 尚未把 `working-context` freshness 从 warning 升级为可配置阻断
- 尚未将这些字段级校验接入 CI

## 已知风险与注意事项

- 当前校验仍以显式字段为界，不会证明 `working-context` 正文的自然语言叙述与所有 primary truth surface 完全同义
- starter 模板为了保留可初始化状态，仍允许 `未绑定` 与 `YYYY-MM-DD`；真正新项目 bootstrap 后仍需尽快更新为真实值
- 若未来继续向 `working-context` 添加更多状态字段，应优先评估是否会与 `status` 或 `traceability-matrix` 职责重叠

## 已验证有效的路线

- 给 `working-context` 增加小规模 metadata header，再做字段级校验，能明显提升 freshness guardrail，同时不破坏当前三层 harness 边界
- 把 stage/status/handoff/REQ/WS 的校验都建立在显式字段上，能保持规则稳定并减少误报
- 同步更新 starter 模板与 bootstrap 生成器，能避免新项目和主仓规则分叉

## 已验证无效的路线

- 直接把 `working-context` 升级成全量结构化状态总表
- 继续依赖 mtime warning，而不提供任何显式字段用于 checker 对齐
- 让 hooks 或 reducer 自动回写 `working-context` 来追求伪“强一致”

## 尚未尝试但建议的路线

- 后续可给 `working-context` 增加更少量的 source refs 校验，例如 `Active Status Source` 是否已被 `docs/ai/index.md` 收录
- 若 CI 接入后误报率可控，可再评估把部分 freshness warning 升级为阻断
- 可在下一轮 hardening 中扩展 `traceability-matrix` 与 `working-context` 的 metadata 交叉检查

## 下一位 Agent 的第一步动作

- 若下一步要继续 hardening，先基于这次元数据头检查结果，补更广的 `traceability-matrix` / `working-context` 显式字段一致性校验，而不是去做自由文本同步

## 建议同步更新

- 已同步 `working-context`
- 已同步 `stage status`
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
