# Standard Tool Contracts

This directory defines the repo-local standard contract registry for harness tools and future MCP-like tools.

The registry is intentionally small, dependency-free, and readable by hooks, CI, and agents. It describes what a tool is allowed to do before automation decides whether it may run unattended, needs a dry run, or requires a human confirmation.

## Registry Files

- `contracts.json`: canonical machine-readable registry.
- `scripts/check_tool_contracts.py`: stdlib-only validator for local use, hooks, and CI.

## Contract Fields

Each contract in `contracts.json` must include:

- `name`: unique stable identifier. Use lowercase letters, numbers, dots, underscores, or hyphens.
- `purpose`: short human-readable reason the tool exists.
- `path`: repo-relative path to the tool entrypoint.
- `command`: default safe invocation from the repo root.
- `inputs`: list of expected input classes, such as repository files, git state, runtime observations, or GitHub API state.
- `outputs`: list of expected output classes, such as stdout report, JSON report, markdown draft, or process exit code.
- `side_effects`: list of side-effect classes from the enum below.
- `permissions`: list of required permissions or preconditions. Use plain strings such as `read-repo`, `write-runtime`, `github-read`, or `human-confirmation-required`.
- `timeout_seconds`: expected upper bound for normal automation. Must be between 1 and 3600.
- `destructive`: `true` only when the default command can delete, overwrite, close, publish, push, merge, or otherwise destroy state.
- `externally_visible`: `true` when the default command can create externally visible effects outside the local machine.
- `automation_mode`: highest unattended mode allowed for the default command.
- `verification_commands`: commands that validate the contract or the tool's normal safe path.

Optional fields are allowed for extra explanation. Current registry entries use:

- `dangerous_flags`: flags that change the default safe invocation into a destructive or externally visible action.
- `notes`: short caveats for agents and reviewers.

## Side-Effect Classes

Allowed `side_effects` values:

- `none`: no repo, runtime, network, browser, git, or GitHub side effect beyond stdout/stderr and exit code.
- `read_repo`: reads repository files.
- `read_runtime`: reads `.codex/runtime/*`.
- `write_runtime`: writes `.codex/runtime/*` or local runtime drafts.
- `write_governance`: writes canonical `docs/ai/*` or `docs/requirements/*`.
- `write_worktree`: writes non-runtime files in the working tree.
- `network_read`: reads from network or package registries.
- `network_write`: writes to a network service.
- `launch_local_server`: starts a local server or listener.
- `browser_automation`: opens or drives a browser.
- `git_read`: reads local or remote git state.
- `git_write`: changes local or remote git state.
- `github_read`: reads GitHub state through `gh` or API.
- `github_write`: writes GitHub state through `gh` or API.

Contracts should describe the default command, not every possible CLI flag. If a normally safe audit command has dangerous flags, list them in `dangerous_flags` and keep `destructive` / `externally_visible` set to the default invocation.

## Automation Modes

Allowed `automation_mode` values:

- `hook`: safe for lifecycle hooks when its timeout is acceptable.
- `ci`: safe for CI or scheduled verification.
- `dry_run`: safe only when invoked in report-only or no-write mode.
- `assistive`: safe for an agent to run during local development after task relevance is established.
- `manual`: should be run manually or with explicit operator intent.
- `human_confirmed`: requires explicit human confirmation before execution.

Destructive default commands must use `human_confirmed` and include `human-confirmation-required` in `permissions`. Externally visible default commands may not use `hook`, `ci`, or `assistive`; use `manual` or `human_confirmed`.

## Hook And CI Usage

Hooks and CI should validate the registry before relying on it:

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py
```

Suggested policy:

1. Load `contracts.json`.
2. Select tools whose `automation_mode` is allowed by the current runner.
3. Reject any default command marked `destructive` unless the run has explicit human confirmation.
4. Reject externally visible default commands in hooks and unattended CI.
5. Enforce the declared `timeout_seconds` in the caller.
6. Run the listed `verification_commands` when a tool contract or tool implementation changes.

The validator does not execute registered tools. It checks that the registry is structurally safe enough for a hook, CI job, or agent to make the next decision.

The registry should also include validators that are added by this standard. That keeps the standard checks themselves visible to future hook, CI, and MCP-like automation decisions.

The P0 linter layer is represented as ordinary contracts too: `ruff_python_linter` for Python harness linting and `git_diff_whitespace_check` for whitespace errors in the changed diff.

The local eval and trace adapter layer is also represented as ordinary contracts:

- `run_agent_eval_dataset` records the safe `--dry-run` invocation for CI and review routing. Executing eval checks without `--dry-run` remains an explicit local action.
- `export_agent_trace_local` records the local JSON adapter path. It does not perform network export.
- `export_agent_trace_otlp_pilot` records the OTLP HTTP JSON pilot path. Its default command is no-network; `--send` requires an explicit `--endpoint` and produces `network_exported=true` plus HTTP status evidence.
- `collect_harness_sample_gaps` records the static sample-gap collector used to target future real-world security, guardrail, and workflow evidence.

## Stop Trace Producer Contract

`stop_runtime_observation` is registered as a hook-safe local runtime writer. Its default command may append sanitized Stop observations and local `agent-trace/v1` JSONL under `.codex/runtime/observations/`, so the contract declares `write_runtime` and `write-runtime`.

The contract is deliberately local-only. It does not claim OpenTelemetry, OpenAI, or any remote trace exporter integration; those remain future work that would need a separate contract and validation path.
