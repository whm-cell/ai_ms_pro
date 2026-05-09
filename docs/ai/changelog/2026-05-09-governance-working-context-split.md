# 2026-05-09 Governance Working Context Split

更新时间：2026-05-09
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `ai_governance_metadata.py`、`ai_governance_working_context.py` 和 `ai_governance_working_context_sources.py`，承接 working-context sync metadata 的解析、来源校验、REQ/WS 绑定和同步时间校验。
- 将 `check_ai_governance.py` 的入口 orchestration 拆成小 helper，入口函数只保留装配顺序。
- 将 `harness_trace_console_blackbox_smoke.py` 的大段浏览器断言脚本提取为模块常量，缩短 `smoke_steps`。
- 固定 smoke 脚本使用的 `@playwright/cli` npm package 版本，和 workflow 的 Playwright browser install 版本一起由环境变量声明。

## 修复问题

- 消除 `check_ai_governance.py::validate_working_context_sync_metadata` 超过 hard ceiling 的 code-shape warning。
- 消除 `check_ai_governance.py::main` 超过 hard ceiling 的 code-shape warning。
- 消除 `harness_trace_console_blackbox_smoke.py::smoke_steps` 超过 warning threshold 的 code-shape warning。
- 将 `.codex/hooks/stop_runtime_observation.py` 压回文件长度阈值内。
- `check_ai_governance.py` 继续保留主调度、projection freshness、runtime traceability 和 staged/runtime 检查，不再承载整段 working-context metadata 细节。

## 行为变化

- 规则语义、错误文案、CLI 入口和退出码保持不变。
- OPEN-14 仍未关闭；剩余文件级长度债务继续按批次处理。

## 破坏性变更

- 无

## 验证范围

- `python -B -m unittest discover -s tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `git diff --check`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
