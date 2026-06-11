# 2026-05-26 Three.js Snake Simple-Skip Samples

更新时间：2026-05-26
阶段或版本：stage-00 harness burn-in
状态：已确认

## 新增功能

- WS-01 Three.js Snake 新增 pause/resume、reset-best 和 HUD status。
- Deterministic smoke 与黑盒 smoke 覆盖 pause/resume、reset-best、game over 和 restart。

## 修复问题

- `GAP-WORKFLOW-SIMPLE-SKIP` 不再停留在 1/2；第二个真实小任务样本已通过 append/outcome review gate。
- 贪吃蛇 smoke 现在覆盖最高分清空路径，避免只验证内部移动/碰撞链路。

## 行为变化

- 玩家可以在 HUD 中清空本地最高分。
- `GAP-WORKFLOW-SIMPLE-SKIP` readiness 从 needs-more-real-samples 进入 ready-for-upgrade-discussion，并由 upgrade decision 保持 keep-advisory。

## 破坏性变更

- 无。

## Harness 结果

- `GAP-WORKFLOW-SIMPLE-SKIP` 新增 2 个 accepted real workflow-task samples。
- 该 gap 当前达到 2/2，并记录 keep-advisory upgrade decision。
- 结论：两个样本证明简单 UI/control/storage 任务可以跳过 heavyweight workflow skill，但仍不足以把 Candidate workflow skills 升级为 always-on。

## 验证范围

- `node --check apps/threejs-snake/main.js`
- `python3 scripts/check_threejs_snake_contract.py`
- `python3 scripts/threejs_snake_smoke.py`
- `python3 scripts/threejs_snake_blackbox_smoke.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --gap-id GAP-WORKFLOW-SIMPLE-SKIP`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
