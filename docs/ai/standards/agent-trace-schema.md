# Agent Trace Schema

Status: draft standard
Scope: repo-local runtime observations and future agent harness trace exports
Schema file: `docs/ai/standards/agent-trace.schema.json`
Sample file: `docs/ai/standards/agent-trace-sample.jsonl`

## Purpose

The agent trace schema defines a dependency-free contract for future runtime observations. It standardizes the smallest useful span/event object needed to reconstruct an agent run, check tool usage, guardrail decisions, and handoff/reducer activity without importing OpenTelemetry, OpenAI Agents SDK packages, or a JSON Schema runtime.

Existing files under `.codex/runtime/` are local recovery artifacts and are not migrated by this standard. New producers should emit this shape when they need portable trace records.

## Stop Hook Producer

`stop_runtime_observation.py` continues to append local reducer input to `.codex/runtime/observations/YYYY-MM-DD.jsonl`. It also emits one portable `agent-trace/v1` event per Stop observation under `.codex/runtime/observations/agent-traces/YYYY-MM-DD.agent-trace.jsonl`.

The producer derives trace metadata from the sanitized observation fields already written by the hook. `trace_id` and `span_id` are deterministic hashes of the session / stop-event identity rather than random values; raw session ids and local cwd values are omitted from trace attributes. Stop observations have no known parent span, so the producer serializes `parent_span_id` as `null` to satisfy the current schema. Trace timestamps are converted to RFC3339 UTC `Z`, and invalid `REQ-*` / `WS-*` identifiers are filtered before writing.

These trace files are still local runtime artifacts. They do not migrate historical `.codex/runtime/*` files and do not make runtime trace data canonical governance truth; stable conclusions still need review before promotion into handoff, status, ADR, plan, or requirements documents.

The trace sample now includes a Stop observation event that mirrors the producer contract. `docs/ai/evals/agent-harness-evals.jsonl` may express matching `trace_expectations`, and `docs/ai/tool-contracts/contracts.json` records the Stop hook as a local `write_runtime` producer. This is a repo-local validation loop only; it is not an OpenTelemetry exporter, OpenAI exporter, hosted eval runner, or remote trace-dashboard integration.

## Local Export Adapter

`scripts/export_agent_trace.py` converts `agent-trace/v1` JSONL into either a local `local-otel-json` adapter payload or an `otlp-http-json` pilot payload. The adapter validates the input against this schema first, maps safe metadata into attributes, and emits JSON to stdout or an explicitly requested local output file.

Default behavior is still no-network:

- `local-otel-json` preserves repo-local trace / span ids for local inspection and sets `network_exported: false`.
- `otlp-http-json` renders an OTLP HTTP JSON-style `resourceSpans` payload with deterministic hex trace/span ids derived from the repo-local ids, while keeping the original ids as attributes.
- network export only happens when both `--format otlp-http-json` and `--send --endpoint <url>` are explicit; successful export records `network_exported: true`, endpoint, and HTTP status evidence.
- this pilot does not claim OpenAI trace backend, MCP server/client, A2A interoperability, or hosted trace grading.

## Record Model

Each JSONL line is one span/event object. A trace is the set of records sharing one `trace_id`. Parentage is represented by `parent_span_id`; root records set it to `null`.

Required fields:

- `schema_version`: string. Current value is `agent-trace/v1`.
- `trace_id`: stable trace identifier for one agent run.
- `span_id`: unique span identifier within the trace.
- `parent_span_id`: parent span id or `null` for root spans.
- `name`: short human-readable span name.
- `kind`: one of `agent_run`, `agent_step`, `tool_call`, `check`, `guardrail`, `handoff`, `reducer`, `event`.
- `start_time`: RFC3339 UTC timestamp.
- `end_time`: RFC3339 UTC timestamp.
- `status`: object with required `code`, one of `ok`, `error`, `unset`; optional `message`.
- `agent`: object with required `name` and `role`.
- `redaction`: object describing whether sensitive content was removed before writing.

Optional fields:

- `event`: short event type, for example `start`, `end`, `decision`, `evidence`, or `handoff_draft`.
- `attributes`: low-cardinality metadata such as command, tool name, exit code, changed file counts, or guardrail result. Keep values scalar or shallow arrays.
- `requirement_ids`: known `REQ-*` IDs. Use an empty array when unknown.
- `workstream_ids`: known `WS-*` IDs. Use an empty array when unknown.
- `links`: related spans, files, PRs, or evidence objects. Do not store full transcripts or raw payloads here.
- `error`: structured error details with optional `type`, `message`, and `retryable`.

## Redaction And Sensitive Data

Trace records must not contain raw secrets, credentials, full transcripts, full PRDs, full prompts, or unreviewed external content. Producers must apply best-effort redaction before writing trace data and must set `redaction.state` honestly:

- `redacted`: sensitive content was present and was removed or summarized.
- `not_applicable`: no sensitive payload was captured.
- `unredacted`: the producer could not apply redaction. This state is allowed for validation visibility, but should be treated as review-required before promotion into shared governance docs.

Use `attributes` for safe metadata and short summaries only. If detailed recovery material is needed, store it under `.codex/runtime/` and promote only reviewed conclusions into `docs/ai/*` or `docs/requirements/*`.

## Parent Linkage Rules

- `span_id` must be unique within a JSONL trace file.
- A root `agent_run` span should have `parent_span_id: null`.
- Non-root records must reference a `span_id` present in the same JSONL file.
- A record must not reference itself as parent.
- Cross-file parentage is intentionally out of scope for the checker.

## Mapping Notes

OpenTelemetry GenAI / agent concepts:

- `trace_id` maps to an OTel trace id.
- `span_id` and `parent_span_id` map to OTel span identifiers.
- `name`, `kind`, `start_time`, `end_time`, and `status` map to standard span fields.
- `attributes` maps to OTel attributes; keep cardinality low and avoid raw payloads.
- `links` maps conceptually to OTel span links.
- `kind` values such as `agent_run`, `tool_call`, and `guardrail` are repo-local semantic span categories for agent harness work.

OpenAI Agents SDK trace concepts:

- `agent_run` represents the top-level run trace.
- `agent_step` represents model or orchestration steps.
- `tool_call` and `check` represent tool spans or validation spans.
- `guardrail` represents input, output, or action guardrail evaluation.
- `handoff` and `reducer` represent repo harness transfer and compression spans.

The mapping is conceptual only. The repo-local schema is the source of truth for validation.
