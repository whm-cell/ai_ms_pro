# Planner Empty Scope Handling

- Date: 2026-05-24
- Scope: harness sample collection planner
- Status: landed

## 新增功能

- `scripts/harness_sample_collection_render.py` 现在为 markdown / capture-card 空过滤范围输出显式 no-match 信息。
- `tests/test_plan_harness_sample_collection.py` 新增空 capture-card 范围与空 JSONL template 范围的 CLI 回归。

## 修复问题

- 修复 `plan_harness_sample_collection.py` 在合法空过滤范围中只输出标题并返回 exit 1 的问题。
- 防止当前没有某个 lane（例如没有 review-ready pending slot）时，被误读成工具失败、已接受证据或缺少输出。

## 行为变化

- 空过滤范围现在成功退出。
- markdown / capture-card 空范围会说明“没有匹配条目”，并强调这不接受、不拒绝、也不证明 gap 完成。
- JSON 空范围仍输出 `[]`。
- `--sample-template` 空范围仍保持 stdout 为空，避免污染 JSONL 管道。

## 破坏性变更

- 无。该变更只影响空过滤范围的 stdout/exit-code 语义；非空队列、JSON schema、样本模板内容和 ledger 均不变。

## 验证范围

- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-DOES-NOT-EXIST --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-DOES-NOT-EXIST --sample-template`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-DOES-NOT-EXIST --json`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
