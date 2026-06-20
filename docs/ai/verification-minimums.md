# Verification Minimums

更新时间：2026-06-20
状态：active routing aid

## 作用

用本文件选择“足够小但可辩护”的验证集合，避免每次小改都重新打开完整 `check-registry` 或 verification command matrix。

## 基本规则

- 先跑 changed-file router，再跑被改动面直接要求的 focused check。
- 产品、文档或需求后期小改默认不扩 harness；发现 harness 问题时先记录为候选或独立小切片，除非当前任务明确以 harness 为目标。具体冻结条件见 `docs/ai/harness-freeze-policy.md`。
- 共享治理 truth 变化时跑 `check_ai_governance.py`。
- 默认上下文、AGENTS、status、handoff、ADR 或 skill surface 变化时跑 `check_context_budget.py`。
- harness Python / scripts / tests 变化时跑对应单测，并按需要跑 `check_code_shape.py --all`；只有 staged closeout 才用 `--staged` 做提交前判断。
- 不用 `--all`、全量 smoke、live provider 或 remote checks 来补普通小改，除非改动面能破坏共享 contract 或用户明确要求。

## 最小集合

| 改动面 | 最小验证 |
| --- | --- |
| `AGENTS.md`、`docs/ai/index.md`、`working-context`、status、handoff、ADR links | `check_ai_governance.py`、`check_context_budget.py`、`git diff --check` |
| `docs/requirements/*`、`REQDOC`、`REQ`、`WS`、traceability | `check_requirements_shape.py`、`check_ai_governance.py`、`git diff --check` |
| `.codex/hooks/*`、hook runner、runtime reducer、runtime token/preflight/loop policy | 相关 hook/unit test、相关 sample checker、`check_warning_sample_code_alignment.py` when warning codes change、`check_ai_governance.py` |
| `scripts/check_*`、verification router、sample-gap planner/checker | 相关 unit test、changed-file follow-up command、相关 checker no-write audit、`check_code_shape.py --all` |
| `.codex/harness.toml`、config schema、prototype/design flags、mock/data/reuse settings | 对应 checker、`check_ai_governance.py`、`check_context_budget.py` |
| Product/demo validation surfaces WS-01 / WS-02 | 直接相关 smoke/static contract；不要把 unrelated harness sample-gap checks 当成功能验证 |
| `.codex/runtime/*` | 默认不作为 canonical doc 输入；只允许 README/templates 被跟踪，必要时用 `git ls-files .codex/runtime` 复核 |
| Commit 前 staged 收口 | `git diff --cached --check`、`check_code_shape.py --staged`、必要的 focused check；不跑长 smoke，除非改动面直接要求 |
| Push feature branch / draft PR | 先确认不在直接推 `main`；push `codex/...` 或业务分支后交给 PR CI 跑远端 smoke / Windows / security evidence |
| 只查看 PR checks | `scripts/report_pr_checks.py <PR>`；只报告 PR 状态、draft、branch、failed / pending checks，不修改文件、不 push |
| PR check repair while local work continues | `scripts/start_pr_repair_worktree.py <PR>` 创建或复用 sibling detached repair worktree；只在 repair worktree 里修复、commit，并用脚本打印的 `git push origin HEAD:<head-branch>` 更新 PR 分支 |
| Late-stage product / requirement refinement that exposes harness idea | 先套用 `harness-freeze-policy.md`；不满足允许条件时只处理产品/需求改动，不新增 harness docs/checks/runners |
| Mixed material change | 先跑 `check_change_triggered_followups.py --files <paths> --markdown`，再跑上表匹配项 |

## Commit / Push Flow

- 本地 commit 只要求 fast gates：staged whitespace、staged code shape、治理 truth 对应的 focused check。
- 长 smoke、Windows runner、security evidence 和 remote branch hygiene 交给 PR / GitHub Actions 异步承接；本地不要为普通提交重复跑全量 smoke。
- PR checks 失败时，优先用独立 repair worktree 修复，避免污染当前开发工作区。
- PR 合并、`main` 更新、本地开发分支同步是独立阶段；合并前确认 PR open、非 draft、head SHA 未变且 checks 通过，合并后不要自动 rebase / pull 当前开发分支。
- 当前 private GitHub Free 下 branch protection / required checks / 禁直推仍是 remote `UNKNOWN`；不要把本地流程写成远端已强制。

## 详细矩阵

完整命令和 warning interpretation 仍在 `.agents/skills/harness-maintenance/references/verification-commands.md`。本文件只做人工路由，不替代 `check-registry.md` 的 check level，也不把 advisory check 升级为 blocking。
