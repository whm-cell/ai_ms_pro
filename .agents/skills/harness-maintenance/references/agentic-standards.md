# Agentic Standards Maintenance

Use this reference when changing repo-local agentic standards: trace schema, trace producer/exporter, eval dataset/runner, tool contracts, sample gap collection, or agentic security control mapping.

## Surfaces

- Trace contract: `docs/ai/standards/agent-trace-schema.md`, schema/sample JSON, `scripts/check_agent_trace_schema.py`.
- Trace export: `scripts/export_agent_trace.py`; default local/no-network export, explicit `--send --endpoint` only for OTLP HTTP JSON pilot evidence.
- Eval: `docs/ai/evals/*`, `scripts/check_agent_eval_dataset.py`, `scripts/run_agent_eval_dataset.py`, and trace evidence helpers.
- Agent-run provenance: `docs/ai/standards/agent-run-provenance.md`, `docs/ai/standards/agent-run-provenance-sample.jsonl`, and `scripts/check_agent_run_provenance.py`.
- CI agent contract: `docs/ai/standards/ci-agent-contract.md`, sample JSONL, and `scripts/check_ci_agent_contract.py`; advisory only, no real CI agent workflow.
- Local execution policy wrapper: `docs/ai/standards/local-execution-policy-wrapper.md` and `scripts/run_sandboxed_command.py`; assistive wrapper only, `native_sandbox=false`.
- External harness decisions: `docs/ai/standards/external-harness-decisions.md`, decision JSONL, and `scripts/check_external_harness_decisions.py`; records source-backed remote trace, external eval/sandbox, MCP/A2A, and CI agent workflow choices plus evidence-backed default permission for bounded local/no-effect improvements without creating external effects.
- Agent productization readiness: `docs/ai/standards/agent-productization-readiness.md`, model JSON, assessment JSONL, and `scripts/check_agent_productization_readiness.py`; review-required gap radar for product-agent runtime, tools, memory, HITL, durability, tracing, eval, sandbox, handoff, structured output, cost, and ops without claiming a product agent platform.
- Bounded loop triage: `docs/ai/standards/bounded-loop-triage.md` and `scripts/summarize_loop_triage.py`; advisory no-write loop layer that ranks current next-action candidates without executing them, writing ledgers, accepting samples, upgrading blocking, or claiming scheduler/runtime capability.
- Mock data boundary: `docs/ai/standards/mock-data-boundary.md` and `scripts/check_mock_data_boundary.py`; review-required frontend/runtime mock data boundary that reports oversized inline mock data, denied mock/fixture runtime imports, missing scenario manifests, and unseeded fixture factories without auto-cleanup or blocking by default.
- Tool contracts: `docs/ai/tool-contracts/contracts.json`, `scripts/check_tool_contracts.py`.
- Security controls: `docs/ai/security/agentic-control-matrix.md` plus security triage docs.
- Sample gaps: `scripts/collect_harness_sample_gaps.py`, generic bounded intake `scripts/check_harness_sample_gap_evidence.py`, real-sample queue `scripts/plan_harness_sample_collection.py`, generated-template drift check `scripts/check_harness_sample_templates.py`, grouped intake bundle `scripts/build_harness_sample_intake_bundle.py`, pending sample slot audit `scripts/check_harness_pending_samples.py`, future-work contract precondition check `scripts/check_harness_future_work_contracts.py`, and `--使用细节/真实场景覆盖缺口待确认.md`.

## Rules

- Keep `AGENTS.md`, `docs/ai/index.md`, `working-context`, and status as routing/current-truth surfaces only.
- Put maintenance mechanics, caveats, command selection, and warning interpretation in this skill reference or deterministic scripts.
- Do not claim OpenAI hosted traces/evals, MCP, A2A, or external OTLP collector interop from local schema, local runner, or no-network payload generation.
- Treat runtime trace files as local recovery evidence until the main agent promotes reviewed conclusions into governance docs.
- Keep advisory/security evidence out of blocking status until real samples, owner, false-positive cost, and repair path are recorded.

## Verification

Use `references/verification-commands.md` for the full command matrix. Minimum checks for this surface usually include:

- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_trace_schema.py`
- `.codex/hooks/run_with_repo_python.sh scripts/export_agent_trace.py --input docs/ai/standards/agent-trace-sample.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/export_agent_trace.py --input docs/ai/standards/agent-trace-sample.jsonl --format otlp-http-json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`
- `.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --dry-run`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_run_provenance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ci_agent_contract.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_external_harness_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_productization_readiness.py`
- `.codex/hooks/run_with_repo_python.sh scripts/summarize_loop_triage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_mock_data_boundary.py`
- `.codex/hooks/run_with_repo_python.sh scripts/run_sandboxed_command.py -- python3 --version`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py`
- `.codex/hooks/run_with_repo_python.sh scripts/collect_harness_sample_gaps.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
