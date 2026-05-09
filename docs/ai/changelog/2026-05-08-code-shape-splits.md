# 2026-05-08 Code Shape Splits

更新时间：2026-05-08
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `scripts/bootstrap_plan_renderer.py`，保持 `bootstrap_harness.render_plan()` 入口不变。
- 新增 `.codex/hooks/runtime_traceability_catalog.py`，拆出 runtime traceability catalog / path helper。
- 新增 `scripts/ai_governance_traceability.py`，拆出 governance traceability catalog 和 alignment 校验。

## 修复问题

- 消除 `bootstrap_harness.py::render_plan` code-shape warning。
- 消除 `.codex/hooks/runtime_traceability.py` 文件长度 warning。
- 消除 `check_ai_governance.py` 中 `load_traceability_catalog` 与 `validate_requirements_traceability_alignment` function warning。

## 行为变化

- 无语义变化；CLI 入口、检查范围和输出口径保持不变。

## 破坏性变更

- 无

## 验证范围

- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `git diff --check`

## 关联文档

- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
