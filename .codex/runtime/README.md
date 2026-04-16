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

子目录：

- `sessions/`：单次会话的本地恢复材料
- `observations/`：运行过程中的本地观察材料
