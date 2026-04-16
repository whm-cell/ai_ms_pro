下面这版是把你当前仓库落成一个**可执行的 harness 分层设计稿**。它不是抽象概念，而是直接对应到现有文件和后续建议新增的目录。

**分层落点**
**1. Runtime Harness**
职责：解决长上下文、resume、压缩前保存、当前会话恢复。

建议放这里的内容：
- [/.codex/hooks.json](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks.json)
- `/.codex/hooks/*.py`
- 新增 `/.codex/runtime/sessions/` 或 `/.codex/runtime/session/`
- 可选新增 `/.codex/runtime/observations/`

建议性质：
- `gitignore`
- 本地状态
- 不进入 `docs/ai/index.md`
- 不作为项目主真相

建议命名：
- `/.codex/runtime/sessions/2026-04-16T15-32-10_main_<thread-or-branch>.md`
- 一个 session 一个文件
- 追加或独立写入，不覆盖旧文件

**2. Governance Harness**
职责：把“当前项目真相”沉淀成 repo 内共享记忆。

你现在已经有这些核心文件：
- [AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [docs/ai/plan.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [docs/ai/handoffs/active/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/_template.md)
- [docs/ai/status/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/_template.md)
- [docs/ai/changelog/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/changelog/_template.md)
- [docs/ai/adr/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/_template.md)

建议继续明确其角色：
- `working-context.md`
  当前态，只保留下一次会话必须立即继承的信息。
- `handoff`
  子任务/暂停/接力的标准交付物。
- `status`
  阶段级压缩。
- `adr`
  长期有效决策。
- `index.md`
  活跃入口，不是自动日志。

**3. Verification Harness**
职责：强制不漏更，但不代写文档。

你现在已有：
- [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)
- [scripts/check_ai_docs.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_docs.py)
- [scripts/check_ai_doc_quality.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_doc_quality.py)
- [/.codex/hooks/stop_ai_docs_check.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_ai_docs_check.py)
- `/.githooks/pre-commit`

它们的职责应保持为：
- 校验
- 阻断
- 报错
- 不自动代写 `index.md` / `handoff` / `status`

**建议目录图**
```text
/Volumes/usd/codes/go_projects/ai_ms_pro
├── AGENTS.md
├── .codex/
│   ├── hooks.json
│   ├── hooks/
│   └── runtime/
│       ├── sessions/          # 新增，建议 gitignore
│       └── observations/      # 可选，后续再加
├── docs/
│   ├── ai/
│   │   ├── index.md
│   │   ├── working-context.md
│   │   ├── plan.md
│   │   ├── handoffs/
│   │   │   ├── active/
│   │   │   └── archive/
│   │   ├── status/
│   │   ├── changelog/
│   │   └── adr/
│   └── requirements/
├── scripts/
│   ├── check_ai_governance.py
│   ├── check_ai_docs.py
│   └── check_ai_doc_quality.py
└── .githooks/
    └── pre-commit
```

**更新流转**
**A. 新 session / resume**
- 读取 [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md) 和 [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- 如需恢复细节，再按需读取最近一个 `/.codex/runtime/sessions/*.md`
- 不更新共享治理文档

**B. 工作进行中**
- runtime hook 可写 session 文件
- 不改 `index.md`
- 不改 `status`
- 不改 `ADR`

**C. 子任务完成或暂停**
- 主 agent 产出或落地一个 `handoff`
- 必要时更新 `working-context.md`
- 若新增活跃 handoff，主 agent 更新 `index.md`

**D. 多个 handoff 积累 / 阶段变化**
- 主 agent 产出 `status`
- 必要时归档旧 handoff
- 更新 `index.md`

**E. 长期决策形成**
- 主 agent 产出 `ADR`
- 更新 `index.md`

**F. Stop / pre-commit / CI**
- 只检查是否漏更
- 不自动补文档
- 失败则阻断

**责任边界**
**runtime hook**
- 只写 `/.codex/runtime/...`
- 不写 `docs/ai/*.md`

**main agent**
- 是共享治理文档的唯一最终作者
- 负责 `working-context`、`handoff`、`status`、`adr`、`index`

**subagent**
- 最稳妥的做法是：返回结构化完成结果或 handoff 草稿
- 由 main agent 落地到 canonical `docs/ai/handoffs/active/*.md`
- 不直接改 `index.md`、`status`、全局 `working-context`

这点我建议比之前再收紧一点。这样多 agent 时更稳。

**每层该放什么**
**session 文件放：**
- 本次会话目标
- 做了哪些尝试
- 哪些命令/文件被碰过
- 当前 open loops
- 下次 resume 提示

**不要放：**
- 阶段正式结论
- 最终架构决策
- 需要 repo 审计的正式交接结论

**handoff 放：**
- 本任务目标
- 已完成内容
- 修改文件
- 关键实现决策
- 当前未完成项
- 风险和下一步

建议你给 handoff 再补三项：
- 已验证有效的路线
- 已验证无效的路线
- 尚未尝试但建议的路线

**working-context 放：**
- 当前主目标
- 当前活跃队列
- 当前风险阻塞
- 最近固化的关键结论
- 下一次会话先读哪些文档

**不要放：**
- 全部历史试错细节
- 已结束子任务的长过程记录

**校验策略建议**
当前脚本已经能查结构。后续应加这几条最有价值：

- 源码变更但 `docs/ai/` 无变化时，warning 或 error
- 新增活跃 `handoff/status/adr/changelog` 后，`index.md` 未同步时报错
- `working-context.md` 时间明显落后于最新 handoff/status 时，warning
- 活跃 handoff 超过阈值但没有 `status` 时，warning
- `/.codex/runtime/sessions/` 出现在 git staged 里时，报错
  这条很重要，因为 runtime 状态不该污染仓库主真相

**为什么这版对后续扩展友好**
这套设计以后可以平滑扩展：
- 加 requirement ID / workstream ID
- 加 branch/worktree/session metadata
- 加 session 到 handoff 的半自动摘要
- 加 observations 和长期经验提炼
- 加 CI 强校验
- 加更多 subagent

因为边界已经先定死了：
- runtime 是 runtime
- governance 是 governance
- verification 是 verification

不会出现“以后想加功能，却发现 session 和 handoff 都在写同一种真相”的结构性冲突。

**我建议的下一步实施顺序**
1. 先写一个 ADR，定下这三层 harness 的职责边界。
2. 再新增 `/.codex/runtime/sessions/` 和 `.gitignore` 规则。
3. 再补 `AGENTS.md`，写清 main agent / subagent / hook 的写入边界。
4. 最后再升级校验脚本。

如果你要，我下一步就直接开始落地第 1 步和第 2 步：
- 写 `ADR-001-harness-layering.md`
- 新增 runtime session 目录约定
- 更新 `AGENTS.md` 和 `docs/ai/index.md` 的相关说明