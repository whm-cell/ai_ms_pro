# Agentic Harness External Standards Crosswalk

Updated: 2026-05-10
Status: draft crosswalk
Scope: external standard alignment for the repo-local agentic harness

## Purpose

This document maps external agent, tracing, eval, tooling, security, and risk-management standards to the current harness surfaces.

It is not an implementation claim. Items that are not present in the repository are marked `gap`, `planned`, or `deferred`.

## Local Baseline

Current local standards from the previous round:

- [Agent Trace Schema](./agent-trace-schema.md): repo-local `agent-trace/v1` JSONL span/event contract.
- [Agent Harness Eval Protocol](../evals/README.md): lightweight eval dataset plus local deterministic runner.
- [Standard Tool Contracts](../tool-contracts/README.md): tool side-effect, permission, and automation-mode registry.
- [Harness Remaining Work](../harness-open-items.md): current backlog and known limits.

This round adds related local hardening tracks:

| Track | Relationship to previous round | Current status in this document |
| --- | --- | --- |
| P0 linter | Adds a conventional Python lint / whitespace gate around harness scripts, hooks, and tests. | Implemented this round through Ruff plus `git diff --check`; semantic standards-honesty checks remain governance review, not Ruff rules. |
| Trace producer and local / OTLP pilot adapter | Emits runtime-derived records that conform to `agent-trace/v1`, translates sample traces to local JSON, and can render OTLP HTTP JSON with no network export by default. | Implemented by the Stop hook runtime trace producer and `scripts/export_agent_trace.py`; OpenAI, MCP, A2A, and external collector exporters remain opt-in future work. |
| Eval runner | Executes or dry-runs declared repo-local eval checks with deterministic grading and can bind declared trace evidence in execute mode. | Implemented by `scripts/run_agent_eval_dataset.py`; hosted evals and trace grading remain gaps. |
| Sample gap collector | Lists real-scenario coverage gaps for security evidence, AI guardrail, workflow skills, and future interop. | Implemented this round by `scripts/collect_harness_sample_gaps.py` and the `--使用细节` gap document. |
| External standards crosswalk | Documents how the local harness maps to external standards and what gaps remain. | This file is the docs artifact. It creates no enforcement by itself. |

## Source Baseline

Official references checked for this crosswalk:

- OpenAI Agents SDK tracing: <https://openai.github.io/openai-agents-python/tracing/>
- OpenAI Agents SDK tools: <https://openai.github.io/openai-agents-python/tools/>
- OpenAI agent evals / trace grading: <https://developers.openai.com/api/docs/guides/agent-evals>
- Anthropic agent patterns: <https://www.anthropic.com/engineering/building-effective-agents>
- Model Context Protocol specification: <https://modelcontextprotocol.io/specification/2025-11-25/basic>
- W3C Trace Context: <https://www.w3.org/TR/trace-context/>
- OpenTelemetry GenAI semantic conventions: <https://opentelemetry.io/docs/specs/semconv/gen-ai/>
- OpenTelemetry GenAI agent spans: <https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/>
- OWASP LLM Top 10 / GenAI Security Project: <https://owasp.org/www-project-top-10-for-large-language-model-applications/>
- OWASP Top 10 for Agentic Applications announcement: <https://genai.owasp.org/2025/12/09/owasp-genai-security-project-releases-top-10-risks-and-mitigations-for-agentic-ai-security/>
- NIST AI RMF and GenAI profile entrypoint: <https://www.nist.gov/itl/ai-risk-management-framework>
- Google / A2A announcement and current A2A spec: <https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/> and <https://a2a-protocol.org/latest/specification/>

## Priority Legend

- `P0`: should influence this round's linter or trace-producer work.
- `P1`: important next hardening once P0 lands.
- `P2`: strategic governance or later interoperability work.
- `Deferred`: explicitly not in the current implementation scope.

## Crosswalk

