# Harness Remaining Work

更新时间：2026-05-02
当前状态：核心链路已在测试仓库和仓外 starter 复演中跑通；CI、hook sync、traceability alignment、runtime metadata 自动发现、WS-01/WS-02 黑盒 smoke、GitHub ownership/supply-chain 守门、可选行为护栏 skill、项目 skill 生命周期模板与 context budget audit 已落地，剩余项以远端 burn-in、GitHub 侧规则确认和后续真实项目样本观察为主

## 作用

本文件用于集中列出当前 harness 仍未完成的事项。

它关注的是“还差什么才能更稳定、更可复用”，不是历史回顾。

## 当前判断

- `0 -> 1 初始化可用性` 已在测试仓库和仓外 starter 复演中验证完成
- `requirements -> implementation -> smoke -> runtime promotion -> status` 已在新仓库内跑通一轮
- Stop hook 的 `REQ/WS` 自动发现现已覆盖 `observation -> session -> reducer draft` 流程
- `harness-trace-console` 与 `threejs-snake` 均已具备黑盒浏览器 smoke；`WS-01` 不再只有 deterministic smoke
- GitHub workflow 已加入最小权限、concurrency、timeout、code-shape、Windows hook runtime job 和 dependency review workflow
- CODEOWNERS 与 Dependabot 配置已落地；GitHub ruleset / branch protection 仍需在远端人工确认
- Karpathy-style 行为护栏已进入 starter 机制层，但仍保持显式调用，不替代仓库治理文档或检查脚本
- project architecture/style/dependency skill 生命周期已进入模板与 ADR；默认不进入短链路，也不新增 blocking checker
- context budget audit 已完成首轮 OPEN-10 triage：starter/default 目标保持 6500，当前 root Stage-00 预算调为 8500，`AGENTS.md`、current status 与 skill description 已压缩，仍保持 warning-only 手动运行
- archive candidate monitor 已落地为 warning-only 检查；自动归档仍不纳入默认 hook
- 当前剩余问题不再是“能不能用”，而是 `CI burn-in + branch protection/ruleset confirmation + longer-term reducer/runtime sample monitoring`

## P0 当前最值得做

### OPEN-01 CI burn-in、required checks 与 GitHub ruleset 确认

- 目标：让新落地的 `governance + windows-hook-runtime + smoke + dependency-review` 守门在 GitHub 远端积累稳定运行历史，并进入 branch protection / ruleset required checks
- 当前缺口：repo 内 workflow、CODEOWNERS、Dependabot 与 dependency review 文件已落地，但还没有足够的远端 green history，也不能从本地证明 GitHub ruleset 已配置
- 远端配置细节：[GitHub 远端配置确认细节](../../--使用细节/github-remote-configuration.md)
- 完成定义：
  - 至少一轮远端 workflow 通过
  - `python3 scripts/sync_hooks_config.py --check` 自动运行
  - `python3 scripts/check_ai_governance.py` 自动运行
  - `python3 scripts/check_code_shape.py --all` 自动运行
  - `python3 scripts/threejs_snake_smoke.py`、`python3 scripts/threejs_snake_blackbox_smoke.py`、`python3 scripts/harness_trace_console_smoke.py` 与 `python3 scripts/harness_trace_console_blackbox_smoke.py` 自动运行
  - Windows runner 至少跑通 Python resolution / hook runner 相关测试
  - dependency review job 在 PR 上可见
  - GitHub branch protection / ruleset 要求 `governance`、`windows-hook-runtime`、`smoke` 和 dependency review job 通过，且要求 PR review、CODEOWNERS review、conversation resolved，并禁止直接 push 到 `main`
  - 失败结果能直接定位到 governance、hook sync、code-shape、Windows runner、supply-chain 或 smoke 维度

## 本轮已关闭

### OPEN-02 外部独立路径复演

- 结果：已在仓外临时目录完成 `starter copy -> bootstrap --force -> git config core.hooksPath .githooks -> git add -> .githooks/pre-commit`
- 关闭原因：starter 的 `run_with_repo_python.sh` 已修复 macOS `/bin/bash` 3.2 空数组兼容性问题，`check_code_shape.py --staged` 也已把 unborn `HEAD` 的首提交 scaffold 视为 baseline
- 备注：starter copied placeholder docs 若要立刻替换成新项目名，仍需显式 `--force`；`AGENTS.md` 仍由人工项目化，README 与 portability guide 已同步说明

### OPEN-03 Runtime Metadata 自动发现验证

- 结果：Stop runtime observation/session 已支持 changed paths、workstream 模块路径和 traceability matrix 驱动的 `REQ/WS` 自动发现
- 关闭原因：已补 observation、session 以及 reducer draft 三层测试，零配置路径能稳定携带 `Requirement IDs` 与 `Workstream IDs`

