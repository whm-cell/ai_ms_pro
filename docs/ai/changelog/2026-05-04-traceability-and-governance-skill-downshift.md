# 2026-05-04 Traceability And Governance Skill Downshift

更新时间：2026-05-04
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `.agents/skills/requirements-traceability-maintenance/`，并同步到 `new_pro_standard`，用于 PRD 导入、`REQDOC / REQ / WS`、traceability matrix 和技术假设状态维护。
- 扩展 `$harness-maintenance` references，新增 session promotion / governance compression 与 verification command selection。

## 修复问题

- 修复 starter 中 verification reference 可能指向不存在 evidence scripts 的问题，同步通用 warning-only scripts 到 `new_pro_standard/scripts/`。
- 减少 `AGENTS.md`、`$repo-governed-coding` 与 harness skill 之间的重复说明。

## 行为变化

- `AGENTS.md` 只保留 runtime 不是真相、需求映射不能漂移、未知映射写 `未绑定`、材料性变更必须验证等硬边界。
- Requirements truth 仍在 `docs/requirements/*`；skills 只承载维护方法，不保存当前验收状态或架构事实。
- Verification truth 仍由 scripts/checks 输出；skill reference 只做命令选择和 warning 解释。

## 破坏性变更

- 无。

## 验证范围

- 已跑 root/starter 10 个 skill 结构校验。
- 已跑 root/starter `check_repo_skills.py`，5 个 repo-local skills 均为 `codex_discoverable=true`、`implicit=false`、`repo-local only`。
- 已跑 root/starter requirements shape、Candidate skill sample check、context budget。
- 已跑 root/starter `check_ai_governance.py` 和 `check_code_shape.py --all`；root 另跑 `check_code_shape.py --staged` 与 `git diff --check`。
- `check_skill_usage_samples.py` 仍提示两个 Candidate workflow skills 为 `0/2` accepted eval samples；这是当前事实，不影响本次下沉。
- `check_code_shape.py --all` 仍报告既有大文件 warning；本次未扩大为 blocking。

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [OpenAI Codex AGENTS.md docs](https://developers.openai.com/codex/guides/agents-md)
- [OpenAI Codex skills docs](https://developers.openai.com/codex/skills)
- [Jama RTM guide](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/traceability-matrix/)
