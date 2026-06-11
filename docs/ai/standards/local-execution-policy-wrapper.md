# Local Execution Policy Wrapper

Updated: 2026-06-07
Status: advisory local wrapper

## Purpose

`scripts/run_sandboxed_command.py` is an opt-in local execution policy wrapper for commands that benefit from a tighter harness boundary.

It is deliberately named as a policy wrapper, not a native sandbox. It provides:

- argv-only execution after `--`
- `shell=False`
- repo-root working directory
- reduced environment allowlist
- timeout with exit code `124`
- bounded raw stdout / stderr / combined artifacts under `.codex/runtime/tool-outputs/`
- metadata that records `native_sandbox=false`
- stdout report line that records `native sandbox: false`
- preflight-risk refusal for destructive, external-send, externally visible, or sensitive-output findings unless a human confirmation reference is supplied

## Boundary

This wrapper does not:

- create an OS-native sandbox
- isolate subprocesses beyond the local argv command boundary
- make a command safe when a human confirmation is missing
- prove OpenAI sandbox, MCP, A2A, hosted runner, or cloud-agent execution support
- replace repository hooks, CI checks, or explicit user confirmation for high-impact actions

## Validation

Run:

```bash
.codex/hooks/run_with_repo_python.sh scripts/run_sandboxed_command.py -- python3 --version
python3 -m unittest tests.test_execution_sandbox_wrapper
python3 tests/test_pre_tool_use_preflight.py
```

The wrapper is assistive. It can preserve bounded local evidence, but it does not upgrade any check level by itself.

External sandbox projects are useful comparison targets, but this wrapper only
upgrades local policy-boundary visibility. It remains outside any native
sandbox, hosted runner, or cloud-agent claim.
