# Harness 分层决策

更新时间：2026-04-16
编号：ADR-001
标题：Runtime、Governance、Verification 三层 Harness 分层
状态：已采纳

## 背景

- 项目已经建立 `AGENTS.md + docs/ai + docs/requirements + Stop hook + 校验脚本` 的治理骨架。
- 当前仓库的共享真相主要保存在 `docs/ai/` 与 `docs/requirements/`，而不是依赖单次会话历史。
- 为了支持更稳定的 vibe coding，需要补充 runtime 级会话恢复能力，但不能破坏现有的 repo-first 治理闭环。
- 如果让 hook 直接改写共享治理文档，在多 session、多 subagent 场景下容易引入高频覆盖和语义误判。

## 决策

- 项目正式采用三层 Harness 分层：
  - Runtime Harness：本地运行时记忆，位于 `.codex/runtime/`
  - Governance Harness：项目共享真相，位于 `docs/ai/` 与 `docs/requirements/`
  - Verification Harness：校验与阻断，位于 `.codex/hooks.json`、`.githooks/`、`scripts/check_*`
- `.codex/runtime/` 只保存本地 session 与 observation 原料，不进入 `docs/ai/index.md` 默认阅读入口。
- hook 可以写入 `.codex/runtime/`，但不能自动改写 `working-context.md`、`handoff`、`status`、`changelog`、`adr`、`index.md` 等共享治理文档。
- `docs/ai/` 下的 canonical 治理文档由主 Agent 在明确语义节点产出和维护。
- subagent 可以返回结构化结果或 handoff 草稿，但 canonical 的 `docs/ai/` 文档由主 Agent 最终落地。
- runtime 层中具有长期价值的结论，必须提升到 `handoff`、`status`、`adr`、`plan` 或 `docs/requirements/`，而不是长期停留在本地 runtime 文件中。

## 备选方案

- 方案 A：只保留 session / hook 驱动的 runtime harness，不维护 repo 内 `handoff`
- 方案 B：只保留 `handoff -> status -> adr/changelog`，不引入本地 runtime session 层
- 方案 C：由 hook 自动改写 `working-context`、`index` 和其他共享治理文档

## 决策理由

- 方案 A 更适合个人本地连续性，但不适合作为当前仓库的共享、可审计控制面。
- 方案 B 可以维持治理一致性，但对长上下文恢复、多次 resume 和压缩前快照的支持较弱。
- 方案 C 表面自动化程度更高，但无法可靠判断“是否已完成子任务”“是否应升级为 status 或 ADR”等语义边界，且更容易在并发场景下发生覆盖。
- 三层分层能把自动化、共享治理和校验职责拆开：
  - runtime 层解决会话恢复
  - governance 层解决共享真相与项目接力
  - verification 层解决漏更新阻断
- 该方案与当前仓库既有的 `AGENTS.md`、`working-context`、`handoff`、`status`、`adr` 结构兼容，迁移成本最低。

## 影响

- 仓库新增 `.codex/runtime/` 作为本地 runtime harness 落点，并通过 `.gitignore` 避免把 session 原料误纳入版本控制。
- `docs/ai/index.md` 继续只索引 repo 共享真相，不索引本地 runtime 文件。
- 默认阅读顺序保持 `index -> working-context -> requirements -> plan -> status -> handoff -> adr`，只有在需要恢复本地细节时才按需读取 `.codex/runtime/sessions/`
- 后续若增强脚本校验，应优先检查“共享治理文档是否漏更”，而不是让 hook 自动代写共享文档。
- 后续若引入 requirement ID、workstream ID、branch/worktree metadata 或 observations 提炼流程，可在此三层边界内继续扩展。

## 关联文档

- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
