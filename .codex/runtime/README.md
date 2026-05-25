# Codex Runtime Harness

本目录用于保存 Codex 的本地 runtime harness 状态。

这些文件服务于：

- 会话恢复
- 压缩前快照
- 运行时观察

它们不是项目共享真相，不替代 `docs/ai/` 和 `docs/requirements/`。

使用规则：

- hook 只能在本目录写入本地 runtime 状态
- 不要把本目录文件加入 `docs/ai/index.md` 的默认阅读入口
- 若某条信息需要跨 agent、跨阶段稳定共享，应提升到 `handoff`、`status`、`adr` 或需求文档
- 当前已启用 `Stop` hook 的 best-effort observation 采集；原始 observation 只追加到 `.codex/runtime/observations/*.jsonl`
- 当前已启用 `Stop` hook 的 best-effort trace producer；portable trace 追加到 `.codex/runtime/observations/agent-traces/*.agent-trace.jsonl`，仍属于本地 runtime 原料
- 当前已启用 `Stop` hook 的 best-effort session 快照写入；该快照只更新本地 runtime 层，不会自动改写共享治理文档
- 当前已启用 `SessionStart` hook 的 best-effort 最近 session 摘要读取；它只注入额外 developer context，不会替代 `docs/ai/` 共享治理文档
- runtime prompt preview、transcript path、SessionStart 摘要和 reducer 草稿会经过 best-effort 脱敏；脱敏不是 secret scanning，不应主动把真实 secret 放入 prompt 或 runtime

子目录：

- `sessions/`：单次会话的本地恢复材料
- `observations/`：运行过程中的本地观察材料、agent trace JSONL 与 reducer 输入原料
- `tool-outputs/`：大工具输出、本地日志和完整 diff 的本地原文；进入 prompt 前应先摘要或定点截取
