# Agentic Harness External Standards Crosswalk

Updated: 2026-05-21
Status: draft crosswalk / standards-honesty guardrail
Scope: external standard alignment for the repo-local agentic harness

## Purpose

This document maps external agent, tracing, eval, tooling, security, and risk-management standards to the current harness surfaces.

It is not an implementation claim. Items that are not present in the repository are marked `gap`, `planned`, or `deferred`.

## Local Baseline

Current local standards:

- [Agent Trace Schema](./agent-trace-schema.md): repo-local `agent-trace/v1` JSONL span/event contract.
- [Agent Run Provenance](./agent-run-provenance.md): local-first run evidence, authority, validation, and claim-boundary contract.
- [Agent Harness Eval Protocol](../evals/README.md): lightweight eval dataset plus local deterministic runner.
- [Standard Tool Contracts](../tool-contracts/README.md): tool side-effect, permission, and automation-mode registry.
- [Harness Remaining Work](../harness-open-items.md): current backlog and known limits.

Current local hardening tracks:

| Track | Local coverage | Crosswalk boundary |
| --- | --- | --- |
| P0 lint / whitespace gate | Ruff plus `git diff --check` around harness scripts, hooks, and tests. | Does not enforce semantic standards-honesty claims. |
| Trace producer and local / OTLP pilot adapter | Stop hook runtime trace producer and `scripts/export_agent_trace.py`; default output is local/no-network. | Does not prove OpenAI, MCP, A2A, W3C, or external collector interoperability. |
| Agent-run provenance | `agent-run-provenance/v1` records REQ/WS bindings, authority, changed files, tool contracts, validation, and claim boundaries. | Does not depend on GitHub Copilot cloud agent tasks, GitHub plan upgrades, hosted traces, or raw runtime records. |
| Eval runner | `scripts/run_agent_eval_dataset.py` deterministic local checks plus optional trace evidence binding in execute mode. | Does not run hosted AgentKit / OpenAI evals or trace grading. |
| Tool contracts | Local MCP-like contract registry for tool side effects, permissions, and automation mode. | Not an MCP server/client, protocol schema, authorization layer, or dynamic capability system. |
| Security controls | Runtime sanitizer, source boundary, high-impact action matrix, workspace sandbox manifest checker, security evidence, red-team evals, local-replay sample ledger, and sample-gap collection. | Best-effort repo governance; local replay is not a replacement for native sandbox isolation, identity, monitoring, real red-team incidents, or remote policy enforcement. |

## 2026-05-21 Refresh

- OpenAI's 2026-04-15 Agents SDK update moves the reference point toward a model-native harness with native sandbox execution, sandbox manifests, separated harness/compute, snapshot and rehydration, isolated subagents, and file/image/terminal/browser-style tool surfaces. This repo now has a local workspace sandbox / rehydration manifest checker, but no native sandbox provider or separated harness/compute runtime.
- OpenAI AgentKit, hosted evals, and trace grading are platform/SDK capabilities. This repo currently has only deterministic local evals and local trace artifacts.
- MCP 2025-11-25 remains an interoperability target, especially authorization/resource/scope/PKCE, capability negotiation, tools/resources/prompts/roots, structured tool output, schema conformance, and security review. This repo has only an MCP-like contract registry.
- A2A latest is in the AgentCard / Task / Artifact / security schemes / skills direction. This repo's handoff and status docs are internal governance artifacts, not A2A messages or agent cards.
- OpenTelemetry GenAI semantic conventions remain a changing semantic target. Payload-bearing prompt, message, tool-definition, tool-argument, and tool-result fields should stay opt-in and redacted by default.
- OWASP Agentic Applications, OWASP Agentic Skills, and 2026 joint cyber guidance raise expectations for least privilege, agent identity, monitoring, red-team evals, third-party component governance, and human confirmation for high-impact actions.

## Source Baseline

Official references checked for this refresh:

