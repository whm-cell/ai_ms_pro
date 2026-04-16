下面是基于当前状态整理的 **harness backlog**，按优先级排过序。

**P0**
- `Runtime session 防误提交`
  在 [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py) 或 `pre-commit` 里加规则：如果 `/.codex/runtime/sessions/` 或 `/.codex/runtime/observations/` 被 staged，直接报错。
  价值：立刻保护“runtime 不是主真相”这条边界。
  成本：低。

- `working-context 新鲜度检查`
  检查 [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md) 是否落后于最新 active handoff/status。
  先做 warning 即可。
  价值：防止当前态长期失真。
  成本：低到中。

- `handoff 堆积阈值检查`
  当 `docs/ai/handoffs/active/` 超过阈值且没有 `status` 时给 warning。
  价值：把 `handoff -> status` 压缩链路真正用起来。
  成本：低。

**P1**
- `Stop hook 分级策略`
  现在 diff-aware 只是 warning。下一步要定义哪些目录变化升级成阻断。
  例如：
  - `cmd/`、`internal/`、`pkg/` 改了但 `docs/ai/` 没动，warning
  - 架构核心目录改了且没有 `ADR` 或 `working-context` 变化，error
  价值：把“文档更新是完成条件”落成更强约束。
  成本：中。

- `Runtime session 最小模板`
  给 `/.codex/runtime/sessions/` 增加一个模板约定，明确每个 session 文件至少包含：
  - 当前目标
  - 已尝试
  - 当前 open loops
  - 下次 resume 提示
  价值：后续才能谈 session 自动化。
  成本：低。

- `Session -> Handoff 提炼规则`
  先不自动生成，先写规则：哪些 session 结果必须升格成 handoff，升格时保留哪些字段。
  价值：避免 runtime 层越积越多却没人提炼。
  成本：低到中。

**P2**
- `Runtime hooks 真正写 session 文件`
  这是 Runtime Harness 的第一条真正自动化链路。
  可以先只做 `Stop` 时写一个本地 session 文件。
  价值：把“目录约定”变成“可运行能力”。
  成本：中。
  风险：一旦实现不好，容易产生噪音文件。

- `SessionStart / Resume 读取最近 session`
  新 session 时自动读取最近一个 session 文件，作为恢复材料。
  价值：真正解决长上下文恢复。
  成本：中。
  风险：如果恢复内容太长，会反过来污染上下文。

- `Observations 采集`
  给 `/.codex/runtime/observations/` 增加最小可用采集逻辑。
  价值：为后续长期经验提炼打基础。
  成本：中。

**P3**
- `Observations -> Long-term memory reducer`
  把 observations 中稳定结论提炼到 `handoff/status/ADR`。
  价值：形成完整闭环。
  成本：中到高。

- `Requirement/workstream metadata`
  在 handoff/status/session 中引入 requirement ID / workstream ID。
  价值：后续真实需求导入后，追踪能力会更强。
  成本：中。

- `CI 强校验`
  把 [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py) 放进 CI。
  价值：把本地约束升级为仓库级约束。
  成本：中。

**我建议的执行顺序**
1. `Runtime session 防误提交`
2. `working-context 新鲜度检查`
3. `handoff 堆积阈值检查`
4. `Runtime session 最小模板`
5. `Session -> Handoff 提炼规则`
6. 再决定是否做真正的 runtime hooks

原因很简单：  
先把 **边界和校验补全**，再去做 runtime 自动化。否则你会很快得到一堆 session 文件，但没有稳定的提炼和治理闭环。

如果你要继续，我建议下一步直接做这三个 P0：
- 防误提交
- working-context 新鲜度 warning
- handoff 堆积阈值 warning