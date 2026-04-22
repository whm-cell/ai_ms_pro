# Harness Trace Console Handoff

更新时间：2026-04-18
阶段：stage-00
任务：harness-trace-console
状态：已完成

## 需求与工作流标识

- Requirement IDs：REQ-004, REQ-005, REQ-006
- Workstream IDs：WS-02
- 绑定关系已记录在 `docs/requirements/traceability-matrix.md`

## 本任务目标

- 用第二个 repo-native 垂直场景验证当前 harness 是否可复用
- 让 `WS-02` 直接消费 primary truth surface，而不是再造状态源
- 把 `requirements -> implementation -> runtime hook/reducer -> handoff/status` 在新 workstream 上再跑通一遍

## 已完成内容

- 新增 repo-native 静态应用 [apps/harness-trace-console/index.html](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/index.html)、[style.css](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/style.css)、[main.js](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/main.js)
- 控制台已直接读取 `docs/ai/working-context.md`、`docs/ai/status/stage-00-runtime-harness-foundation.md`、`docs/requirements/traceability-matrix.md`，展示当前阶段、摘要卡片、活跃队列、风险和 traceability rows
- 控制台已支持按 `stage / workstream / status / search` 过滤，并在 detail panel 中查看单条 requirement 的 canonical evidence
- 新增应用说明 [apps/harness-trace-console/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/README.md)
- 新增 repo-level smoke [scripts/harness_trace_console_smoke.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/harness_trace_console_smoke.py)，已验证 `load -> WS-02 filter -> REQ-006 search -> completed status`
- 已收紧 [scripts/harness_trace_console_smoke.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/harness_trace_console_smoke.py) 与 [scripts/threejs_snake_smoke.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/threejs_snake_smoke.py) 的 Playwright session 命名，避免 macOS unix socket 路径截断导致的本地 smoke 冲突
- 已新增 `REQDOC-002 / REQ-004~006 / WS-02` 需求文档和 canonical traceability mapping
- 已显式调用 runtime hooks 生成 `.codex/runtime/observations/2026-04-18.jsonl` 中的 `WS-02` observation，以及 [.codex/runtime/sessions/2026-04-18T21-35-33_main_main_ws02-manual-validation-2026-04-18.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/2026-04-18T21-35-33_main_main_ws02-manual-validation-2026-04-18.md) 运行时 session 快照
- 已用 `python3 scripts/reduce_runtime_observations.py ... --workstream-id WS-02` 生成 `WS-02 Harness Trace Console Reducer Draft`，验证 reducer 能带着同一组 metadata 输出 handoff-first 草稿

## 修改文件

- [apps/harness-trace-console/index.html](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/index.html)
- [apps/harness-trace-console/style.css](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/style.css)
- [apps/harness-trace-console/main.js](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/main.js)
- [apps/harness-trace-console/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/README.md)
- [scripts/harness_trace_console_smoke.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/harness_trace_console_smoke.py)
- [scripts/threejs_snake_smoke.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/threejs_snake_smoke.py)
- [docs/requirements/source/REQDOC-002-harness-trace-console-validation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/source/REQDOC-002-harness-trace-console-validation.md)
- [docs/requirements/normalized/REQ-004-harness-primary-truth-console.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-004-harness-primary-truth-console.md)
- [docs/requirements/normalized/REQ-005-traceability-filter-and-inspection.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-005-traceability-filter-and-inspection.md)
- [docs/requirements/normalized/REQ-006-smoke-verifiable-governance-console.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-006-smoke-verifiable-governance-console.md)
- [docs/requirements/workstreams/WS-02-harness-trace-console.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams/WS-02-harness-trace-console.md)
- [docs/requirements/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
- [docs/requirements/traceability-matrix.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)
- [docs/ai/plan.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)

## 关键实现决策

- 第二个 workstream 不再选另一个“玩具页面”，而是选一个直接消费 repo 主真相文档的 repo-native 控制台
- 页面继续采用零构建静态接入，避免把“验证 harness 可复用性”变成“先引入新工具链”
- 控制台只消费 `working-context`、stage `status` 和 `traceability-matrix` 这组 primary truth surface，不自建平行状态
- deterministic smoke 继续采用 `?smoke=1` 下的 namespaced API，但只验证加载、过滤、搜索和选择行为，不把断言建立在脆弱的像素快照上
- repo-level smoke 的 Playwright session 名必须保持足够短，避免在当前 macOS 环境中触发 unix socket 路径截断冲突
- runtime validation 通过显式 `Requirement IDs / Workstream IDs` 调用 Stop hooks 与 reducer，验证 metadata 在第二个 workstream 上可贯穿 runtime 到 governance

## 当前未完成项

- 仍未给 AI-side metadata 与 `traceability-matrix.md` 做自动一致性校验
- `WS-02` smoke 仍是 deterministic 功能验证，不覆盖视觉回归、CI 或长期稳定性
- runtime metadata 仍依赖显式传入或环境变量，尚未证明任意调用方都能零配置带齐 IDs

## 已知风险与注意事项

- `WS-02` 解析依赖当前 Markdown 结构；若 `working-context`、stage `status` 或 `traceability-matrix` 格式变化，控制台需要同步调整
- 当前 runtime hook 验证是一次显式手工触发，证明链路可用，但不等于所有未来会话都已自动带齐 metadata
- reducer 输出仍是候选草稿，不自动发布 canonical 文档；主 Agent 仍要负责最终语义判断

## 已验证有效的路线

- 在第二个 workstream 中直接消费 primary truth surface，能更真实地验证 governance 文档是否足够稳定可复用
- 零构建静态接入仍足以支撑第二个 repo-native 场景，说明当前仓库不依赖新工具链也能扩展真实切片
- `Stop hook -> observation/session -> reducer draft` 这条链路在 `WS-02` 上带着显式 metadata 也能跑通
- 把 smoke 聚焦在 deterministic 交互和 canonical evidence 检查上，比做脆弱的 UI 截图断言更稳

## 已验证无效的路线

- 只继续强化 `WS-01` 而不引入第二个 workstream，无法证明 harness 在新场景中的复用性
- 为了验证第二个场景先引入新构建工具链，会把问题从 harness 复用性转移到工程搭建
- 只验证页面功能、不验证 runtime hook 和 reducer，会让“全链路可用”仍然缺一段

## 尚未尝试但建议的路线

- 在 `WS-02` 基础上补 metadata consistency 提示或 drift 可视化，进一步验证多 workstream 情况下的治理可读性
- 若后续要进入 CI，可把 `harness_trace_console_smoke.py` 和 governance check 一起纳入 merge 前校验
- 如果后续需要更黑盒的治理验证，可再补一层不依赖 namespaced API 的浏览器回归

## 下一位 Agent 的第一步动作

- 先打开 [apps/harness-trace-console/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/harness-trace-console/README.md) 跑起控制台，再结合 [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md) 判断下一步是推进 metadata consistency 自动校验，还是压缩 Stage-00

## 建议同步更新

- 已同步 `docs/requirements/traceability-matrix.md`
- 已同步 `docs/ai/working-context.md`
- 已同步 `docs/ai/status/stage-00-runtime-harness-foundation.md`
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
