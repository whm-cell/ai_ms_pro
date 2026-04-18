# 标准化需求：Traceability 交互筛选与详情检查

更新时间：2026-04-18
需求编号：REQ-005
来源文档：REQDOC-002
需求标题：支持按 requirement/workstream/stage/status 交互筛选 traceability
状态：已完成

## 背景

- 仅把 `traceability-matrix.md` 原样展示出来，还不能证明第二个真实场景具备实际使用价值。
- 为了验证 harness 在真实任务中的可读性，需要提供最基本的筛选、搜索和详情查看能力。

## 目标

- 提供按关键维度筛选 traceability 行的交互能力
- 让执行者能快速定位某个 requirement 或 workstream 的当前证据

## 范围

### 包含

- 按 `stage`、`workstream`、`status` 筛选
- 按文本搜索 requirement、workstream、验收证据
- 选中单条 requirement 显示详情面板

### 不包含

- 可视化编辑 traceability matrix
- 复杂图谱关系图或时序回放
- 全量 requirements lint 修复建议

## 验收条件

- 过滤器和搜索框能够改变可见条目集合
- 详情面板能显示被选中的 requirement/workstream/evidence
- 至少一个 workstream 可以被独立过滤并验证结果

## 依赖与前置条件

- 依赖 `REQ-004` 已完成主真相数据读取
- 依赖 traceability matrix 使用稳定的 Markdown 表格格式

## 风险与待澄清项

- 若后续 matrix 结构新增列，详情渲染逻辑需要调整
- 当前交互仍以轻量过滤为主，暂不覆盖更复杂的跨文档关联追踪

## 关联工作流

- WS-02：Harness Trace Console

## 关联阶段

- STAGE-00：真实场景验证与治理固化
