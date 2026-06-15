# Playwright Smoke npx Resolution

日期：2026-06-15

## 新增功能

- 无；本次为跨平台兼容性修复。

## 修复问题

- 修复 Windows 下 Python `subprocess(shell=False)` 直接调用 `npx` 时无法解析 `.cmd` 启动器的问题。
- 新增 `scripts/playwright_smoke_utils.py`，在 Windows 优先解析 `npx.cmd` / `npx.exe` / `npx.bat`，在 macOS / Linux 保持 plain `npx`。
- WS-01 / WS-02 Playwright smoke 继续使用 argv list 和 `shell=False`，不引入 shell 解析。

## 行为变化

- `scripts/threejs_snake_smoke.py` 与 `scripts/harness_trace_console_smoke.py` 通过共享 helper 获取 `npx` 可执行入口。
- Blackbox smoke 通过导入基础 smoke 脚本自动继承该兼容修复。

## 破坏性变更

- 无。

## 验证范围

```bash
.codex/hooks/run_with_repo_python.ps1 tests/test_playwright_smoke_utils.py
.codex/.venv/Scripts/ruff.exe check .codex/hooks scripts tests
.codex/hooks/run_with_repo_python.ps1 scripts/threejs_snake_smoke.py
.codex/hooks/run_with_repo_python.ps1 scripts/threejs_snake_blackbox_smoke.py
.codex/hooks/run_with_repo_python.ps1 scripts/harness_trace_console_smoke.py
.codex/hooks/run_with_repo_python.ps1 scripts/harness_trace_console_blackbox_smoke.py
.codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --all
git diff --check
```

## 边界

- 本次只修复本地 Playwright smoke 启动器解析。
- 不改变 browser smoke 覆盖范围，不新增 remote / hosted / external collector claim。
