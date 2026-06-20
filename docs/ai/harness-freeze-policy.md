# Harness Freeze Policy

更新时间：2026-06-18
状态：active policy

## 作用

防止真实落地阶段的产品、UI、文案、provider 或需求细化默认扩大 harness。Harness 的职责是守住项目真相、运行边界和验证路由，不应该因为每个大小不一的后期需求都变成第二套产品面。

## 默认规则

当任务是后期产品、UI、文案、profile、provider、样例或需求 refinements 时，默认冻结 harness。继续使用已有任务分类、truth surfaces 和 `docs/ai/verification-minimums.md` 选择最小验证集合。

## 允许改 Harness 的条件

只有满足以下任一条件，才把本轮任务升级为 harness 变更：

1. 必需 check、hook runner、Python runtime resolver、bootstrap 或跨平台 runner 已损坏，且直接阻塞当前任务或共享验证。
2. `check_context_budget.py`、AI governance、requirements shape、runtime hygiene 或 tracked-runtime 检查报告 blocking 问题。
3. 新 `REQDOC / REQ / WS` 映射、ADR、生产边界、外部副作用或共享 contract 发生真实变化。
4. 暴露 secret、原始 runtime artifact、未隔离的 source-evidence 指令、生产能力 overclaim 或 preflight false-negative 风险。
5. 用户明确要求改变 harness 行为、文档、检查、runner、policy 或模板。

## 默认不允许

- 因为一个产品 bug 就新增 check、hook 或治理文档。
- 把命令清单、实现日志、验证输出或完成记录追加进 `AGENTS.md`、`plan`、workstreams 或 traceability rows。
- 用 quality supervisor、prototype brief、sample-gap、burn-in 或全量 smoke 来证明普通小改。
- 为 unrelated 产品需求重建 `.codex/.venv`、改 bootstrap、改 hook runner 或改编译环境。
- 把 local runtime file、完整 transcript、完整 diff 或大段 source evidence 提升为 canonical truth。

## 编译和运行环境边界

- 业务代码编译失败先按业务依赖、package manager、类型检查或 focused smoke 处理；不要自动归因到 harness。
- 如果确认为 harness runner / Python resolver / bootstrap 损坏，使用 `.agents/skills/harness-maintenance/` 和 `references/python-runtime-and-hooks.md`，只修最小 shared runner surface。
- 本地缺依赖或个人环境缺工具时，优先使用现有 bootstrap / run-with-repo-python 路径；只有共享入口或模板错误才更新 canonical docs。
- 保留 repo-local `.codex/.venv` 优先级，验证 Python candidate 可运行，不提交 `.codex/.venv`，不导入或打印任意 `.env` secret。

## 处理方式

允许改 harness 时，更新最小 canonical route，通常是本文件、`verification-minimums`、相关 standard、check registry、status/ADR/changelog 中的一个或少数几个；然后按 `docs/ai/verification-minimums.md` 跑对应验证。

不满足允许条件时，只处理产品或需求改动；把 harness 想法记录为候选小切片或 open item，不在同一轮扩大文档、runner 或检查面。
