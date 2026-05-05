# new_pro_standard

This directory is a portable Codex-first harness starter for a new repository.

It intentionally includes:

- governance rules
- Codex hooks
- Git hooks
- governance check scripts
- GitHub PR template, CODEOWNERS, dependency review, and starter workflows
- runtime templates
- project skill lifecycle template
- candidate skill eval protocol
- optional repo-local behavioral skill
- optional harness maintenance skill
- optional requirements traceability maintenance skill
- optional progressive feature development skill
- optional PRD-to-project-skills classifier
- optional team PR conflict control skill
- document templates
- a bootstrapped minimal `docs/ai` and `docs/requirements` control plane
- portable migration and rewrite guides

It intentionally does not include:

- old project's `working-context`
- old project's `status` or `handoff`
- old project's real `REQDOC / REQ / WS`
- old project's runtime session or observation artifacts
- old project's smoke/demo apps
- old project's remote branch protection or ruleset state

## Optional Behavioral Guardrails

This starter includes `.agents/skills/repo-governed-coding/` as an optional task-level skill adapted from the Karpathy-style coding guidelines.

Use it when a non-trivial implementation, review, or refactor should explicitly record:

- assumptions before coding
- scope boundary for the diff
- success criteria
- verification plan

It is not an always-on governance replacement. `AGENTS.md`, `docs/ai/*`, `docs/requirements/*`, hooks, and check scripts remain the default harness control plane.

## Project Skill Lifecycle

The starter includes `docs/ai/templates/project-skill-lifecycle.md` for architecture, style, and dependency skills.

Use it only when a project-specific skill is being created or changed. It keeps volatile 0-1 project constraints out of the default context while still requiring durable decisions to be promoted to `status`, ADR, requirements, or checks.

## Harness Maintenance Skill

The starter includes `.agents/skills/harness-maintenance/` for changes to bootstrap, hook runners, runtime reducers, session compression, verification command selection, GitHub guardrails, and code-shape checks.

It keeps detailed harness mechanics out of `AGENTS.md`; use it only when modifying the harness itself.

## Requirements Traceability Skill

The starter includes `.agents/skills/requirements-traceability-maintenance/` for PRD import, `REQDOC / REQ / WS` updates, traceability-matrix maintenance, and technical assumption classification.

It keeps requirement-maintenance mechanics out of `AGENTS.md`; requirement truth and acceptance status still belong in `docs/requirements/*` and `docs/ai/*`.

## Progressive Feature And PRD Skills

The starter includes two optional repo-local workflow skills:

- `.agents/skills/progressive-feature-development/` for non-trivial feature work that needs progressive discovery and a technical-plan gate before implementation
- `.agents/skills/prd-to-project-skills/` for classifying stable PRD / requirement / workstream patterns into candidate project skills

They are mechanism-layer assets, not starter truth. They should not run for simple tasks, and they must not turn current progress, latest validation evidence, or acceptance status into hidden skill state.

## Team PR Conflict Control Skill

The starter includes `.agents/skills/team-pr-conflict-control/` for multi-person or multi-AI development where PR touch-set overlap, high-risk files, PR templates, CODEOWNERS, or merge queue readiness need explicit review.

It is a mechanism-layer asset. The starter also includes `.github/pull_request_template.md`, CODEOWNERS, portable GitHub workflows, and `scripts/check_pr_touch_conflicts.py`; the new repository must still verify remote branch protection, rulesets, and merge queue settings on GitHub before claiming direct pushes to `main` are blocked.

## Starter Shape

The default shared recovery surface is intentionally slim:

`docs/ai/index.md -> docs/ai/working-context.md -> latest stage status -> configured active handoff budget`

This starter keeps that shape by:

- treating `index.md` as a stable router instead of a full stage report
- treating `working-context.md` as incremental truth instead of a second directory view
- warning when active handoffs or bound handoffs reach the configured default budget
- expecting absorbed handoffs to move into `docs/ai/handoffs/archive/`
- keeping exact active handoff bindings in `docs/ai/working-context.md` sync metadata instead of duplicating them across multiple router docs

## First Use

1. Copy the contents of this directory to the root of the new repository.
2. Run `python3 scripts/bootstrap_harness.py --project-name "Your Project Name"` in the new repository root.
3. The bootstrap step will create `.codex/.venv` from the current environment, an explicit override, or the best runnable Python 3.11+ candidate it can find.
4. Dependency installation is best-effort by default, so offline bootstrap can still finish. If you need a strict dependency install, rerun with `--strict-python-deps`.
5. Enable Git hooks with `git config core.hooksPath .githooks`.
6. `scripts/bootstrap_harness.py` will refresh `.codex/hooks.json` for the current host shell.
7. If you want the copied starter placeholders to be replaced with the new project name immediately, rerun bootstrap with `--force`.
8. Rewrite `AGENTS.md` manually for the new project; bootstrap does not projectize it for you.
9. Import the first real `REQDOC / REQ / WS`.
10. Start the first vertical slice implementation.

## Wake The Harness

After copying the starter, the mechanism is considered "awake" only when these conditions are true:

1. The repository root contains `AGENTS.md`, `.codex/`, `docs/ai/`, `docs/requirements/`, and `scripts/`.
2. You have run `python3 scripts/bootstrap_harness.py --project-name "Your Project Name"`.
3. You have enabled Git hooks with `git config core.hooksPath .githooks`.
4. Your Codex/AI session is opened from the repository root so it can see `AGENTS.md` and `.codex/config.toml`.
5. Your first prompt tells the agent to initialize or confirm the control plane before writing business code.

Recommended first prompt:

