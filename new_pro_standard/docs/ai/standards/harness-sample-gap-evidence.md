# Harness Sample Gap Evidence

Status: draft standard
Schema: `harness-sample-gap-evidence/v1`
Sample ledger: `docs/ai/standards/harness-sample-gap-evidence.jsonl`
Checker: `scripts/check_harness_sample_gap_evidence.py`
Collection planner: `scripts/plan_harness_sample_collection.py`

## Purpose

This ledger records bounded evidence for roadmap gaps that do not yet have a
dedicated sample checker. It is an intake surface for security evidence,
guardrail, workflow, and trace interop gaps listed by
`scripts/collect_harness_sample_gaps.py`.

The checker is advisory. It validates shape, raw-runtime boundaries, local vs
real sample type, and gap-specific constraints where the evidence would be easy
to overstate.

## Boundary

- Do not store prompts, transcripts, raw command output, request bodies,
  response bodies, credentials, or `.codex/runtime/*` paths.
- `local-interop-run` and `local-replay` samples can prove local harness
  behavior only. They do not prove hosted collector, OpenAI, MCP, A2A, or native
  sandbox interoperability.
- `accepted` records need bounded evidence refs and an explicit action taken.
- `synthetic-regression` records can protect the checker shape, but they do not
  count as real or local gap burn-in evidence.

## Required Fields

- `schema_version`: `harness-sample-gap-evidence/v1`
- `id`: `GAP-SAMPLE-YYYY-MM-DD-...`
- `gap_id`: a `GAP-*` id from `collect_harness_sample_gaps.py`
- `sampled_at`: `YYYY-MM-DD`
- `source_type`: one of the checker-supported real, local, manual, or synthetic
  source types
- `outcome`: `accepted`, `pending`, or `rejected`
- `local_only`, `no_external_claim`, `false_positive`, `network_exported`
- `endpoint_scope`, `remote_status`
- `sample_summary`, `decision`, `boundary_note`
- `action_taken`, `evidence_refs`, `checker_refs`

## Current Local Pilot

The first accepted record covers `GAP-TRACE-OTLP-PILOT-BURNIN` using the
existing localhost capture-server test path. It records only local OTLP HTTP
JSON pilot evidence: explicit `--send`, explicit endpoint, `network_exported`
true, and HTTP 2xx status. It intentionally leaves hosted tracing and external
interop gaps open.

## Current Source Boundary Sample

The second and fourth accepted records cover `GAP-GUARDRAIL-SOURCE-BOUNDARY`.
They record bounded continuation/source-priority cases where user-provided goal
context, prior-session summary, memory lookup, repo docs, and current checker
output had to be normalized before making implementation or status claims. They
record only source categories, boundary decisions, and checker refs. They do not
store raw prompt bodies, transcripts, full command output, or external payload
content. The gap reached the 2/2 upgrade-discussion target, but its current
upgrade decision is `keep-advisory` until broader PRD, issue, web, Slack, or
pasted-source diversity is observed.

## Current Control Matrix Sample

The third and fifth accepted records cover `GAP-SEC-CONTROL-MATRIX-BURNIN` by
mapping accepted source-boundary evidence to `AC-01` in the agentic control
matrix. They record the control id, evidence refs, owner decision, and upgrade
boundary only. They prove two bounded control-matrix mappings and restraint
against premature blocking upgrade. The gap reached the 2/2 upgrade-discussion
target, but its current upgrade decision is `keep-advisory` until broader
external-source and cross-control diversity is observed.

## Collection Queue

Use `scripts/plan_harness_sample_collection.py` to see the next real-sample
capture queue. The planner reads the current gap registry and checker counts,
then routes each outstanding gap to a target artifact and target checker command.
It does not create evidence, approve high-impact actions, or downgrade missing
real samples.

Use `--gap-id <GAP-ID> --capture-card` when a real event is happening and the
operator needs a focused checklist. Capture cards expand the target artifact,
target checker command, pending slot status, pending ledger refs, pending review
blockers, ledger action, source type, current evidence, evidence fields, and
boundary text for one gap. The ledger action tells the operator whether the next
real event should fill an existing placeholder, append a new pending row, review
an existing pending row, review a ready gap's upgrade decision, stay in
future-work contract definition, or avoid sample collection because the gap
already has accepted local-only evidence.

Use `--area <AREA>`, `--priority P0|P1|P2|P3`, or `--ledger-action
<ACTION>` to scope the queue when an operator is collecting only one roadmap
area, the next highest-priority sample, or one ledger handling lane. For
example, `--ledger-action fill-existing-placeholder` lists existing placeholder
slots that should be completed from a real event, while `--ledger-action
append-new-pending-slot` lists gaps that still need a new pending row. These
filters only narrow the stdout planning view; they do not change readiness
counts, pending slots, or any ledger outcome.

Accepted local-only evidence appears in inclusive views as
`no-sample-collection`. Use `--include-accepted --ledger-action
no-sample-collection --capture-card` to inspect that routing. The card is a
boundary reminder, not a sample request: it must not produce a sample template,
intake bundle row, or append-new-pending-slot command unless the roadmap status
changes.

