# Real Data Activation Gate

日期：2026-06-17

## 新增功能

- 新增 `[data_activation]` 配置，支持 `smoke | shadow-real | real` 三种审计模式。
- 新增 `scripts/check_data_activation.py`，把 smoke/mock 数据退场变成 no-write / review-required 检查。
- 扩展 `mock-data-scenario/v1` 可选字段：`activation_state`、`real_adapter_path`、`activation_evidence_refs`、`retire_when`。

## 行为变化

- `shadow-real` 模式要求 `surface=dev|demo` 的 scenario 标出真实 adapter 与退场条件。
- `real` 模式要求产品 runtime 不再消费 mock/fixture/dev-seeds，并要求 dev/demo scenario retired 且带 bounded evidence refs。
- `surface=test|story|contract-sample` 仍可保留 smoke 数据用于测试、story 和 contract sample。

## 修复问题

- 无。

## 破坏性变更

- 无。

## 边界

- 本机制不自动迁移页面、不删除 fixture、不创建后端 API、不调用真实 provider。
- `real_adapter_path` 只证明 repo 中有真实 adapter/API/provider 绑定点；真实数据质量仍由业务测试、smoke/e2e 或人工 evidence 证明。
- v1 保持 review-required；`--strict` 只能在后续 burn-in 后按项目选择。

## 验证范围

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_data_activation.py
.codex/hooks/run_with_repo_python.sh scripts/check_mock_data_boundary.py
python3 tests/test_data_activation.py
python3 tests/test_mock_data_boundary.py
.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py
.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```

## 关联文档

- [Mock Data Boundary](../standards/mock-data-boundary.md)
- [Check Registry](../check-registry.md)
- [AI 文档入口索引](../index.md)
