# new_pro_standard Starter Sync

日期：2026-06-15

## 新增功能

- `new_pro_standard` 已同步当前公共 harness 机制，包括 hook launcher、runtime snapshot、sample-gap / burn-in 检查、agent productization readiness、config contract、enterprise boundary、tool contracts、eval dataset、checkpoint 和 code-shape 相关脚本与测试。
- starter 新增空样本与 deferred ledger 面：checkpoint、pre-tool-use、loop-scope、local-trace、agentic red-team、upgrade decision、external decision、future-work contract 和 productization readiness 均只保留模板安全记录。
- starter `.codex/harness.toml` 已恢复为新项目默认边界：prototype design brief 默认关闭，config contract registry/template 为空，sample evidence 只接受新项目真实事件。

## 修复问题

- 修正 starter 中旧 `GAP-STARTER-*` 示例、项目专属 tool contract、项目 burn-in 状态和当前 repo 专属 verification command 泄入模板的问题。
- 修正 starter 检查面与当前公共脚本不同步的问题，补齐新增脚本、测试、skill reference、hook helper 和模板安全文档。

## 行为变化

- starter 验证面现在覆盖 287 个单元测试，并包含当前 root harness 的 portable hooks、Python helper 拆分、sample routing、burn-in readiness、workspace sandbox、CI agent contract 和 runtime execution snapshot 检查。
- 追加同步 starter-safe 公共测试覆盖后，starter 验证面提升到 420 个单元测试；新增测试按 starter 空样本 / blocked future-work contract / 未绑定 REQ-WS 语义改写断言。
- `docs/ai/tool-contracts/contracts.json` 已过滤为 starter-safe 合约，不引用当前项目专属 smoke、demo 或不存在的测试命令。
- `GAP-STARTER-*` 占位命名已收敛为通用 `GAP-*` 示例，避免把 starter 模板 gap 与当前项目 burn-in 真相混在一起。

## 破坏性变更

- 无。当前项目专属事实未进入 starter；新项目仍需要生成自己的 requirements、workstreams、samples、runtime artifacts 和产品验证。

## 边界

- 未复制当前项目的 REQ/WS、accepted real samples、runtime artifacts、Three.js Snake / Harness Trace Console demo apps、source evidence 或远端能力结论。
- starter 内的 synthetic / deferred / pending 记录只用于引导新项目采样；不能作为本项目或新项目的 accepted evidence。
- 外部能力仍不声明完成：remote trace、hosted eval、native sandbox、MCP/A2A、CI agent runtime 和生产原型均保持未证明状态。
- 未同步 root 专属 demo/smoke 脚本：`check_threejs_snake_contract.py`、`threejs_snake_smoke.py`、`threejs_snake_blackbox_smoke.py`、`harness_trace_console_smoke.py`、`harness_trace_console_blackbox_smoke.py`、`playwright_smoke_utils.py`。
- 未同步 root 当前样本状态测试：`test_governance_workflow_sample_outputs.py`、`test_harness_burn_in_readiness.py`、`test_harness_pending_samples.py`、`test_harness_placeholder_replacement.py`、`test_harness_sample_append.py`、`test_harness_sample_followup_coverage.py`、`test_harness_sample_intake_bundle.py`、`test_harness_sample_outcome.py`、`test_harness_sample_templates.py`、`test_harness_upgrade_decision_candidate.py`、`test_harness_upgrade_decisions.py`；这些测试绑定当前项目 accepted samples / ready gaps / full CI summary workflow，不适合作为空 starter 默认断言。
- 未同步 demo/helper 测试：`test_threejs_snake_contract.py`、`test_playwright_smoke_utils.py`。

## 验证范围

```bash
cd new_pro_standard
../.codex/.venv/bin/python -m unittest discover -s tests
../.codex/.venv/bin/python -m unittest tests.test_agentic_red_team_samples tests.test_archive_candidate_monitor tests.test_burn_in_upgrade_decisions tests.test_check_burn_in_ledger tests.test_external_harness_decisions tests.test_governance_stage_alignment tests.test_harness_collection_config tests.test_harness_future_work_contract_candidate tests.test_harness_future_work_contracts tests.test_local_trace_summary_samples tests.test_loop_scope_monitor_samples tests.test_pre_tool_use_preflight_samples tests.test_runtime_reducer_metadata tests.test_stage_checkpoints tests.test_task_profile_audit tests.test_warning_sample_code_alignment
../.codex/.venv/bin/python scripts/check_tool_contracts.py
../.codex/.venv/bin/python scripts/check_stage_checkpoints.py
../.codex/.venv/bin/python scripts/check_task_profile_audit.py
../.codex/.venv/bin/python scripts/check_agent_productization_readiness.py
../.codex/.venv/bin/python scripts/check_harness_future_work_contracts.py
../.codex/.venv/bin/python scripts/check_harness_burn_in_readiness.py
../.codex/.venv/bin/python scripts/check_harness_collection_config.py
../.codex/.venv/bin/python scripts/check_harness_sample_templates.py
../.codex/.venv/bin/python scripts/check_burn_in_ledger.py
../.codex/.venv/bin/python scripts/check_burn_in_upgrade_decisions.py
../.codex/.venv/bin/python scripts/check_external_harness_decisions.py
../.codex/.venv/bin/python scripts/check_agent_eval_dataset.py
../.codex/.venv/bin/python scripts/run_agent_eval_dataset.py --dry-run
../.codex/.venv/bin/python scripts/check_agent_run_provenance.py
../.codex/.venv/bin/python scripts/check_ci_agent_contract.py
../.codex/.venv/bin/python scripts/check_runtime_execution_snapshots.py
../.codex/.venv/bin/python scripts/check_remote_trace_interop_report.py
../.codex/.venv/bin/python scripts/check_env_template_sync.py --warning-only
../.codex/.venv/bin/python scripts/check_agent_trace_schema.py
../.codex/.venv/bin/python scripts/check_workspace_sandbox.py
../.codex/.venv/bin/python scripts/check_skill_catalog.py
../.codex/.venv/bin/python scripts/check_repo_skills.py
../.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests
git diff --check -- new_pro_standard docs/ai/index.md docs/ai/working-context.md docs/ai/status docs/ai/changelog
```

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [new_pro_standard README](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/README.md)
