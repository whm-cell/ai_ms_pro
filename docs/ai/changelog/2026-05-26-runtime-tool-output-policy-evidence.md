# Runtime Tool Output Policy Evidence

更新时间：2026-05-26
阶段或版本：stage-00
状态：已确认

## 新增功能

- PreToolUse preflight 新增 risk catalog，并对 likely large-output command 增加 bounded alternatives，例如 `rg -n -m 20`、`rg -l`、`git diff --stat`、`git diff --name-only`、artifact redirect 和 `summarize_tool_output.py`。
- Risk catalog 现在覆盖 broad search/listing、logs、secret/env exposure、long-running test/build/install、full diff/show 和外部可见/破坏性动作。
- `$harness-maintenance` 的 runtime token budget reference 增加外部理证和可行控制清单。
- `new_pro_standard` 同步 runtime token budget reference，避免 starter 只带 hook 行为而缺少维护理由。

## 修复问题

- 之前 PreToolUse 只提示部分大输出风险，没有给出可直接执行的低 token 替代命令，也没有把真实项目里的 logs、secret/env、verbose tests/builds 纳入同一个 catalog。
- 之前 starter harness-maintenance skill 没有 runtime token pressure reference。

## 行为变化

- 大输出风险仍是 warning-only；hook 不静默改写用户命令，也不阻断工具调用。
- 后续真实样本达到足够数量前，不把该策略升级为 blocking 或 auto-rewrite。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_pre_tool_use_preflight.py`
- `new_pro_standard/tests/test_pre_tool_use_preflight.py`
- `ruff check .codex/hooks scripts tests`
- root / starter PreToolUse hook smoke

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [runtime-token-budget.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.agents/skills/harness-maintenance/references/runtime-token-budget.md)
- [new_pro_standard runtime-token-budget.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/.agents/skills/harness-maintenance/references/runtime-token-budget.md)
