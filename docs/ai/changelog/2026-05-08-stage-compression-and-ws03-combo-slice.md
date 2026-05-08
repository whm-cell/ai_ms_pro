# 2026-05-08 Stage Compression And WS-03 Combo Slice

## 新增功能

- WS-03 browser slice 增加 combo scoring 与 rank feedback。
- 新增 `docs/ai/security/remote-merge-gates.md`，记录远端 branch protection / ruleset 的可证明状态。
- 新增 `scripts/check_branch_hygiene.py`，区分 open PR 分支、merged/closed stale 分支和 unmanaged 远端分支。
- `governance-and-smoke.yml` 的 governance job 会在 PR/main push 中以 `check_branch_hygiene.py --strict` 报告并阻断 active PR / stale branch 预算问题。
- 真实 PR CI 暴露 branch hygiene self-check 风险后，PR job 改为传入 `--current-pr`；pending checks 不再被算作 failed open PR，当前 PR 自己的 check rollup 也不参与 failed-open-PR 判定。
- PR CI 环境中的 `origin/pull/*` 合成 refs 不参与 remote branch hygiene，避免把 GitHub checkout 产生的临时 ref 误判为 unmanaged branch。
- `.github/dependabot.yml` 改为 dependency groups，并将每个 ecosystem directory 的 `open-pull-requests-limit` 收紧为 1。
- 新增 SAMPLE-002，作为 `prd-to-project-skills` 与 `progressive-feature-development` 的第二个 accepted real-task eval。

## 修复问题

- 压缩 `docs/ai/index.md` 与 Stage-00 status，降低默认上下文面。
- 将 ADR-005 移入 ADR archive，避免 active ADR count 长期卡在预算上限。
- 拆出 `code_shape_ast.py` 与 session snapshot renderer，减少低风险 code-shape 债务。
- 开启 GitHub `delete_branch_on_merge`，并清理已合并 PR #1 的 Codex 分支。
- 关闭失败的 Dependabot GitHub Actions PR #2-#6，并删除对应远端分支；当前 active 分支只剩 PR #9 和 green 的 PR #7/#8。

## 行为变化

- `scripts/godot_platformer_slice_smoke.py` 现在验证 score、combo、rank、completion 和 reset。
- Candidate workflow skills 达到 2/2 accepted samples，但不会自动变成 always-on。
- Remote merge gates 仍以 `UNKNOWN` 暴露，直到 GitHub 远端配置可被证明。
- Open PR 分支不直接删除；merged/closed PR 分支由 branch hygiene check 驱动清理。
- Failed open PR 现在会触发 branch hygiene strict 失败；显式运行 `check_branch_hygiene.py --close-failed-dependabot-prs` 才会关闭并删 Dependabot 分支。

## 破坏性变更

- 无。Godot engine、GUT、export preset、assets、localization 和 release pipeline 仍未采纳。

## 验证范围

- `python3 scripts/godot_platformer_slice_smoke.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
