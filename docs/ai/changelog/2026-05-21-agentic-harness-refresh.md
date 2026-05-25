# 2026-05-21 Agentic Harness Refresh

## 新增功能

- 刷新 external standards crosswalk，纳入 OpenAI Agents SDK sandbox / rehydration、AgentKit eval / trace grading、MCP 2025-11-25、A2A latest、OpenTelemetry GenAI、OWASP Agentic Applications / Skills 和 2026 joint cyber guidance。
- 新增 repo-local workspace sandbox / rehydration manifest 与 `scripts/check_workspace_sandbox.py`，用于校验本地路径、network 默认限制、subagent isolation 规则和外部互通禁止过度声明。
- 扩展 agentic red-team eval 与 sample gaps，覆盖 tool / skill squatting、memory / context poisoning、inter-agent handoff confusion、cascading agents、human confirmation 和 sandbox / rehydration honesty。

## 修复问题

- 修正 `harness-open-items.md` 中“当前 code-shape 检查无 warning”的过期表述，改为记录现有 warning。
- 补齐 external standards crosswalk 对 2026-05-21 最新 agentic / harness 实践的差距描述。

## 行为变化

- Governance workflow 增加 workspace sandbox manifest check。
- Tool contract registry 增加 `check_workspace_sandbox`。
- Check registry 将 workspace sandbox checker 记录为 blocking-candidate；它是本地 contract，不证明 native sandbox provider、OpenAI hosted sandbox、MCP/A2A 或外部 OTLP 互通。
- `collect_harness_sample_gaps.py` 从静态缺口列表升级为附带当前样本 checker 计数的报告；这些计数只反映已登记样本，不自动生成真实样本或升级 blocking。

## 影响范围

- 不改变游戏业务代码。
- 不接入远端 OpenAI eval / trace、MCP server、A2A endpoint 或外部 OTLP collector。
- `.codex/sandbox-manifest.toml` 当前受本地文件沙箱限制未能创建；manifest 放在 `docs/ai/standards/workspace-sandbox-manifest.toml` 作为 repo-local governance artifact。

## 破坏性变更

- 无。新增 checker 进入 CI 后会要求 manifest 保持有效，但不改变现有业务运行方式。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_workspace_sandbox.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`
- `.codex/hooks/run_with_repo_python.sh scripts/collect_harness_sample_gaps.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh tests/test_workspace_sandbox.py`
- `python3 tests/test_harness_sample_gaps.py`
