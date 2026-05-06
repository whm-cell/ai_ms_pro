# SAMPLE-001 Team PR Conflict Control Validation

更新时间：2026-05-04
状态：已完成验证；不计入真实多人 PR accepted 样本

## 验证目标

验证 `.agents/skills/team-pr-conflict-control/` 是否能在不增加默认流程税的前提下，按需完成多人 / 多 AI PR 冲突控制判断。

本次验证只证明 skill 结构、触发边界、当前仓库适配和场景规则可用；它不证明真实团队样本已经足够，也不证明 PR template、changed-files overlap check 或 merge queue enforcement 已启用。

## 验证方案

1. Static skill validation
- root 与 starter 的 `SKILL.md` frontmatter、目录结构、`agents/openai.yaml` schema 必须通过 `quick_validate.py`。

2. Repo discoverability validation
- root 与 starter 的 skill 必须位于 `.agents/skills/`。
- `scripts/check_repo_skills.py` 必须显示 `codex_discoverable=true`、`implicit=false`、`repo-local only`。

3. Current repo scenario validation
- 使用当前分支、本地 touch-set、open PR 列表、CODEOWNERS、workflow trigger 和 PR template 状态验证 skill 输出。
- GitHub 查询失败时必须标记 `UNKNOWN`；本次 GitHub 查询可用。

4. Offline rule-matrix validation
- 构造简单任务、普通文件 overlap、高风险文件 overlap、GitHub 状态不可用、merge queue 缺 `merge_group`、PR template 缺字段六类场景。
- 每类场景必须产生 skill 要求的固定输出字段，并给出 `continue / coordinate / block until resolved / UNKNOWN` 等判断。

5. Governance and budget validation
- 运行 governance、context budget、code shape 和 whitespace 检查，确认新增 skill 不破坏默认恢复面或治理质量。

## 当前仓库实测

- Current branch: `codex/harness-stage-00-hardening`
- Open PRs: only PR #1, `Harden Stage-00 harness governance flow`, base `main`, head `codex/harness-stage-00-hardening`; PR file count observed: 100
- Other open PR overlap: none observed
- Local touch-set includes governance and skill surfaces:
  - `AGENTS.md`
  - `.agents/skills/team-pr-conflict-control/**`
  - `docs/ai/adr/ADR-012-github-harness-gatekeeping.md`
  - `docs/ai/status/stage-00-runtime-harness-foundation.md`
  - `docs/ai/harness-open-items.md`
  - `docs/ai/index.md`
  - `docs/ai/working-context.md`
  - `new_pro_standard/**`
- High-risk files:
  - `AGENTS.md`
  - `.agents/skills/team-pr-conflict-control/**`
  - `docs/ai/adr/ADR-012-github-harness-gatekeeping.md`
  - `docs/ai/status/stage-00-runtime-harness-foundation.md`
- CODEOWNERS readiness: present; broad `* @whm-cell` covers the repo, with explicit coverage for `AGENTS.md`, `.github/workflows/**`, `scripts/check_*`, `docs/ai/**`, and `docs/requirements/**`. `.agents/**` is covered by broad ownership but not separately listed.
- PR template coverage: missing; `.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE/*` is not present.
- Merge queue readiness: not proven; workflows currently include `pull_request`, but no `merge_group` trigger.

Skill output for current repo scenario:

```text
Collaboration Mode: high-risk team
Current Touch Set: AGENTS.md, .agents/skills/team-pr-conflict-control/**, docs/ai/** governance surfaces, new_pro_standard/** starter surfaces
Open PR Overlap Result: no other open PR observed; current branch is PR #1
High-Risk Files: AGENTS.md, .agents/skills/**, docs/ai/adr/**, docs/ai/status/**
Required Coordination Action: coordinate owner review before merge; no block from open-PR overlap, but do not claim merge-queue readiness
PR Template Coverage: missing
CODEOWNERS / Merge Queue Readiness: CODEOWNERS present; merge_group missing
Governance Writeback Decision: keep this validation in skill-evals and changelog; keep OPEN-11 until real team PR samples exist
```

## Offline Rule Matrix

