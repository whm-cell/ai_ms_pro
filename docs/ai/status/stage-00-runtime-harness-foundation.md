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
- 把远端门禁、context budget、skill eval 和 code-shape 债务做成可复查证据。

## 当前完成度

- Runtime / Governance / Verification 主链路已可用：Stop hooks、runtime reducer、traceability metadata、repo-local Python runner、hook sync、governance、code shape、context budget、requirements shape、GitHub guardrails 和 skill eval checks 均已落地。
- WS-01、WS-02、WS-03 均有 repo-native 实现和 smoke；WS-03 继续以浏览器薄切片验证 REQDOC-003，未引入完整 Godot 工程。
- `new_pro_standard` 已同步机制层；当前 repo 的 REQ/WS、PR、CI、status、样本和历史 truth 不复制到 starter。
- `.agents/skills` 已作为按需方法层接入；Candidate workflow skills 保持显式触发，不替代 requirements、status、ADR、checks 或 `AGENTS.md`。
- GitHub 侧已有 workflow 最小权限、concurrency、timeout、CODEOWNERS、PR template、Dependabot grouping / PR limit、dependency review、security evidence、PR touch conflict、branch hygiene strict PR budget、`delete_branch_on_merge` 和 `merge_group` 触发；远端强制门禁仍需 branch protection / ruleset 证明。

## 本阶段关键成果

- 三个 workstream 已跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 默认上下文面已通过 stage compression 降到预算 warning 以下；ADR 计数也低于预算。
- Candidate workflow skills 已有两个 accepted real-task eval samples，但仍不自动升级 always-on。
- `new_pro_standard` 保持机制层同步，不复制当前项目 truth。

## 风险与阻塞

- OPEN-01 仍开放：`check_github_guardrails.py` 当前显示 `main` branch protection 404、branch rulesets 为空；远端 required checks、review、conversation resolved 和禁止直推 `main` 仍不能声明已强制。
- PR #1 的已合并 Codex 分支已删除；失败的 Dependabot GitHub Actions PR #2-#6 已关闭并删除分支；当前剩余远端非 main 分支都对应 open 且 green 的 PR。active PR 预算为 total 10、Codex 3、Dependabot 4、failed open 0。
- dependency review、Scorecard、CodeQL、SBOM 当前仍以 advisory / artifact evidence 为主；升级 blocking 需要远端能力和更多 CI burn-in。
- runtime stage drift、archive candidate、context budget 和 change-triggered followups 继续 warning-only；升级阻断要等更多样本。
- Code-shape 历史债务仍存在于 `check_ai_governance.py`、`bootstrap_harness.py`、runtime hooks、blackbox smoke 和 reducer；本轮只做低风险拆分。
- REQDOC-003 的 Godot 4.6.2、GUT、导出 preset、素材、本地化和发布管线仍是 proposed / 待确认；root repo 只保留 harness 研究所需的薄业务样本。

## 本轮收敛

- 上下文：默认面执行 stage compression，细节下沉到按需文档；旧 ADR 开始移入 ADR archive，避免 ADR 计数长期卡预算。
- 业务样本：WS-03 新增连击计分与评级反馈，并由 `scripts/godot_platformer_slice_smoke.py` 覆盖。
- Skill eval：本轮登记 SAMPLE-002，`prd-to-project-skills` 与 `progressive-feature-development` 达到 2/2 accepted eval samples；是否升级仍需单独决策，不自动 always-on。
- Code-shape：拆出 `code_shape_ast.py` 与 session snapshot renderer，减少低风险大文件压力；剩余大文件按后续 PR 继续拆。

## 下一阶段重点

- 继续推动 OPEN-01：获得远端 branch protection / ruleset 证据，或明确 GitHub plan / visibility blocker 后由人工配置处理。
- 将 `godot_platformer_slice_smoke.py` 接入独立 CI PR，避开 Dependabot workflow PR 的 touch-set 冲突。
- 评估 Candidate workflow skills 达到 2/2 后是否保持显式调用、升级稳定 skill，或继续观察更多样本。
- 继续压缩 Stage-00 历史：完成型 handoff 归档、status 保持摘要、ADR 旧决策归档或 supersede。
- 分批拆 `check_ai_governance.py`、`bootstrap_harness.py`、runtime hooks 和 reducer，避免一次性重写。

## 验收判断

- Stage-00 已证明 harness 能跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 当前尚未完全进入下一阶段，因为远端强制门禁、CI burn-in、Godot engine spike 和长期 skill/PR 样本仍需确认。
- 剩余风险主要是远端 enforcement、长期上下文增长和维护性债务，不是本地 harness 能否使用。

## 关联文档

- [项目计划](../plan.md)
- [Harness Remaining Work](../harness-open-items.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Candidate Skill Usage Samples](../skill-usage-samples.md)
- [ADR-014 Context Budget Audit](../adr/ADR-014-context-budget-audit.md)
- [ADR-015 Progressive Feature And PRD Skills](../adr/ADR-015-progressive-feature-and-prd-skills.md)
