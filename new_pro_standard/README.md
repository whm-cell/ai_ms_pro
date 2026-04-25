# new_pro_standard

This directory is a portable Codex-first harness starter for a new repository.

It intentionally includes:

- governance rules
- Codex hooks
- Git hooks
- governance check scripts
- runtime templates
- document templates
- a bootstrapped minimal `docs/ai` and `docs/requirements` control plane
- portable migration and rewrite guides

It intentionally does not include:

- old project's `working-context`
- old project's `status` or `handoff`
- old project's real `REQDOC / REQ / WS`
- old project's runtime session or observation artifacts
- old project's smoke/demo apps

## Starter Shape

The default shared recovery surface is intentionally slim:

`docs/ai/index.md -> docs/ai/working-context.md -> latest stage status -> <=5 active handoff`

This starter keeps that shape by:

- treating `index.md` as a stable router instead of a full stage report
- treating `working-context.md` as incremental truth instead of a second directory view
- warning when active handoffs or bound handoffs grow past the default budget
- expecting absorbed handoffs to move into `docs/ai/handoffs/archive/`
- keeping exact active handoff bindings in `docs/ai/working-context.md` sync metadata instead of duplicating them across multiple router docs

## First Use

1. Copy the contents of this directory to the root of the new repository.
2. Run `python3 scripts/bootstrap_harness.py --project-name "Your Project Name"` in the new repository root.
3. The bootstrap step will use the current environment Python, unless overridden, to create `.codex/.venv`.
4. Dependency installation is best-effort by default, so offline bootstrap can still finish. If you need a strict dependency install, rerun with `--strict-python-deps`.
5. Enable Git hooks with `git config core.hooksPath .githooks`.
6. `scripts/bootstrap_harness.py` will refresh `.codex/hooks.json` for the current host shell; then rewrite `AGENTS.md`, `docs/ai/working-context.md`, `docs/ai/plan.md`, and `.codex/harness.toml` for the new project.
7. Import the first real `REQDOC / REQ / WS`.
8. Start the first vertical slice implementation.

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
- shared truth stays in `docs/ai/*` and `docs/requirements/*`
- local runtime memory goes to `.codex/runtime/*`
- `Stop` runs the governance check automatically when Codex hooks are enabled
- the default shared recovery surface stays small unless the repo explicitly chooses otherwise

## Python Runtime

- Codex hooks and Git hooks resolve Python through the repo-local hook runners in `.codex/hooks/`.
- The starter includes both `.sh` and `.ps1` entrypoints so Windows and POSIX workspaces can share the same harness logic.
- `scripts/bootstrap_harness.py` refreshes `.codex/hooks.json` for the current host shell during setup, so normal new-project bootstrap no longer needs manual hook entrypoint edits.
- Resolution order is repo-local `.codex/.venv`, then current `VIRTUAL_ENV`, then `CONDA_PREFIX`, then `CODEX_HARNESS_PYTHON`, then `python3`, then `python`, then `py -3` when available.
- Python candidates are probed before use, and bootstrap can rebuild a broken repo-local `.codex/.venv` in place.
- Do not commit `.codex/.venv`.
- `.codex/requirements.txt` currently carries optional compatibility dependencies, so a finished bootstrap does not guarantee every optional pip package is already installed.

## Included Checks

- `scripts/check_ai_docs.py`
- `scripts/check_ai_doc_quality.py`
- `scripts/check_ai_governance.py`
- `scripts/check_code_shape.py`
- `scripts/reduce_runtime_observations.py`

The shipped Git hook runs:

- `scripts/check_ai_governance.py`
- `scripts/check_code_shape.py --staged`

## Included Guides

- `docs/ai/harness-portability-guide.md`
- `docs/ai/new-project-agents-rewrite-guide.md`
- `docs/ai/traditional-project-harness-kickoff.md`
- `docs/requirements/v2-requirements-splitting-template.md`

## Included Bootstrap

- `scripts/bootstrap_harness.py` initializes the minimal shared control plane.
- It is safe to rerun after the initial copy.
- The generated starter docs follow the slim governance surface budget by default.
- The bootstrap flow supports Windows and POSIX venv layouts, refreshes hook config for the current host shell, and keeps optional dependency installation best-effort unless `--strict-python-deps` is requested.
