# Harness Remaining Work

更新时间：2026-05-26
当前状态：核心链路已在测试仓库、仓外 starter 复演、WS-01 Three.js Snake capability sample 和 WS-02 Harness Trace Console governance UI sample 中跑通；`new_pro_standard` 已补齐 starter-safe runtime hooks、context / lint gates 和空样本闭环；WS-01 pause/resume 与 reset-best 已作为 workflow simple-skip 真实样本纳入账本并记录 keep-advisory 决策；当前 blocking browser smoke 保留 WS-01 / WS-02；剩余项以真实样本观察、远端 plan ceiling 和 closeout review 为主。

## 作用

本文件用于集中列出当前 harness 仍未完成的事项。

它关注的是“还差什么才能更稳定、更可复用”，不是历史回顾。

## 当前判断

- `0 -> 1 初始化可用性` 已在测试仓库和仓外 starter 复演中验证完成。
- `requirements -> implementation -> smoke -> runtime promotion -> status` 已在新仓库内跑通。
- Stop hook 的 `REQ/WS` 自动发现已覆盖 `observation -> session -> reducer draft` 流程。
- Runtime sanitizer 已覆盖 Stop observation、Stop session、SessionStart additional context 和 reducer draft；prompt preview、transcript path 与历史 runtime 读取路径会做 best-effort redaction。
- Requirements source docs 已增加 source trust、instruction handling 和 sanitization status；外部网页摘录 / 大段粘贴需求必须作为 evidence / data 处理，而不是 agent 可执行指令。
- 高影响动作矩阵已覆盖远端分支删除、PR close / merge、workflow permission、secret / env、deployment / release、external sending、destructive file / database operations；hooks 只允许提示、dry-run、draft 或 evidence collection。
- `threejs-snake` 是当前 WS-01 harness capability validation sample；pause/resume 与 reset-best 小切片已补入 deterministic smoke、黑盒 smoke 和 `GAP-WORKFLOW-SIMPLE-SKIP` accepted 样本账本。`harness-trace-console` 是当前 WS-02 governance UI sample。
- GitHub workflow 已加入最小权限、concurrency、timeout、full-SHA action pinning、fixed-version Playwright smoke browser / CLI packages、WS-01 / WS-02 browser smoke、code-shape、Windows hook runtime job、PR touch conflict check、change-triggered advisory summary、`merge_group` 触发、dependency review workflow 和 security evidence workflow。
- CODEOWNERS、PR template、Dependabot grouping / PR limit、branch hygiene strict PR budget 与 `delete_branch_on_merge` 配置已落地；仓库现为 private 且账号为 GitHub Free，GitHub API 对 branch protection / rulesets 返回 plan limit HTTP 403，因此这些能力当前只能作为 future upgrade gates，不能作为 Stage-00 本地工程阻塞项。
- `$progressive-feature-development` 与 `$prd-to-project-skills` 已进入 root 和 starter 的 `.agents/skills` 机制层，作为 Candidate skills 显式调用；当前仍保持 Candidate，避免把方案先行流程变成简单任务默认流程。
- `scripts/check_repo_skills.py`、`scripts/check_requirements_shape.py`、`scripts/check_skill_usage_samples.py`、`scripts/check_github_guardrails.py` 与 `scripts/check_change_triggered_followups.py` 已落地为 warning-only evidence / follow-up checks。
- Agentic standards 相关 trace / eval / tool-contract / sample-gap checks 已落地为可校验 contract；维护规则、互通边界和最小验证命令见 `$harness-maintenance` `references/agentic-standards.md`。
- P0 linter 已落地为 `pyproject.toml` + pinned Ruff + `git diff --check`；当前只覆盖保守 Python lint 和 whitespace，不替代 semantic standards review、security policy 或 tool-contract checks。
- External standards crosswalk 与 agentic control matrix 已落地；第一阶段只作为 evidence / gap review，不把 hosted trace/eval、MCP/A2A 或外部 collector 视为已完成。
- `docs/ai/check-registry.md` 已记录 check 等级；Scorecard、CodeQL、SBOM 和 dependency review 已作为 security evidence / advisory evidence 接入，第一阶段不作为 required checks；triage / SLO 见 `docs/ai/security/security-evidence-triage.md`。
- Candidate skill promotion 已从“样本登记”升级为 with/without 对照 eval；技术假设检查要求状态和 verification method。
- project architecture/style/dependency skill 生命周期已进入模板与 ADR；默认不进入短链路，也不新增 blocking checker。
- context budget audit 已完成首轮 OPEN-10 triage 并补充增长护栏：starter/default 目标保持 6500，当前 root 预算为 8500，80/90 高水位、ADR 到达预算和 stage status 行数触发 warning。
- archive candidate monitor 已落地为 warning-only 检查；自动归档仍不纳入默认 hook。
- runtime reducer、runtime traceability、bootstrap `render_plan`、governance traceability、working-context sync metadata、bootstrap harness、governance checker、eval checker、code-shape checker 和 requirements-shape checker 已完成低风险拆分；`check_code_shape.py --all` 当前无 warning，后续新增 warning 按新的 code-shape batch 处理。
- 当前剩余问题不再是“能不能用”，而是 `post-burn-in event-driven sample watchlist + private-Free plan ceiling visibility + security evidence triage samples + AI/Agent guardrails sample monitoring + runtime / trace interop sample monitoring`；`GAP-WORKFLOW-SIMPLE-SKIP` 已达到 2/2 但保持 keep-advisory，下一步需要 WS-01 之外的 simple-skip、negative 或 process-tax 样本；无法主动验证的真实样本统一留存在 [Harness Real Sample Watchlist](./harness-real-sample-watchlist.md)，以后遇到真实事件再唤醒。
- `new_pro_standard` 现在可作为复制到新项目的 starter：已包含 PreToolUse / Stop warning hooks、runtime sanitizer、traceability / local trace producer、Ruff / whitespace gate、context-budget gate、starter sample-gap 空账本和 no-write checker；它仍有意排除当前 repo 的真实样本 ledger、upgrade decision 结论、runtime 原料和 WS-01 / WS-02 demo apps。

