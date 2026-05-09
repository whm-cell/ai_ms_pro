# Stage-00 Runtime Harness Foundation Status

更新时间：2026-05-09
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

- Runtime / Governance / Verification 主链路已可用：Stop hooks、runtime reducer/sanitizer、source boundary、action matrix、traceability、repo-local Python、hook sync、governance、code shape、context budget、requirements shape、GitHub guardrails 和 skill eval checks 已落地。
- WS-01、WS-02、WS-03 均有 repo-native 实现和 CI browser smoke；WS-03 继续以浏览器薄切片验证 REQDOC-003，未引入完整 Godot 工程。
- `new_pro_standard` 已同步机制层；当前 repo 的 REQ/WS、PR、CI、status、样本和历史 truth 不复制到 starter。
- `.agents/skills` 已作为按需方法层接入；Candidate workflow skills 保持显式触发，不替代 requirements、status、ADR、checks 或 `AGENTS.md`。
- GitHub 侧已有最小权限 workflow、full-SHA action pinning、fixed-version Playwright packages、CODEOWNERS、PR template、Dependabot、dependency review、security evidence、PR conflict / branch hygiene 和 `merge_group`；private Free 下 branch protection / rulesets 仍是 future gates。
- PR #11 已完成首轮远端 burn-in 并合入 `main`；merge commit `c1f170f` 的 `main` push workflows 均为 success。

## 本阶段关键成果

- 三个 workstream 已跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`，且 WS-01/02/03 browser smoke 已纳入 CI `smoke` job。
- 首轮 PR + main push CI burn-in 已跑通：PR #11 和合并后的 `main` push 覆盖 governance、Windows hook runtime、WS-01/02/03 smoke、dependency review、Scorecard、CodeQL artifact 和 SBOM artifact。
- 默认上下文面已通过 stage compression 降到预算 warning 以下；ADR 计数也低于预算。
- Candidate workflow skills 已有两个 accepted real-task eval samples，但仍不自动升级 always-on。
- `new_pro_standard` 保持机制层同步，不复制当前项目 truth。
- AI/Agent security P0/P1/P2 已覆盖 runtime redaction、source boundary、高影响动作矩阵、首批 samples 和 security triage。

## 风险与阻塞

- OPEN-01 已调整为 private GitHub Free 最大边界：GitHub API 对 branch protection / rulesets 返回 plan limit HTTP 403；远端 required checks、review、conversation resolved 和禁止直推 `main` 不能声明已强制，但也不再作为本地代码缺口追打。
- PR #1 的已合并 Codex 分支已删除；失败的 Dependabot GitHub Actions PR #2-#6 已关闭并删除分支；当前剩余远端非 main 分支都对应 open 且 green 的 PR。active PR 预算为 total 10、Codex 3、Dependabot 4、failed open 0。
- dependency review、Scorecard、CodeQL、SBOM 和 secret scanning advisory 当前仍以 advisory / artifact evidence 为主；private Free 下不作为 required gate；CodeQL code-scanning 注解已登记为 advisory platform evidence。
- runtime stage drift、archive candidate、context budget、source boundary 和 change-triggered followups 继续 warning / review-required；高影响动作矩阵不允许 hooks 自动执行 destructive、externally visible 或 permission-changing 动作。
- Code-shape 债务已收窄：runtime traceability、reducer、bootstrap `render_plan`、governance traceability、working-context sync metadata、governance main orchestration、trace console blackbox smoke 和 Stop observation warnings 已消除；剩余见 OPEN-14。
- REQDOC-003 的 Godot 4.6.2、GUT、导出 preset、素材、本地化和发布管线仍是 proposed / 待确认；root repo 只保留 harness 研究所需的薄业务样本。

## 本轮收敛

- 上下文：默认面执行 stage compression，细节下沉到按需文档；旧 ADR 开始移入 ADR archive，避免 ADR 计数长期卡预算。
- 业务样本：WS-03 新增连击计分与评级反馈，并由 `scripts/godot_platformer_slice_smoke.py` 覆盖；该 smoke 现已接入 CI。
- Skill eval：本轮登记 SAMPLE-002，`prd-to-project-skills` 与 `progressive-feature-development` 达到 2/2 accepted eval samples；是否升级仍需单独决策，不自动 always-on。
- Code-shape：已拆出多组 renderer/catalog/traceability/working-context metadata/orchestration 小模块，并提取 trace console blackbox 断言脚本；剩余大文件按 OPEN-14 分批拆。
- Security：新增 runtime sanitizer、source boundary metadata、action matrix、guardrail samples、security triage 和 Private Free attestation 边界；runtime 写入/读取路径会做 best-effort redaction，高影响动作只允许提示、dry-run、draft 或 evidence collection。

## 下一阶段重点

- OPEN-01 首轮远端 burn-in 已完成；下一步积累 scheduled / 后续 PR 样本；branch protection / rulesets / required reviews 仅作为 future gates。
- 观察 AI/Agent guardrails 与 security evidence 真实样本：source boundary warning 误报率、高影响动作 review-required 提示、security triage SLO 是否足够清晰，以及是否需要后续升级或保持 advisory。
- 继续观察 WS-01 / WS-02 / WS-03 browser smoke 在后续 CI 中的 burn-in 结果，失败时区分 Playwright 版本、浏览器安装和应用切片回归。
- 评估 Candidate workflow skills 达到 2/2 后是否保持显式调用、升级稳定 skill，或继续观察更多样本。
- 继续压缩 Stage-00 历史：完成型 handoff 归档、status 保持摘要、ADR 旧决策归档或 supersede。
- 继续按 OPEN-14 分批拆剩余 code-shape 债务。

## 验收判断

- Stage-00 已证明 harness 能跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 当前尚未完全进入下一阶段，因为 Godot engine spike、长期 skill/PR 样本、后续 CI 样本和 AI/Agent guardrails 真实样本仍需确认；远端强制门禁在 private Free 下已归类为 plan-limited ceiling。
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
