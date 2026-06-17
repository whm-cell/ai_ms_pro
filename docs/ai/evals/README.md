# Agent Harness Eval Protocol

Updated: 2026-06-17
Status: standard lightweight dataset

## Purpose

This directory now carries two repo-local eval layers:

- `agent-harness-evals.jsonl`: workflow / guardrail / tooling behavior
- `task-outcome-evals.jsonl`: task completion quality and bounded cost proxies

Neither layer is a hosted eval service. Together they let the harness distinguish:

- whether an agent followed the harness correctly
- whether the harness helped the agent finish a real task without overreach

## Files

- `agent-harness-evals.jsonl`: workflow behavior dataset
- `task-outcome-evals.jsonl`: task outcome dataset
- `scripts/check_agent_eval_dataset.py`: workflow dataset validator
- `scripts/run_agent_eval_dataset.py`: workflow dataset runner
- `scripts/check_task_outcome_eval_dataset.py`: task outcome dataset validator
- `scripts/run_task_outcome_eval_dataset.py`: task outcome dataset runner
- `tests/test_agent_eval_dataset.py`, `tests/test_agent_eval_runner.py`
- `tests/test_task_outcome_eval_dataset.py`

## Dataset Item Fields

Each JSONL item must contain:

- `id`: Stable unique ID, using `EVAL-NNN-kebab-name`.
- `title`: Short human-readable task name.
- `category`: One of `simple-code`, `requirements-traceability`, `high-impact-guardrail`, `resume-runtime`, or `skill-harness`.
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
- task-outcome runner execute mode now also treats soft output signals such as `WARN:` / `Warnings:` / `review-required` as observed `warn` or `review-required` instead of counting them as a clean pass.
- matching trace evidence grades `pass`; missing or invalid trace evidence grades `fail` in execute mode.
- any non-zero exit code grades `fail`.
- `--dry-run` grades `not-run` and is the safe CI path for runner wiring.

This runner is local-only. It does not call model APIs, hosted eval services, OpenTelemetry, OpenAI trace backends, MCP servers, or A2A systems.

## Task Outcome Eval Layer

`task-outcome-evals.jsonl` adds a second deterministic layer for benchmark-like task slices.

It records:

- benchmark group
- expected changed surface
- expected command class
- expected repo-local validation commands with `expected_outcome` limited to `pass` / `warn` / `review-required`
- bounded overreach expectation
- resume-stability expectation
- guardrail posture expectation

`scripts/run_task_outcome_eval_dataset.py` reports:

- `task_outcome`
- `command_count`
- `timeout_budget_seconds`
- `latency_budget_seconds`
- `model_usage`
- `estimated_model_cost_usd`
- `measurement_boundary`
- `overreach`
- `resume_stability`
- `guardrail_posture`
- per-check `observed_signal` alongside `expected_outcome`
- aggregate `pass_count`, `warn_count`, `review_required_count`, `fail_count`, `not_run_count`
- aggregate `blocked_by_resume` and `blocked_by_guardrail`

Execute-mode `warn` is an expected soft signal class for checks such as context budget or governance advisory output. It should be reviewed, but it is not the same as `fail` unless the dataset row expected a clean pass or the command exits non-zero.

This is still local-only. It does not judge model quality from hidden grader prompts or external telemetry, but it gives the harness a stable way to compare “workflow passed” against “task outcome passed”.

The default deterministic runner records `model_usage=none` and
`estimated_model_cost_usd=0.0`, because it executes repo-local checks rather than
calling a model API. `latency_budget_seconds` is timeout-derived and should be
read as a bounded execution budget, not measured wall-clock latency or hosted
service latency.

When `--output <path>` is used, the runner now creates missing parent directories automatically so the first local artifact write does not fail on an empty runtime folder.

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

`EVAL-006` through `EVAL-020` cover skill-harness hardening: third-party skill catalog/proxy/lock handling, skill/tool output scanning, source quarantine, mixed-stack code-shape, changed-file follow-up routing, multi-surface context budget, and starter portability.

`EVAL-027-runtime-token-budget-audit` covers the runtime token pressure layer: large tool output, last-input spikes, fresh-input/cache-miss spikes, and long-session warnings remain separate from static default-context budget.

`EVAL-028-tool-output-artifact-summary` covers artifact-preserving compression: raw tool output stays in `.codex/runtime/tool-outputs/`, while the transcript receives bounded summaries and line windows.

`EVAL-029-planner-executor-reviewer-sample` covers a minimal planner / executor / reviewer sample shape using the existing `agent-trace/v1`, `agent-run-provenance/v1`, and workflow eval schemas. It is explicitly unbound from current REQ / WS validation chains and is sample-only: no scheduler/runtime, hosted trace backend, external collector, A2A interoperability, cloud agent task support, or red-team evidence is claimed.

`task-outcome-evals.jsonl` starts with nine benchmark groups: `simple-fix`, `cross-file`, `docs-sync`, `risk-judgment`, `tool-selection`, `resume-durability`, `trace-interop-boundary`, `warning-review-signal`, and `overreach-prevention`.

## Validation

Run:

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --dry-run
.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --id EVAL-005-stop-trace-evidence-contract
.codex/hooks/run_with_repo_python.sh scripts/check_task_outcome_eval_dataset.py
.codex/hooks/run_with_repo_python.sh scripts/run_task_outcome_eval_dataset.py --dry-run
.codex/.venv/bin/python tests/test_agent_eval_dataset.py
.codex/.venv/bin/python tests/test_agent_eval_runner.py
python3 tests/test_task_outcome_eval_dataset.py
```