## P0 当前最值得做

### OPEN-15 Agentic Harness Gap Roadmap

- 目标：把动作前拦截、loop/scope monitor、本地 trace summary、candidate check burn-in、red-team 样本、tool/skill surface control 和 task profile audit 拆成可验证的小切片。
- 当前状态：差距和迭代顺序已记录在 [Agentic Harness Gap Roadmap](./agentic-harness-gap-roadmap.md)；P0 preflight guard v1、P1 loop / scope monitor、P1 local trace summary、P1 sample-gap readiness / pending queue、P1 candidate check burn-in ledger、P2 red-team local replay 和 P2 task profile audit 均已形成 warning-only / advisory v1；WS-01 pause/resume 与 reset-best 提供了 2 个 workflow simple-skip accepted real samples，并已 keep-advisory。
- 下一步：当前只在真实 warning、真实跨任务 resume、真实 security workflow、真实高影响确认、真实 workflow skill task、真实 red-team incident 或真实 remote interop 出现时唤醒对应 no-write review lane；不再把反复运行 planner / intake / readiness 当成当前推进项。
- 完成定义：每个切片都有最小脚本或 hook、单测、文档入口和样本证据；新能力默认 advisory / warning-only，升级 blocking 前必须按 check registry 记录真实样本、误报率和修复路径；默认上下文不因路线图膨胀。

### OPEN-01 Private GitHub Free 最大边界与 CI evidence burn-in

- 目标：在 private GitHub Free 的能力边界内，把可用的本地/CI/process 证据层跑满；branch protection、rulesets、required checks、required reviews 和 merge queue 保留为升级 GitHub 计划或改 public 后的 future gates。
- 当前状态：首轮 PR + main push 远端 CI burn-in 已完成；repo 内 workflow、CODEOWNERS、PR template、PR touch conflict checker、advisory follow-up summary、check registry、security evidence workflow、Dependabot、dependency review 与 `scripts/check_github_guardrails.py` 已落地；GitHub API 已对 branch protection / rulesets 返回 private-Free plan limit HTTP 403，后续不应继续把该项当作本地代码缺口。
- 首轮完成定义状态：远端 workflow 通过、本地 governance / code-shape / smoke / Windows runtime job 可见、dependency review job 在 PR 上可见、branch protection / rulesets 输出 plan-limited `UNKNOWN`、失败结果能定位到治理维度。
- 后续观察：继续积累至少一轮 scheduled / 后续 PR security evidence 样本，确认 CodeQL code-scanning 注解是否持续出现；除非升级 GitHub plan、改 public 或启用 code scanning，不把该注解升级为 blocking。

