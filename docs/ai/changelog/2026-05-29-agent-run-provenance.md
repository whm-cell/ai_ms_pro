# Agent Run Provenance Local Standard

更新时间：2026-05-29
阶段或版本：stage-00
状态：已完成

## 新增功能

- 新增 `docs/ai/standards/agent-run-provenance.md` 和 `agent-run-provenance-sample.jsonl`，定义 local-first `agent-run-provenance/v1` 记录。
- 新增 `scripts/check_agent_run_provenance.py` 与 `tests/test_agent_run_provenance.py`，校验 REQ/WS 绑定或显式 unbound、authority、canonical write、changed files、tool contracts、validation evidence 和 claim boundaries。
- 将该 checker 纳入 tool contracts、check registry、change-triggered follow-up、agentic standards reference、control matrix 和索引。

## 修复问题

- 无。

## 行为变化

- 不把 GitHub plan 升级、branch protection / rulesets 强制化、GitHub Copilot cloud agent task、hosted trace、MCP/A2A、OpenAI sandbox 或外部 OTLP 互通作为当前实现目标。
- `.codex/runtime/*` 仍是本地恢复材料，不能作为 canonical provenance evidence。
- GitHub Actions / PR / security artifact 可作为 evidence，不等同远端 enforcement。

## 文档同步

- `index`、`working-context`、stage status、check registry、agentic control matrix、tool contracts 和 remote merge gates 已同步 local-first provenance 边界。

## 破坏性变更

- 无。

## 验证范围

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_agent_run_provenance.py
python3 tests/test_agent_run_provenance.py
.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py
python3 tests/test_change_triggered_followups.py
```
