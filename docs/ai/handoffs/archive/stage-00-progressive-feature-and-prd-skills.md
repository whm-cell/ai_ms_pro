# Progressive Feature And PRD Skills Handoff

更新时间：2026-05-04
阶段：stage-00
任务：progressive-feature-and-prd-skills
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务是 harness workflow 能力增强，不新增 requirements canonical mapping

## 本任务目标

- 把“渐进式功能发现”和“PRD-to-Skill 分类”做成两个独立 repo-local skills
- 避免把完整功能开发流程写成 always-on 规则，降低简单任务流程税
- 将同样机制同步进 `new_pro_standard`，但不复制当前 repo truth

## 已完成内容

- 新增 `$progressive-feature-development`，用于非平凡功能开发的技术方案 gate
- 新增 `$prd-to-project-skills`，用于把稳定 PRD / requirement / workstream 模式分类为候选项目 skill
- 为两个 skill 拆出 references checklist，避免 `SKILL.md` 过胖
- 同步两个 skill 到 `new_pro_standard/.agents/skills/`
- 新增 ADR-015 和 changelog，并同步当前 status / working-context / index / open-items

## 修改文件

- [.agents/skills/progressive-feature-development/SKILL.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.agents/skills/progressive-feature-development/SKILL.md)
- [.agents/skills/prd-to-project-skills/SKILL.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.agents/skills/prd-to-project-skills/SKILL.md)
- [new_pro_standard/.agents/skills/progressive-feature-development/SKILL.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/.agents/skills/progressive-feature-development/SKILL.md)
- [new_pro_standard/.agents/skills/prd-to-project-skills/SKILL.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/.agents/skills/prd-to-project-skills/SKILL.md)
- [ADR-015](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-015-progressive-feature-and-prd-skills.md)
- [Changelog](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/changelog/2026-05-04-progressive-feature-and-prd-skills.md)
- [AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [new_pro_standard/AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/AGENTS.md)
- [new_pro_standard/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/README.md)

## 关键实现决策

- 两个 workflow skill 均为 Candidate，并关闭隐式调用
- `AGENTS.md` 只保留触发规则，不展开完整功能开发流水线
- PRD 当前状态、验收进度、最新 smoke 证据和 blockers 继续留在 requirements / governance docs
- Starter 只同步机制层，不带当前 repo 的 REQ/WS、CI、PR 或历史状态

## 行为护栏摘要

- Assumptions：用户已选择两个独立 skill，并要求同步 starter
- Scope Boundary：不复制 ECC commands/hooks，不新增 blocking checker，不改业务功能
- Success Criteria：root/starter skill 结构有效，治理文档同步，简单任务不默认触发完整流程
- Verification：需运行 skill quick validate、governance check、context budget check

## 已验证有效的路线

- 使用 repo-local skill 承载渐进式发现方法，并让 ADR/status 记录长期边界
- 用 references checklist 承载 gate 细节，保持 `SKILL.md` 较轻

## 已验证无效的路线

- 直接把完整方案先行流程写入 `AGENTS.md` 会增加默认流程税
- 整包复制 ECC PRP commands/hooks 会形成第二套控制面

## 尚未尝试但建议的路线

- 在下一个真实非平凡功能任务里显式调用 `$progressive-feature-development`
- 在后续 PRD / workstream 梳理中显式调用 `$prd-to-project-skills`

## 当前未完成项

- 尚未形成两个新 skill 的真实项目使用样本
- 尚未决定这两个 Candidate skill 是否应升级为 stable 或 always-on 规则

## 已知风险与注意事项

- 不要把两个新 skill 当成简单任务默认流程
- 不要把 PRD 当前状态或最新验收证据写进 skill
- 后续若 skill 输出改变长期工作方式，应继续更新 ADR/status/check

## 下一位 Agent 的第一步动作

- 先运行验证命令；后续真实功能任务中再收集两个新 skill 是否降低返工和上下文成本的证据

## 建议同步更新

- 当前已同步 `status`、`working-context`、`index`、`harness-open-items`、ADR 和 changelog
