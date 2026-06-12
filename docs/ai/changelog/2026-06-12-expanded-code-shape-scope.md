# Expanded Code Shape Scope

更新时间：2026-06-12
阶段或版本：stage-00
状态：已确认

## 新增功能

- 扩展 `.codex/code_shape.toml` 的 scope，覆盖 Next-style `app/`、`components/`、`lib/`，以及 `scripts/`、`services/`、`tests/` 中的 TS/JS 代码文件。
- `check_code_shape.py` 新增 JavaScript 文件类型识别：`.js`、`.jsx`、`.mjs`、`.cjs`。
- `check_code_shape.py` 新增 PowerShell 文件类型识别：`.ps1`。
- `check_code_shape.py` 新增 path-specific 单文件预算，用于测试文件和 fixture/cases/mock data 文件。
- 补全 `$harness-maintenance` 的 code-shape reference，写明 TS/JS、CSS/SCSS、SQL、shell 和 PowerShell 的单文件预算。

## 样本依据

- `D:\codes\gs_projects\demo_txt_t_proto` 中发现当前 scope 漏掉的长文件样本：
  - `app/globals.css` 约 6205 行。
  - `components/open-design/GenerateWorkbench.tsx` 约 952 行。
  - `lib/profile-memory/serviceSchema.ts` 约 719 行。
  - 多个 `scripts/*.mjs` 超过 450 行。
- 该样本说明旧 scope 只覆盖 `apps/**`、Python、Rust、SQL 和部分 CSS/TS 路径，无法覆盖常见 Next 项目结构。

## 修复问题

- 修复 `apps/**/*.js` 已在配置附近但 checker 不识别 JS 后缀的问题。
- 修复 Next 项目常见 `app/`、`components/`、`lib/` 长文件不进入 code-shape scope 的问题。
- 修复 `$harness-maintenance` code-shape reference 只说明 Python / Rust 阈值、遗漏其它语言预算的问题。

## 行为变化

- 新增或 staged 的 Next-style 前端文件、JavaScript/MJS 脚本、SCSS、services SQL、tests 代码和 PowerShell hook 脚本会进入 code-shape file-level budget。
- `tests/**` 单文件 warning 放宽到 800 行、new-file error 放宽到 1500 行；Python 测试函数/类仍使用全局函数/类预算。
- `*Cases.*`、`fixtures.*`、`*Fixture.*`、`mockData.*` 单文件 warning 放宽到 900 行、new-file error 放宽到 1800 行；只作为数据/样例文件预算，不作为业务逻辑放宽口。
- Python 仍保留单文件、函数/方法、类三层预算；非 Python 语言当前只做单文件行数检查。
- 现有 legacy 大文件只产生 warning；新增文件超过 hard ceiling 才失败。

## 破坏性变更

- 无。`check_code_shape.py` 的治理等级仍跟随 `docs/ai/check-registry.md`，本轮不升级为新的 blocking 规则。

## 验证范围

- `.codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --staged`
- `.codex/hooks/run_with_repo_python.ps1 -m pytest tests/test_code_shape_initial_commit.py`
- `.codex/hooks/run_with_repo_python.ps1 scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.ps1 scripts/check_context_budget.py`
- `.codex/.venv/Scripts/python.exe -m ruff check .codex/hooks scripts tests`
- `git diff --check`
