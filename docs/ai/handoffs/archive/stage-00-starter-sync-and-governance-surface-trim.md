# Starter Sync And Governance Surface Trim Handoff

更新时间：2026-04-25
阶段：stage-00
任务：starter-sync-and-governance-surface-trim
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务处理的是 harness 机制层同步与共享治理面的去重，不新增当前 repo 的 requirement/workstream canonical mapping

## 本任务目标

- 把 `new_pro_standard` 补齐到当前 harness 的关键机制层能力
- 收缩默认治理面中的重复当前态展开
- 把本轮同步结果写回 canonical 文档面

## 已完成内容

- 已同步 `new_pro_standard` 的 PowerShell hook entrypoints、`check_code_shape.py`、`.codex/code_shape.toml`、最新 `bootstrap_harness.py`、最新 `check_ai_governance.py`、最新 Python runner 与最新 Git hook 行为
- 已让 root 与 `new_pro_standard` 的 `scripts/bootstrap_harness.py` 在 setup 时自动按当前宿主环境刷新 `.codex/hooks.json`
- 已更新 `new_pro_standard/README.md` 与 `new_pro_standard/AGENTS.md`，补齐 portability、traceability、observation reduction、code-shape 与 completion condition 规则
- 已收缩 [AI 文档入口索引](../../index.md)，不再在默认路由层重复展开完整 active handoff / ADR / changelog 当前态清单
- 已收缩 [当前工作上下文](../../working-context.md) 的“下一次会话先读”，把精确 active handoff 集合回收到同步元数据
- 已同步 [Stage-00 Runtime Harness Foundation Status](../../status/stage-00-runtime-harness-foundation.md)、[Harness Remaining Work](../../harness-open-items.md) 与 [2026-04-25 Harness Starter Sync And Surface Trim](../../changelog/2026-04-25-harness-starter-sync-and-surface-trim.md)

## 修改文件

- [new_pro_standard/AGENTS.md](/D:/codes/github/ai_ms_pro/new_pro_standard/AGENTS.md)
- [new_pro_standard/README.md](/D:/codes/github/ai_ms_pro/new_pro_standard/README.md)
- [new_pro_standard/.codex/hooks.json](/D:/codes/github/ai_ms_pro/new_pro_standard/.codex/hooks.json)
- [new_pro_standard/.codex/hooks/run_hook.ps1](/D:/codes/github/ai_ms_pro/new_pro_standard/.codex/hooks/run_hook.ps1)
- [new_pro_standard/.codex/hooks/run_with_repo_python.ps1](/D:/codes/github/ai_ms_pro/new_pro_standard/.codex/hooks/run_with_repo_python.ps1)
- [new_pro_standard/.codex/hooks/run_with_repo_python.sh](/D:/codes/github/ai_ms_pro/new_pro_standard/.codex/hooks/run_with_repo_python.sh)
- [new_pro_standard/.codex/code_shape.toml](/D:/codes/github/ai_ms_pro/new_pro_standard/.codex/code_shape.toml)
- [new_pro_standard/.githooks/pre-commit](/D:/codes/github/ai_ms_pro/new_pro_standard/.githooks/pre-commit)
- [new_pro_standard/scripts/bootstrap_harness.py](/D:/codes/github/ai_ms_pro/new_pro_standard/scripts/bootstrap_harness.py)
- [new_pro_standard/scripts/check_ai_governance.py](/D:/codes/github/ai_ms_pro/new_pro_standard/scripts/check_ai_governance.py)
- [new_pro_standard/scripts/check_code_shape.py](/D:/codes/github/ai_ms_pro/new_pro_standard/scripts/check_code_shape.py)
- [docs/ai/index.md](/D:/codes/github/ai_ms_pro/docs/ai/index.md)
- [docs/ai/working-context.md](/D:/codes/github/ai_ms_pro/docs/ai/working-context.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](/D:/codes/github/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [docs/ai/harness-open-items.md](/D:/codes/github/ai_ms_pro/docs/ai/harness-open-items.md)
- [docs/ai/changelog/2026-04-25-harness-starter-sync-and-surface-trim.md](/D:/codes/github/ai_ms_pro/docs/ai/changelog/2026-04-25-harness-starter-sync-and-surface-trim.md)

## 关键实现决策

- 机制层文件采用“直接对齐主仓当前版本”的方式同步，避免继续维护一套语义相同但实现渐渐漂移的 starter 副本
- 默认治理面中的精确 active handoff 集合不再由 `index.md` 和“下一次会话先读”双份维护，而是回收到 `working-context` 的同步元数据
- starter 的平台差异先通过“同时携带 `.sh` / `.ps1` runner + bootstrap 刷新当前宿主环境 hook config”解决新项目起手问题；后续若要继续优化，重点是已初始化仓库的跨 host shell 迁移体验

## 已验证有效的路线

- 对于机制层同源文件，直接同步主仓版本比逐项手改更不容易漏能力
- 把“路由层”与“精确当前态集合”拆开后，治理面更接近 ADR-007 的预算目标
- 用 `status + changelog + archived handoff` 记录本轮同步，能避免把一次完成型子任务继续留在 active surface

## 已验证无效的路线

- 只靠 `working-context` 或 `status` 文本声明“starter 已同步”，不核对 starter 真实文件
- 让 `index.md` 同时承担稳定入口、当前手册、active handoff 清单和 ADR 清单四种职责

## 尚未尝试但建议的路线

- 为已初始化仓库补更顺滑的跨 host shell 迁移提示或自动探测
- 在仓库外独立路径再做一轮 starter copy -> bootstrap -> governance check 复演，确认本轮同步不是环境共振

## 当前未完成项

- 仓库外独立路径复演仍未完成
- reducer/runtime 与 `REQ <-> WS <-> STAGE` 组合关系校验仍未收紧
- 已初始化仓库若后续迁移到另一种 host shell，仍需要重新 bootstrap 或只调整 `.codex/hooks.json`

## 已知风险与注意事项

- `new_pro_standard` 现在会在 bootstrap 时按当前宿主环境刷新 `.codex/hooks.json`；若仓库初始化后再跨 host shell 迁移，仍需重新 bootstrap 或只调整该文件
- `index.md` 去重后，下一位 Agent 若需要精确 active handoff 清单，应以 `working-context` 的同步元数据为准，而不是期待索引再展开一份完整列表

## 下一位 Agent 的第一步动作

- 若继续推进 hardening，先从 [Harness Remaining Work](../../harness-open-items.md) 的 OPEN-01、OPEN-02、OPEN-03、OPEN-04、OPEN-06 中选当前优先项。

## 建议同步更新

- 已同步 `working-context`
- 已同步 `stage status`
- 已同步 `changelog`
- 检查 [AI 文档入口索引](../../index.md)
