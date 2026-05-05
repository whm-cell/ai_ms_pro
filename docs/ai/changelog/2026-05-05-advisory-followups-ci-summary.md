# 2026-05-05 Advisory Followups CI Summary

更新时间：2026-05-05
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_change_triggered_followups.py` 新增 `--markdown` 输出，用于 GitHub Actions Summary。
- root 与 `new_pro_standard` 的 `governance-and-smoke` workflow 在 PR / main push 上写入 changed-file follow-up advisory summary。
- `merge_group` 事件保留阻断式治理、Windows 和 smoke gates，并写入说明，避免把 merge queue 场景误描述成 changed-file PR summary。

## 修复问题

- 降低 advisory checker 只存在于本地手动命令、PR 审查时不可见的风险。
- 避免为了提高可见性把 follow-up 规则重新塞回 always-on `AGENTS.md`。

## 行为变化

- advisory summary 只提高 PR / CI 可见性，不升级为 required check。
- checker 仍只根据 changed files 提示可能需要补跑的检查和 reference，不证明这些命令已经执行。
- workflow checkout 使用 `fetch-depth: 0`，以便 PR / push 场景能用 base diff 生成 summary。

## 破坏性变更

- 无。

## 验证范围

- `python3 -m unittest discover -s tests -p "test_change_triggered_followups.py"`
- `python3 -m unittest discover -s tests -p "test_change_triggered_followups.py"` from `new_pro_standard`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files .github/workflows/governance-and-smoke.yml scripts/check_change_triggered_followups.py --markdown`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `git diff --check`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Change Triggered Followups](./2026-05-05-change-triggered-followups.md)
- [Harness Maintenance Verification Commands](../../../.agents/skills/harness-maintenance/references/verification-commands.md)
