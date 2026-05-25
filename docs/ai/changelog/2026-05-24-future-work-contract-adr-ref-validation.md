# Future Work Contract ADR Ref Validation

- Date: 2026-05-24
- Scope: harness future-work contract control plane
- Status: landed

## 新增功能

- `scripts/check_harness_future_work_contracts.py` 现在会在 contract 进入 `approved-for-sampling` 时校验 ADR refs。
- `scripts/check_harness_future_work_contract_candidate.py <candidate-jsonl>` 通过底层 contract checker 继承相同的 approved sampling ADR gate。

## 修复问题

- 防止 future-work contract 只填任意 `adr_refs` 字符串就被视为可采样。
- 防止 candidate gate 接受缺失 ADR、非 repo ADR 路径，或未覆盖 contract 身份和边界字段的 ADR。

## 行为变化

- `approved-for-sampling` 必须引用存在的已采纳 repo ADR。
- ADR 必须覆盖 `gap_id`、contract id、`auth_model`、`endpoint_or_authority_scope`、`redaction_or_boundary_model` 和 `cost_or_stop_boundary`。
- 当前 `needs-adr` contracts 保持 blocked，不改变现有 readiness / pending sample 统计。

## 破坏性变更

- 无。该检查仍是 advisory / no-write；只收紧未来手动批准采样前的 deterministic review。

## 验证范围

- `python3 tests/test_harness_future_work_contracts.py`
- `python3 tests/test_harness_future_work_contract_candidate.py`
- `python3 tests/test_harness_sample_templates.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
