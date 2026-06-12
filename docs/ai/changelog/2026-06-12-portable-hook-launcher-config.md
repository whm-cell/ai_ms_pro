# Portable Hook Launcher Config

更新时间：2026-06-12
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `.codex/hooks/run_hook.cmd` 作为跨平台 hook launcher：Windows batch 路径调用 `run_hook.ps1`，macOS / Linux shell 路径转入 `run_hook.sh`。
- 新增 `.gitattributes` 规则，固定 `.codex/hooks/run_hook.cmd` 为 LF 行尾，避免 POSIX shell 解析 CRLF。

## 修复问题

- 避免 Codex hook 在 Windows 上经过 `.py` 文件关联启动，导致用户选择 VS Code 或 Python launcher 后反复打开编辑器、默认应用选择框或独立终端窗口。
- 避免 `.codex/hooks.json` 在 Windows 与 macOS / Linux 之间来回同步为不同命令；当前配置改为宿主无关。

## 行为变化

- `.codex/hooks.json` 现在统一指向 `.codex/hooks/run_hook.cmd`。
- `scripts/hook_config_lib.py` 不再按 `platform.system()` 输出不同 hook runner；`--system Windows`、`--system Darwin` 和 `--system Linux` 渲染结果一致。
- Windows 仍由 PowerShell runner 显式解析可运行 Python；macOS / Linux 仍由 POSIX shell runner 显式解析可运行 Python。

## 破坏性变更

- 无。hook 目标脚本、Python 解析顺序和 blocking policy 不变。

## 验证范围

- `cmd.exe /d /c ".codex\hooks\run_hook.cmd pre_tool_use_preflight.py"`
- `.codex/hooks/run_hook.cmd pre_tool_use_preflight.py`
- `.codex/hooks/run_with_repo_python.ps1 scripts/sync_hooks_config.py --system Windows --check`
- `.codex/hooks/run_with_repo_python.ps1 scripts/sync_hooks_config.py --system Darwin --check`
- `.codex/hooks/run_with_repo_python.ps1 scripts/sync_hooks_config.py --system Linux --check`
- `.codex/hooks/run_with_repo_python.ps1 tests/test_hooks_config_sync.py`

## 关联文档

- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [AI 文档入口索引](../index.md)