## 本轮已关闭

### Workspace Sandbox Manifest 与 Agentic Red-Team Coverage

- 结果：新增 workspace sandbox manifest、checker 和 red-team local-replay 样本账本，把 prompt injection、tool-output injection、skill squatting、memory/context poisoning、handoff / A2A confusion、cascade autonomy、human confirmation 和 sandbox claim honesty 纳入同一账本。
- 关闭原因：已形成本地可校验的 sandbox / rehydration boundary 和 agentic red-team routing surface。
- 备注：该 manifest 和 red-team replay 样本都是 repo-local contract，不是 `.codex` 运行时配置，也不是 native sandbox provider。

### Eval Runner、Trace Local / OTLP Pilot Adapter 与 Sample Gap Collector

- 结果：新增 eval runner、trace exporter、sample gap collector 和对应单测；governance workflow 已接入 runner dry-run、trace sample local export 和 sample gap collector；trace exporter 新增 no-network `otlp-http-json` pilot，显式 `--send --endpoint` 才会 POST。
- 关闭原因：eval runner + deterministic grader + trace evidence binding、本地 `agent-trace/v1` export adapter、OTLP HTTP JSON pilot、security / guardrail / workflow sample collection harness 已具备本地可验证路径。
- 备注：OpenAI hosted trace/eval、MCP / A2A 真实互通、外部 collector、scheduled / PR / 跨 workstream 真实样本仍是 future work。

### P0 Linter、Trace Producer 与 External Standards Crosswalk

- 结果：新增 P0 Ruff linter、CI `git diff --check`、Stop hook `agent-trace/v1` producer、external standards crosswalk，并把 Ruff / whitespace check 写入 tool contract registry。
- 关闭原因：linter、trace producer、external standards crosswalk 已转为 repo 内可检查或可路由 artifact。
- 备注：Ruff 当前启用 `E9` 与 Pyflakes `F`；Stop trace 仍是 `.codex/runtime/*` 本地原料，不自动成为共享治理真相。

### OPEN-12 Runtime 敏感信息脱敏闭环

- 结果：新增 runtime sanitizer，Stop observation、Stop session、SessionStart additional context 和 reducer draft 已统一脱敏；2026-05-08 已按人工指令清理旧 runtime observation/session 文件。
- 关闭原因：已补测试覆盖 secret / token / email / phone / transcript path，不再只靠 `compact_text()` 截断。
- 备注：这是 best-effort 防扩散层，不替代 secret scanning；历史本地 runtime 文件若要彻底清理，仍需人工删除或重建。

### OPEN-13 Prompt injection 边界与高影响动作矩阵

- 结果：requirements source template 与现有 source docs 已补 `来源可信度`、`指令处理`、`清洗状态`；`scripts/check_requirements_shape.py` 会对缺失或语义不清的边界元数据输出 review-required warning；新增 `docs/ai/security/agent-action-guardrails.md`，并在 `scripts/check_change_triggered_followups.py` 中加入 `high-impact-agent-actions` advisory follow-up。
- 关闭原因：外部内容已明确作为 evidence / data 处理，不作为 agent 可执行指令；高影响动作已具备人工确认、允许工具、验证证据和 hook automation boundary 的可审计矩阵。
- 备注：P1/P2 均先保持 warning / review-required，不直接升级 blocking；后续用真实 source、GitHub、deployment 或 external-send 样本观察误报率和 reviewer 负担。

### OPEN-02 外部独立路径复演

