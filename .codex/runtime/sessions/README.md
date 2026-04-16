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
