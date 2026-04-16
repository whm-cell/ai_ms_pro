# 当前工作上下文

更新时间：2026-04-16
当前阶段：STAGE-00 规划与治理固化
当前模式：Codex-first harness engineering

## 作用

本文件只保留当前开发阶段最需要被下一次会话立即继承的真相。

它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

## 当前主目标

- 把项目从“文档和规则初始化”推进到“可持续接入真实需求并开始开发”
- 保持 `docs/ai/` 与 `docs/requirements/` 的入口、模板、验证层一致
- 为后续真实需求导入预留稳定的 requirements ingestion 流程

## 当前活跃队列

1. 把真实需求文档录入 `docs/requirements/source/`
2. 将原始需求整理为 `normalized/` 文档
3. 将标准化需求归并为 `workstreams/`
4. 把工作流映射回 `plan.md` 与后续阶段文档

## 当前风险与阻塞

- 当前仓库仍处于治理骨架阶段，尚未导入真实需求内容
- `plan.md` 仍然是占位版，未进入项目真实规划状态
- 文档质量检查已上线，并已覆盖 `handoff` 模板中的有效/无效/候选路线结构；当前普通实现变更仍以 diff-aware warning 为主，但 `scripts/`、`.codex/hooks*`、`.githooks/` 等核心治理实现改动若未同步 `working-context` 或 `ADR`，已升级为阻断
- verification 层已新增 `working-context` 新鲜度 warning、活跃 `handoff` 堆积 warning 和 runtime session/observation staged 阻断；当前已接入 `Stop` 时的 runtime session best-effort 自动写入，但尚未接入 `SessionStart / Resume` 自动读取

## 当前真实入口

- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
- [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- [Runtime Stop Session Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-runtime-stop-session.md)

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
4. [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
5. [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
6. [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
7. [Runtime Stop Session Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-runtime-stop-session.md)

## 最近已固化的决策

- 项目采用 `AGENTS.md + Codex Stop hook + pre-commit + 脚本校验` 的治理方式
- 项目采用 `docs/requirements/` 与 `docs/ai/` 分层管理需求与执行上下文
- 新增 skill 的记录位置由 scope 决定，而不是全部写入 `AGENTS.md`
- 项目采用 `Runtime Harness + Governance Harness + Verification Harness` 的三层分工
- `.codex/runtime/` 只保存本地 session/observation 原料，不替代 `docs/ai/` 共享治理文档
- `handoff` 模板已强化为“任务结果 + 有效路线 + 无效路线 + 候选路线”的接力结构
- 治理脚本已新增 Phase-1 级 diff-aware warning，用于提示实现改动后未同步更新 `docs/ai/` 或 `docs/requirements/`
- 治理脚本已新增 runtime state 防误提交规则，并对 `working-context` 新鲜度和 `handoff -> status` 压缩节奏给出 warning
- 项目已定义 runtime session 最小模板，并已固化 “session 作为本地原料、handoff 作为共享交付物” 的提升规则
- Stop hook 分级策略已上线：普通实现变更缺文档更新时给 warning，核心治理实现变更缺 `working-context` 或 `ADR` 更新时直接失败
- `Stop` hook 已新增本地 runtime session 快照写入能力，产物仅进入 `.codex/runtime/sessions/`，不会自动改写共享治理文档
- 当前活跃 `handoff` 已切换为 runtime Stop session 接力，下一步目标是补上 `SessionStart / Resume` 读取最近 session 的最小链路

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
