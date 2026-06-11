# Changelog: Agentic Red-Team Samples

更新时间：2026-05-24
阶段或版本：stage-00 / stage-01 harness hardening
状态：已确认

## 新增功能

- 新增 `docs/ai/security/agentic-red-team-samples.md` 与 `agentic-red-team-samples.jsonl`，定义 G6/G7 red-team / surface-control 的 bounded 样本账本。
- 新增 `scripts/check_agentic_red_team_samples.py` 与 `tests/test_agentic_red_team_samples.py`，校验 AC control 映射、risk family、local-replay / real-incident 类型、false-positive rule、replay command、evidence refs 和 raw runtime 边界。
- 接入 governance workflow、check registry、changed-file follow-up、sample gap target docs 和 `$harness-maintenance` verification reference。

## 修复问题

- 修复 G6/G7 只有 eval / sample-gap routing 和控制矩阵、缺少统一可复查 red-team sample artifact 的问题。

## 行为变化

- 当前有 8 个 accepted local-replay 样本，覆盖 prompt injection、tool-output injection、skill squatting、memory poisoning、handoff / A2A confusion、cascade autonomy、human confirmation 和 sandbox claim honesty。
- `check_agentic_red_team_samples.py` 会报告 accepted real incident 仍为 0；这是 burn-in 状态，不是 blocking failure。

## 边界

- 该检查保持 advisory，不执行攻击，不读取 raw runtime，不声明真实外部攻击或外部互通完成。
- `upgrade_signal=candidate` 只能用于 `real-incident` 样本；local replay 样本不能推动 blocking 升级。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_agentic_red_team_samples.py`
- `python3 tests/test_agentic_red_team_samples.py`
- `python3 tests/test_skill_catalog.py`
- `.codex/hooks/run_with_repo_python.sh tests/test_workspace_sandbox.py`
- `python3 tests/test_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Agentic Control Matrix](../security/agentic-control-matrix.md)
- [Agentic Red-Team Samples](../security/agentic-red-team-samples.md)
