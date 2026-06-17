# Python Runtime Template Resolution

日期：2026-06-17

## 新增功能

- `scripts/bootstrap_harness.py` 增加父级目录 `.env` / pyenv Python 版本解析，用于创建 repo-local `.codex/.venv`。
- 父级 `.env` 只读取 allowlisted Python selector：`CODEX_HARNESS_PYTHON`、`PYTHON`、`PYTHON3`、`PYTHON_BIN`、`PYTHON_EXECUTABLE`、`CODEX_HARNESS_PYTHON_VERSION`、`PYTHON_VERSION`、`PYENV_VERSION`。
- `new_pro_standard` 同步相同行为与 README 说明，避免 starter 在新项目 full test 或 bootstrap 时意外落到系统 Python 3.9。

## 行为变化

- 新项目 bootstrap 会在 PATH / launcher fallback 前尝试父级 `.env` selector 和 pyenv selected Python。
- starter 自身的 full unittest 验证推荐使用 `pyenv exec python` 或 bootstrap 后的 `.codex/.venv/bin/python`，不再假设裸 `python3` 总是 pyenv。

## 修复问题

- 修复 starter 在某些目录 PATH 顺序下裸 `python3` 解析到 macOS system Python 3.9，导致 `tomllib` / `datetime.UTC` 相关测试失败的验证路径。

## 破坏性变更

- 无。

## 边界

- 不复制父级 `.env`，不读取或输出任意 secret/config value。
- 不提交 `.codex/.venv`。
- 只改变 bootstrap 阶段的 harness Python 选择逻辑；hook runner 仍优先使用 repo-local `.codex/.venv`，不改变业务代码、REQ/WS 或 blocking policy。

## 验证

## 验证范围

```bash
python3 -m unittest tests.test_python_resolution
cd new_pro_standard && python3 -m unittest tests.test_python_resolution
cd new_pro_standard && pyenv exec python -m unittest discover -s tests
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all
```
