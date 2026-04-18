# Harness Trace Console

Repo-native static console that reads shared governance truth directly from:

- `docs/ai/working-context.md`
- `docs/ai/status/stage-00-runtime-harness-foundation.md`
- `docs/requirements/traceability-matrix.md`

## Run

Serve the repository root with any static server, for example:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/apps/harness-trace-console/
```

## Features

- Summary cards for current stage, completed trace rows, smoke-backed rows, and workstream count
- Working-context queue and risk view
- Interactive filtering by stage, workstream, status, and search
- Detail panel for selected requirement row

## Smoke Check

Run the repo-level smoke flow:

```bash
python3 scripts/harness_trace_console_smoke.py
```

The smoke script:

- starts a temporary static server
- opens `apps/harness-trace-console/?smoke=1` with `playwright-cli`
- uses `window.__HARNESS_TRACE_CONSOLE_TEST__` to verify load, filtering, search, and detail selection
- removes temporary `.playwright-cli/` artifacts before exit