### OPEN-04 Reducer 压缩阈值验证

- 结果：已统计 2026-04-16 至 2026-04-30 的多日 observation 样本，并用 `2026-04-30.jsonl` 跑 reducer 样本审查
- 关闭原因：已形成当前阈值判定标准：runtime-only 或无工作区变更保留本地；单次共享层改动默认生成 handoff 草稿；跨 session 重复出现且已影响 stage 风险、规则或长期策略时再压缩到 `status` 或 `ADR`
- 备注：后续长期样本质量继续归入 OPEN-01 / stage compression 观察，不再作为“基础阈值未定义”缺口

### OPEN-05 更广的黑盒浏览器回归

- 结果：已新增 `scripts/threejs_snake_blackbox_smoke.py`，覆盖真实页面 `load -> keyboard turn -> game over -> Enter restart`
- 关闭原因：`WS-01` 已有黑盒用户路径，`WS-02` 已有黑盒 DOM 路径，两个真实 workstream 都不再只依赖内部 test API

### OPEN-06 Traceability / Metadata 一致性自动校验

- 结果：governance checker 已校验 `working-context` 的 `Current Stage` 与 traceability matrix 中当前 REQ/WS 的 STAGE 关系；runtime session / observation artifact 的同类错配先以 warning 暴露
- 关闭原因：已具备至少一层 `REQ <-> WS <-> STAGE` 自动校验，primary truth mismatch 会阻断，runtime/reducer mismatch 先保持 warning-only

### OPEN-10 Context budget warning triage

- 结果：已创建 [OPEN-10 Context Budget 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/context-budget-open-10.md)；当前 root Stage-00 budget 调整为 8500，starter/new-project 初始目标保留 6500；`AGENTS.md` 压缩到 300 行以内，current status 压缩为短判断，`$repo-governed-coding` description 已缩短
- 关闭原因：已完成本轮“是否调整预算、是否压缩默认面、是否接 Stop hook”的判断；context budget audit 继续保持 warning-only 手动运行，不自动 compact，不自动归档
- 备注：未来如果 context budget 再次持续 warning，再开新的 triage 项，而不是把 OPEN-10 长期保持开放

## P1 次高优先级

- 暂无。当前剩余 P1 级 hardening 已转入本轮关闭项或 OPEN-01 远端确认。

## P2 策略性决策

### OPEN-07 Starter 是否保留 Quick Notes 样板

- 目标：决定 `Quick Notes Inbox` 是继续作为 starter 自带样板，还是只保留治理机制层
- 当前缺口：当前测试仓库已经证明样板有价值，但 starter 默认是否应带示例仍未定
- 完成定义：
  - 明确选择“保留样板”或“只保留治理面”
  - 相应更新 starter 文档和迁移说明

### OPEN-08 行为护栏 skill 是否升级为默认 workflow

- 目标：观察 `$repo-governed-coding` 在更多真实任务中的收益，决定它继续显式调用，还是升级为更稳定的 stage / repo 默认策略
- 当前缺口：已进入 starter，但还缺少多任务样本证明它适合作为默认工作流
- 完成定义：
  - 至少几个非平凡实现/审查任务中显式使用该 skill
  - 能证明 assumptions / scope / success criteria / verification plan 对 handoff/status 提炼有实际帮助
  - 若升级为默认，补对应 `status` 或 `ADR`；若不升级，保持显式调用并避免写入 always-on 规则

### OPEN-09 Project architecture/style/dependency skill 生命周期真实样本观察

- 目标：验证 `docs/ai/templates/project-skill-lifecycle.md` 是否足以指导新项目在架构、样式和依赖约束变化时创建、升级、偏离或废弃项目 skill
- 当前缺口：模板、ADR 与 starter 同步已落地，但还缺少真实新项目中的多轮 architecture/style/dependency skill 使用样本
- 完成定义：
  - 模板存在且不进入默认短链路
  - ADR 已采纳并说明 skill 不替代 canonical governance truth
  - `new_pro_standard` 已同步模板和说明
  - governance check 与 code-shape check 通过
  - 至少一个后续真实项目能按 `Draft -> Candidate Skill -> Stable Skill -> Promote -> Deprecate` 路径处理项目约束变更

## 当前不纳入本轮

- 发布 / 部署体系
- 多 workstream 并行治理
- 复杂前端或后端工具链验证
- 自动归档 handoff / changelog 策略；当前只提供 warning-only candidate monitor
- CodeQL；等业务代码进入 release / CI maturity 阶段后再评估

## 建议阅读顺序

1. [AI 文档入口索引](./index.md)
2. [当前工作上下文](./working-context.md)
3. [Stage-00 Runtime Harness Foundation Status](./status/stage-00-runtime-harness-foundation.md)
4. [New Repo Rehearsal Handoff](./handoffs/archive/stage-00-new-repo-rehearsal.md)
