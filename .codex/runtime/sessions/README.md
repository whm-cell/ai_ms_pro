# Runtime Sessions

本目录保存本地 session 级恢复材料。

建议命名：

- `YYYY-MM-DDTHH-MM-SS_main_<branch-or-thread>.md`
- `YYYY-MM-DDTHH-MM-SS_subagent_<task>.md`

规则：

- 每次 session 使用独立文件，不覆盖旧文件
- 优先追加或新建，不要把多个并发 session 写入同一文件
- 内容仅供恢复本地上下文，不作为项目共享真相
- 若结论需要被下一位 Agent 默认读取，应同步提升到 `docs/ai/`
- 当前 `Stop` hook 会按 session 维度 best-effort 刷新同一个本地快照文件；它不会自动发布 `handoff`
- 当前 `SessionStart` hook 会在 `startup|resume` 时 best-effort 读取最近 session 文件，并把精简摘要注入额外 developer context

模板：

- 使用 [session 模板](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md) 作为最小结构
- 模板中的“需提升到共享治理层的内容”与“是否需要提升为 Handoff”用于判断是否必须进入 `docs/ai/handoffs/active/*.md`
