# Harness 可迁移清单

更新时间：YYYY-MM-DD
适用范围：将当前 Codex-first harness 迁移到一个全新的项目仓库

## 核心原则

- 复制机制，不复制当前项目真相。
- 机制层包括规则、hook、检查脚本、模板和 bootstrap 入口。
- 真相层包括当前项目的 `working-context`、`status`、`handoff`、`traceability-matrix`、真实 `REQ/WS` 文档和 runtime 原料。
- 新项目的第一步应该是 bootstrap 最小控制面，而不是直接沿用旧项目共享文档内容。

## 迁移时应保留

以下内容适合作为 harness 机制层复制到新仓库：

- `AGENTS.md`
- `.gitignore`
- `.githooks/pre-commit`
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/`
- `.github/CODEOWNERS`
- `.github/pull_request_template.md`
- `.github/workflows/`
- `.github/dependabot.yml`
- `.agents/skills/repo-governed-coding/`（可选行为护栏；只保留机制，不写当前项目真相）
- `.agents/skills/harness-maintenance/`（可选 harness 维护能力；下沉 runtime / hook / compression / verification / GitHub / code-shape 细则）
- `.agents/skills/requirements-traceability-maintenance/`（可选 requirements 维护能力；下沉 PRD / REQDOC / REQ / WS / traceability / 技术假设细则）
- `.agents/skills/progressive-feature-development/`（可选非平凡功能方案 gate；只保留机制，不写当前项目真相）
- `.agents/skills/prd-to-project-skills/`（可选 PRD-to-skill 分类器；只保留机制，不写当前项目真相）
- `.agents/skills/team-pr-conflict-control/`（可选多人 / 多 AI PR 冲突控制；只保留机制，不证明远端规则已启用）
- `.codex/requirements.txt`
- `scripts/check_ai_governance.py`
- `scripts/check_ai_docs.py`
- `scripts/check_ai_doc_quality.py`
- `scripts/check_archive_candidates.py`
- `scripts/check_context_budget.py`
- `scripts/check_change_triggered_followups.py`
- `scripts/check_repo_skills.py`
- `scripts/check_requirements_shape.py`
- `scripts/check_skill_usage_samples.py`
- `scripts/check_github_guardrails.py`
- `scripts/check_pr_touch_conflicts.py`
- `scripts/reduce_runtime_observations.py`
- `scripts/bootstrap_harness.py`
- `.codex/harness.toml`
- `docs/ai/handoffs/active/_template.md`
- `docs/ai/status/_template.md`
- `docs/ai/changelog/_template.md`
- `docs/ai/adr/_template.md`
- `docs/ai/templates/project-skill-lifecycle.md`
- `docs/ai/skill-evals/README.md`（eval 机制说明；不带当前项目样本）
- `docs/requirements/source/_template.md`
- `docs/requirements/normalized/_template.md`
- `docs/requirements/workstreams/_template.md`
- `.codex/runtime/sessions/_template.md`
- `.codex/runtime/README.md`
- `.codex/runtime/sessions/README.md`
- `.codex/runtime/observations/README.md`

## 迁移时应清空或重建

以下内容属于当前项目真相，不应原样带入新仓库：

- `docs/ai/index.md`
- `docs/ai/working-context.md`
- `docs/ai/plan.md`
- `docs/ai/handoffs/active/*.md`
- `docs/ai/status/*.md`
- `docs/ai/changelog/*.md`
- `docs/ai/adr/ADR-*.md`
- `docs/requirements/index.md`
- `docs/requirements/traceability-matrix.md`
- `docs/requirements/source/REQDOC-*.md`
- `docs/requirements/normalized/REQ-*.md`
- `docs/requirements/workstreams/WS-*.md`
- `.codex/runtime/sessions/*.md`
- `.codex/runtime/observations/*.jsonl`
- `apps/threejs-snake/`
- `apps/harness-trace-console/`
- 任意只服务于当前项目验证样板的 smoke 脚本

## 迁移时必须参数化

以下内容在新仓库里必须按项目实际情况调整：

- `AGENTS.md` 中的项目目标、文档职责和默认 workflow 偏好
- `.codex/harness.toml` 中的 `required_ai_docs`、`required_requirements_docs`、`context_surface` 与 `context_budget` 预算阈值
- `.githooks/pre-commit` 与 `.codex/hooks/*` 依赖的 Python 入口；默认会优先使用 repo-local `.codex/.venv/bin/python`，POSIX/macOS 与 Windows PowerShell fallback 会枚举候选并优先 Python 3.11+
- `.codex/hooks.json` 的 hook command entrypoint；bootstrap 会按当前宿主环境刷新为 `.ps1` 或 `.sh` 入口
- `.github/CODEOWNERS` 中的 owner 占位符；把 `@REPLACE_WITH_OWNER` 改为新项目真实 owner/team
- `.github/workflows/` 中的 smoke job；starter 默认只跑 harness context budget smoke，新项目应替换为真实业务 smoke
- `.codex/requirements.txt` 中的 Python 兼容依赖；当前默认是可选 best-effort 安装，不应让离线 bootstrap 直接失败
- `.agents/skills/repo-governed-coding/` 的使用策略；默认保持显式调用，不应替代 `AGENTS.md` 和治理检查
- `.agents/skills/harness-maintenance/` 的使用策略；默认只在修改 runtime、hook、reducer、session compression、verification command reference、GitHub guardrails 或 code-shape checks 时按需调用
- `.agents/skills/requirements-traceability-maintenance/` 的使用策略；默认只在 PRD 导入、`REQDOC / REQ / WS`、traceability matrix 或技术假设状态变化时按需调用
- `.agents/skills/progressive-feature-development/` 的使用策略；默认只在非平凡功能、跨模块、API / storage / architecture 或测试策略变化时按需调用
- `.agents/skills/prd-to-project-skills/` 的使用策略；默认只在 PRD / requirements / workstream 中出现稳定可复用模式时按需调用
- `.agents/skills/team-pr-conflict-control/` 的使用策略；默认只在多人 / 多 AI 并行开发、PR touch-set overlap、PR template、CODEOWNERS 或 merge queue readiness 时按需调用
- `scripts/check_repo_skills.py` 的使用策略；默认只做 repo-local / globally installed 事实报告，不替代 skill 安装
- `scripts/check_requirements_shape.py` 的使用策略；默认在 PRD / REQ / WS 导入后手动运行，第一阶段不做 blocking hook
- `scripts/check_skill_usage_samples.py` 的使用策略；默认用于 Candidate skill with/without eval evidence，不应伪造样本或强制升级
- `scripts/check_change_triggered_followups.py` 的使用策略；默认 warning-only，用 changed files 提示可能遗漏的专项检查和 skill/reference
- `scripts/check_github_guardrails.py` 的使用策略；默认手动运行，远端未登录或缺权限时输出 `UNKNOWN` 而不是伪装成 OK
- `scripts/check_pr_touch_conflicts.py` 的使用策略；默认在 PR 上阻断 high-risk changed-file overlap，普通 overlap 先提示协调
- `docs/ai/templates/project-skill-lifecycle.md` 的使用策略；默认只在 architecture/style/dependency skill 任务中按需读取，不应进入默认短链路
- `docs/ai/index.md` 中的阅读顺序、活跃文档入口和阶段状态
- `docs/ai/working-context.md` 中的当前主目标、活跃队列和风险
- `docs/ai/plan.md` 中的项目目标、范围和阶段规划
- `docs/requirements/index.md` 中的当前活跃内容
- `docs/requirements/traceability-matrix.md` 中的首个真实 `REQDOC / REQ / WS`
- 第一个垂直切片的应用目录与 smoke 脚本

## 推荐迁移步骤

1. 复制机制层文件，不复制当前项目真相和 runtime 原料。
2. 在新仓库运行 `python3 scripts/bootstrap_harness.py --project-name "你的项目名"`；如果你希望 starter 自带的 `plan / working-context / requirements index / traceability-matrix` 立刻替换成新项目名，再追加一次 `--force`。
3. bootstrap 会优先取当前 `VIRTUAL_ENV` / `CONDA_PREFIX`、显式 `CODEX_HARNESS_PYTHON` 或最佳 Python 3.11+ 候选来创建 repo-local `.codex/.venv`；如需指定解释器，用 `--python /path/to/python3`。
4. Python 依赖安装默认是 best-effort；离线或受限网络下即使 `pip install` 失败，bootstrap 也应继续完成 venv 初始化。若你需要强制安装成功，可追加 `--strict-python-deps`。
5. 执行 `git config core.hooksPath .githooks`，让 Git hook 与 Codex hook 统一通过 repo-local Python 入口运行；bootstrap 会同时按当前宿主环境刷新 `.codex/hooks.json`。
6. 按新项目实际情况改写 `AGENTS.md` 与 `.codex/harness.toml`；`AGENTS.md` 不会由 bootstrap 自动项目化。
7. 让 AI 先初始化或确认 `docs/ai/`、`docs/requirements/` 控制面，而不是直接写业务代码。
8. 导入首个真实 `REQDOC / REQ / WS`。
9. 落第一个垂直切片实现，并在完成后补 `handoff/status`。
10. 再让 runtime hooks、reducer 和 governance check 进入常规工作流。

## 新项目的首条 Prompt 建议

```text
先不要写业务功能。基于当前仓库实际结构初始化 Codex-first harness：
1. 检查工具链和目录现状
2. 确认或生成最小 docs/ai 和 docs/requirements 控制面
3. 初始化 index、working-context、plan、traceability-matrix
4. 根据我的目标，落首个 REQDOC / REQ / WS
5. 然后再开始第一个垂直切片实现
```

## 已知边界

- bootstrap 只解决最小控制面初始化，不会自动替你决定首个真实 workstream。
- repo-local `.codex/.venv` 是 harness Python 的默认落点，但不会自动提交，也不应复制到别的仓库。
- `.codex/requirements.txt` 里的依赖目前按可选兼容层处理；离线时 bootstrap 完成不代表这些包一定已经安装。
- `runtime` metadata 的自动携带仍依赖调用环境；新项目若要更强一致性，仍需后续补校验。
- `check_ai_docs.py` 已改成“最小默认 + 可配置”，但 repo-specific 附加文档是否设为必需，仍需项目自己决定。
- repo-local 行为 skill 只能约束执行方法；跨会话共享结论仍必须提升到 `handoff/status/ADR` 或 requirements 文档。
- requirements traceability、progressive feature、PRD-to-skill 与 team PR conflict control skills 只能约束维护、发现、分类和协作控制方法；PRD 当前状态、验收进度、最新验证证据和远端 GitHub 配置不得藏进 skill。
- starter 可以携带 PR template、CODEOWNERS、workflow 和 touch-conflict checker，但不能自动证明新仓库远端已启用 branch protection、rulesets 或 merge queue；这些必须在 GitHub 侧确认。
- project skill 生命周期模板只提供创建、升级、偏离和废弃 skill 的治理路径；不会自动决定新项目的架构、样式或依赖栈。
- archive candidate monitor 只适合作为压缩前提醒，不应替代主 Agent 对 `handoff -> status -> archive` 的语义判断。
- context budget audit 只适合作为默认上下文体检，不应替代 Task Discovery 或主 Agent 的语义取舍；starter/new-project 默认目标保持 6500，成熟项目若有证据可按需调高本地预算。