Use `--actionable-only --pending-state without-pending --capture-card` to focus
the queue on real-sample gaps that can be acted on now and do not already have
any pending slot. Use `--actionable-only --pending-state
without-review-ready-pending --capture-card` for the capture queue that still
needs real events: it keeps placeholder pending rows in scope and only excludes
gaps with review-ready pending records. Both filters exclude future-work contract
blockers and local-only evidence.

Use `--gap-id <GAP-ID> --sample-template` to emit a stdout-only JSONL draft for
the target ledger shape. Templates always use `outcome: pending`, keep TBD
placeholders, and must be reviewed against a real event before appending to a
ledger or counting as accepted evidence. CLI-generated templates default
`sampled_at` to the current local date; pass `--sampled-at YYYY-MM-DD` when a
deterministic draft date is needed for review or tests. Dedicated-ledger
templates also include an explicit `gap_id`; legacy rows without `gap_id` remain
mapped by ledger default, while `scripts/check_harness_pending_samples.py`
rejects a dedicated ledger row whose explicit `gap_id` points at a different
roadmap gap.

Future-work gaps are the exception: while their contract status remains
`needs-adr`, `--sample-template` emits a `harness-future-work-contract/v1`
precondition draft with `sample_collection_allowed: false` instead of sample
evidence. The planner's target checker command routes those drafts to
`scripts/check_harness_future_work_contracts.py`. That draft can only define the
ADR/contract boundary; it must not be counted as collected evidence.

Run `scripts/check_harness_sample_templates.py` after changing template routing
or ledger checker schemas. Add the same `--area`, `--priority`,
`--ledger-action`, `--actionable-only`, and `--pending-state` filters used by
the planner or intake bundle when validating a focused draft set. Use
`without-review-ready-pending` for gaps that still need real event capture, and
use `without-pending` only when the question is strictly whether a gap has any
pending ledger row. The checker validates generated pending templates against
the target checkers and catches drift without writing evidence. It also reports
draft review-state counts and per-template blockers in JSON so a passing schema
audit is not mistaken for review-ready sample evidence.

Use `scripts/build_harness_sample_intake_bundle.py` when an operator wants the
same actionable-without-review-ready-pending drafts grouped by target artifact.
The bundle is stdout-only, validates each generated template before display, and
binds entries to the target checker command. It reports the same readiness
source metric and current / target count as the planner so intake reviewers do
not mistake raw accepted ledger rows for the metric that controls upgrade
readiness. It also reports draft `template_review_state` and
`template_review_blockers`, so a schema-valid template is still visibly a
placeholder until real-event fields are replaced.
Pending slot metadata includes review blockers when placeholder rows are not
review-ready yet, so the summary can show exactly which fields still need a real
event. The bundle supports the same `--area`, `--priority`, `--gap-id`, `--ledger-action`, and
`--pending-state` focus filters for manual review and CI summaries, and reports
ledger action counts so placeholder fills are not confused with new pending-row
appends. It does not write ledgers, accept samples, approve future-work
sampling, or count templates as burn-in evidence.

Use `scripts/check_harness_pending_samples.py --review-cards` when pending slots
already exist and need review. Review cards bind each pending line to its target
checker, evidence class, review state, readiness metric, current / target count,
review blockers, and boundary note. The pending audit also splits accepted
records by evidence class and marks pending rows as `review-ready` or
`placeholder`, so synthetic regression, local replay, local-only evidence, and
placeholder rows are not mistaken for accepted real burn-in. They are read-only
and do not change `outcome`. Its `actionable without review-ready pending` count
is the audit-side counterpart to the intake bundle queue: placeholder rows stay
in scope until a real event fills the listed blocker fields and makes them
review-ready, or a reviewer rejects them.

The pending audit JSON also exposes `queued_readiness_metrics_by_gap` and
`accepted_real_readiness_metric_deltas`. Use those fields, or the readiness
audit itself, when a checker-specific source metric differs from raw ledger
`accepted_real_by_gap`. For example, Stage Checkpoint currently has accepted
real ledger rows from the harness-hardening thread, but its readiness metric is
still `accepted cross-task resume samples: 0/2`. The capture-focus cards show
the same `Metric` and `Current / target` values so a focused handoff does not
mistake ledger-row presence for upgrade readiness.

Use `--gap-id <GAP-ID> --review-cards` for a focused pending review card after a
single-gap capture card identifies the target slot. Use `--review-state
review-ready --review-cards` to list only pending rows that appear ready for
human review; if nothing matches, the command prints an explicit empty-state
message so an empty card list is not mistaken for accepted or missing evidence.
The pending audit JSON and text report also group queued and actionable gaps by
ledger action, so the audit can show which gaps need an existing placeholder
filled versus a new pending row appended without re-running the planner.
It also emits `next_collection_lane_commands`: a read-only command bundle per
active ledger-action lane. The default audit currently points placeholder fills
to the focused planner, intake summary, and placeholder review cards; new
pending-row appends to the focused planner and intake summary; and, when
future-work gaps are included, contract preconditions to the future-work planner
view and contract checker. Local-only accepted gaps remain visible in
`no-sample-collection` counts, but do not produce next collection lane commands.
These commands are routing hints only; they do not write ledgers or accept
samples.
