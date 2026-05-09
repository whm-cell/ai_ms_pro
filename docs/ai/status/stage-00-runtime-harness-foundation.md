# Stage-00 Runtime Harness Foundation Status

更新时间：2026-05-08
阶段：stage-00
状态：进行中

## 需求与工作流标识

- Requirement IDs：REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-008, REQ-009
- Workstream IDs：WS-01, WS-02, WS-03
- 当前阶段已通过 WS-01、WS-02、WS-03 完成三个真实场景的 requirements traceability 与实现验证。

## 当前阶段目标

- 建立可恢复、可压缩、可验证的 runtime / governance / verification harness。
- 用真实业务薄切片验证 PRD 能通过 REQ/WS 进入 harness，而不是把完整 PRD 长期放进默认上下文。
- 把 GitHub private Free 最大边界、AI/Agent security guardrails、context budget、skill eval 和 code-shape 债务做成可复查证据。

## 当前完成度

- Runtime / Governance / Verification 主链路已可用：Stop hooks、runtime reducer、runtime sanitizer、external content boundary metadata、high-impact action matrix、traceability metadata、repo-local Python runner、hook sync、governance、code shape、context budget、requirements shape、GitHub guardrails 和 skill eval checks 均已落地。
- WS-01、WS-02、WS-03 均有 repo-native 实现和 smoke；WS-03 继续以浏览器薄切片验证 REQDOC-003，未引入完整 Godot 工程。
- `new_pro_standard` 已同步机制层；当前 repo 的 REQ/WS、PR、CI、status、样本和历史 truth 不复制到 starter。
- `.agents/skills` 已作为按需方法层接入；Candidate workflow skills 保持显式触发，不替代 requirements、status、ADR、checks 或 `AGENTS.md`。
- GitHub 侧已有 workflow 最小权限、concurrency、timeout、CODEOWNERS、PR template、Dependabot grouping / PR limit、dependency review、security evidence、PR touch conflict、branch hygiene strict PR budget、`delete_branch_on_merge` 和 `merge_group` 触发；当前仓库为 private 且账号为 GitHub Free，branch protection / rulesets 已确认为 plan-limited future gates。

## 本阶段关键成果

- 三个 workstream 已跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 默认上下文面已通过 stage compression 降到预算 warning 以下；ADR 计数也低于预算。
- Candidate workflow skills 已有两个 accepted real-task eval samples，但仍不自动升级 always-on。
- `new_pro_standard` 保持机制层同步，不复制当前项目 truth。
- AI/Agent security P0/P1/P2 已覆盖 runtime redaction、外部内容 source boundary 和高影响动作矩阵，降低敏感信息扩散、间接 prompt injection 和 excessive agency 风险。

## 风险与阻塞

- OPEN-01 已调整为 private GitHub Free 最大边界：GitHub API 对 branch protection / rulesets 返回 plan limit HTTP 403；远端 required checks、review、conversation resolved 和禁止直推 `main` 不能声明已强制，但也不再作为本地代码缺口追打。
- PR #1 的已合并 Codex 分支已删除；失败的 Dependabot GitHub Actions PR #2-#6 已关闭并删除分支；当前剩余远端非 main 分支都对应 open 且 green 的 PR。active PR 预算为 total 10、Codex 3、Dependabot 4、failed open 0。
- dependency review、Scorecard、CodeQL、SBOM 当前仍以 advisory / artifact evidence 为主；private Free 下不作为 required gate，升级 blocking 需要 GitHub 计划/可见性变化和更多 CI burn-in。
- runtime stage drift、archive candidate、context budget、source boundary 和 change-triggered followups 继续 warning / review-required；高影响动作矩阵不允许 hooks 自动执行 destructive、externally visible 或 permission-changing 动作。
- Code-shape 债务已收窄：runtime traceability、reducer、bootstrap `render_plan` 和 governance traceability 函数 warning 已消除；剩余见 OPEN-14。
- REQDOC-003 的 Godot 4.6.2、GUT、导出 preset、素材、本地化和发布管线仍是 proposed / 待确认；root repo 只保留 harness 研究所需的薄业务样本。

## 本轮收敛

- 上下文：默认面执行 stage compression，细节下沉到按需文档；旧 ADR 开始移入 ADR archive，避免 ADR 计数长期卡预算。
- 业务样本：WS-03 新增连击计分与评级反馈，并由 `scripts/godot_platformer_slice_smoke.py` 覆盖。
- Skill eval：本轮登记 SAMPLE-002，`prd-to-project-skills` 与 `progressive-feature-development` 达到 2/2 accepted eval samples；是否升级仍需单独决策，不自动 always-on。
- Code-shape：已拆出多组 renderer/catalog/traceability 小模块；剩余大文件按 OPEN-14 分批拆。
- Security：新增 runtime sanitizer、requirements source boundary metadata 和 high-impact action matrix；runtime 写入、SessionStart 读取和 reducer 草稿生成都会做 best-effort redaction，高影响动作只允许提示、dry-run、draft 或 evidence collection。

## 下一阶段重点

- 继续推动 OPEN-01：在 private Free 能力边界内积累 CI evidence；branch protection / rulesets / required reviews 仅作为升级计划或改 public 后的 future gates。
- 观察 AI/Agent guardrails 真实样本：source boundary warning 误报率、高影响动作 review-required 提示是否足够清晰，以及是否需要后续升级或保持 advisory。
- 将 `godot_platformer_slice_smoke.py` 接入独立 CI PR，避开 Dependabot workflow PR 的 touch-set 冲突。
- 评估 Candidate workflow skills 达到 2/2 后是否保持显式调用、升级稳定 skill，或继续观察更多样本。
- 继续压缩 Stage-00 历史：完成型 handoff 归档、status 保持摘要、ADR 旧决策归档或 supersede。
- 继续按 OPEN-14 分批拆剩余 code-shape 债务。

## 验收判断

- Stage-00 已证明 harness 能跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 当前尚未完全进入下一阶段，因为 CI burn-in、Godot engine spike、长期 skill/PR 样本和 AI/Agent guardrails 真实样本仍需确认；远端强制门禁在 private Free 下已归类为 plan-limited ceiling。
- 剩余风险主要是远端 enforcement 不可用时的人审纪律、长期上下文增长和维护性债务，不是本地 harness 能否使用。

## 关联文档

- [项目计划](../plan.md)
- [Harness Remaining Work](../harness-open-items.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Agent Harness Security](../security/agent-harness-security.md)
- [Candidate Skill Usage Samples](../skill-usage-samples.md)
- [ADR-014 Context Budget Audit](../adr/ADR-014-context-budget-audit.md)
- [ADR-015 Progressive Feature And PRD Skills](../adr/ADR-015-progressive-feature-and-prd-skills.md)
