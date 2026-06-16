# External Harness Decisions

Updated: 2026-06-16
Status: active bounded decision ledger

## Purpose

`external-harness-decision/v1` records operator-level decisions for harness
surfaces that could otherwise drift into broad platform claims:

- remote trace pilot
- external eval / sandbox comparison
- MCP / A2A tool interop direction
- CI agent workflow direction

The ledger turns these choices into reviewable local evidence without creating
external effects by default. Each active record now also carries first-party
`source_evidence` so the decision is tied to current external signals rather
than an unreviewed manual preference.

As of 2026-06-08, active records also carry `default_permission`. This records
the operator policy that evidence-backed, positive, bounded harness
improvements are permitted by default when they stay inside the record's local
upgrade scope and all no-claim boundaries remain true.

## Files

- `external-harness-decisions.md`: human-readable standard.
- `external-harness-decisions.jsonl`: current decision records.
- `coding-agent-browser-harness-selection.md`: scoped coding-agent comparator
  and browser harness transport selection rules.
- `scripts/check_external_harness_decisions.py`: stdlib validator.
- `tests/test_external_harness_decisions.py`: validator tests.

## Decision Policy

Current active decisions:

- Remote trace pilot: defer any external send until an explicit endpoint and
  operator confirmation exist; local/no-send reports remain valid evidence for
  shape only.
- External eval / sandbox: run comparison-only research and local wrapper
  checks first; use `mini-swe-agent` as the current lightweight coding-agent
  comparator when relevant, while keeping SWE-agent main as historical /
  SWE-bench context; do not add a new dependency or native sandbox claim.
- MCP / A2A: stay contract-registry-only until a concrete runtime integration
  proposal exists. For deterministic coding-agent and browser smoke harnesses,
  prefer repo-local CLI / skills before MCP; reserve MCP evaluation for
  persistent state, rich introspection, or explicit client interop needs.
- CI agent workflow: keep the CI agent contract advisory; do not create a real
  GitHub agent workflow in Stage-00.

## Source-Backed Upgrade Policy

Every record must include `source_evidence` entries with:

- `source_type`: `official-doc`, `github-release`, `pypi-release`, or
  `official-spec`.
- `source_date`: publication date when known, or an accessed date when the
  source is a living document.
- `url`: HTTPS first-party source URL.
- `positive_signal=true`: the source supports the local decision direction.
- `finding`: bounded explanation of what the source demonstrates.
- `local_upgrade_scope`: the local-only upgrade scope allowed by this decision.

Positive external evidence can upgrade local decision quality, comparison
criteria, metadata discipline, and boundary visibility. It does not by itself
upgrade `ai_ms_pro` to hosted tracing, hosted eval, native sandbox, MCP / A2A
runtime, verified remote interop, or real CI agent workflow.

## Evidence-Backed Default Permission

`default_permission` must be present on every active record and must include:

- `policy`: `evidence-backed-default-permit`.
- `positive_for_current_harness=true`.
- `evidence_grade`: `first-party-source-backed`.
- `permitted_scope`: bounded local work that is allowed without another
  manual decision.
- `blocked_scope`: explicit capability claims and external effects that remain
  blocked.
- `evidence_threshold`: the evidence and boundary requirements that must remain
  true.
- `verification_commands`: validators that must pass after the change.

This default permission is intentionally narrow. It permits local/no-effect
decision hardening, metadata alignment, comparison-only analysis, and advisory
contract improvements when first-party evidence supports the direction. It does
not permit raw payload export, verified remote claims, hosted eval claims,
native sandbox claims, MCP / A2A runtime claims, real CI agent workflow
creation, or externally visible effects without explicit confirmation and the
record's activation gates.

## Required Boundaries

Every record must keep these no-claim flags true:

- `no_hosted_trace_or_eval_claim`
- `no_verified_remote_claim_without_operator_review`
- `no_native_sandbox_claim`
- `no_mcp_a2a_runtime_claim`
- `no_real_ci_agent_workflow_claim`
- `no_external_effect_without_explicit_confirmation`

These flags are deliberately global so a record cannot quietly claim a nearby
capability while discussing a different one.

## Validation

Run:

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_external_harness_decisions.py
python3 tests/test_external_harness_decisions.py
```

The checker is read-only. It validates the decision ledger, referenced tool
contracts, source evidence, evidence refs, and required area coverage. It does
not create remote probes, install external eval tools, add MCP / A2A runtime
code, or create a CI agent workflow.
