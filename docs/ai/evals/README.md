# Agent Harness Eval Protocol

Updated: 2026-05-10
Status: standard lightweight dataset

## Purpose

This directory defines a repo-local standard eval dataset for agent workflow behavior.

It is not a hosted eval service and does not judge model quality by itself. The dataset gives future agents, reviewers, and harness maintainers a small set of realistic tasks with expected artifacts, expected checks, grading signals, and risk tags. A checker validates the dataset shape, and a local runner can execute declared repo-local checks with a deterministic pass / warn / review-required / fail grader.

## Files

- `agent-harness-evals.jsonl`: JSONL dataset. Each line is one eval item.
- `scripts/check_agent_eval_dataset.py`: stdlib-only dataset validator.
- `scripts/run_agent_eval_dataset.py`: local eval runner and deterministic grader.
- `tests/test_agent_eval_dataset.py`: unit tests for the validator.
- `tests/test_agent_eval_runner.py`: unit tests for the runner and grader.

## Dataset Item Fields

Each JSONL item must contain:

- `id`: Stable unique ID, using `EVAL-NNN-kebab-name`.
- `title`: Short human-readable task name.
- `category`: One of `simple-code`, `requirements-traceability`, `high-impact-guardrail`, or `resume-runtime`.
- `task_prompt`: The task an agent would receive.
- `expected_artifacts`: List of repo-relative files or directories expected to be touched, created, or inspected.
- `expected_checks`: List of check objects with `command`, `expected_outcome`, and `rationale`.
- `grading_signals`: Object with `pass`, `warn`, and `fail` lists.
- `risk_tags`: List of allowed risk tags used for review and routing.
- `notes`: Short explanation of the scenario boundary.

`expected_checks.command` must look like a plausible repo command. The validator allows repo-local Python wrapper checks, unittest commands, and direct `python3 scripts/...` checks when the referenced script or test module exists.

Items may also include `trace_expectations` when an eval needs trace evidence:

- `schema_version`: Current value must be `agent-trace/v1`.
- `producer`: Trace producer or hook name that should emit the evidence.
- `required_event`: Event name expected in trace records.
- `required_kinds`: Trace `kind` values expected for the scenario.
- `required_attributes`: Safe trace attribute keys that should be present.
- `required_redaction_states`: Allowed redaction states that prove payload handling was considered.
- `evidence_artifacts`: Repo-relative evidence paths or local runtime glob patterns.
- `tool_contracts`: Tool contract names that govern the producer or validator.
- `notes`: Short boundary note.

The checker validates `trace_expectations` shape and referenced tool contract names. It does not run an eval, read local runtime traces, export traces, or prove remote interoperability.

## Local Runner And Deterministic Grader

`scripts/run_agent_eval_dataset.py` validates the dataset first, filters by optional eval id or category, then executes each selected `expected_checks.command` from the repo root unless `--dry-run` is provided.

For eval items with `trace_expectations`, execute mode also reads the declared local evidence artifacts, validates them as `agent-trace/v1`, and reports matched trace ids, evidence files, and redaction states. `--dry-run` lists the expected trace evidence without reading runtime files, so CI can keep using the runner safely.

The deterministic grader is intentionally simple:

- `expected_outcome=pass` with exit code `0` grades `pass`.
- `expected_outcome=warn` with exit code `0` grades `warn`.
- `expected_outcome=review-required` with exit code `0` grades `review-required`.
- matching trace evidence grades `pass`; missing or invalid trace evidence grades `fail` in execute mode.
- any non-zero exit code grades `fail`.
- `--dry-run` grades `not-run` and is the safe CI path for runner wiring.

This runner is local-only. It does not call model APIs, hosted eval services, OpenTelemetry, OpenAI trace backends, MCP servers, or A2A systems.

## Grading Outcomes

The dataset uses outcome signals rather than hidden scoring:

- `pass`: Evidence the agent handled the workflow correctly.
- `warn`: Review-required behavior that may still be acceptable.
- `fail`: Behavior that should reject the run or require repair.

The grader can be human, this deterministic local runner, or a future model-assisted reviewer. The deterministic runner proves declared checks can be executed and graded; it does not prove the full behavioral quality of an arbitrary future model run.

## Relation To Existing Tests

Browser and app smoke tests prove concrete slices still run. Skill eval samples compare Candidate skill usage with and without a skill. This dataset sits between them:

- Smoke tests validate product or harness behavior by executing commands.
- Skill samples validate whether a repo-local skill is worth promoting.
- Agent harness evals describe standardized workflow tasks and expected governance behavior.

The dataset should stay small, readable, and dependency-free. New evals should prefer checks that are already documented in `docs/ai/tool-contracts/contracts.json`.

`EVAL-005-stop-trace-evidence-contract` is the first trace-aware case. It connects the Stop trace producer, the `agent-trace/v1` schema checker, and the `stop_runtime_observation` tool contract while keeping runtime trace files local-only evidence.

## Validation

Run:

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --dry-run
.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --id EVAL-005-stop-trace-evidence-contract
.codex/.venv/bin/python tests/test_agent_eval_dataset.py
.codex/.venv/bin/python tests/test_agent_eval_runner.py
```