| External standard | Current harness coverage | Gap | Upgrade action | Priority |
| --- | --- | --- | --- | --- |
| OpenAI Agents SDK tracing | `agent-trace/v1` has `trace_id`, `span_id`, `parent_span_id`, span `kind`, status, agent, redaction, links, and conceptual OpenAI mapping for agent run, step, tool call, guardrail, handoff, and reducer spans. Stop observations now produce local `agent-trace/v1` events, and `export_agent_trace.py` emits local `local-otel-json`. | No OpenAI trace exporter, no OpenAI trace id format guarantee, no `workflow_name` / `group_id` first-class fields, no custom trace processor, and no trace dashboard integration. Sensitive data capture defaults are not equivalent to the OpenAI SDK behavior. | Keep `agent-trace/v1` as local source of truth. Future producer work may add stable workflow/group metadata in `attributes` or future fields, keep redaction mandatory, and avoid exporter claims until an exporter exists. | P1 |
| OpenAI agent evals / trace grading | `docs/ai/evals/agent-harness-evals.jsonl` defines task prompts, expected artifacts, checks, grading signals, risk tags, shape validation, local deterministic execution, and trace evidence binding through `run_agent_eval_dataset.py`. | No hosted dataset/eval API usage, no OpenAI trace grading integration, and no automated regression dashboard. Trace evidence is local artifact evidence only. | Keep the local runner explicit and small. Avoid hosted-eval claims until API-backed runs are recorded. | P1 |
| OpenAI Agents SDK tooling | Tool contract registry captures purpose, path, command, inputs, outputs, side effects, permissions, destructive/external visibility, automation mode, and verification commands. | No SDK tool namespace, hosted MCP, tool search, approval-gate implementation, or dynamic tool loading. The registry does not execute tools or prove remote permissions. | Keep destructive and externally visible defaults enforced by `check_tool_contracts.py`, not by Ruff. Future tool adapters may map contracts to SDK/MCP descriptors, but only after human-confirmation semantics are preserved. | P1 |
| Anthropic agent patterns | Task discovery profiles, explicit skill triggers, compact subagent packets, workflow-skill eval samples, eval dataset, guardrail docs, and status/handoff compression reflect simple-first and composable workflow practice. | No pattern-level metadata for prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, or autonomous-loop stopping conditions. No checker proves a task used the simplest viable pattern. | Add optional `agent_pattern` tags to eval samples and trace attributes when useful. For autonomous loops, trace producer should record checkpoints, blockers, and human-confirmation pauses without storing raw prompts. | P1 |
| Model Context Protocol | Tool contracts provide an MCP-like local policy surface for tools; source-boundary and runtime-root concepts exist in governance docs. | No MCP server/client, no JSON-RPC lifecycle, no capability negotiation, no roots/resources/prompts/tools protocol messages, no MCP auth layer, and no schema dialect conformance check. | Treat MCP as an interoperability target, not current behavior. Future adapter should derive MCP tool descriptors from `contracts.json`, expose explicit roots, and preserve local automation-mode restrictions. | P1 |
| W3C Trace Context | Local traces already model trace/span/parent relationships and can conceptually map to distributed trace parentage. The Stop hook producer now emits local root events with deterministic trace/span ids. | Local IDs are not guaranteed to be W3C `trace-id` / `parent-id` hex formats. No `traceparent`, `tracestate`, sampled flag, or HTTP propagation behavior exists. | Future trace producer work should either generate W3C-compatible IDs or record a separate `trace_context.traceparent` attribute when crossing process/network boundaries. Do not claim W3C propagation until headers are emitted and parsed. | P1 |
| OpenTelemetry semantic conventions | `agent-trace-schema.md` documents a conceptual OTel mapping. `export_agent_trace.py` emits local JSON and no-network OTLP HTTP JSON-style `resourceSpans`; explicit `--send --endpoint` records `network_exported` and HTTP status evidence. | No default network export, no external collector burn-in, no stable `gen_ai.*` attribute map, and no opt-in policy for prompt/message/tool-definition payloads. OTel GenAI conventions are still marked development. | Keep payload-bearing `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, and `gen_ai.tool.definitions` out by default. Treat external collector export as separate ADR / contract work. | P1 |
| OWASP LLM / Agentic AI security | Runtime sanitizer, source trust metadata, high-impact action guardrails, tool side-effect contracts, security evidence docs, advisory follow-ups, and `agentic-control-matrix.md` cover prompt-injection, excessive-agency, sensitive-disclosure, unsafe-plugin/tool, and supply-chain themes at a repo-policy level. | No red-team eval set, no automated skill/MCP scanner, and no proof that every high-impact action path is covered by a contract. | Use the control matrix for real-sample triage. Add separate contract/security checks for high-impact automation paths when the path is in scope. | P1 |
| NIST AI RMF / GenAI profile | Governance docs, requirements traceability, status/handoff/ADR/changelog, check registry, eval protocol, security triage, and `agentic-control-matrix.md` provide Govern/Map/Measure/Manage-style evidence surfaces. | Owner fields are still placeholders; no impact assessment template or metrics proving long-term risk reduction. | Replace owner placeholders when confirmed, and record real samples against control IDs before upgrading checks. | P2 |
| Google A2A / Agent2Agent | Local handoff/status/changelog concepts provide internal collaboration artifacts only. There is no external agent-to-agent protocol implementation. | No Agent Card, A2A client/server endpoint, task lifecycle, artifacts, streaming, auth, modality negotiation, or cross-agent discovery. | Defer until the repo needs cross-system agent interoperability. When reopened, start from an Agent Card draft and task/artifact threat model; do not retrofit A2A into local handoff docs. | Deferred |

## P0 Completion Mapping

Completed this round:

1. P0 linter: Ruff is pinned in `.codex/requirements.txt`, configured for `E9` plus Pyflakes `F` in `pyproject.toml`, and run in the governance workflow with `git diff --check`.
2. Trace producer: Stop observations now emit local `agent-trace/v1` JSONL under `.codex/runtime/observations/agent-traces/`.
3. Eval runner: `run_agent_eval_dataset.py` validates the dataset and can execute selected local expected checks with deterministic grading; CI uses `--dry-run`.
4. Local / OTLP pilot trace adapter: `export_agent_trace.py` converts valid `agent-trace/v1` JSONL into local `local-otel-json` and no-network `otlp-http-json`; network export only runs with explicit `--send --endpoint`.
5. Sample gap collector: `collect_harness_sample_gaps.py` lists pending real-scenario coverage gaps.
6. Crosswalk routing: `docs/ai/index.md` links this file as an agentic standards entry.

Still intentionally not claimed:

1. Ruff does not enforce semantic standards-honesty language, missing tool contracts, MCP compatibility, or A2A behavior.
2. The trace producer and local / OTLP pilot adapter do not emit W3C `traceparent`, OpenAI trace exports, MCP protocol messages, A2A task artifacts, or default network export.
3. Runtime trace files remain local artifacts and must still be reviewed before any conclusion is promoted into `docs/ai/*` or `docs/requirements/*`.

## Current Non-Goals

- No OpenAI, MCP, A2A, or default external OpenTelemetry exporter is created by this document.
- No existing `.codex/runtime/*` file is migrated by this document.
- No hosted eval service, trace grading backend, or model-quality dashboard is introduced by this document.
- No external standard is claimed fully implemented unless the repository has a corresponding doc, checker, or runtime producer.

## Review Checklist

Before using this crosswalk as an enforcement input, verify:

- The P0 linter exists and explicitly reads or encodes the intended rules.
- The trace producer emits records that pass `scripts/check_agent_trace_schema.py`.
- The local trace adapter output is generated by `scripts/export_agent_trace.py` and still declares `network_exported=false` unless explicit `--send --endpoint` was used.
- The eval runner is invoked explicitly and does not treat `--dry-run` as completed behavioral evaluation.
- Any W3C or OpenTelemetry compatibility claim is backed by ID/header/attribute tests.
- Any MCP or A2A compatibility claim is backed by protocol message/schema tests.
- `docs/ai/index.md` links this file once the write scope allows index maintenance.
