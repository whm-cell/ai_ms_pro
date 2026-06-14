---
name: enterprise-code-boundary-maintenance
description: Maintain enterprise coding boundaries for logging/redaction, error contracts, runtime side effects, and config routing. Use when changing logs, errors, API/provider/client/repository/queue side effects, or config guardrails.
---

# Enterprise Code Boundary Maintenance

## Current Status

Candidate

## Scope

Use this skill for enterprise coding boundary work in this repository:

- logging, telemetry, tracing, redaction, or diagnostic output
- error codes, exception mapping, API error responses, and user-visible error text
- runtime side effects such as network, database, filesystem, queue, provider, or adapter calls
- config/env/provider/model/endpoint boundaries that route to Config Contract Boundary

Do not use this skill for simple local edits that do not touch these boundaries, or as a replacement for `AGENTS.md`, standards, deterministic checks, ADRs, status, or requirements.

## Default Workflow

1. Classify the changed surface.
- Config/env/provider/model/endpoint: read `docs/ai/standards/config-contract-boundary.md`.
- Logging/redaction: read `docs/ai/standards/logging-redaction-boundary.md`.
- Error contracts: read `docs/ai/standards/error-contract-boundary.md`.
- Runtime side effects: read `docs/ai/standards/runtime-side-effect-boundary.md`.

2. Keep canonical truth outside the skill.
- Standards live in `docs/ai/standards/*`.
- Current project state lives in `working-context`, `status`, handoff, ADR, requirements, or changelog.
- Checks and follow-up rules detect drift; this skill only tells the agent how to route the work.

3. Match enforcement to evidence.
- Treat v1 enterprise code boundaries as review-required.
- Do not claim blocking, SIEM/DLP, production observability, global error platform, service mesh, secret manager, or remote side-effect audit unless a dedicated checker, ADR, and evidence say so.
- Add or update checker coverage only when the boundary has repeat samples, low false-positive risk, a repair path, and acceptable CI/reviewer cost.

4. Close the loop.
- Update affected standards or governance docs when a durable rule changes.
- Update change-triggered follow-up when a new file family should route to a boundary review.
- Run focused tests and the repo governance checks selected by the changed surface.

## Required Output

When active, record or report:

- Boundary area reviewed
- Standard document used
- Current level: review-required, blocking-candidate, or blocking
- Checker decision: existing, new, deferred with reason, or not applicable
- Verification commands run
- Any canonical doc updates made

## Escape Hatch

You may skip or narrow this skill when a task only touches tests, docs, or local scaffolding and the changed files cannot affect logging, redaction, error responses, runtime side effects, or configuration boundaries. If a task intentionally violates a boundary, record the reason in the relevant status, handoff, or ADR.

## Evidence

- Config Contract Boundary has a working harness mechanism and focused tests.
- Logging/redaction, error contracts, and runtime side effects start as review-required standards only.

## Promotion Rule

Promote a boundary from Candidate guidance to stable rules, `AGENTS.md`, ADR, or checker enforcement only after 2-3 non-trivial tasks show the rule reduces drift without unacceptable false positives or process cost.

## Deprecation Rule

Deprecate or split this skill if a boundary becomes independently stable, gains its own checker and ownership model, or conflicts with newer repo architecture decisions. Do not keep conflicting active skills for the same boundary.
