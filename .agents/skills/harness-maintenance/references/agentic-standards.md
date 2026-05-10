# Agentic Standards Maintenance

Use this reference when changing repo-local agentic standards: trace schema, trace producer/exporter, eval dataset/runner, tool contracts, sample gap collection, or agentic security control mapping.

## Surfaces

- Trace contract: `docs/ai/standards/agent-trace-schema.md`, schema/sample JSON, `scripts/check_agent_trace_schema.py`.
- Trace export: `scripts/export_agent_trace.py`; default local/no-network export, explicit `--send --endpoint` only for OTLP HTTP JSON pilot evidence.
- Eval: `docs/ai/evals/*`, `scripts/check_agent_eval_dataset.py`, `scripts/run_agent_eval_dataset.py`, and trace evidence helpers.
- Tool contracts: `docs/ai/tool-contracts/contracts.json`, `scripts/check_tool_contracts.py`.
- Security controls: `docs/ai/security/agentic-control-matrix.md` plus security triage docs.
- Sample gaps: `scripts/collect_harness_sample_gaps.py` and `--使用细节/真实场景覆盖缺口待确认.md`.

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
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/collect_harness_sample_gaps.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
