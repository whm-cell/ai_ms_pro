# Evidence-Based Coding Standards

更新时间：2026-06-12
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 [Evidence-Based Coding Standards](../standards/evidence-based-coding-standards.md)，把魔法值、复杂度、长函数/大类、重复代码、命名和公共抽象边界整理为 review-required 标准。
- 扩展 `$repo-governed-coding`，新增按需 checklist：`.agents/skills/repo-governed-coding/references/evidence-based-coding-checklist.md`。
- 在 [Check Registry](../check-registry.md) 中登记该标准为 review-required，并把 Ruff `PLR2004`、`C901`、`PLR0912`、`PLR0915` 和未来 JS/TS `no-magic-numbers` 作为 blocking-candidate 方向，而不是本轮启用。
- 基于 Google code review、Ruff / ESLint 规则文档和重复代码 structured review 补充 review 严重度、处置标签、magic value 例外、code-shape 语言覆盖边界和边界型抽象例外。

## 修复问题

- 避免魔法值、复杂度、重复和公共抽象判断只停留在 prompt 或 reviewer 记忆中。
- 避免把“消除重复”或“抽公共类”机械升级成 blocking 规则；重复和抽象仍按实证边界做 review 判断。

## 行为变化

- 非平凡实现、review 或 refactor 触及魔法值、复杂度、重复、命名或公共抽象时，应按 `$repo-governed-coding` 读取 evidence-based checklist。
- 现有 blocking 面不变：Ruff 仍只覆盖 `E9/F`，`git diff --check` 和 code-shape 仍按原等级运行。
- 重复代码和公共抽象只进入 review checklist，不做机械 blocker。
- Review 结论应区分 High / Medium / Low，并用 `checked`、`fixed`、`deferred with rationale` 或 `no material issue` 做可审计 closeout。

## 破坏性变更

- 无。本轮不改 `pyproject.toml`、ESLint 配置或 CI workflow 来启用新 lint。

## 验证范围

- `.codex/hooks/run_with_repo_python.ps1 scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.ps1 scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.ps1 scripts/check_repo_skills.py`
- `.codex/hooks/run_with_repo_python.ps1 scripts/check_skill_catalog.py`
- `.codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --staged`
- `.codex\.venv\Scripts\python.exe -m ruff check .codex/hooks scripts tests`
- `git diff --check`

## 关联文档

- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
