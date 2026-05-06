# 2026-05-04 Progressive Feature And PRD Skills

更新时间：2026-05-04
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added `$progressive-feature-development` as an optional repo-local technical-plan gate for non-trivial feature work.
- Added `$prd-to-project-skills` as an optional classifier for stable PRD / requirement / workstream patterns that may become project skills.
- Synced both skills into `new_pro_standard` as portable mechanism-layer assets.
- Added ADR-015 to record the skillized workflow boundary.

## 修复问题

- Avoided turning the full feature-development workflow into always-on `AGENTS.md` process.
- Avoided copying ECC PRP commands / hooks into a second control plane.
- Clarified that PRD current state and acceptance truth stay in requirements / governance docs, not skills.

## 行为变化

- Simple tasks should not load either new skill by default.
- Non-trivial feature, cross-module, API / storage / architecture, testing strategy, or explicit plan-first work may load `$progressive-feature-development`.
- PRD / requirement / workstream material may load `$prd-to-project-skills` only when stable project guidance could reduce future context.

## 破坏性变更

- 无

## 验证范围

- Skill structure validation for root and starter skill directories
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`

## 关联文档

- [ADR-015 Progressive Feature And PRD Skills](../adr/ADR-015-progressive-feature-and-prd-skills.md)
- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
