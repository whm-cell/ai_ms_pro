# Requirement Workstream Metadata Handoff

更新时间：2026-04-16
阶段：stage-00
任务：requirement-workstream-metadata
状态：进行中

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 当前任务目标是建立 metadata 位点本身，因此尚未绑定到真实需求

## 本任务目标

- 在 runtime session、observation reducer、handoff 和 status 中补上统一的 `Requirement IDs` / `Workstream IDs` 元数据位点
- 保持 `docs/requirements/traceability-matrix.md` 作为 canonical mapping，而 AI 侧文档只做引用和同步
- 为真实需求导入后的追踪能力预留稳定字段和默认规则

## 已完成内容

- 更新 [AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)，新增 requirement traceability 规则，明确 AI 侧 artifact 应引用而不是发明 `REQ-XXX` / `WS-XX`
- 更新 runtime session 模板 [._template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md)、handoff 模板 [active/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/_template.md) 和 [status/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/_template.md)，统一新增 metadata section
- 更新 runtime hooks [stop_runtime_session.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_session.py) 与 [stop_runtime_observation.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_observation.py)，支持从 payload/env 捕获 requirement/workstream IDs
- 更新 [session_start_runtime_context.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/session_start_runtime_context.py)，使 `SessionStart` 恢复摘要在 metadata 已知时一并带回 requirement/workstream 绑定
- 更新 reducer [reduce_runtime_observations.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/reduce_runtime_observations.py)，支持显式 `--requirement-id` / `--workstream-id` 输入，并聚合 observation 中已有 metadata
- 新增 [ADR-004-requirement-workstream-metadata.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)，固化 metadata 约定
- 更新 [docs/requirements/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md) 与 [traceability-matrix.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)，明确 AI 侧 metadata 需要与 requirements 侧保持一致

## 修改文件

- [AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [sessions/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md)
- [active/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/_template.md)
- [status/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/_template.md)
- [stop_runtime_session.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_session.py)
- [stop_runtime_observation.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_observation.py)
- [session_start_runtime_context.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/session_start_runtime_context.py)
- [reduce_runtime_observations.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/reduce_runtime_observations.py)
- [check_ai_doc_quality.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_doc_quality.py)
- [ADR-004-requirement-workstream-metadata.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)
- [docs/requirements/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
- [traceability-matrix.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)

## 关键实现决策

- metadata 采用统一 section，而不是散落在自由文本中，便于后续脚本和检查器读取
- 当真实绑定未知时明确写 `未绑定`，避免伪造 `REQ` / `WS` 编号
- observation 和 session 只记录显式传入或环境提供的 IDs，不做不可靠的自动推断
- `traceability-matrix.md` 继续是 canonical mapping，AI 侧 metadata 是引用层，不是第二套真相

## 当前未完成项

- 尚未在真实 requirement/workstream 文档导入后验证 metadata 同步流程
- 尚未为 quality/governance 脚本增加 AI 侧 metadata 与 traceability matrix 一致性的自动校验
- 尚未把 metadata 接入 `working-context` 或 future status 压缩规则的更强检查

## 已知风险与注意事项

- 当前项目还没有真实 `REQ` / `WS` 文档，因此 metadata 只能先以 `未绑定` 作为合法占位
- hook payload 默认并不保证携带 requirement/workstream IDs，真实接入时可能仍需要主 Agent 显式补齐
- observation/reducer 里的 metadata 只表示“当前已知绑定”，不能替代 requirements 侧的 canonical 追踪关系

## 已验证有效的路线

- 先把 metadata 位点统一到模板、runtime writer 和 reducer，再导入真实需求，迁移成本最低
- 用 `未绑定` 作为合法状态，能避免在需求未导入阶段出现伪精确 ID
- 保持 `requirements` 侧为 canonical mapping，AI 侧只做引用，符合 repo-first 治理边界

## 已验证无效的路线

- 让 runtime hook 自动猜测 `REQ` / `WS` 绑定，当前没有稳定语义来源，风险过高
- 把 metadata 只写在自由文本里，不给统一字段，会削弱后续脚本校验和自动提炼能力
- 在需求尚未导入前预先发明 `REQ` / `WS` 编号，会破坏后续追踪一致性

## 尚未尝试但建议的路线

- 在导入第一批真实需求后，选一个 workstream 试跑完整链路：requirements -> traceability matrix -> handoff/status/session/reducer metadata
- 后续为治理脚本增加 AI 侧 metadata 与 traceability matrix 的一致性校验
- 当 status 文档真正启用后，再评估是否对 metadata 缺失从 warning 升级为 error

## 下一位 Agent 的第一步动作

- 在第一批真实 `REQ` / `WS` 文档落地后，优先用一个真实任务验证 metadata 能否从 requirements 侧顺畅传递到 handoff、session 和 reducer 输出

## 建议同步更新

- 真实需求导入后更新 `docs/requirements/traceability-matrix.md`
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
