# Next Best Work Review Advisory

日期：2026-05-30
阶段或版本：stage-00

## 新增功能

- 新增 `docs/ai/templates/next-best-work-review.md`，用于完成 `REQ/WS`、阶段 checkpoint 或发现计划不合适时记录下一步选择判断。
- 在 `$repo-governed-coding` governance checklist 中加入 Next Best Work Review 触发条件、必答问题和 `continue / re-scope / split / pivot / park / cancel / ask-user` 决策枚举。
- `status` 模板和 runtime handoff 草稿会提示下一步选择判断；语义判断仍由主 Agent 完成。
- 新增 warning-only 检查：完成型 active `handoff/status` 或显式 pivot/scope-change 文档缺少 review 小节时只输出 warning，不阻断。

## 修复问题

- 研发中完成一个需求后，计划中的下一项可能已经不再是当前阶段最合适的工作；harness 需要一个轻量机制记录继续、重排、拆分、搁置或询问用户的判断。
- 该机制先以 advisory 方式 burn-in，避免简单任务被强制长篇复盘。

## 行为变化

- 不改变当前 Stage-00 scope、active validation boundary、REQ/WS 绑定或 blocking policy。
- 第四阶段需要真实任务样本观察 process tax 和防错收益；不能用 synthetic evidence 宣称机制已证明有效。

## 破坏性变更

- 无。该机制保持 advisory / warning-only。

## 验证范围

- `python3 tests/test_runtime_reducer_metadata.py`
- `python3 tests/test_next_best_work_review.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged`
- `git diff --check`
