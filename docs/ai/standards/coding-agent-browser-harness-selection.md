# Coding Agent And Browser Harness Selection

更新时间：2026-06-16
状态：review-required selection standard

## 定位

本标准把两条外部调研结论转成 repo-local 选择规则：

- 当前编码 agent 对照物不再只看 SWE-agent 主仓库。
- browser / coding harness 不默认优先 MCP；先按任务形态选择 CLI / skills 或 MCP。

它不新增依赖、不创建 MCP / A2A runtime、不创建 CI agent workflow，也不声明
native sandbox、hosted trace / eval 或 verified remote interop。

## Source-Backed Inputs

- SWE-agent 主 README 在 2026-06-16 复核时说明主要开发精力已转向
  `mini-swe-agent`，并建议新用户优先使用 `mini-SWE-agent`。
- Playwright MCP README 在 2026-06-16 复核时说明，coding agent 场景中
  CLI-based workflows exposed as skills 往往更 token-efficient；MCP 仍适合
  需要 persistent state、rich introspection 或 iterative page reasoning 的循环。

这些来源只支持本地选择规则和比较口径，不证明本仓库已具备对应外部运行时。

## Coding Agent Comparator Rule

默认选择：

- 当前轻量 coding-agent 对照物优先使用 `mini-swe-agent`。
- SWE-agent 主仓库保留为历史架构、SWE-bench、trajectory format、tool bundle
  和研究背景参考。

禁止口径：

- 不把 SWE-agent 主仓库写成唯一当前编码 agent benchmark。
- 不把 mini-swe-agent 参考写成 ai_ms_pro 已具备真实 coding-agent runtime。
- 不用外部 README 推导本仓库的 sandbox、cloud execution 或 CI agent 能力已完成。

## Browser Harness Transport Rule

默认选择：

- deterministic browser smoke、CI gate、local static app check、可重复截图/DOM
  检查优先使用 repo script + CLI / skills。
- 需要 persistent browser state、rich accessibility-tree introspection、exploratory
  automation、self-healing tests 或明确 MCP client interop 时，再考虑 MCP。

禁止口径：

- 不把 MCP 当成所有 browser / coding harness 的默认答案。
- 不为 token-heavy 或一次性 smoke 场景引入 MCP runtime。
- 不把 MCP README 或 server config 当作本仓库 MCP / A2A runtime 证明。

## Decision Matrix

| 场景 | 默认选择 | 需要额外决策的情况 |
| --- | --- | --- |
| 当前 coding-agent comparator | `mini-swe-agent` | 如果评估 SWE-agent 主仓库专有 trajectory/tool bundle，再单独说明原因 |
| SWE-bench / 历史研究参考 | SWE-agent 主仓库可用 | 不得把它写成唯一当前实现参考 |
| WS-01 / WS-02 browser smoke | repo-local Playwright CLI scripts | 需要持久页面会话或 MCP client interop 时再提 ADR / contract |
| exploratory browser automation | 先看 CLI / skills 是否足够 | 需要 persistent state 或 rich introspection 时可评估 MCP |
| MCP / A2A runtime | 默认不进入 Stage-00 runtime | 需要 auth、transport、scope、redaction、cost 和 stop boundary 的 ADR |

## Verification

相关变更至少运行：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_external_harness_decisions.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```

如果修改 checker 或 changed-file routing，再运行对应单元测试。
