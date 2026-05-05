# Supply Chain Security Evidence

Use this reference when adding or changing Scorecard, CodeQL, SBOM, artifact attestation, SLSA provenance, Dependabot, or dependency review behavior.

## Stage-00 Policy

- Scorecard, CodeQL, and SBOM are evidence-producing advisory jobs until burn-in proves signal quality.
- Dependency review remains advisory when GitHub reports dependency graph / Advanced Security is unavailable.
- SLSA provenance is planned at the artifact boundary; do not require provenance before the project has release artifacts.
- Do not claim supply-chain enforcement is active unless the relevant GitHub job or remote setting has been observed.

## Required Records

- Update `docs/ai/check-registry.md` when a supply-chain check changes level.
- Update `docs/ai/security/supply-chain-provenance-plan.md` when artifact or provenance expectations change.
- Keep `AGENTS.md` light; add only trigger rules if supply-chain work becomes a recurring default.

## Verification

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py
```

Security evidence workflow failures should be treated as advisory until a later ADR promotes a specific check to blocking.
