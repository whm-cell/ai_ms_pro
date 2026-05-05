# 2026-05-05 GitHub Guardrails Refactor And CI Burn-in Fix

更新时间：2026-05-05
阶段或版本：stage-00
状态：已确认

## 新增功能

- 将 `scripts/check_github_guardrails.py` 拆成薄 CLI 与 `scripts/github_guardrails/` helper 模块，并同步到 `new_pro_standard`。
- 新增 orphan gitlink 检查，避免无 `.gitmodules` 映射的演练仓库或输出目录再次破坏 GitHub Actions checkout。
- `check_github_guardrails.py` 继续保持兼容导出，既有测试和调用入口不需要改名。

## 修复问题

- 推送后确认远端已能通过 GitHub API 看到 `.github/workflows/security-evidence.yml`，`remote workflows` WARN 已消失。
- PR #1 的 `scorecard` 首轮失败根因是 `actions/checkout` 在清理子模块时遇到误跟踪的 `output/harness_rehearsal_20260419_100339` gitlink，不是 Scorecard 规则失败。
- 从 Git 索引移除该演练输出 gitlink，并将 `output/` 作为本地生成产物忽略；本地演练目录保留，不作为主 repo truth。
- PR #1 第二轮 governance 失败根因是 GitHub GraphQL 504 触发 PR touch conflict `UNKNOWN`，而 workflow 把 `--strict-unknown` 作为阻断；已调整为只阻断已确认的 high-risk overlap，`UNKNOWN` 在 burn-in 阶段保持可见但不阻断。
- PR #1 第三轮 CodeQL 失败根因是 private repo 未启用 GitHub code scanning；已改为 `upload: never` 并上传 CodeQL SARIF artifact，保持 advisory evidence 不污染 required-check 信号。

## 行为变化

- GitHub guardrails 输出新增 `tracked gitlinks` 结构检查。
- branch protection / rulesets 仍按 `OK / WARN / UNKNOWN` 区分；GitHub 403 时不能宣称禁止直推 `main` 已生效。
- PR touch conflict checker 仍支持 `--strict-unknown`，但默认 PR workflow 暂不启用该开关，避免 GitHub API 瞬时 504 变成流程性 CI flake。
- CodeQL 结果暂存为 workflow artifact；只有启用 GitHub code scanning 后，才考虑改回上传到 Code Scanning 并讨论是否升级。
- Scorecard / CodeQL / SBOM 仍处于 burn-in advisory 阶段，不进入 required checks。

## 破坏性变更

- 无。删除的是误跟踪的 gitlink 记录，不删除本地 `output/` 演练目录。

## 验证范围

- `python3 -m unittest discover -s tests -p test_github_guardrails.py`
- `python3 -m unittest discover -s new_pro_standard/tests -p test_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `python3 new_pro_standard/scripts/check_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `git diff --check`

## 关联文档

- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Harness Maintenance GitHub Guardrails Reference](../../../.agents/skills/harness-maintenance/references/github-guardrails.md)