- OpenAI Agents SDK 2026-04-15 update: <https://openai.com/index/the-next-evolution-of-the-agents-sdk/>
- OpenAI Agents SDK tracing: <https://openai.github.io/openai-agents-python/tracing/>
- OpenAI AgentKit / trace grading / agent evals: <https://platform.openai.com/docs/guides/agents>, <https://platform.openai.com/docs/guides/trace-grading>, <https://platform.openai.com/docs/guides/agent-evals>
- Model Context Protocol 2025-11-25: <https://modelcontextprotocol.io/specification/2025-11-25/basic>, <https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization>, <https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle>, <https://modelcontextprotocol.io/specification/2025-11-25/schema>
- A2A latest specification: <https://a2a-protocol.org/latest/specification/> and <https://a2a-protocol.org/latest/definitions/>
- W3C Trace Context: <https://www.w3.org/TR/trace-context/>
- OpenTelemetry GenAI semantic conventions: <https://opentelemetry.io/docs/specs/semconv/gen-ai/> and <https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/>
- OWASP Agentic Applications and Agentic Skills: <https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/> and <https://owasp.org/www-project-agentic-skills-top-10/>
- Joint cyber guidance, Careful Adoption of Agentic AI Services: <https://www.cyber.gov.au/business-government/secure-design/artificial-intelligence/careful-adoption-of-agentic-ai-services>

## Priority Legend

- `P0`: standards-honesty, redaction, least-privilege, sandbox/rehydration gap, or human-confirmation boundary that should shape near-term harness work.
- `P1`: adapter or schema preparation that can be added after P0 safety and claim boundaries stay intact.
- `P2`: strategic governance or later interoperability work.
- `Deferred`: explicitly not in the current implementation scope.

## Crosswalk

