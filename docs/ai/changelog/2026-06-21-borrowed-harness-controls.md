# Borrowed Harness Controls

更新时间：2026-06-21
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `[quality_supervisor]` 配置块，默认 `enabled = false`，用于承载从 `demo_txt_t_proto` 吸收的只读质量监督子代理协议。
- 新增 `scripts/check_quality_supervisor_protocol.py`，disabled 时只审计配置可解析；enabled 时要求 AGENTS、标准、registry 和 index 的协议闭环。
- 新增 `scripts/start_async_verification.py`，提供 `active-browser-smoke` 与 `active-static-contracts` 本地 preset，并把 status/log 写入 `.codex/runtime/async-verification/`。
- `check_context_budget.py` 新增默认面最长行报告；`context_budget_warnings.py` 对超出 line-density budget 的默认面长行发出 blocking finding。
- `ai_governance_changed_paths.py` 将 `.codex/runtime/**` 下非 README / `_template.md` / `.gitkeep` 文件统一视为 generated runtime artifact，并允许 staged deletion 用于索引清理。

## 修复问题

- 修复 runtime staging gate 只覆盖 sessions / observations / tool-outputs 的漏网问题，避免新增 runtime 子目录绕过治理。

## 行为变化

- `check_ai_governance.py` 现在会运行 quality supervisor protocol checker；当前配置 disabled，因此不会要求或宣称 subagent 启动。
- `check_change_triggered_followups.py` 会对 quality supervisor protocol 和 async verification 变更提示专项 follow-up。
- `docs/ai/verification-minimums.md` 新增 async verification 路由：未检查 `status.json` 与日志前不得宣称通过。
- `.codex/runtime/**` 现在默认 ignore；只放行目录、README、`_template.md` 和 `.gitkeep`。
- `check_ai_governance.py` 会阻断 staged generated runtime artifacts，但允许 `git rm --cached` staged deletion 完成历史索引清理。
- `check_change_triggered_followups.py` 将 default-context-budget 路由标为 blocking，以匹配当前 governance strict gate。

## 破坏性变更

- 新的 generated runtime artifact staging 会被治理门禁阻断。
- 默认面超长单行会被 context budget 阻断。除此之外，新增机制不创建 hosted eval、CI agent workflow、scheduler、MCP/A2A 或自动 subagent runtime。

## 验证范围

- `python3 tests/test_quality_supervisor_protocol.py`
- `python3 tests/test_async_verification.py`
- `python3 tests/test_context_budget.py`
- `python3 tests/test_ai_governance_changed_paths.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_quality_supervisor_protocol.py`
- `.codex/hooks/run_with_repo_python.sh scripts/start_async_verification.py --list`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `git diff --check`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Quality Supervisor Protocol](../standards/quality-supervisor-protocol.md)
- [Verification Minimums](../verification-minimums.md)
