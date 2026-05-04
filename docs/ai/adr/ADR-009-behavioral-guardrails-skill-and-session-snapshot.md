# Behavioral Guardrails Skill And Session Snapshot

更新时间：2026-04-30
编号：ADR-009
标题：将 Karpathy-style 行为护栏沉淀为可选 skill 与 runtime session 快照字段
状态：已采纳

## 背景

- `forrestchang/andrej-karpathy-skills` 当前实现是一个轻量行为层：通过 `CLAUDE.md`、Claude plugin skill 和 Cursor rule 反复强调 assumptions、simplicity、surgical changes 与 goal-driven verification。
- 本仓库已经有 `Runtime Harness + Governance Harness + Verification Harness` 三层结构；直接把外部项目作为 always-on 规则并不能替代 `AGENTS.md`、`docs/ai/*`、`docs/requirements/*` 和检查脚本。
- 当前 root 已有 repo-local `$repo-governed-coding` skill，但 starter 还没有把它作为可复制机制层交付；runtime session 模板也没有显式留出 assumptions / scope / success criteria / verification plan 的提炼位点。

## 决策

- 采用外部项目中可复用的行为护栏思想，但只作为 task-level method layer。
- `new_pro_standard` 纳入 `.agents/skills/repo-governed-coding/`，默认显式调用，不作为 always-on 替代控制面。
- runtime session 模板和 Stop session 快照新增 `行为护栏快照`：
  - Assumptions
  - Scope Boundary
  - Success Criteria
  - Verification Plan
- active handoff 模板新增 `行为护栏摘要`，用于把 runtime/session 或 skill 过程中的关键执行判断提升为共享接力材料。
- starter `AGENTS.md` 增补 repo-local skill note 与 skill escalation policy，明确何时只留在 prompt、何时进入 `status`、何时提升到 `AGENTS.md` 或 `ADR`。
- 行为护栏产生的长期结论仍必须通过 `handoff -> status -> ADR/changelog` 或 requirements 文档提升；skill 不能自动决定治理层发布。

## 备选方案

- 方案 A：直接复制外部项目的 `CLAUDE.md` 作为 always-on 规则
- 方案 B：只保留当前 root repo-local skill，不放入 starter
- 方案 C：把行为护栏做成 verification 脚本的强制语义检查

## 决策理由

- 方案 A 会和当前 `AGENTS.md` 的仓库级规则重叠，而且容易让行为提示替代真实治理文档。
- 方案 B 让 root 有能力但 starter 缺少同等机制，后续新仓库仍要手工补一遍。
- 方案 C 难以可靠验证“是否足够简单”“是否有正确假设”等语义质量，容易变成文案级误报。
- 可选 skill + runtime session 快照位点能把行为约束变成可复用机制，同时保持主真相仍在治理文档和检查脚本中。

## 影响

- 新项目复制 `new_pro_standard` 后，可以通过 `$repo-governed-coding` 直接调用行为护栏。
- Runtime session 原料会提示主 Agent 填写 assumptions、scope、success criteria 和 verification plan，后续提升 handoff/status 时更容易保留关键执行判断。
- `AGENTS.md` 继续是默认规则入口；skill 只负责“怎么做”的方法约束，不负责“做不做”的治理决策。
- 本次采用外部项目的原则形态，不复制其平台绑定方式；Claude plugin、Cursor rule 只作为 packaging 参考，不进入当前 Codex-first 默认链路。

## 关联文档

- [Repo Governed Coding Skill](../../../.agents/skills/repo-governed-coding/SKILL.md)
- [Harness 可迁移清单](../harness-portability-guide.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [当前工作上下文](../working-context.md)
