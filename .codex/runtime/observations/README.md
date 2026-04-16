# Runtime Observations

本目录保存运行时观察材料，例如：

- 工具调用观察
- 压缩前快照
- 需后续提炼的临时发现

当前最小实现：

- `Stop` hook 会 best-effort 追加 observation 到 `YYYY-MM-DD.jsonl`
- 每条记录都是 append-only 原料，不直接替代 `handoff`、`status`、`adr`
- observation 会记录时间戳、session id、agent、当前分支/线程、工作区变更、是否建议提升到共享治理层

当前字段侧重点：

- `prompt_preview`：本次 Stop 事件可提取到的精简用户意图
- `changed_paths` / `changed_path_count`：当前工作区触碰范围
- `needs_governance_promotion` / `promotion_reason`：供后续 reducer 或主 Agent 判断是否要升格为 `handoff`

Reducer 用法：

- `python3 scripts/reduce_runtime_observations.py`
  默认读取最近一个 observation JSONL，并输出 handoff-compatible 草稿到 stdout
- `python3 scripts/reduce_runtime_observations.py --input /path/to/observations.jsonl --output /tmp/observation-draft.md`
  显式指定输入文件和输出路径
- 默认提升顺序是 `observations -> handoff draft -> 主 Agent 审核 -> status/ADR`

规则：

- 只保存本地 runtime 原料
- 不直接代替 `handoff`、`status`、`adr`
- 有复用价值的稳定结论，应提炼后写入仓库治理文档
