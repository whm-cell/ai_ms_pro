# Harness Portability Template Handoff

更新时间：2026-04-30
阶段：stage-00
任务：harness-portability-template
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务处理的是跨项目可迁移的治理机制，不新增当前 repo 的 requirement/workstream canonical mapping

## 本任务目标

- 把当前 harness 拆成“可复制机制层”和“必须重建的真相层”
- 让新项目能够通过一个 bootstrap 入口初始化最小控制面
- 去掉校验脚本中阻碍迁移的 repo-specific 硬编码

## 已完成内容

- 更新 [scripts/check_ai_docs.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_docs.py)，改为“最小默认 + `.codex/harness.toml` 可配置”
- 新增默认最小配置 [.codex/harness.toml](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/harness.toml)
- 新增 [scripts/bootstrap_harness.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/bootstrap_harness.py)，可在新项目中生成 `index / working-context / plan / requirements index / traceability-matrix`
- 新增 repo-level Python runner，统一 Codex hook 与 Git hook 对 `.codex/.venv` 的优先解析，避免落到系统 Python 3.9
- 新增 [Harness 可迁移清单](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-portability-guide.md)，明确哪些文件保留、清空和参数化
- 新增 [ADR-006 Harness 可迁移性与 Bootstrap 决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-006-harness-portability-bootstrap.md)
- 更新 `handoff/status/adr` 模板中的内部链接为相对路径，避免迁移时带入当前仓库绝对路径
- 已同步 `working-context`、stage `status` 与 `docs/ai/index.md`
- 已把 `new_pro_standard` 下的 `index`、`working-context`、`AGENTS.md`、`README.md` 与 portability guide 同步到 slim governance surface 逻辑
- 已同步 root 与 starter 两份 `scripts/bootstrap_harness.py`，避免 bootstrap 重新生成旧的 fat governance surface 模板
- 已为 `new_pro_standard/scripts/check_ai_governance.py` 增加 active handoff / working-context bound handoff 预算 warning
- 2026-04-30: 已把 Karpathy-style 行为护栏沉淀为 starter 内的可选 `.codex/skills/repo-governed-coding/`，并将 runtime session 模板/Stop 快照补上 `行为护栏快照`

## 修改文件

- [.codex/harness.toml](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/harness.toml)
- [scripts/check_ai_docs.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_docs.py)
- [scripts/bootstrap_harness.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/bootstrap_harness.py)
- [.codex/hooks/run_with_repo_python.sh](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/run_with_repo_python.sh)
- [.codex/hooks/run_hook.sh](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/run_hook.sh)
- [.githooks/pre-commit](/Volumes/usd/codes/go_projects/ai_ms_pro/.githooks/pre-commit)
- [.codex/requirements.txt](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/requirements.txt)
- [docs/ai/harness-portability-guide.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-portability-guide.md)
- [docs/ai/adr/ADR-006-harness-portability-bootstrap.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-006-harness-portability-bootstrap.md)
- [docs/ai/handoffs/active/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/_template.md)
- [docs/ai/status/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/_template.md)
- [docs/ai/adr/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/_template.md)
- [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [new_pro_standard/docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/docs/ai/index.md)
- [new_pro_standard/docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/docs/ai/working-context.md)
- [new_pro_standard/AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/AGENTS.md)
- [new_pro_standard/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/README.md)
- [new_pro_standard/docs/ai/harness-portability-guide.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/docs/ai/harness-portability-guide.md)
- [new_pro_standard/scripts/bootstrap_harness.py](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/scripts/bootstrap_harness.py)
- [new_pro_standard/scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/scripts/check_ai_governance.py)
- [.codex/skills/repo-governed-coding/SKILL.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/skills/repo-governed-coding/SKILL.md)
- [.codex/runtime/sessions/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md)
- [.codex/hooks/stop_runtime_session.py](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/hooks/stop_runtime_session.py)
- [docs/ai/handoffs/active/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/_template.md)
- [docs/ai/adr/ADR-009-behavioral-guardrails-skill-and-session-snapshot.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-009-behavioral-guardrails-skill-and-session-snapshot.md)
- [new_pro_standard/.codex/skills/repo-governed-coding/SKILL.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/.codex/skills/repo-governed-coding/SKILL.md)
- [new_pro_standard/.codex/runtime/sessions/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/.codex/runtime/sessions/_template.md)
- [new_pro_standard/.codex/hooks/stop_runtime_session.py](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/.codex/hooks/stop_runtime_session.py)
- [new_pro_standard/docs/ai/handoffs/active/_template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/docs/ai/handoffs/active/_template.md)

## 关键实现决策

- 不把当前项目的 `working-context/status/handoff/traceability` 当成可复制模板，而是只复制机制层
- `check_ai_docs.py` 的默认要求保持最小，repo-specific 附加文档交给 `.codex/harness.toml` 决定
- 新项目从 0 到 1 的首个动作固定为 bootstrap 最小控制面，而不是直接进入业务实现
- bootstrap 默认使用当前环境 Python 创建 repo-local `.codex/.venv`，并由统一 runner 供 Git hook 与 Codex hook 共用
- 模板文档优先使用相对链接，避免把当前仓库绝对路径污染到新项目
- portability starter 与 root bootstrap generator 必须同源对齐；否则一次手工瘦身会被下一次 bootstrap 重新打回旧模板
- 行为护栏只作为显式调用的 method layer 进入 starter；不能替代 `AGENTS.md`、共享治理文档或 verification scripts

## 已验证有效的路线

- 先收掉 repo-specific 硬编码，再给 bootstrap 入口，比只写迁移说明更可执行
- 把“复制机制，不复制真相”写成 ADR 和迁移清单，能明显降低新项目误启动风险
- 默认最小 `.codex/harness.toml` 更适合作为跨项目可复制基线
- Git hook 与 Codex hook 共用同一个 repo-level Python 解析入口后，能稳定避开 `/usr/bin/python3` 3.9 引发的 `tomllib` 类兼容性问题
- 把 assumptions / scope boundary / success criteria / verification plan 写入 runtime session 模板，比只复制外部行为说明更容易进入后续 handoff/status 压缩链路

## 已验证无效的路线

- 把当前项目整套共享文档原样复制到新仓库，再让 AI 自己分辨哪些是真相、哪些是样板
- 只靠口头提醒“别复制旧文档”，不提供 bootstrap 和配置入口
- 让模板保留当前仓库绝对路径链接

## 尚未尝试但建议的路线

- 后续可继续把 `AGENTS.md` 也拆出一个更项目中立的 starter 版本
- 若未来需要一键迁移，可再补一个 `--export-template` 或脚手架目录
- 等下一个新项目真正使用这套 bootstrap 后，再补一轮 portability review

## 当前未完成项

- 尚未给 `AGENTS.md` 提供独立 starter 版本
- 尚未在真实外部新仓库中实际演练一次完整 bootstrap 流程
- 尚未把更多 smoke/validation 样板做成可选模块

## 已知风险与注意事项

- 新项目若直接复制当前 repo 全量内容且不运行 bootstrap，仍可能先继承错误上下文
- `.codex/harness.toml` 只解决 required docs 的配置，不会自动替项目决定附加治理文档
- bootstrap 只生成最小控制面和 repo-local Python 运行时，不生成首个真实 `REQDOC / REQ / WS`

## 下一位 Agent 的第一步动作

- 若目标是把 harness 带去新项目，先运行 `python3 scripts/bootstrap_harness.py --project-name "新项目名"`，再改写 `AGENTS.md` 和 `.codex/harness.toml`

## 建议同步更新

- 已同步 `working-context`
- 已同步 `stage status`
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
