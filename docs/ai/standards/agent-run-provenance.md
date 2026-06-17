# Agent Run Provenance Standard

Updated: 2026-06-17
Status: local-first standard

## Purpose

`agent-run-provenance/v1` records the bounded evidence for a meaningful agent run without depending on GitHub plan upgrades, GitHub Copilot cloud agent tasks, hosted traces, MCP / A2A interop, or raw runtime files.

It answers:

- What task profile was used.
- Which `REQ` / `WS` bindings were carried, or whether the task was explicitly unbound.
- Which actor had authority to write canonical docs or only produce a draft.
- Which files changed and which tool contracts governed the work.
- Which validation commands were actually run.
- Which model / token / cost / latency boundary applied to the run.
- Which claims are verified locally, which remain plan-limited / unknown, and which are explicitly not claimed.

## Files

- `agent-run-provenance.md`: human-readable standard.
- `agent-run-provenance-sample.jsonl`: canonical sample records.
- `scripts/check_agent_run_provenance.py`: stdlib validator.
- `tests/test_agent_run_provenance.py`: validator tests.

## Record Shape

Required fields:

- `schema_version`: must be `agent-run-provenance/v1`.
- `id`: stable `ARP-YYYY-MM-DD-kebab-case` id.
- `recorded_at`: `YYYY-MM-DD`.
- `task_profile`: one of `simple`, `medium`, `complex`, `0-1-stage`, or `recovery-dispute`.
- `task_summary`: bounded summary of the work.
- `requirement_ids` / `workstream_ids`: either concrete `REQ-XXX` / `WS-XX` values or both set to `["unbound"]`.
- `platform_boundary`: one of `local-only`, `local-with-ci-evidence`, or `manual-github-evidence`.
- `run_metrics`: model usage, model name, estimated input / output tokens, estimated cost,
  latency, and measurement boundary.
- `authority`: actor, authority level, canonical-write flag, and allowed outputs.
- `changed_files`: repo-relative files or directories touched by the run.
- `tool_contracts`: names from `docs/ai/tool-contracts/contracts.json`.
- `validation`: command, outcome, and evidence refs.
- `claim_boundaries`: verified claims, plan-limited / unknown items, and explicitly not-claimed items.
- `evidence_refs`: repo-relative supporting files.
- `decision_summary`: bounded result or decision.

## Local-First Boundary

Current project policy keeps this standard local-first:

- GitHub Free private branch protection / rulesets stay `UNKNOWN` and plan-limited.
- GitHub Actions, PR metadata, dependency review, Scorecard, CodeQL, and SBOM may be recorded as evidence, not as remote enforcement.
- GitHub Copilot cloud agent tasks and GitHub hosted agent task APIs are not first-class provenance sources for this repo.
- `.codex/runtime/*` remains local recovery material and must not be referenced as canonical provenance evidence.
- Hosted trace, MCP, A2A, OpenAI sandbox, and external OTLP claims require separate adopted ADRs and real evidence before they can move out of `not_claimed` or `future-work`.
- Local deterministic checks should set `run_metrics.model_usage=none`,
  `estimated_cost_usd=0`, and `latency_ms=0`. Real model-backed runs must state
  the model class/name, estimated tokens, estimated cost, latency, and whether the
  values are measured or bounded estimates.

## Validation

Run:

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_agent_run_provenance.py
python3 tests/test_agent_run_provenance.py
```