| External standard | Current harness coverage | Gap | Upgrade action | Priority |
| --- | --- | --- | --- | --- |
| OpenAI Agents SDK model-native harness and native sandboxes | Local governance has runtime/session artifacts, tool contracts, local traces, evals, hooks, and a repo-local workspace sandbox / rehydration manifest checker. | No native sandbox provider abstraction, separated harness/compute model, executable snapshot/rehydration runtime, or enforced isolated subagent execution contract. File/image/terminal/browser tool surfaces are not described as a unified runtime capability. | Keep the local manifest as a claim-honesty contract. Add provider/runtime work only with mounted input/output/secrets/network/tool-access evidence and subagent isolation tests. | P0 |
| OpenAI Agents SDK tracing | `agent-trace/v1` models trace/span/parent ids, span kinds, status, agent metadata, redaction, links, and local OpenAI-style conceptual mapping. Stop observations can produce local trace artifacts; `export_agent_trace.py` can render local/no-network OTLP-style JSON. | No OpenAI trace exporter, Trace dashboard integration, OpenAI trace id format guarantee, custom trace processor, or OpenAI-sensitive-data behavior equivalence. | Keep `agent-trace/v1` as local source of truth. Add exporter claims only after API-backed export evidence exists and redaction policy is explicit. | P1 |
| OpenAI AgentKit, hosted evals, and trace grading | `docs/ai/evals/agent-harness-evals.jsonl` plus `run_agent_eval_dataset.py` provide deterministic local checks and local trace evidence binding. | No Agent Builder workflow, hosted dataset/eval run, OpenAI trace grading, grader dashboard, or hosted regression evidence. | Continue to label this as local deterministic eval. A future hosted-eval bridge needs recorded run ids, grader definitions, data-handling review, and trace-payload policy. | P1 |
| OpenAI / Codex-style tool surfaces | Tool contracts capture purpose, command/path, inputs, outputs, side effects, permissions, destructive/external visibility, automation mode, and verification. | No SDK tool namespace, no dynamic tool discovery, no browser/computer tool contract, no sandbox-backed shell contract, and no approval-gate runtime implementation. | Preserve human confirmation and destructive/external visibility semantics before mapping contracts to SDK tools. | P1 |
| Model Context Protocol 2025-11-25 | Tool contracts are an MCP-like local policy registry; governance docs track source boundaries and runtime-root concepts. | No MCP server/client, JSON-RPC lifecycle, initialize capability negotiation, OAuth/resource/scope/PKCE authorization, roots/resources/prompts/tools protocol messages, structured tool output validation, or MCP security review. | Treat MCP as an interop target. Future adapter should derive tool descriptors from contracts, expose explicit roots, negotiate capabilities, validate schemas, and keep local automation-mode restrictions. | P1 |
| A2A latest spec | Handoff, status, changelog, and ADR docs support internal agent collaboration and resumability. | No AgentCard, skill advertisement, A2A endpoint, Task lifecycle, Artifact/Part model, streaming/push updates, security schemes, or cross-agent discovery. Local handoff/status docs are not A2A. | Defer protocol work until cross-system agent interoperability is a real requirement. Start from an AgentCard and Task/Artifact threat model, not by relabeling governance docs. | Deferred |
| OpenTelemetry GenAI semantic conventions | `agent-trace-schema.md` documents conceptual OTel mapping; `export_agent_trace.py` emits local/no-network OTLP-style JSON. | GenAI conventions are still development-status and changing. No stable `gen_ai.*` map, no external collector burn-in, and payload-bearing attributes are sensitive. | Keep prompt/message/tool-definition/tool-argument/tool-result payloads opt-in, redacted, or external-reference-only. Require a separate ADR before default external export or payload capture. | P0 |
| W3C Trace Context | Local traces model trace/span/parent relationships. | Local ids are not guaranteed W3C `trace-id` / `parent-id` format; no `traceparent`, `tracestate`, sampled flag, or HTTP propagation. | Generate W3C-compatible ids or record explicit `trace_context.traceparent` only when crossing process/network boundaries. | P2 |
| OWASP Agentic Applications / Agentic Skills / 2026 joint cyber guidance | Runtime sanitizer, source trust metadata, high-impact action guardrails, tool contracts, security evidence, red-team eval routing, sample gaps, and `agentic-control-matrix.md` cover several governance themes. | No real red-team sample burn-in, no agent identity model, no native sandbox isolation proof, no third-party component attestation beyond local catalog/checks, and no runtime monitor proving every high-impact path is covered. | Prioritize least privilege, distinct agent identity, monitoring/audit logs, third-party component registry/provenance, real red-team samples, and mandatory human confirmation for high-impact or hard-to-reverse actions. | P0 |
| NIST AI RMF / GenAI profile | Governance docs, requirements traceability, status/handoff/ADR/changelog, check registry, eval protocol, and security triage provide Govern/Map/Measure/Manage-style evidence surfaces. | Owner fields and long-term metrics remain partial; no complete impact assessment template or quantitative risk-reduction evidence. | Replace placeholders with confirmed owners and record real samples against control ids before upgrading checks. | P2 |

## Current Non-Goals

- No OpenAI, MCP, A2A, W3C Trace Context, or default external OpenTelemetry interoperability is claimed by this document.
- No hosted eval service, trace grading backend, AgentKit workflow, GitHub Copilot cloud agent task surface, or model-quality dashboard is introduced by this document.
- No native sandbox provider, enforced subagent isolation runtime, or executable snapshot/rehydration runtime is introduced by this document; the local workspace manifest is a claim-honesty contract only.
- No runtime payload capture policy changes are introduced by this document.

## Review Checklist

Before using this crosswalk as an enforcement input, verify:

- Any OpenAI SDK parity claim is backed by a real sandbox/manifest/export/eval artifact.
- Any MCP or A2A compatibility claim is backed by protocol message/schema/auth tests.
- Any W3C or OpenTelemetry compatibility claim is backed by id/header/attribute tests.
- Trace payload fields remain opt-in/redacted unless a separate ADR and data-handling review approve them.
- High-impact tool actions have least-privilege scope, audit evidence, and human confirmation semantics.
- `docs/ai/index.md` links this file; per narrow write scopes, update the index only when allowed.
