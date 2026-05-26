# Runtime Token Budget

Use this reference when a task changes runtime transcript handling, long-session recovery,
tool-output strategy, prompt/cache budget policy, or `scripts/check_runtime_token_budget.py`.

## Why This Exists

Static context budget checks protect always-on docs and known task packets, but they do not
detect runtime blowups caused by long sessions, repeated validation loops, broad shell output,
large screenshots, full diffs, or cache misses.

Primary evidence:

- OpenAI describes Codex as an agent loop where the model issues function calls, tools return
  outputs, and those outputs are appended to the transcript before the next model turn. This
  makes oversized tool output a direct prompt-growth risk.
  Source: https://openai.com/index/unrolling-the-codex-agent-loop/
- OpenAI prompt caching exposes `cached_input_tokens`, so a low cache-hit turn with a high
  `input_tokens` count is observable evidence that a large context was reprocessed.
  Source: https://openai.com/index/api-prompt-caching/
- Anthropic's tool-context guidance treats tool-result growth as a first-class context-management
  concern and documents clearing or trimming stale tool results to control context pressure.
  Source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/manage-tool-context
- Anthropic's context engineering guidance says agents need explicit strategies for curating
  evolving context state, and calls out context rot: as tokens grow, recall quality degrades.
  Source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Claude Code documents a similar operational policy: context contains command outputs; when
  context fills, older tool outputs are cleared first, and subagents isolate intermediate noise.
  Source: https://code.claude.com/docs/en/how-claude-code-works
- LangChain's context editing middleware mirrors Anthropic-style tool result clearing by pruning
  older tool results after configured token thresholds.
  Source: https://reference.langchain.com/javascript/functions/langchain.index.contextEditingMiddleware.html
- `Lost in the Middle` shows that long-context models can perform worse when relevant
  information is buried in the middle of long inputs; larger windows do not remove the need for
  input reduction. Source: https://arxiv.org/abs/2307.03172
- `RULER` evaluates effective context length and reinforces that nominal context size and
  reliable long-context use are different properties. Source: https://arxiv.org/abs/2404.06654

## Policy

- Treat runtime transcripts as evidence, not canonical shared truth.
- Default shell and diagnostic commands should keep `max_output_tokens` at or below `4000` unless
  the task explicitly needs a larger bounded excerpt.
- PreToolUse warnings should be catalog-driven and name bounded alternatives, not just warn.
  The current starter-safe catalog covers broad search/listing (`rg`, recursive `grep`, `find`,
  `tree`, `ls -R`), logs (`docker logs`, `kubectl logs`, `journalctl`), full diffs, secret/env
  exposure (`env`, `.env`, `kubectl get secret`, cloud auth/env commands), project search tools
  (`fd`, `ag`, `ack`, `gh api --paginate`), and long-running test/build/install output.
- Avoid broad `rg`, full `ps`, full logs, full diffs, full `SKILL.md`, complete screenshots/base64,
  or complete transcript/runtime JSONL in prompt context. Filter first, write large raw output to
  `.codex/runtime/tool-outputs/<timestamp>-<slug>.log`, then summarize the bounded evidence.
- Use `scripts/capture_tool_output.py --slug <name> -- <command>` when a high-risk command needs
  full raw output preserved but only a bounded summary should enter the transcript. The wrapper
  writes `.log` and `.meta.json` artifacts, returns the wrapped command exit code, and prints only
  the bounded summary.
- Use `scripts/summarize_tool_output.py --input <artifact>` to bring only the artifact path,
  size, estimated tokens, error matches, tail, and selected line windows into the transcript.
  The summarizer streams the raw artifact, bounds each emitted line with `--max-line-chars`
  (default `800`), bounds total output with `--max-output-chars` (default `12000`), limits
  `--around` windows with `--max-windows` (default `3`), and marks truncation instead of pasting
  full base64/JSON payloads.
- When the first summary is not enough for debugging, re-run the summary with `--around <line>`
  instead of pasting the whole raw artifact.
- Checkpoint and start a fresh session when a task becomes a long validation loop, typically after
  `60-90` minutes, after several `task_complete` cycles, or after context approaches `120k`.
- Run `scripts/check_runtime_token_budget.py --transcript <rollout-jsonl>` when diagnosing quota
  drops, long-session slowdowns, context-window pressure, cache-miss spikes, or unusually large
  tool output.
- The `Stop` hook `stop_runtime_token_pressure.py` runs the same transcript audit when the hook
  payload includes the current transcript path. It is warning-only: when pressure is found, it
  writes a deterministic runtime-only compression draft under `.codex/runtime/sessions/` and
  returns only the draft path plus a recovery reminder in `additionalContext`.

## Feasible Controls

Use these controls in order; each is implementable with repo-local scripts and hooks.

1. Prefer bounded commands:
   - `rg -n -m 20 "pattern" path/`
   - `rg -l "pattern" path/`
   - `grep -R -n -m 20 "pattern" path/`
   - `git diff --stat`
   - `git diff --name-only`
   - `docker logs --tail 200 <container>`
   - `kubectl logs --tail=200 <pod>`
   - `journalctl -n 200 --no-pager`
   - `sed -n '1,160p' path`
2. For raw output that may exceed `5000` estimated tokens, run:
   `python3 scripts/capture_tool_output.py --slug <name> -- <command>`.
   This writes `.codex/runtime/tool-outputs/<timestamp>-<slug>.log`, records metadata, and
   summarizes the artifact without losing the raw evidence.
3. For long sessions or repeated validation loops, write a checkpoint / handoff, then start a
   fresh session instead of repeatedly compacting the same noisy transcript.
4. Use subagents for noisy exploration only when their final result can be a bounded summary.
   This protects the parent context but does not reduce total token consumption.
5. Keep this warning-only until enough accepted real samples justify blocking or command
   rewriting. A warning can recommend a safer command; it must not silently change user intent.

## Thresholds

Configured in `.codex/harness.toml` under `[runtime_token_budget]`:

- `tool_output_token_budget`: single tool output warning threshold.
- `last_input_token_budget`: single-turn input warning threshold.
- `fresh_input_token_budget`: single-turn `input_tokens - cached_input_tokens` warning threshold.
- `task_complete_budget`: session slice count warning threshold.
- `token_snapshot_budget`: token-count event warning threshold.
- `session_minutes_budget`: elapsed runtime warning threshold.

These thresholds are `blocking-candidate`: real transcript audits should be reviewed first. CI
only runs the no-transcript wiring path; the Stop hook uses the thresholds only to warn the next
turn when the current transcript already shows runtime pressure.

## Verification

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_runtime_token_budget.py
.codex/hooks/run_with_repo_python.sh scripts/check_runtime_token_budget.py --transcript <rollout-jsonl>
python3 scripts/summarize_tool_output.py --input .codex/runtime/tool-outputs/<artifact>.log
python3 scripts/summarize_tool_output.py --input .codex/runtime/tool-outputs/<artifact>.log --around <line> --max-line-chars 800 --max-output-chars 12000
python3 scripts/capture_tool_output.py --slug smoke -- python3 -c "print('ok')"
.codex/hooks/run_with_repo_python.sh scripts/build_runtime_compression_draft.py --transcript <rollout-jsonl>
python3 -m unittest tests.test_runtime_token_budget
python3 tests/test_stop_runtime_token_pressure.py
python3 tests/test_summarize_tool_output.py
python3 tests/test_capture_tool_output.py
python3 tests/test_runtime_compression_draft.py
```
