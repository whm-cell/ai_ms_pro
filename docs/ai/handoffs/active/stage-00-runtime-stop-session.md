# Runtime Hooks Handoff

更新时间：2026-04-16
阶段：stage-00
任务：runtime-hooks
状态：进行中

## 本任务目标

- 为当前仓库补上最小可用的 runtime harness 自动化链路：`Stop` 写本地 observation 与 session 快照，`SessionStart` 读取最近 session 摘要
- 保持 runtime 产物只落本地层，不自动改写 `docs/ai/` 共享治理文档
- 继续强化治理校验，使 runtime 自动化不会破坏 repo-first 文档闭环

## 已完成内容

- 新增 `Stop` runtime hook 脚本 [stop_runtime_observation.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_observation.py)，会 best-effort 追加 observation 到 `.codex/runtime/observations/YYYY-MM-DD.jsonl`
- 新增 `Stop` runtime hook 脚本 [stop_runtime_session.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_session.py)，会 best-effort 读取 hook stdin JSON 并刷新当前 session 的本地快照文件
- 更新 [hooks.json](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks.json)，使 `Stop` 先写 runtime observation、再写 runtime session、最后执行治理检查
- 新增 `SessionStart` runtime hook 脚本 [session_start_runtime_context.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/session_start_runtime_context.py)，会在 `startup|resume` 时读取最近 session 文件并通过 `additionalContext` 注入精简恢复提示
- 为 runtime session 增补最小模板 [._template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md) 与提升规则 [ADR-002-session-to-handoff-promotion.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- 更新 runtime README 和工作上下文，明确 `Stop` 只写本地 observation/session 文件，`SessionStart` 只读取本地 session 摘要，三者都不会自动发布 `handoff`
- 为治理脚本加入分级策略：普通实现漂移继续 warning，核心治理实现改动缺少 `working-context` 或 `ADR` 更新时直接失败
- 手工用模拟 `Stop` payload 验证过 observation 追加脚本，随后已清理测试产物
- 手工用模拟 `Stop` payload 验证过 session 写入脚本，随后已清理测试产物
- 手工用模拟 `SessionStart` payload 验证过 `additionalContext` 注入 JSON 形状与最近 session 摘要读取逻辑，随后已清理测试产物
- `python3 scripts/check_ai_governance.py` 当前通过

## 修改文件

- [stop_runtime_observation.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_observation.py)
- [stop_runtime_session.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_session.py)
- [session_start_runtime_context.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/session_start_runtime_context.py)
- [hooks.json](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks.json)
- [.codex/runtime/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/README.md)
- [observations/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/observations/README.md)
- [sessions/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/README.md)
- [sessions/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md)
- [check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)
- [ADR-002-session-to-handoff-promotion.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- [working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)

## 关键实现决策

- runtime observation 自动化采用 append-only JSONL，便于后续 reducer 或手工提炼稳定结论
- runtime session 自动化采用 best-effort 写入，脚本内部异常不会阻断 `Stop`
- `Stop` hook 只写 `.codex/runtime/observations/` 与 `.codex/runtime/sessions/`，不触碰 `handoff`、`status`、`ADR`、`index.md`
- `SessionStart` hook 只读取最近 runtime session 并注入精简 `additionalContext`，不修改任何本地或共享文档
- 同一 session 通过 `session_id` 复用同一个快照文件；首次出现时创建，后续 Stop 刷新同一文件
- runtime staged 阻断规则排除了 `README.md` 与 `_template.md`，避免把仓库规则文件误判为本地运行态
- 核心治理实现范围当前以 `scripts/`、`.codex/hooks*`、`.githooks/`、`.codex/hooks.json`、`.codex/config.toml` 为准

## 已验证有效的路线

- 先定义 runtime session 模板与提升规则，再上 `Stop` 自动写入，能减少自动化产物和共享治理层之间的边界混乱
- 先把 observation 设计成 append-only 原料，再考虑 reducer，能避免 runtime 层过早承担共享治理职责
- 将 runtime 写入和治理校验拆成两个独立 `Stop` hook，职责清晰且便于后续继续扩展
- 在治理脚本里做分级策略，比直接让 hook 自动代写共享文档更稳
- 使用 `SessionStart.additionalContext` 注入精简恢复提示，适合做 runtime 层读取，而不需要改写共享治理文档

## 已验证无效的路线

- 将 `.codex/runtime/sessions/_template.md` 一并纳入 runtime staged 阻断，会误伤仓库内需要版本化的规则文件
- 只靠 warning 不同步更新 `working-context`，会被新的核心治理实现分级策略拦下
- 让 observation 直接发布 repo 共享文档会越过主 Agent / reducer 的语义判断边界，不适合当前 repo-first 治理模型

## 尚未尝试但建议的路线

- 为 runtime observation / session writer 增加更稳健的 payload 提取逻辑，例如更好地识别 user prompt、thread id、resume 标记
- 为 runtime session reader 增加更稳健的 payload 识别与摘要裁剪逻辑，例如更好地识别真实 resume 对应 session、减少无关上下文注入
- 若后续 session 文件噪音过大，可增加文件刷新节流或“仅在 payload/工作区发生变化时重写”策略
- 若 observation 噪音过大，可增加 reducer 前去重或按 session/阶段聚合策略

## 当前未完成项

- 尚未把 runtime observation / session 原料与 `handoff` 提炼做半自动映射
- 尚未定义 observation reducer 是先产出 `handoff` 草稿还是先产出长期经验候选
- 尚未把治理检查接入 CI
- 尚未验证真实 Codex 运行时 payload 下 `SessionStart` 摘要提取是否需要补充更多字段适配

## 已知风险与注意事项

- 当前 `Stop` runtime writer 对 hook payload schema 采用弱依赖解析；如果上游字段变化，最坏情况是 session 内容变得不完整，但不应阻断主流程
- 当前 observation 记录按 Stop 事件追加，若会话很长，原始 observation 噪音可能较多，需要后续 reducer 或聚合策略
- session 文件会记录当前工作区变更列表；如果工作区长期脏，快照里的“触碰文件”可能比真实本次会话更宽
- 当前仓库仍处于 STAGE-00，runtime harness 已有最小自动化链路，但 observations 的提升/压缩规则尚未自动化

## 下一位 Agent 的第一步动作

- 先读 [working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)、[ADR-001-harness-layering.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)、[ADR-002-session-to-handoff-promotion.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)，再决定 observation reducer 应先对接 `handoff` 还是长期经验提炼

## 建议同步更新

- runtime 自动化继续推进后，必要时更新 `status`
- 若 `SessionStart / Resume` 改变长期工作流边界，补充 `ADR`
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
