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

It intentionally does not include:

- old project's `working-context`
- old project's `status` or `handoff`
- old project's real `REQDOC / REQ / WS`
- old project's runtime session or observation artifacts
- old project's smoke/demo apps

## First Use

1. Copy the contents of this directory to the root of the new repository.
2. Run `python3 scripts/bootstrap_harness.py --project-name "Your Project Name"` in the new repository root.
3. The bootstrap step will use the current environment Python, unless overridden, to create `.codex/.venv`.
4. Dependency installation is best-effort by default, so offline bootstrap can still finish. If you need a strict dependency install, rerun with `--strict-python-deps`.
5. Enable Git hooks with `git config core.hooksPath .githooks`.
6. Rewrite `AGENTS.md`, `docs/ai/working-context.md`, `docs/ai/plan.md`, and `.codex/harness.toml` for the new project.
7. Import the first real `REQDOC / REQ / WS`.
8. Start the first vertical slice implementation.

## Python Runtime

- Codex hooks and Git hooks resolve Python through `.codex/hooks/run_with_repo_python.sh`.
- Resolution order is repo-local `.codex/.venv`, then current `VIRTUAL_ENV`, then `CONDA_PREFIX`, then `CODEX_HARNESS_PYTHON`, then `python3`.
- Do not commit `.codex/.venv`.
- `.codex/requirements.txt` currently carries optional compatibility dependencies, so a finished bootstrap does not guarantee every optional pip package is already installed.

## Included Checks

- `scripts/check_ai_docs.py`
- `scripts/check_ai_doc_quality.py`
- `scripts/check_ai_governance.py`
- `scripts/reduce_runtime_observations.py`

## Included Bootstrap

- `scripts/bootstrap_harness.py` initializes the minimal shared control plane.
- It is safe to rerun after the initial copy.
