# 2026-06-16 Mock Data Boundary

## 新增功能

- 新增 `scripts/check_mock_data_boundary.py`、`scripts/mock_data_boundary_lib.py`、`scripts/mock_data_manifest.py` 与 `scripts/mock_data_fixture_checks.py`，按 `[mock_data_boundary]` 扫描前端/runtime 代码中的大型 inline mock、生成式 mock、runtime mock/fixture import、scenario manifest 和 fixture factory seed 边界。
- 新增 `docs/ai/standards/mock-data-boundary.md`，定义 fixture / mock / story / test 与产品 runtime path 的边界。

## 修复问题

- 针对公司项目开发中页面生成超大 mock 数据、后续还要统一迁移的问题，新增 review-required 的早期发现机制，并补充 scenario manifest / deterministic seed 的收敛入口。

## 行为变化

- 默认检查只输出 `REVIEW:`，不阻断；`--strict` 可在后续 burn-in 后作为显式升级路径。
- `.codex/harness.toml` 新增 `[mock_data_boundary]`，集中声明扫描根、fixture path、allowed consumer、manifest path、runtime import denied path、alias prefix 和阈值。
- JSON finding 增加 `suggested_layer`、`suggested_paths` 和 `doc_ref` 字段；文本输出仍保持 `REVIEW: path:line code: message` 形态，并追加建议层级。

## 破坏性变更

- 无。机制不自动删除旧代码、不移动 mock 数据、不改变业务 runtime。

## 验证范围

- `python3 tests/test_mock_data_boundary.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_mock_data_boundary.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_mock_data_boundary.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [Mock Data Boundary](../standards/mock-data-boundary.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
