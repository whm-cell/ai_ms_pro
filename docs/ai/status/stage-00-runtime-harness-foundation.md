# Stage-00 Runtime Harness Foundation Status

更新时间：2026-04-25
阶段：stage-00
状态：进行中

## 需求与工作流标识

- Requirement IDs：REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs：WS-01, WS-02
- 当前阶段已通过 `WS-01` 与 `WS-02` 完成两个真实场景的 requirements traceability 与实现验证

## 当前阶段目标

- 为项目建立最小可用的 runtime harness、governance harness 和 verification harness 协作链路
- 保持 repo-first 治理边界，同时补齐 session、observation、reducer 与 traceability metadata 的基础能力
- 为后续真实需求导入和阶段化开发预留稳定的 requirements traceability 位点

## 当前完成度

- 已完成：
  - `Stop` runtime observation/session writer
  - `SessionStart` runtime session resume context
  - observation handoff-first reducer
  - requirement/workstream metadata 位点与 ADR 规则
  - runtime staged 阻断、working-context 新鲜度检查、handoff 堆积 warning
  - 首个真实场景 `WS-01 / Three.js Snake MVP` 的 requirements 导入、实现落地与 handoff/status 压缩
  - `WS-01` 的 repo-level deterministic smoke runner，覆盖 `load -> eat -> game over -> restart`
  - `plan/workstream` projection surface boundary 与显式状态字段 freshness 校验
  - 第二个真实场景 `WS-02 / Harness Trace Console` 的 requirements 导入、实现落地与 handoff/status 压缩
  - `WS-02` 的 repo-level deterministic smoke runner，覆盖 `load -> WS-02 filter -> REQ-006 search -> completed status`
  - 显式 `REQ/WS` metadata 下的 Stop hook observation/session 与 reducer 验证
  - repo-level smoke 的 Playwright session 命名已收紧，避免当前 macOS 环境中的 unix socket 路径截断冲突
  - `check_ai_docs.py` 已收紧为“最小默认 + `.codex/harness.toml` 可配置”，并新增 `bootstrap_harness.py` 作为跨项目最小控制面初始化入口
  - Git hook 与 Codex hook 已统一收敛到 repo-level Python runner，默认优先使用 `.codex/.venv`
  - bootstrap 已补齐离线容错：Python 兼容依赖安装默认 best-effort，不再因为受限网络阻断 `.codex/.venv` 初始化
  - 已在 `output/harness_rehearsal_20260419_100339` 完成全新测试仓库演练，starter copy -> bootstrap -> 首个 `REQDOC / REQ / WS` -> 最小实现 -> governance check 已闭环
  - 已在测试仓库内补齐 `WS-01 Quick Notes` 的 smoke、runtime promotion 与首个 stage `status` 压缩
  - `working-context` 已新增轻结构化同步元数据头，并开始校验 stage/status/handoff/REQ/WS 的显式字段一致性
  - 已新增 repo-local `$repo-governed-coding` skill，把 Karpathy-style 行为约束适配为当前仓库的显式调用能力，并补入文档同步、traceability、verification 与 projection boundary 规则
  - governance checker 已新增 active `handoff` / `status` 的 `REQ/WS` 字段存在性校验，把 metadata consistency 自动化从 `working-context` 扩展到更多 primary truth surface
  - 默认治理面已收缩为 `index -> working-context -> stage status -> <=5 active handoff`，并已将被 stage `status` / ADR 吸收的完成型 handoff 归档
  - 2026-04-24: `ghtt_crawler` 中已验证的 Windows hook entry、runnable Python resolution、repo-local venv self-heal 与 staged code-shape budget 已反哺进当前 harness；长期决策记录在 `ADR-008-cross-platform-hooks-and-code-shape.md`
  - 2026-04-25: `new_pro_standard` 已同步 PowerShell hook entrypoints、code-shape budget、runnable Python resolution、坏 `.codex/.venv` 自愈、staged code-shape pre-commit 与 active handoff/status `REQ/WS` metadata 校验；bootstrap 也会按当前宿主环境刷新 `.codex/hooks.json`，默认治理面中的重复当前态展开已进一步回收到 `working-context` 同步元数据与 stage `status`
- 进行中：
  - 基于 [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md) 收敛剩余 hardening 项
  - 评估是否可以将 Stage-00 压缩并进入下一阶段
  - metadata consistency 自动校验已从 `working-context` 扩展到 active `handoff/status`，但仍未覆盖 reducer/runtime 与更细的组合关系
- 未开始：
  - CI 强校验接入
  - reducer 到 `status` / `ADR` 的更强自动压缩策略

## 本阶段关键成果

