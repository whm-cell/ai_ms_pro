# New Repo Rehearsal Handoff

更新时间：2026-04-19
阶段：stage-00
任务：new-repo-rehearsal
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务用于验证 harness 在全新测试仓库中的 0 到 1 初始化，不绑定当前 repo 的 canonical REQ / WS

## 本任务目标

- 在一个全新测试仓库中完整演练 starter copy -> bootstrap -> Git hook 初始化
- 导入首个真实 `REQDOC / REQ / WS`
- 验证新仓库在首轮初始化后已进入“可继续开发”状态

## 已完成内容

- 在 [`output/harness_rehearsal_20260419_100339`](/Volumes/usd/codes/go_projects/ai_ms_pro/output/harness_rehearsal_20260419_100339) 创建独立测试仓库并初始化 Git
- 从 [`new_pro_standard/`](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard) 复制 portable starter bundle
- 在测试仓库中执行 `python3 scripts/bootstrap_harness.py --project-name "Harness Rehearsal Demo"`，完成 `.codex/.venv` 初始化
- 在测试仓库中执行 `git config core.hooksPath .githooks`
- 导入首个真实需求链：`REQDOC-001 / REQ-001 / REQ-002 / WS-01`
- 落地首个最小实现 [`apps/quick-notes-inbox/index.html`](/Volumes/usd/codes/go_projects/ai_ms_pro/output/harness_rehearsal_20260419_100339/apps/quick-notes-inbox/index.html)
- 验证测试仓库中的 `python3 scripts/check_ai_governance.py` 与 `PATH=/usr/bin:/bin .githooks/pre-commit` 均通过

## 修改文件

- [scripts/bootstrap_harness.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/bootstrap_harness.py)
- [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)
- [scripts/check_ai_doc_quality.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_doc_quality.py)
- [docs/ai/harness-portability-guide.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-portability-guide.md)
- [docs/ai/adr/ADR-006-harness-portability-bootstrap.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-006-harness-portability-bootstrap.md)
- [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [new_pro_standard/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/README.md)
- [new_pro_standard/scripts/bootstrap_harness.py](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/scripts/bootstrap_harness.py)
- [new_pro_standard/scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/scripts/check_ai_governance.py)
- [new_pro_standard/scripts/check_ai_doc_quality.py](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/scripts/check_ai_doc_quality.py)
- [output/harness_rehearsal_20260419_100339](/Volumes/usd/codes/go_projects/ai_ms_pro/output/harness_rehearsal_20260419_100339)

## 关键实现决策

- 演练仓库放在当前 repo 的 `output/` 下，避免污染主治理面
- bootstrap 的 Python 依赖安装改为 best-effort；离线或受限网络下，`.codex/.venv` 初始化不应因可选兼容依赖失败而中断
- governance checker 的 changed-path 采集改为 `git status --porcelain=v1 -uall`，避免全新仓库首次提交前只看到顶层目录而误判同步缺失
- workstream 质量检查同时接受 `## 验收模型` 和历史 `## 验收重点`

## 已验证有效的路线

- `new_pro_standard/` 已能作为新仓库 starter，完成 Git hook、repo-local Python 和最小控制面初始化
- 全新仓库里导入首个真实 `REQDOC / REQ / WS` 后，再补 handoff，就能进入可继续开发状态
- Git hook 与治理检查在 Python 3.9 路径下也能通过 repo-level runner 正常工作

## 已验证无效的路线

- 把 Python 可选兼容依赖安装当作 bootstrap 强依赖，在离线环境下会阻断初始化
- 让 governance checker 只读取 `git status` 的目录级未跟踪结果，会在新仓首跑时误判“治理实现变了但文档没同步”
- 让 workstream quality rule 只接受旧标题 `## 验收重点`，会和 projection-surface 新模板冲突

## 尚未尝试但建议的路线

- 在测试仓库里继续跑一次 runtime observation / reducer / promotion
- 为 `apps/quick-notes-inbox/` 增加最小 smoke
- 再演练一次非静态前端或后端场景，验证 starter 的第二类工作流

## 当前未完成项

- 当前测试仓库尚未跑 observation / reducer
- 当前测试仓库尚未生成阶段 `status`
- 还没有在仓库外部路径再演练一次 starter

## 已知风险与注意事项

- `output/harness_rehearsal_20260419_100339` 是当前 repo 内的测试仓库，不应被误当作主项目代码
- bootstrap 的 best-effort 依赖安装只保证初始化不断档，不代表所有可选 pip 包都已安装
- 当前测试场景仍偏轻量，后续还需要更复杂场景继续施压 harness

## 下一位 Agent 的第一步动作

- 若要继续验证 portability，先读本 handoff 与 [`ADR-006`](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-006-harness-portability-bootstrap.md)，然后进入测试仓库补 runtime observation / reducer 演练

## 建议同步更新

- 已同步 `working-context`
- 已同步 stage `status`
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
