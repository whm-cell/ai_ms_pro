# Harness Remaining Work

更新时间：2026-05-09
当前状态：核心链路已在测试仓库、仓外 starter 复演和 REQDOC-003 -> WS-03 薄业务切片中跑通；WS-03 Godot thin-slice smoke 已接入 CI；Candidate workflow skills 达到 2/2 accepted eval 前置证据；GitHub private + Free 下 branch protection / ruleset 已确认为 plan-limited ceiling；CI action pinning、Playwright smoke browser / CLI 版本固定、security evidence triage、AI/Agent P0/P1/P2 guardrails 和首批 guardrail samples 已落地；OPEN-01 首轮 PR + main push 远端 CI burn-in 已完成；剩余项以真实样本观察、升级决策和 code-shape 分批拆分为主

## 作用

本文件用于集中列出当前 harness 仍未完成的事项。

它关注的是“还差什么才能更稳定、更可复用”，不是历史回顾。

## 当前判断

- `0 -> 1 初始化可用性` 已在测试仓库和仓外 starter 复演中验证完成
- `requirements -> implementation -> smoke -> runtime promotion -> status` 已在新仓库内跑通一轮
- Stop hook 的 `REQ/WS` 自动发现现已覆盖 `observation -> session -> reducer draft` 流程
- Runtime sanitizer 已覆盖 Stop observation、Stop session、SessionStart additional context 和 reducer draft；prompt preview、transcript path 与历史 runtime 读取路径会做 best-effort redaction
- Requirements source docs 已增加 source trust、instruction handling 和 sanitization status；外部 PRD / 网页摘录 / 大段粘贴需求必须作为 evidence / data 处理，而不是 agent 可执行指令；`external-web` / `third-party` / `unknown` 且 `pending` 的来源会触发 review-required warning
- 高影响动作矩阵已覆盖远端分支删除、PR close / merge、workflow permission、secret / env、deployment / release、external sending、destructive file / database operations；hooks 只允许提示、dry-run、draft 或 evidence collection
- `harness-trace-console`、`threejs-snake` 与 `godot-platformer-slice` 均已具备浏览器 smoke；`WS-03` 用薄切片验证长 PRD 进入 harness 的压缩路径
- GitHub workflow 已加入最小权限、concurrency、timeout、full-SHA action pinning、fixed-version Playwright smoke browser / CLI packages、WS-01 / WS-02 / WS-03 browser smoke、code-shape、Windows hook runtime job、PR touch conflict check、change-triggered advisory summary、`merge_group` 触发、dependency review workflow 和 security evidence workflow；`security-evidence.yml` 已被远端 API 识别，首轮 checkout 失败根因是误跟踪的演练输出 gitlink
- CODEOWNERS、PR template、Dependabot grouping / PR limit、branch hygiene strict PR budget 与 `delete_branch_on_merge` 配置已落地；仓库现为 private 且账号为 GitHub Free，GitHub API 对 branch protection / rulesets 返回 plan limit HTTP 403，因此这些能力当前只能作为 future upgrade gates，不能作为 Stage-00 本地工程阻塞项。
- Karpathy-style 行为护栏已进入 starter 机制层，但仍保持显式调用，不替代仓库治理文档或检查脚本
- `$progressive-feature-development` 与 `$prd-to-project-skills` 已进入 root 和 starter 的 `.agents/skills` 机制层，作为 Candidate skills 显式调用；SAMPLE-001 / SAMPLE-002 已达到 2/2 accepted eval 前置证据，但是否升级仍需单独决策，避免把方案先行流程变成简单任务默认流程
- `scripts/check_repo_skills.py`、`scripts/check_requirements_shape.py`、`scripts/check_skill_usage_samples.py`、`scripts/check_github_guardrails.py` 与 `scripts/check_change_triggered_followups.py` 已落地为 warning-only evidence / follow-up checks；`check_github_guardrails.py` 已拆分为 helper 模块并新增 orphan gitlink 检查，`check_change_triggered_followups.py --markdown` 已接入 PR / main push 的 GitHub Actions Summary 并显示 check level / CI coverage
- `docs/ai/check-registry.md` 已记录 check 等级；Scorecard、CodeQL、SBOM 和 dependency review 已作为 security evidence / advisory evidence 接入，第一阶段不作为 required checks；triage / SLO 见 `docs/ai/security/security-evidence-triage.md`
- Candidate skill promotion 已从“样本登记”升级为 with/without 对照 eval；PRD 技术假设检查要求状态和 verification method
- REQDOC-003 已完成首轮标准化并绑定 REQ-007 / REQ-008 / REQ-009 与 WS-03；Godot engine 仍保持 proposed，后续如继续推进应先做独立 engine spike
- project architecture/style/dependency skill 生命周期已进入模板与 ADR；默认不进入短链路，也不新增 blocking checker
- context budget audit 已完成首轮 OPEN-10 triage 并补充增长护栏：starter/default 目标保持 6500，当前 root Stage-00 预算为 8500，80/90 高水位、ADR 到达预算和 stage status 行数触发 warning；本轮已执行默认面 compression 并开始归档旧 ADR；changed-file follow-up triage 继续 warning-only / 按需使用
- archive candidate monitor 已落地为 warning-only 检查；自动归档仍不纳入默认 hook
- runtime reducer、runtime traceability、bootstrap `render_plan`、governance traceability 和 working-context sync metadata 校验已完成低风险拆分；本轮已消除对应 code-shape warning
- 当前剩余问题不再是“能不能用”，而是 `post-burn-in sample monitoring + private-Free plan ceiling visibility + security evidence triage samples + AI/Agent guardrails sample monitoring + runtime sample monitoring`

