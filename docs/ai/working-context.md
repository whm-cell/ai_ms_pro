# 当前工作上下文

更新时间：2026-04-30
当前阶段：STAGE-00 真实场景验证与治理固化
当前模式：Codex-first harness engineering

## 作用

本文件只保留当前开发阶段最需要被下一次会话立即继承的真相。

它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: docs/ai/status/stage-00-runtime-harness-foundation.md
- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-governance-surface-slimming.md
  - docs/ai/handoffs/active/stage-00-runtime-stop-session.md
  - docs/ai/handoffs/active/stage-00-observation-reducer.md
  - docs/ai/handoffs/active/stage-00-harness-portability-template.md
  - docs/ai/handoffs/active/stage-00-new-repo-rehearsal.md
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs: WS-01, WS-02
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-04-30

## 当前主目标

- 判断 Stage-00 是否已经在外部 starter 复演、runtime metadata 自动发现和首条黑盒浏览器回归落地后达到可压缩状态，并把最新 stage `status` 中收敛出的剩余缺口继续压成小规模 backlog
- 保持 `docs/ai/` 与 `docs/requirements/` 的默认控制面轻量、稳定、可恢复
- 确认 `new_pro_standard` 现在已经可以按“starter copy -> bootstrap -> hook/pre-commit -> 首个真实 REQ/WS”路径作为新项目起手式
- 继续把 runtime、reducer 与 traceability 的一致性校验推进到更长期样本与 stage 组合关系
- 让 Karpathy-style 行为护栏停留在可显式调用的 method layer，并通过 runtime session 快照与 handoff 模板为后续提炼留下 assumptions、scope、success criteria 和 verification 位点

## 当前活跃队列

1. 以 [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md) 为准，继续推进 OPEN-01、OPEN-04、OPEN-05、OPEN-06
2. 观察新引入的 governance + smoke workflow 是否稳定，并确认 hook sync check 与新增黑盒 smoke 在 CI 上没有额外漂移
3. 用更长期 observation 样本验证 reducer 压缩阈值，并继续补 `REQ <-> WS <-> STAGE` 自动校验
4. 判断 Stage-00 是否可以在完成本轮剩余 hardening 后压缩并进入下一阶段

## 当前风险与阻塞

