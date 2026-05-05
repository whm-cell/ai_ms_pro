# PR Branch Guardrails

更新时间：2026-05-05
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `.github/pull_request_template.md`，要求 PR 显式填写 `REQ/WS`、touch-set、parallel PR conflict check、verification 和 governance impact。
- 新增 `scripts/check_pr_touch_conflicts.py`，用于比较当前 PR changed files 与同 base open PR，发现 high-risk same-file overlap 时可阻断。
- `governance-and-smoke.yml` 在 PR 上运行 PR touch conflict check，并新增 `merge_group` 触发。
- `dependency-review.yml` 新增 `merge_group` 触发；dependency review job 仅在 `pull_request` 事件运行。
- `scripts/check_github_guardrails.py` 现在检查 PR template、PR touch conflict checker、workflow `merge_group` 触发和扩展后的 CODEOWNERS 覆盖。
- 同步 `new_pro_standard` 机制层：portable `.github` workflows、CODEOWNERS、PR template、Dependabot、`scripts/check_pr_touch_conflicts.py`、单测和 starter 文档说明。

## 修复问题

- 修复多人 / 多 AI PR 冲突控制只有 skill 方法层、缺少仓库内 PR 模板和 changed-files overlap 检查的问题。
- 修复 workflow 缺少 `merge_group` 触发，导致不能宣称已适配 merge queue required-check 运行面的缺口。

## 行为变化

- PR 上的 high-risk file overlap 会通过 `scripts/check_pr_touch_conflicts.py --strict-high-risk --strict-unknown` 阻断。
- 普通文件 overlap 仍只提示协调，不默认阻断。
- 远端 branch protection / ruleset 仍不能由 repo 文件保证；2026-05-05 使用 `gh api` 尝试配置 `main` branch protection 返回 HTTP 403，需要 GitHub Pro 或 public repo。

## 破坏性变更

- 无。

## 验证范围

- `python3 -m unittest discover -s tests -p "test_pr_touch_conflicts.py"`
- `python3 -m unittest discover -s tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_pr_touch_conflicts.py --current-pr 1 --strict-high-risk --strict-unknown`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `python3 scripts/check_ai_governance.py` from `new_pro_standard`
- `python3 scripts/check_context_budget.py` from `new_pro_standard`
- `python3 scripts/check_github_guardrails.py` from `new_pro_standard`
- `python3 -m unittest discover -s tests` from `new_pro_standard`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [ADR-012 GitHub Harness Gatekeeping](../adr/ADR-012-github-harness-gatekeeping.md)
