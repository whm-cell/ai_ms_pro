# Verification Minimums

更新时间：2026-06-18
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
| Late-stage product / requirement refinement that exposes harness idea | 先套用 `harness-freeze-policy.md`；不满足允许条件时只处理产品/需求改动，不新增 harness docs/checks/runners |
| Mixed material change | 先跑 `check_change_triggered_followups.py --files <paths> --markdown`，再跑上表匹配项 |

## 详细矩阵

完整命令和 warning interpretation 仍在 `.agents/skills/harness-maintenance/references/verification-commands.md`。本文件只做人工路由，不替代 `check-registry.md` 的 check level，也不把 advisory check 升级为 blocking。