- 结果：已在仓外临时目录完成 `starter copy -> bootstrap --force -> git config core.hooksPath .githooks -> git add -> .githooks/pre-commit`。
- 关闭原因：starter 的 `run_with_repo_python.sh` 已修复 macOS `/bin/bash` 3.2 空数组兼容性问题，`check_code_shape.py --staged` 也已把 unborn `HEAD` 的首提交 scaffold 视为 baseline。
- 备注：starter copied placeholder docs 若要立刻替换成新项目名，仍需显式 `--force`；`AGENTS.md` 仍由人工项目化，README 与 portability guide 已同步说明。

### OPEN-03 Runtime Metadata 自动发现验证

- 结果：Stop runtime observation/session 已支持 changed paths、workstream 模块路径和 traceability matrix 驱动的 `REQ/WS` 自动发现。
- 关闭原因：已补 observation、session 以及 reducer draft 三层测试，零配置路径能稳定携带 `Requirement IDs` 与 `Workstream IDs`。

### OPEN-04 Reducer 压缩阈值验证

- 结果：已统计多日 observation 样本，并用代表性样本跑 reducer 审查。
- 关闭原因：已形成当前阈值判定标准：runtime-only 或无工作区变更保留本地；单次共享层改动默认生成 handoff 草稿；跨 session 重复出现且已影响 stage 风险、规则或长期策略时再压缩到 `status` 或 `ADR`。
- 备注：后续长期样本质量继续归入 OPEN-01 / stage compression 观察，不再作为“基础阈值未定义”缺口。

### OPEN-05 更广的黑盒浏览器回归

- 结果：已新增 WS-01 和 WS-02 的黑盒浏览器 smoke。
- 关闭原因：两个真实 workstream 都不再只依赖内部 test API。

### OPEN-06 Traceability / Metadata 一致性自动校验

- 结果：governance checker 已校验 `working-context` 的 `Current Stage` 与 traceability matrix 中当前 REQ/WS 的 STAGE 关系；runtime session / observation artifact 的同类错配先以 warning 暴露。
- 关闭原因：已具备至少一层 `REQ <-> WS <-> STAGE` 自动校验，primary truth mismatch 会阻断，runtime/reducer mismatch 先保持 warning-only。

### OPEN-10 Context budget warning triage

- 结果：已创建 [上下文预算 OPEN-10 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/上下文预算OPEN-10使用细节.md)；当前 root Stage-00 budget 调整为 8500，starter/new-project 初始目标保留 6500；默认面 80/90 高水位、ADR 到达预算和 stage status 行数纳入 warning。
- 关闭原因：已完成本轮“是否调整预算、是否压缩默认面、是否接 Stop hook”的判断；context budget audit 继续保持 warning-only 手动运行，不自动 compact，不自动归档。
- 备注：未来如果 context budget 再次持续 warning，再开新的 triage 项，而不是把 OPEN-10 长期保持开放。

### OPEN-14 Code-shape 分批拆分

- 结果：`check_ai_governance.py`、`bootstrap_harness.py`、`check_agent_eval_dataset.py`、`check_code_shape.py` 与 `check_requirements_shape.py` 已拆分到 code-shape 阈值内；新增 helper 模块保持 CLI / facade 行为不变。
- 关闭原因：`check_code_shape.py --all` 当前无 warning；原有大文件 warning、`check_candidate` 函数 warning 和 eval checker warning 都已清掉。
- 备注：后续若新增 warning，应作为新的 code-shape batch 处理，不重开 OPEN-14。

## P1 次高优先级

### OPEN-11 多人 / 多 AI PR touch-set 冲突控制验证

- 目标：用真实团队 PR 样本验证 `$team-pr-conflict-control` 是否能降低同文件改动、治理文件冲突和 merge queue 前返工。
- 当前缺口：repo-local skill、PR template、changed-files overlap check 与 `merge_group` workflow 触发已落地；仍缺少真实多人 PR 样本和远端 merge queue / branch protection enforcement。
- 当前验证：`docs/ai/skill-evals/SAMPLE-001-team-pr-conflict-control-validation.md` 已完成结构、discoverability、当前 PR 与离线场景矩阵验证；该验证不计入真实多人 PR accepted 样本。
