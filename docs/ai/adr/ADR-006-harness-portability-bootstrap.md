# Harness 可迁移性与 Bootstrap 决策

更新时间：2026-04-18
编号：ADR-006
标题：将 harness 划分为“机制层可复制 + 真相层重建”，并提供最小 bootstrap 入口
状态：已采纳

## 背景

- 当前仓库已经形成较完整的 Codex-first harness，但其中混合了两类内容：
  - repo-generic 的机制层
  - 仅当前项目成立的共享真相
- 如果把整套目录原样复制到新项目，AI 会先读到旧项目的 `working-context`、`status`、`traceability-matrix` 和 `REQ/WS` 文档，产生错误上下文。
- `scripts/check_ai_docs.py` 之前还把当前 repo 的某些文档名写死为必需项，导致新项目即使只想保留最小控制面，也会被旧项目假设卡住。

## 决策

- harness 正式划分为两层：
  - 机制层：可复制到新仓库
  - 真相层：必须在新仓库重新初始化
- `scripts/check_ai_docs.py` 改为“最小默认 + `.codex/harness.toml` 可配置”。
- `.codex/harness.toml` 的默认值保持最小，不带当前 repo 的专题文档假设。
- 新仓库的初始化入口统一为 `python3 scripts/bootstrap_harness.py`。
- 模板文件中的内部链接改为相对路径，避免把当前仓库绝对路径带到新项目。

## 备选方案

- 方案 A：继续把当前仓库完整拷贝到新项目，再让主 Agent 手工删旧真相
- 方案 B：只提供一份迁移说明，不改检查脚本和模板
- 方案 C：让 hook 在新项目第一次 Stop 时自动生成控制面

## 决策理由

- 方案 A 容易让 AI 在第一轮就继承错误上下文，也会把清理旧文档变成额外工作。
- 方案 B 只能靠人记住所有迁移细节，不足以降低实际误用概率。
- 方案 C 会让 hook 越过“是否真的要创建这些文档”的语义边界，且不利于项目自定义。
- 机制层可复制、真相层重建，再配合 bootstrap 入口，能把新项目从 0 到 1 的第一步变成可重复流程。

## 影响

- 新项目不再需要先复制旧项目 `working-context/status/handoff/traceability` 再人工清洗。
- `check_ai_docs.py` 不再默认要求当前 repo 特有的附加文档；项目若需要更多 always-on 文档，可在 `.codex/harness.toml` 中追加。
- 新项目第一次启动时，AI 应优先执行 bootstrap 和首个 `REQDOC / REQ / WS` 初始化，而不是直接写业务功能。

## 关联文档

- [Harness 可迁移清单](../harness-portability-guide.md)
- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [AI 文档入口索引](../index.md)