- runtime 层已经具备 `Stop observation -> Stop session -> SessionStart additionalContext` 的最小自动化闭环
- governance 层已经明确采用 `handoff -> status -> adr/changelog` 压缩链路，并新增 handoff-first reducer
- requirements traceability 规则已经进入 handoff、status、session 和 reducer 输出，且 canonical mapping 保持在 `docs/requirements/traceability-matrix.md`
- quality / governance 检查已经能识别 metadata section 缺失，并继续阻断 runtime state 误提交
- quality / governance 检查已开始利用 `working-context` 同步元数据验证 stage source、handoff source 和 REQ/WS 显式绑定
- `WS-01 / Three.js Snake MVP` 已作为首个真实场景落地，证明当前 harness 能支撑从 requirements 到代码实现的完整闭环
- `WS-01` 已新增 repo 内可直接运行的浏览器 smoke 入口，不再只依赖一次性手工打开页面验证
- `WS-02 / Harness Trace Console` 已作为第二个真实场景落地，证明当前 harness 在新 workstream 上也能复用 requirements、implementation 和 shared truth surface
- `WS-02` 已通过显式 `REQ-004~006 / WS-02` metadata 运行 Stop hooks 与 reducer，验证 runtime promotion 链路不只在首个 workstream 有效
- harness 已具备跨项目 bootstrap 能力，说明当前阶段成果不只适用于本 repo，也可作为新项目起手式
- repo-level Python runner 已补齐 Git hook 与 Codex hook 的解释器一致性，减少系统 Python 版本差异对治理检查的影响
- 通过真实新仓库演练可以暴露 portability 边界问题；当前已确认“离线安装可选兼容依赖失败”不应视为 bootstrap 失败
- governance checker 已通过 `-uall` 修复全新仓库首次初始化时的目录级未跟踪误判
- `WS-01 Quick Notes` 已在新仓库内完成 `requirements -> implementation -> smoke -> runtime promotion -> status`
- `plan` 与 `workstream` 已收缩为 projection surface，当前完成度与验证证据默认回收到 `working-context`、`handoff`、`status`、`traceability-matrix`
- governance 脚本已新增 projection freshness 规则，但仅检查显式状态字段，避免自由文本级误报
- `index` 已回收为稳定路由层，`working-context` 已回收为增量真相层，默认恢复面不再重复展开完整阶段目录
- governance checker 已新增 active handoff 与 `working-context` 绑定 handoff 的预算 warning，用于持续压缩默认治理面
- repo-local `$repo-governed-coding` skill 已证明当前 harness 不只支持文档与 hook 规则，也能承载显式调用的行为层约束；当前仍保持为策略补强，而不是主治理面替换
- repo-local `$repo-governed-coding` skill 已在首个真实实现任务中完成前向使用，说明它不只停留在结构校验层面，也能驱动一个受控的小范围 hardening 变更闭环
- 2026-04-24 portability hardening establishes a cleaner cross-platform hook/Python baseline and keeps code-shape checks separate from AI governance checks.
- `new_pro_standard` 现已和当前 harness 的关键机制层重新对齐，starter 不再遗漏 2026-04-24 portability hardening 与 metadata consistency 的核心能力
- `index -> working-context -> stage status` 的默认恢复链路进一步去重，精确 active handoff 集合以 `working-context` 同步元数据为准

## 风险与阻塞

- observation 与 session 仍依赖 best-effort hook payload，真实运行时字段可能需要继续适配
- reducer 目前只做轻量聚合，尚未在真实长期 observation 数据上验证压缩质量
- 当前前端 smoke 通过 `?smoke=1` 下的 namespaced API 走 deterministic 断言，后续若要覆盖真实用户输入路径，仍需补更黑盒的浏览器回归
- 当前前端场景采用零构建静态接入，若后续引入更多复杂前端功能，可能需要重新评估工具链
- `WS-02` 当前通过显式环境变量携带 `REQ/WS` metadata，说明链路可用，但自动化一致性仍未完全收紧
- `AGENTS.md` 仍是当前项目版本；若新项目直接复制但不改写项目目标和 repo-specific 规则，仍可能带入旧假设
- repo-local `$repo-governed-coding` skill 当前只在本仓库以显式调用方式提供；是否值得提升为 starter 资产仍需更多真实任务样本
- 当前 metadata consistency 自动化仍只覆盖 `working-context + active handoff/status` 的字段级检查，尚未扩展到 reducer output、runtime artifact 或 `REQ <-> WS <-> STAGE` 组合关系
- starter 当前已同时携带 `.sh` 与 `.ps1` hook runner，且 bootstrap 会按当前宿主环境刷新 `.codex/hooks.json`；若仓库在初始化后跨 host shell 迁移，仍需重新 bootstrap 或只调整 hook 入口配置
- active surface budget 当前仍是 warning 而不是 blocking；后续仍需观察阈值是否足够稳定

## 下一阶段重点

- 用真实 observation 数据验证 reducer 输出，并明确何时应进一步压缩到 `status` 或 `ADR`
- 判断 `WS-01` 与 `WS-02` 是否应归档为已验证样板，或继续演化成更完整的示例
- 评估是否将治理检查接入 CI，并逐步增加 metadata 一致性检查
- 评估是否要继续收紧“仓库初始化后跨 host shell 迁移”的体验，例如自动探测或迁移提示，而不是继续阻塞新项目起手
- 在几个真实实现任务中显式调用 `$repo-governed-coding`，判断它是否只需保留为 repo-local skill，还是值得进入 starter / ADR
- 若继续推进 OPEN-06，优先补 reducer/runtime 或 `REQ <-> WS` 组合关系校验，而不是直接做自由文本级语义推断

## 验收判断

- 当前阶段的“runtime harness foundation”目标已在两个真实 workstream 上得到验证：三层 harness、traceability、projection boundary 和 runtime promotion 均已跑通
- 尚未完全进入下一阶段，因为 reducer 压缩阈值、CI 接入和 metadata consistency 自动校验仍未完成；剩余问题更偏 hardening，而不是“是否可用”

## 关联文档

- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
- [已归档 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)
- [ADR-007 Governance Surface Budget](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-007-governance-surface-budget.md)
- [ADR-008 Cross-Platform Hooks And Code Shape Budget](../adr/ADR-008-cross-platform-hooks-and-code-shape.md)
- [2026-04-25 Harness Starter Sync And Surface Trim](../changelog/2026-04-25-harness-starter-sync-and-surface-trim.md)
- 当前默认恢复顺序与 active handoff 集合由 `working-context` 的同步元数据维护；已被本 stage `status` / ADR 吸收的完成型 handoff 已归档
