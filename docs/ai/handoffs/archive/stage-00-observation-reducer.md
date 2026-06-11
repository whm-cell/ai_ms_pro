# Observation Reducer Handoff

更新时间：2026-04-16
阶段：stage-00
任务：observation-reducer
状态：已归档（历史 observation reducer handoff，当前真相已吸收到 status / closeout handoff）

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 历史语境：当时 reducer 已支持 metadata 位点，但项目尚未导入真实需求绑定

## 本任务目标

- 为 runtime observations 补上一个显式触发的 reducer，形成从本地 observation 原料到共享治理层的最小闭环
- 保持 reducer 先生成 handoff-compatible 草稿，而不是直接改写 canonical `status` 或 `ADR`
- 用 ADR 固化 observation reduction 的默认顺序，避免后续扩展时边界漂移

## 已完成内容

- 新增 reducer 脚本 [reduce_runtime_observations.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/reduce_runtime_observations.py)，会读取 observation JSONL 并输出 handoff-compatible markdown 草稿
- reducer 默认优先处理 `needs_governance_promotion=true` 的 observation；如果没有 promotable 记录，则回退到最近 observations
- reducer 支持 `--input`、`--output`、`--limit`、`--stage`、`--task`、`--title`、`--requirement-id`、`--workstream-id` 参数，便于按需生成草稿
- 新增 [ADR-003-observation-reducer-order.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/archive/ADR-003-observation-reducer-order.md)，正式采纳 “observations -> handoff draft -> 主 Agent 审核 -> status/ADR” 的默认顺序
- 新增 [ADR-004-requirement-workstream-metadata.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)，正式采纳 requirement/workstream metadata 的统一位点和绑定规则
- 更新 [AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)、[working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)、[index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md) 和 runtime observations README，同步 reducer 的职责边界与 metadata 规则
- 已用临时 observation JSONL 样本手工验证 reducer 输出结构，确认生成结果可直接作为 handoff 草稿起点

## 修改文件

- [reduce_runtime_observations.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/reduce_runtime_observations.py)
- [ADR-003-observation-reducer-order.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/archive/ADR-003-observation-reducer-order.md)
- [ADR-004-requirement-workstream-metadata.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)
- [AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [observations/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/observations/README.md)
- [working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)

## 关键实现决策

- observation reducer 作为显式脚本运行，不接入 hook 自动执行
- reducer 默认输出 handoff-compatible 草稿，而不是直接输出 canonical `status` 或 `ADR`
- reducer 只根据 observation 中的 promotion flag、共享层 changed paths、prompt preview、promotion reason 和显式 requirement/workstream metadata 生成候选摘要，最终发布仍由主 Agent 审核决定
- 当 observations 中没有 promotable 记录时，reducer 允许回退到最近 observations，以便生成 review 起点，但这类草稿默认不应直接发布

## 当前未完成项

- 尚未把 reducer 输出与 session 文件自动关联
- 尚未定义 reducer 何时应直接建议 `status` 或 `ADR` 候选
- 尚未在真实长期 observation 数据上验证 reducer 的噪音水平
- 尚未验证真实任务绑定进入后，metadata 与 `traceability-matrix.md` 的同步流程是否顺滑

## 已知风险与注意事项

- reducer 依赖 best-effort observation 字段，若 hook payload 变化，输出质量可能下降
- observations 的 `changed_paths` 来源于当前工作区可见改动，不是精确的 per-step provenance
- 当前 reducer 只做轻量聚合与模板渲染，尚未做去重、聚类或多阶段压缩
- 如果 observation 文件样本太少，生成的草稿更多是 review 起点，而不是接近完成的 canonical handoff

## 已验证有效的路线

- 把 observations 的默认提升顺序定义为 handoff-first，能和现有 `handoff -> status -> adr/changelog` 链路兼容
- 使用显式脚本而不是 hook 自动发布，能保留主 Agent 的语义判断边界
- 先输出 handoff-compatible 结构，再视稳定性继续压缩，适合当前 STAGE-00 的治理成熟度

## 已验证无效的路线

- 让 observations 直接产出 canonical `status` 或 `ADR`，会把局部线索过早提升为长期真相
- 让 reducer 在 hook 中自动执行并回写共享文档，会破坏 repo-first 治理边界
- 完全不做 reducer，只保留 observation 原料，无法形成稳定的共享接力闭环

## 尚未尝试但建议的路线

- 为 reducer 接入 session 文件引用，提升草稿对上下文的还原能力
- 在 reducer 中增加重复模式识别，只有跨 session 稳定出现时才建议压缩到 `status` 或 `ADR`
- 在真实需求导入后，用 `--requirement-id` / `--workstream-id` 运行 reducer，验证 metadata 是否足够支撑后续追踪

## 后续参考动作

- 若后续要复核 reducer，再用真实 runtime observation 样本运行 [reduce_runtime_observations.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/reduce_runtime_observations.py)，并结合当前 active closeout handoff 和 `working-context.md` 判断是否要发布新的 canonical handoff

## 建议同步更新

- 如果 reducer 在真实 observation 数据上稳定可用，后续补 `status` 或新的 ADR 记录其压缩阈值
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