## P0 当前最值得做

### OPEN-01 Private GitHub Free 最大边界与 CI evidence burn-in

- 目标：在 private GitHub Free 的能力边界内，把可用的本地/CI/process 证据层跑满；branch protection、rulesets、required checks、required reviews 和 merge queue 保留为升级 GitHub 计划或改 public 后的 future gates
- 当前状态：首轮 PR + main push 远端 CI burn-in 已完成；repo 内 workflow、CODEOWNERS、PR template、PR touch conflict checker、advisory follow-up summary、check registry、security evidence workflow、Dependabot、dependency review 与 `scripts/check_github_guardrails.py` 已落地；PR touch conflict 在 burn-in 阶段只阻断已确认 high-risk overlap；GitHub API 已对 branch protection / rulesets 返回 private-Free plan limit HTTP 403，后续不应继续把该项当作本地代码缺口
- 远端配置细节：[GitHub 远端配置确认细节](../../--使用细节/GitHub远端配置确认细节.md)
- 首轮完成证据：
  - PR #11 已合并到 `main`，merge commit 为 `c1f170faa701885882a0ed7a2105c1054fe956ea`
  - PR #11 上 `Dependency Review`、`governance`、`windows-hook-runtime`、`smoke` 和 `security-evidence` 全部通过
  - `main` push 上 [Governance And Smoke run 25599034611](https://github.com/whm-cell/ai_ms_pro/actions/runs/25599034611) 通过，覆盖 hook sync、main advisory summary、main branch hygiene、unit tests、AI governance、code-shape、Windows hook runtime、WS-01 / WS-02 / WS-03 smoke
  - `main` push 上 [Security Evidence run 25599034597](https://github.com/whm-cell/ai_ms_pro/actions/runs/25599034597) 通过，Scorecard、CodeQL artifact 和 SBOM artifact 完成；CodeQL code-scanning 上传注解已登记到 security evidence triage，当前按 advisory / plan-setting 边界处理
- 首轮完成定义状态：
  - 至少一轮远端 workflow 通过：已完成
  - `python3 scripts/sync_hooks_config.py --check` 自动运行
  - `python3 scripts/check_ai_governance.py` 自动运行
  - `python3 scripts/check_code_shape.py --all` 自动运行
  - `scripts/check_change_triggered_followups.py --markdown` 在 PR / main push 的 GitHub Actions Summary 中展示 advisory follow-ups
  - `python3 scripts/threejs_snake_smoke.py`、`python3 scripts/threejs_snake_blackbox_smoke.py`、`python3 scripts/harness_trace_console_smoke.py`、`python3 scripts/harness_trace_console_blackbox_smoke.py` 与 `python3 scripts/godot_platformer_slice_smoke.py` 自动运行，覆盖 WS-01 / WS-02 / WS-03 browser smoke
  - Windows runner 至少跑通 Python resolution / hook runner 相关测试
  - dependency review job 在 PR 上可见；private Free 下若无法作为 required check，则保持 advisory / evidence，不升级 blocking
  - `scripts/check_github_guardrails.py` 对 branch protection / rulesets 输出 private-Free plan-limited `UNKNOWN`，并在 recommended actions 中提示“升级计划或改 public 后再启用”，而不是继续要求本地修复
  - GitHub Actions workflow 的 third-party / official actions 使用 full-length commit SHA pinning，并保留原 tag 注释，后续 Dependabot /人工升级时同步验证
  - Playwright browser install 和 smoke CLI 使用 workflow 级 `PLAYWRIGHT_VERSION` / `PLAYWRIGHT_CLI_VERSION` 固定 npm package 版本，避免 smoke job 运行时跟随 `latest` 漂移
  - Future upgrade gates 记录在 `docs/ai/security/remote-merge-gates.md`：若仓库升级 GitHub plan 或改 public，再要求 `governance`、`windows-hook-runtime`、`smoke`、dependency review、PR review、CODEOWNERS review、conversation resolved 和禁止直推 `main`
  - `scripts/check_branch_hygiene.py --strict` 显示 active PR budget 未超限、failed open 0/0，且 stale remote/local branch 均为 0；PR #11 合并并清理本地 stale 分支后为 total 2/10、Codex 0/3、Dependabot 2/4；open PR 分支通过 merge/close 消化，不直接删除
  - GitHub Actions 默认 token 若无法读取 `statusCheckRollup.*.workflowRun`，branch hygiene summary 必须明确显示 failed-open-PR 审计降级说明；active PR budget 与 stale/unmanaged branch 检查继续运行，不把权限不足伪装成完整 OK
  - `scripts/check_github_guardrails.py` 能返回远端状态；未登录、缺权限或 plan-limited 时必须明确显示 `UNKNOWN`，不能伪装成 OK
  - 失败结果能直接定位到 governance、hook sync、code-shape、Windows runner、supply-chain 或 smoke 维度
- 后续观察：继续积累至少一轮 scheduled / 后续 PR security evidence 样本，确认 CodeQL code-scanning 注解是否持续出现；除非升级 GitHub plan、改 public 或启用 code scanning，不把该注解升级为 blocking

## 本轮已关闭

### OPEN-12 Runtime 敏感信息脱敏闭环

- 结果：新增 runtime sanitizer，Stop observation、Stop session、SessionStart additional context 和 reducer draft 已统一脱敏；2026-05-08 已按人工指令清理 49 个旧 runtime observation/session 文件
- 关闭原因：已补测试覆盖 secret / token / email / phone / transcript path，不再只靠 `compact_text()` 截断
- 备注：这是 best-effort 防扩散层，不替代 secret scanning；历史本地 runtime 文件若要彻底清理，仍需人工删除或重建

### OPEN-13 Prompt injection 边界与高影响动作矩阵

- 结果：`docs/requirements/source/_template.md` 与现有 source docs 已补 `来源可信度`、`指令处理`、`清洗状态`；`scripts/check_requirements_shape.py` 会对缺失或语义不清的边界元数据输出 review-required warning；新增 `docs/ai/security/agent-action-guardrails.md`，并在 `scripts/check_change_triggered_followups.py` 中加入 `high-impact-agent-actions` advisory follow-up
- 关闭原因：外部内容已明确作为 evidence / data 处理，不作为 agent 可执行指令；高影响动作已具备人工确认、允许工具、验证证据和 hook automation boundary 的可审计矩阵；2026-05-09 已记录首批 P1/P2 guardrail samples
- 备注：P1/P2 均先保持 warning / review-required，不直接升级 blocking；后续用真实 PRD、GitHub、deployment 或 external-send 样本观察误报率和 reviewer 负担

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

- 结果：已创建 [上下文预算 OPEN-10 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/上下文预算OPEN-10使用细节.md)；当前 root Stage-00 budget 调整为 8500，starter/new-project 初始目标保留 6500；默认面 80/90 高水位、ADR 到达预算和 stage status 行数纳入 warning；`AGENTS.md` 压缩到 300 行以内，current status 压缩为短判断，`$repo-governed-coding` description 已缩短
- 关闭原因：已完成本轮“是否调整预算、是否压缩默认面、是否接 Stop hook”的判断；context budget audit 继续保持 warning-only 手动运行，不自动 compact，不自动归档
- 备注：未来如果 context budget 再次持续 warning，再开新的 triage 项，而不是把 OPEN-10 长期保持开放

## P1 次高优先级

### OPEN-14 Code-shape 分批拆分

- 目标：继续把大 harness 脚本拆成可审查的小模块，保持行为不变、验证先行
- 当前缺口：`check_ai_governance.py` 和 `bootstrap_harness.py` 文件总长仍 warning；剩余主要是大文件模块边界继续拆分，不再有本轮已知的 hard-ceiling function warning
- 已完成：`reduce_runtime_observations.py` 渲染拆分、`runtime_traceability.py` catalog 拆分、`bootstrap_harness.py::render_plan` 拆分、`check_ai_governance.py` traceability catalog / alignment / working-context sync metadata / main orchestration 拆分，`harness_trace_console_blackbox_smoke.py::smoke_steps` 断言脚本提取，以及 `stop_runtime_observation.py` 小幅压缩到阈值内
- 完成定义：剩余 warning 分批消除；每批保持 CLI 行为不变，并跑相关 unittest、`check_code_shape.py --all`、`check_ai_governance.py` 与 `git diff --check`

### OPEN-11 多人 / 多 AI PR touch-set 冲突控制验证

- 目标：用真实团队 PR 样本验证 `$team-pr-conflict-control` 是否能降低同文件改动、治理文件冲突和 merge queue 前返工
- 当前缺口：repo-local skill、PR template、changed-files overlap check 与 `merge_group` workflow 触发已落地；仍缺少真实多人 PR 样本和远端 merge queue / branch protection enforcement
- 当前验证：`docs/ai/skill-evals/SAMPLE-001-team-pr-conflict-control-validation.md` 已完成结构、discoverability、当前 PR 与离线场景矩阵验证；该验证不计入真实多人 PR accepted 样本
- 完成定义：
  - 至少两次多人或多 AI 并行 PR 使用该 skill 记录 touch-set overlap、high-risk files 与 coordination action
  - 若样本有效，再决定是否进一步收紧 merge queue / required-check enforcement
  - 若样本证明流程税高于收益，保持显式调用并不升级 always-on

## P2 策略性决策

### OPEN-07 Starter 是否保留 Quick Notes 样板

- 目标：决定 `Quick Notes Inbox` 是继续作为 starter 自带样板，还是只保留治理机制层
- 当前缺口：当前测试仓库已经证明样板有价值，但 starter 默认是否应带示例仍未定
- 完成定义：
  - 明确选择“保留样板”或“只保留治理面”
  - 相应更新 starter 文档和迁移说明

### OPEN-08 行为护栏 skill 是否升级为默认 workflow

- 目标：观察 `$repo-governed-coding` 在更多真实任务中的收益，决定它继续显式调用，还是升级为更稳定的 stage / repo 默认策略
- 当前缺口：已进入 starter，且本轮明确不把功能开发全流程并入默认 workflow；仍缺少多任务样本证明 `$repo-governed-coding` 是否适合升级
- 完成定义：
  - 至少几个非平凡实现/审查任务中显式使用该 skill
  - 能证明 assumptions / scope / success criteria / verification plan 对 handoff/status 提炼有实际帮助
  - 若升级为默认，补对应 `status` 或 `ADR`；若不升级，保持显式调用并避免写入 always-on 规则
  - `$harness-maintenance` 仍保持按需调用；不要把 runtime / hook / GitHub / code-shape 细则重新塞回 `AGENTS.md`

### OPEN-09 Project architecture/style/dependency skill 生命周期真实样本观察

- 目标：验证 `docs/ai/templates/project-skill-lifecycle.md` 是否足以指导新项目在架构、样式和依赖约束变化时创建、升级、偏离或废弃项目 skill
- 当前缺口：模板、ADR、starter 同步、两个 Candidate workflow skills 与 with/without eval registry 已落地；`check_skill_usage_samples.py` 当前显示两个 workflow skills 都是 0/2 accepted eval samples
- 完成定义：
  - 模板存在且不进入默认短链路
  - ADR 已采纳并说明 skill 不替代 canonical governance truth
  - `new_pro_standard` 已同步模板和说明
  - Candidate workflow skills 已验证不会替代 requirements / AI governance truth
  - `check_skill_usage_samples.py` 已显示关键 Candidate skills 达到 2 个 accepted with/without eval samples；下一步是决定升级、继续观察或保持 Candidate
  - governance check 与 code-shape check 通过
  - 至少一个后续真实项目能按 `Draft -> Candidate Skill -> Stable Skill -> Promote -> Deprecate` 路径处理项目约束变更

## 当前不纳入本轮

- 发布 / 部署体系
- 多 workstream 并行治理；当前仅新增 `$team-pr-conflict-control` 作为按需方法层，未做全局阻断式并行治理
- 复杂前端或后端工具链验证
- 自动归档 handoff / changelog 策略；当前只提供 warning-only candidate monitor
- CodeQL blocking / required-check 升级；当前仅作为 security evidence advisory 运行，等业务代码进入 release / CI maturity 阶段后再评估

## 建议阅读顺序

1. [AI 文档入口索引](./index.md)
2. [当前工作上下文](./working-context.md)
3. [Stage-00 Runtime Harness Foundation Status](./status/stage-00-runtime-harness-foundation.md)
4. [New Repo Rehearsal Handoff](./handoffs/archive/stage-00-new-repo-rehearsal.md)
