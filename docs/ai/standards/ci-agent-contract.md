# CI Agent Contract Standard

Updated: 2026-06-06
Status: advisory local standard

## Purpose

`ci-agent-contract/v1` defines a bounded, advisory contract for describing agent-like work inside CI without adding a real agent workflow.

The contract exists to keep future CI automation honest about scope:

- Execution is limited to `pull_request` events.
- `pull_request_target` is never an execution trigger.
- Default permissions remain read-only / default-minimal unless the record is explicitly `human_confirmed`.
- Secrets, OIDC, repository writes, PR comments, labels, merge, release, deploy, and external-send capabilities are forbidden.
- Inputs, outputs, and referenced tool contracts are bounded and reviewable.
- Claim boundaries do not assert hosted/cloud-agent execution or remote enforcement.

## Files

- `ci-agent-contract.md`: human-readable standard.
- `ci-agent-contract.sample.jsonl`: canonical sample record.
- `scripts/check_ci_agent_contract.py`: stdlib-only advisory validator.
- `tests/test_ci_agent_contract.py`: validator tests.

## Record Shape

Required fields:

- `schema_version`: must be `ci-agent-contract/v1`.
- `id`: stable record identifier.
- `recorded_at`: `YYYY-MM-DD`.
- `purpose`: bounded explanation of the advisory CI-agent boundary.
- `event.execution_triggers`: exactly `["pull_request"]`.
- `permissions`: `profile`, `human_confirmed`, and `scopes`.
- `capabilities`: explicit false booleans for forbidden capabilities.
- `bounded_inputs`: non-empty bounded input classes.
- `bounded_outputs`: non-empty bounded output classes.
- `tool_contracts`: existing names from `docs/ai/tool-contracts/contracts.json`.
- `claim_boundary`: explicit no-claim flags for hosted/cloud-agent execution, remote enforcement, and real workflow creation.
- `evidence_refs`: repo-relative files supporting the contract.

## Validation

Run:

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ci_agent_contract.py
python3 tests/test_ci_agent_contract.py
```

This checker is advisory. It validates the sample contract shape; it does not create, modify, or prove any GitHub Actions workflow.