```text
先不要直接写业务功能。
先基于当前仓库实际结构唤醒并检查这套 harness：
1. 确认 AGENTS.md、codex hooks、docs/ai、docs/requirements 是否齐全
2. 检查或运行 bootstrap，确保最小控制面有效
3. 阅读 index、working-context、requirements index、plan
4. 根据我的目标建立首个 REQDOC / REQ / WS
5. 然后再开始第一个垂直切片实现
```

If the harness is awake, the expected behavior is:

- the agent reads `AGENTS.md` and `docs/ai/index.md` first
- the agent classifies substantial tasks and selects the matching reading profile before expanding context
- users usually do not need to label task type manually; optional override phrases are `按简单任务处理`, `按复杂任务处理`, `这是 0-1 阶段任务`, `不要读 archive`, and `需要深挖历史`
- shared truth stays in `docs/ai/*` and `docs/requirements/*`
- local runtime memory goes to `.codex/runtime/*`
- optional behavior guidance can be invoked with `$repo-governed-coding` for non-trivial coding tasks
- optional requirements traceability guidance can be invoked with `$requirements-traceability-maintenance` for PRD import, `REQDOC / REQ / WS`, matrix, or technical assumption changes
- optional progressive feature guidance can be invoked with `$progressive-feature-development` for non-trivial plan-first work
- optional PRD-to-skill guidance can be invoked with `$prd-to-project-skills` when stable requirement patterns may become project skills
- optional team PR conflict control can be invoked with `$team-pr-conflict-control` when multiple people or AIs may touch overlapping PR surfaces
- PRs should use `.github/pull_request_template.md`, and PR CI can run `scripts/check_pr_touch_conflicts.py` to block high-risk changed-file overlap
- project architecture/style/dependency skill guidance stays in the lifecycle template until a real project chooses to create a concrete skill
- `Stop` runs the governance check automatically when Codex hooks are enabled
- the default shared recovery surface stays small unless the repo explicitly chooses otherwise

## Python Runtime

- Codex hooks and Git hooks resolve Python through the repo-local hook runners in `.codex/hooks/`.
- The starter includes both `.sh` and `.ps1` entrypoints so Windows and POSIX workspaces can share the same harness logic.
- `scripts/bootstrap_harness.py` refreshes `.codex/hooks.json` for the current host shell during setup, so normal new-project bootstrap no longer needs manual hook entrypoint edits.
- Resolution order is repo-local `.codex/.venv`, then current `VIRTUAL_ENV`, then `CONDA_PREFIX`, then `CODEX_HARNESS_PYTHON`, then the best PATH Python candidate, then launcher/system fallback.
- On POSIX/macOS, PATH fallback enumerates all visible `python3` / `python` candidates and prefers Python 3.11+ so `/usr/bin/python3` does not mask pyenv or another managed Python.
- On Windows, the PowerShell runner compares `python3`, `python`, `py -3`, and common per-user Python installs with the same Python 3.11+ preference.
- Python candidates are probed before use, and bootstrap can rebuild a broken repo-local `.codex/.venv` in place.
- Do not commit `.codex/.venv`.
- `.codex/requirements.txt` currently carries optional compatibility dependencies, so a finished bootstrap does not guarantee every optional pip package is already installed.

## Included Checks

- `scripts/check_ai_docs.py`
- `scripts/check_ai_doc_quality.py`
- `scripts/check_ai_governance.py`
- `scripts/check_archive_candidates.py`
- `scripts/check_context_budget.py`
- `scripts/check_code_shape.py`
- `scripts/check_change_triggered_followups.py`
- `scripts/check_repo_skills.py`
- `scripts/check_requirements_shape.py`
- `scripts/check_skill_usage_samples.py`
- `scripts/check_github_guardrails.py`
- `scripts/check_pr_touch_conflicts.py`
- `scripts/reduce_runtime_observations.py`

The shipped Git hook runs:

- `scripts/check_ai_governance.py`
- `scripts/check_code_shape.py --staged`

Run `scripts/check_archive_candidates.py` manually through the repo-local Python runner when active handoffs reach the `.codex/harness.toml` surface budget or before a stage compression pass. It only reports archive candidates; it does not move files.

Run `scripts/check_context_budget.py` manually when the default context feels heavy. It reports always-on surface size, skill description/body size, duplicate instructions, ADR count, and MCP server count without blocking the task.

Run `scripts/check_change_triggered_followups.py` when you want changed files mapped to likely missed follow-up checks and skill/reference surfaces. It also supports `--markdown` for PR / CI summaries. It is advisory and does not prove that suggested commands already ran.

Run `scripts/check_requirements_shape.py` after PRD / `REQDOC / REQ / WS` imports or traceability-matrix changes. The evidence checks remain warning-oriented until a new project explicitly promotes them to blocking policy.

Run `scripts/check_github_guardrails.py` after configuring the GitHub repository. The starter can ship workflows, CODEOWNERS, PR template, and PR touch-conflict checks, but remote branch protection / rulesets are external GitHub settings and may require a paid plan or a public repository.

## Included Guides

- `docs/ai/harness-portability-guide.md`
- `docs/ai/templates/project-skill-lifecycle.md`
- `docs/ai/new-project-agents-rewrite-guide.md`
- `docs/ai/traditional-project-harness-kickoff.md`
- `docs/requirements/v2-requirements-splitting-template.md`

## Included Bootstrap

- `scripts/bootstrap_harness.py` initializes the minimal shared control plane.
- It is safe to rerun after the initial copy.
- The generated starter docs follow the slim governance surface budget from `.codex/harness.toml` by default.
- The bootstrap flow supports Windows and POSIX venv layouts, refreshes hook config for the current host shell, and keeps optional dependency installation best-effort unless `--strict-python-deps` is requested.