| Scenario | Input | Expected Decision | Result |
| --- | --- | --- | --- |
| Simple solo task | one local typo fix, no PR overlap, no high-risk file | skip skill or `continue` without full gate | PASS |
| Ordinary overlap | current PR and another open PR both touch `apps/site/src/pages/home.tsx` | `coordinate` and document merge order | PASS |
| High-risk overlap | current PR and another open PR both touch `AGENTS.md` | `block until resolved` | PASS |
| GitHub unavailable | open PR list cannot be fetched | mark overlap `UNKNOWN`; do not claim safe | PASS |
| Merge queue missing trigger | merge queue desired, workflows lack `merge_group` | merge queue readiness not proven | PASS |
| PR template missing fields | PR body lacks `REQ/WS`, touch-set, overlap, verification, governance impact | mark template gap; suggest template/check before enforcement | PASS |

## Verification Commands

```bash
python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/team-pr-conflict-control
python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py new_pro_standard/.agents/skills/team-pr-conflict-control
.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py
python3 scripts/check_repo_skills.py # from new_pro_standard
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
python3 scripts/check_ai_governance.py # from new_pro_standard
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
python3 scripts/check_context_budget.py # from new_pro_standard
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all
git diff --check
gh pr list --state open --json number,title,url,headRefName,baseRefName
gh pr view 1 --json files,baseRefName,headRefName,url,title,number
```

## Verification Results

- Root `quick_validate.py`: PASS
- Starter `quick_validate.py`: PASS
- Root `scripts/check_repo_skills.py`: PASS; `team-pr-conflict-control` is `repo-local only`, `codex_discoverable=true`, `implicit=false`
- Starter `scripts/check_repo_skills.py`: PASS; `team-pr-conflict-control` is `repo-local only`, `codex_discoverable=true`, `implicit=false`
- Root `scripts/check_ai_governance.py`: PASS
- Starter `scripts/check_ai_governance.py`: PASS
- Root `scripts/check_context_budget.py`: PASS; default surface `7133 / 8500`, warnings none
- Starter `scripts/check_context_budget.py`: PASS; default surface `5018 / 6500`, warnings none
- Root `scripts/check_code_shape.py --all`: PASS with existing legacy size warnings only
- `scripts/check_skill_usage_samples.py`: PASS with expected warnings for unrelated Candidate skills `prd-to-project-skills` and `progressive-feature-development` still at `0/2`
- `git diff --check`: PASS
- `gh pr list`: PASS; only PR #1 observed
- `gh pr view 1`: PASS; PR #1 has 100 files

## Acceptance

- Outcome: validation-passed
- Evidence Type: validation-task, not real-team-pr
- Requirement IDs: 未绑定
- Workstream IDs: 未绑定
- baseline_without_skill: 冲突控制只能散落在 `AGENTS.md`、口头流程或 GitHub 设置讨论中，容易遗漏 PR template、open-PR overlap、high-risk path 和 `merge_group` readiness。
- run_with_skill: 使用 skill 后能固定输出协作模式、touch-set、overlap、高风险文件、协调动作、PR hygiene、CODEOWNERS / merge queue readiness 和治理回写判断。
- delta: 默认上下文没有超标；复杂多人 PR 控制细节保持按需加载；当前发现 PR template 和 `merge_group` 仍未落地。
- acceptance: 只接受为 skill 可用性验证，不计入 OPEN-11 的真实团队 PR accepted 样本。
- verification: 本文件列出的结构、discoverability、治理、预算、code shape、whitespace 和 GitHub 查询检查。
- Doc Promotion: 留在 `docs/ai/skill-evals/` 和 changelog；真实多人 PR 样本再决定是否提升到 status、ADR、PR template 或 check。

## 后续判断

- 当前 skill 可以继续保留为 repo-local on-demand mechanism。
- 不应升级为 always-on，也不应立即阻断简单任务。
- OPEN-11 仍需真实多人 / 多 AI PR 样本；至少两次真实样本后再判断是否实现 `.github/pull_request_template.md`、`scripts/check_pr_touch_conflicts.py` 或 `merge_group` required-check 收紧。
