# Runtime Tool Outputs

This directory stores local raw tool-output artifacts such as full logs, long diffs, or large
diagnostic command output.

These files are local recovery evidence only. They are not canonical project memory and do not
replace `docs/ai/*` or `docs/requirements/*`.

Use rules:

- write large raw output here before summarizing it into the conversation
- keep transcript content bounded by using `scripts/summarize_tool_output.py`
- use line windows from the raw artifact when debugging needs more context
- do not stage raw output files from this directory
