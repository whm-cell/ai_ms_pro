# Change Triggered Followups

更新时间：2026-05-05
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 `scripts/check_change_triggered_followups.py`，根据 changed files 提示可能需要补跑的专项检查和应打开的 skill/reference。
- 新增 root 与 `new_pro_standard` 的单测，覆盖 `AGENTS.md`、GitHub、requirements、skills 和 harness Python 变更面。
- 将 checker 接入 `$harness-maintenance` 的 verification command reference、AI index、working-context 和 starter README。

## 修复问题

- 降低 `AGENTS.md` 压缩后未来 agent 漏打开按需 skill/reference 的执行风险。
- 避免把 projection、verification、GitHub、requirements、skill lifecycle 细则重新塞回 always-on `AGENTS.md`。

## 行为变化

- checker 默认读取当前 git status（含 untracked files），也支持 `--files`、`--staged`、`--base`、`--json` 和 `--strict`。
- checker 会保留 `.agents` / `.github` 等 dot-directory 路径，并对 `new_pro_standard/**` 提示 starter 自身验证。
- 默认保持 advisory / warning-only；它只建议 follow-up surfaces，不证明命令已经执行。

## 破坏性变更

- 无。

## 验证范围

- `python3 -m unittest discover -s tests -p "test_change_triggered_followups.py"`
- `/Users/coolm/.pyenv/versions/3.11.13/bin/python3 -m unittest discover -s tests -p "test_change_triggered_followups.py"` from `new_pro_standard`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files AGENTS.md .github/workflows/governance-and-smoke.yml docs/requirements/source/REQDOC-001.md .agents/skills/harness-maintenance/SKILL.md scripts/check_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `git diff --check`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [AGENTS Default Context Compression](./2026-05-05-agents-default-context-compression.md)
- [Harness Maintenance Verification Commands](../../../.agents/skills/harness-maintenance/references/verification-commands.md)
