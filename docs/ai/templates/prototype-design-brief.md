# Prototype Design Brief

更新时间：YYYY-MM-DD
状态：draft projection
文档定位：design projection surface

## Project Metadata

- Project: `[PROJECT_NAME]`
- Product domain: `[PRODUCT_DOMAIN]`
- Current stage: `[STAGE-XX]`
- Target prototype use: design review / visual exploration / implementation handoff
- Design consumer: `未绑定` until a downstream prototype or design tool is selected
- Canonical truth source: requirements, workstreams, ADRs, status, handoff, and traceability docs
- Projection rule: this brief summarizes design input; it does not replace canonical requirements or ADRs

## Source Truth

List only reviewed and canonical sources. For an active checked brief, requirement, workstream, ADR, and traceability inputs must be bound.

- Requirement IDs: `[REQ-XXX]`
- Workstream IDs: `[WS-XX]`
- ADR IDs: `[ADR-XXX]`
- Traceability source: `docs/requirements/traceability-matrix.md`
- Requirement docs:
  - `[REQ-XXX title](../../requirements/normalized/REQ-XXX-example.md)`
- Workstream docs:
  - `[WS-XX title](../../requirements/workstreams/WS-XX-example.md)`
- Decision docs:
  - `[ADR-XXX title](../adr/ADR-XXX-example.md)`

## Product Scope

- Product goal:
- Primary user:
- Secondary user:
- Buyer / approver:
- Core job:
- Core path:
- Success signal:
- Current implementation boundary:

## Target Surfaces

Declare every surface explicitly. Public pages, app screens, admin/config screens, and developer/debug surfaces should not share one visual grammar by accident.

| Surface | Routes or screens | User question | Shell | Density | Notes |
| --- | --- | --- | --- | --- | --- |
| Buyer website | `/` | Why should I trust or buy this? | public nav | medium | optional |
| Product tour | `/product/*` | How does this capability work? | public nav + tour sections | medium-high | optional |
| Operator app | `/app/*` | What do I need to do now? | logged-in app shell | high | required when product has real workflow |
| Admin/config | `/app/settings/*` | How do I configure or govern this? | logged-in app shell | high | optional |
| Developer/debug | drawer or advanced tab | What happened technically? | secondary surface | dense | optional |

## Page Map

| Page | Surface | Purpose | Primary action | Required modules | Critical states |
| --- | --- | --- | --- | --- | --- |
| `[page_id]` | `[surface]` | `[purpose]` | `[action]` | `[modules]` | `[states]` |

## Critical States

Cover trust, permission, payment/quota, review, blocked, deletion, model/service failure, and empty states where relevant.

| State | Where | Trigger | User message | Recovery action | Business impact |
| --- | --- | --- | --- | --- | --- |
| `[state]` | `[page/flow]` | `[trigger]` | `[message]` | `[recovery]` | `[impact]` |

## Boundary Rules

- Scope rule:
- Permission rule:
- Source / provenance rule:
- Candidate / review rule:
- Deletion / opt-out rule:
- Fail-closed rule:
- Display-safe summary rule:
- Prompt, secret, or raw-data leakage bans:

## Non-Goals

- No production implementation claims from prototype-only screens.
- No secrets, full prompts, raw private input, or raw runtime artifacts in prototype artifacts.
- No unbound requirement, workstream, or ADR inputs in checked active briefs.

## Prototype Handoff

This section is for downstream prototype generation, design review, or implementation handoff. Do not name a specific local tool unless the project has adopted it as a canonical consumer.

- Handoff intent:
- Expected downstream consumer: `未绑定`
- Required handoff artifacts:
  - `provenance.md`
  - `normalized-prd.md`
  - `surface-identity.md`
  - `page-map.md`
  - `state-matrix.md`
  - `constraints.md`
  - `artifact-review.md`
- Artifact review target:
- Must preserve:
- Must not change:

## Review And Sync Rules

Update this brief when any of these change:

- Requirement or workstream scope.
- ADR boundary.
- User, role, permission, payment, quota, memory, deletion, review, or source rules.
- Target surfaces, pages, or critical states.
- Prototype artifact review returns `partial pass` or `fail`.

Run:

```bash
# Enable [prototype_design_brief] in .codex/harness.toml before making this a blocking governance check.
.codex/hooks/run_with_repo_python.sh scripts/check_prototype_design_brief.py
```

If an artifact review package or static prototype route exists, also enable `[prototype_design_brief].artifact_review_enabled = true` and configure `artifact_dir`, `prototype_page_path`, `prototype_route`, `fixture_paths`, and `required_states`.