- governance + repo-native smoke 已进入 workflow，但尚无远端稳定运行历史，暂时不能把“已接 CI”当成完全收敛
- reducer 已可用，但尚未在更长期 observation 数据上证明压缩质量
- 当前 metadata consistency 自动化仍未覆盖 reducer/runtime artifact 与 `REQ <-> WS <-> STAGE` 组合关系
- `harness-trace-console` 已有黑盒 DOM 回归，但 `WS-01 / threejs-snake` 仍主要依赖 deterministic smoke
- starter 现在已能在仓外完成 bootstrap + pre-commit，但 copied placeholder docs 仍需 `--force` 才会立刻换成新项目名，`AGENTS.md` 仍需人工项目化；相关说明已回写 starter README/guide
- hook 配置现在已有共享 renderer、独立 `sync_hooks_config.py`、POSIX Python 入口和 Windows PowerShell 入口；但仓库初始化后若跨 host shell/OS 迁移，仍需重新 bootstrap 或显式同步 `.codex/hooks.json`
- active surface budget 当前只是 warning，不是 blocking；若后续 handoff 再次堆积，仍需要主 Agent 主动压缩/归档
- archive candidate monitor 已可按需列出候选，但不会接入默认 Stop hook，也不会自动移动文件；归档仍由主 Agent 在 stage compression 时确认
- `$repo-governed-coding` 已进入 starter 机制层，但仍是显式调用能力；若未来把它变成默认 workflow，必须再更新 `AGENTS.md` / `ADR`，避免行为 skill 绕过治理文档
- macOS/POSIX 与 Windows PowerShell Python 解析已修复为优先 `.codex/.venv` 与 Python 3.11+ 候选；后续仍需观察没有 `.codex/.venv` 的全新宿主是否按预期创建 3.11 venv

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
3. [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
4. [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
5. [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)：当任务直接落在 `REQ/WS` 或 traceability 时再进入
6. [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)：当需要长期决策背景时再进入

## 最近已固化的决策

- 项目继续采用 `Runtime Harness + Governance Harness + Verification Harness` 的三层分工，runtime 只保留本地恢复原料
- `plan/workstream` 继续作为 projection surface；当前状态真相默认集中在 `working-context`、`handoff`、`status`、`traceability-matrix`
- `working-context` 继续只保留轻结构化同步元数据和下一步增量真相，不升级为第二份阶段状态总表
- `Stop -> observation/session -> SessionStart additionalContext -> reducer draft` 的最小 runtime promotion 链路已成立，但 reducer 仍维持 handoff-first
- `WS-01` 与 `WS-02` 已验证当前 harness 能支撑两个真实 repo-native workstream
- 默认治理面已收缩为 `index -> working-context -> stage status -> <=5 active handoff`；已被 stage `status` / ADR 吸收的完成型 handoff 进入 archive
- `new_pro_standard` 已同步 Windows hook entrypoints、repo-local Python runnable probe、坏 venv 自愈、staged code-shape pre-commit 与 active handoff/status traceability metadata 校验；新仓 bootstrap 还会按当前宿主环境刷新 `.codex/hooks.json`，默认生成轻量路由型 `index` 与增量真相型 `working-context`
- `index` 与 `working-context` 已进一步去重：精确 active handoff 集合由同步元数据维护，默认恢复入口不再重复展开同一组文档清单
- 2026-04-24: `ghtt_crawler` 中已验证的 Windows hook entry、runnable Python resolution、repo-local venv self-heal 与 staged code-shape budget 已反哺进当前 harness，并在 ADR-008 固化。
- 2026-04-29: root harness 已补上共享 hook renderer、`scripts/sync_hooks_config.py`、POSIX `run_hook.py` 入口、hook-sync 单测，以及 `governance + hook sync + repo-native smoke` 的 workflow 守门。
- 2026-04-29: governance checker 已从“字段存在性”推进到 `REQ/WS` 组合关系、normalized/workstream 文档覆盖和 traceability matrix 文档存在性对齐校验。
- 2026-04-29: Stop runtime observation/session 已支持基于 changed paths、workstream 模块路径和 traceability matrix 的 `REQ/WS` 自动发现，且 observation -> session -> reducer 已补单测验证零配置 metadata 贯通。
- 2026-04-29: `harness-trace-console` 已新增不依赖 namespaced test API 的黑盒 DOM smoke，保留原 deterministic smoke 作为更细粒度回归层。
- 2026-04-29: starter 的 `run_with_repo_python.sh` 已修复 macOS `/bin/bash` 3.2 下空数组 + `set -u` 兼容性问题；`check_code_shape.py --staged` 在 unborn `HEAD` 的首提交场景下会把 inherited scaffold 视为 baseline，不再阻断 starter 首次提交。
- 2026-04-30: 已对照 `forrestchang/andrej-karpathy-skills`，把可复用行为层沉淀为 starter 内的可选 `$repo-governed-coding` skill，并在 runtime session 模板/Stop 快照及 handoff 模板中新增行为护栏位点；长期决策记录在 ADR-009。
- 2026-04-30: 已修复跨平台 Python 解析链路：`run_hook.py` 不再优先继承启动器 Python，POSIX shell runner、Windows PowerShell runner 与 bootstrap 会枚举候选并优先 Python 3.11+，长期决策回写 ADR-008。
- 2026-04-30: 已新增 `scripts/check_archive_candidates.py` 作为 warning-only context-pressure monitor；当前扫描列出的归档候选是 governance surface slimming、harness portability template、new repo rehearsal，真正移动前仍需人工确认。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
