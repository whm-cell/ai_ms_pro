# 2026-05-07 Skill Eval And Code Shape Debt First Slice

更新时间：2026-05-07
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 REQDOC-003 / WS-03 的 Candidate workflow skill eval 记录，将本轮真实 PRD 到首轮薄切片任务登记为 `prd-to-project-skills` 与 `progressive-feature-development` 的 SAMPLE-001 accepted real-task 样本。
- 新增详细 eval 文件 `docs/ai/skill-evals/SAMPLE-001-reqdoc-003-ws03-first-slice.md`，记录 `baseline_without_skill`、`run_with_skill`、`delta`、`acceptance` 与 `verification`。

## 修复问题

- 修复 `docs/ai/skill-usage-samples.md` 仍显示两个 workflow Candidate skills 为 0/2 的证据缺口。
- 将 `scripts/check_ai_docs.py` 与 `scripts/check_ai_doc_quality.py` 的 oversized `main()` 拆成小函数，code-shape hard-ceiling warning 减少 2 项。
- 同步 `working-context` 与 stage status，避免当前 truth surface 继续保留“无 accepted 样本”的旧事实。

## 行为变化

- `prd-to-project-skills` 与 `progressive-feature-development` 现在均为 1/2 accepted samples；仍不得升级为 always-on。
- 本轮只处理低风险文档检查器的 code-shape 债务；runtime hooks、bootstrap、核心 governance checker、runtime reducer 与 smoke 脚本的历史 warning 继续保留为后续分批处理项。
- SAMPLE-001 的 `baseline_without_skill` 是反事实基线，不是独立重跑，因此不能单独证明 workflow skills 应默认触发所有任务。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_docs.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_doc_quality.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `python3 -m unittest discover -s tests`
- `git diff --check`

## 关联文档

- [Candidate Skill Usage Samples](../skill-usage-samples.md)
- [SAMPLE-001 REQDOC-003 WS-03 First Slice Candidate Skill Eval](../skill-evals/SAMPLE-001-reqdoc-003-ws03-first-slice.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [AI 文档入口索引](../index.md)
