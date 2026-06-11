# Runtime Observations

本目录保存运行时观察材料，例如：

- 工具调用观察
- 压缩前快照
- 需后续提炼的临时发现

当前最小实现：

- `Stop` hook 会 best-effort 追加 observation 到 `YYYY-MM-DD.jsonl`
- `Stop` hook 会 best-effort 追加 portable trace 到 `agent-traces/YYYY-MM-DD.agent-trace.jsonl`
- 每条记录都是 append-only 原料，不直接替代 `handoff`、`status`、`adr`
- observation 会记录时间戳、session id、agent、当前分支/线程、工作区变更、是否建议提升到共享治理层

当前字段侧重点：

- `prompt_preview`：本次 Stop 事件可提取到的精简用户意图
- `changed_paths` / `changed_path_count`：当前工作区触碰范围
- `needs_governance_promotion` / `promotion_reason`：供后续 reducer 或主 Agent 判断是否要升格为 `handoff`
- `requirement_ids` / `workstream_ids`：如 payload 或环境显式提供，则一并写入 observation 原料，供 reducer 聚合

Trace producer：

- trace 文件使用 `docs/ai/standards/agent-trace.schema.json` 的 `agent-trace/v1` 形状
- trace record 从已清洗 observation 字段派生，不写入完整 prompt、完整 transcript、secret 或未审查外部内容
- trace 文件仍是本地 runtime 原料；稳定结论需要由主 Agent 审核后再提升到共享治理文档

Reducer 用法：

- `python3 scripts/reduce_runtime_observations.py`
  默认读取最近一个 observation JSONL，并输出 handoff-compatible 草稿到 stdout
- `python3 scripts/reduce_runtime_observations.py --input /path/to/observations.jsonl --output /tmp/observation-draft.md`
  显式指定输入文件和输出路径
- `python3 scripts/reduce_runtime_observations.py --requirement-id REQ-001 --workstream-id WS-01`
  为生成草稿显式补齐 requirement/workstream metadata
- 默认提升顺序是 `observations -> handoff draft -> 主 Agent 审核 -> status/ADR`

规则：

- 只保存本地 runtime 原料
- 不直接代替 `handoff`、`status`、`adr`
- 有复用价值的稳定结论，应提炼后写入仓库治理文档
