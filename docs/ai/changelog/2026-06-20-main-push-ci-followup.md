# Main Push CI Follow-up

日期：2026-06-20
阶段：STAGE-00 Runtime Harness Foundation
Requirement IDs：未绑定
Workstream IDs：未绑定

## 新增功能

- 无新增 runtime 或 product capability。
- 增加 main-push CI follow-up 的 canonical 记录，用于说明本次主分支推送后的 CI 边界调整。

## 行为变化

- PR branch hygiene 继续使用 `--strict --current-pr`。
- main-push branch hygiene 改为 advisory markdown summary，不再因无关 unmanaged remote branch cleanup warning 阻断已推送的 `main` 状态。
- root 与 `new_pro_standard` starter 同步 workflow 和 check-registry / remote-merge-gates 口径。

## 修复问题

将 `codex/real-data-activation-gate` 的当前 HEAD 推送到 GitHub `main` 后，`Governance And Smoke` 在两个 CI 面暴露问题：

- `windows-hook-runtime` 的 Python resolution 单测使用 POSIX shell fake Python，在 Windows runner 上不可执行，导致测试没有验证到 parent `.env` selector 路径。
- main-push branch hygiene summary 使用 `--strict`，会把无关 unmanaged remote branch review warning 升级成主分支发布失败。

- Python resolution 单测改为 mock `bootstrap_harness.python_version`，保持“只接受 runnable Python candidate”的生产逻辑不变，同时让 Windows runner 验证 selector precedence。

## 破坏性变更

- 无。PR branch hygiene strict gate 保持不变；manual cleanup command 仍保持显式执行。

## 边界

- 不删除 remote branch，不关闭 PR，不声明 branch protection / rulesets 已远端 enforced。
- main-push advisory 只改变 CI 阻断语义；manual cleanup 仍需显式命令和确认。

## 验证范围

- `tests/test_python_resolution.py`
- `new_pro_standard/tests/test_python_resolution.py`
- `.github/workflows/governance-and-smoke.yml`
- `new_pro_standard/.github/workflows/governance-and-smoke.yml`
- `scripts/check_branch_hygiene.py --markdown`
- `scripts/check_ai_governance.py`
- `scripts/check_context_budget.py`
- `scripts/check_code_shape.py --all`
- `git diff --check`

## 关联文档

- [Check Registry](../check-registry.md)
- [Remote Merge Gates](../security/remote-merge-gates.md)
