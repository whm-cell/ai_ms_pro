# Runtime Stop Session Handoff

更新时间：2026-04-16
阶段：stage-00
任务：runtime-stop-session
状态：待接力

## 本任务目标

- 为当前仓库补上第一条真正的 runtime harness 自动化链路：`Stop` 时将本地 session 快照写入 `.codex/runtime/sessions/`
- 保持 runtime 产物只落本地层，不自动改写 `docs/ai/` 共享治理文档
- 继续强化治理校验，使 runtime 自动化不会破坏 repo-first 文档闭环

## 已完成内容

- 新增 `Stop` runtime hook 脚本 [stop_runtime_session.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_session.py)，会 best-effort 读取 hook stdin JSON 并刷新当前 session 的本地快照文件
- 更新 [hooks.json](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks.json)，使 `Stop` 先写 runtime session，再执行治理检查
- 为 runtime session 增补最小模板 [._template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md) 与提升规则 [ADR-002-session-to-handoff-promotion.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- 更新 runtime README 和工作上下文，明确 `Stop` 只写本地 session 文件，不会自动发布 `handoff`
- 为治理脚本加入分级策略：普通实现漂移继续 warning，核心治理实现改动缺少 `working-context` 或 `ADR` 更新时直接失败
- 手工用模拟 `Stop` payload 验证过 session 写入脚本，随后已清理测试产物
- `python3 scripts/check_ai_governance.py` 当前通过

## 修改文件

- [stop_runtime_session.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_session.py)
- [hooks.json](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks.json)
- [.codex/runtime/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/README.md)
- [sessions/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/README.md)
- [sessions/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md)
- [check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)
- [ADR-002-session-to-handoff-promotion.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- [working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)

## 关键实现决策

- runtime session 自动化采用 best-effort 写入，脚本内部异常不会阻断 `Stop`
- `Stop` hook 只写 `.codex/runtime/sessions/`，不触碰 `handoff`、`status`、`ADR`、`index.md`
- 同一 session 通过 `session_id` 复用同一个快照文件；首次出现时创建，后续 Stop 刷新同一文件
- runtime staged 阻断规则排除了 `README.md` 与 `_template.md`，避免把仓库规则文件误判为本地运行态
- 核心治理实现范围当前以 `scripts/`、`.codex/hooks*`、`.githooks/`、`.codex/hooks.json`、`.codex/config.toml` 为准

## 已验证有效的路线

- 先定义 runtime session 模板与提升规则，再上 `Stop` 自动写入，能减少自动化产物和共享治理层之间的边界混乱
- 将 runtime 写入和治理校验拆成两个独立 `Stop` hook，职责清晰且便于后续继续扩展
- 在治理脚本里做分级策略，比直接让 hook 自动代写共享文档更稳

## 已验证无效的路线

- 将 `.codex/runtime/sessions/_template.md` 一并纳入 runtime staged 阻断，会误伤仓库内需要版本化的规则文件
- 只靠 warning 不同步更新 `working-context`，会被新的核心治理实现分级策略拦下

## 尚未尝试但建议的路线

- 下一步优先实现 `SessionStart / Resume` 读取最近 session 文件的最小链路
- 为 runtime session writer 增加更稳健的 payload 提取逻辑，例如更好地识别 user prompt、thread id、resume 标记
- 若后续 session 文件噪音过大，可增加文件刷新节流或“仅在 payload/工作区发生变化时重写”策略

## 当前未完成项

- 尚未实现 `SessionStart / Resume` 自动读取最近 session
- 尚未接入 `observations/` 的自动采集
- 尚未把 runtime session 快照与 `handoff` 提炼做半自动映射
- 尚未把治理检查接入 CI

## 已知风险与注意事项

- 当前 `Stop` runtime writer 对 hook payload schema 采用弱依赖解析；如果上游字段变化，最坏情况是 session 内容变得不完整，但不应阻断主流程
- session 文件会记录当前工作区变更列表；如果工作区长期脏，快照里的“触碰文件”可能比真实本次会话更宽
- 当前仓库仍处于 STAGE-00，`working-context` 里的主活跃队列尚未完全切换到 runtime harness 后续事项

## 下一位 Agent 的第一步动作

- 先读 [working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)、[ADR-001-harness-layering.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)、[ADR-002-session-to-handoff-promotion.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)，然后继续实现 `SessionStart / Resume` 读取最近 session 的最小链路

## 建议同步更新

- runtime 自动化继续推进后，必要时更新 `status`
- 若 `SessionStart / Resume` 改变长期工作流边界，补充 `ADR`
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
