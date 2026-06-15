# Task Profile Audit

更新时间：2026-05-25
状态：v1 / advisory

## 作用

本文件定义 P2 Task Profile Audit 的本地证据格式，用来检查 task profile 选择与实际读取面、验证面是否匹配。

它不是新的 always-on 规则层，也不要求用户手动标注每个任务；Agent 仍按 `AGENTS.md` 的 Task Discovery Protocol 自动分类。

## 证据格式

审计样本使用 JSONL，每行一个任务记录。默认样本位于 `task-profile-audit-sample.jsonl`。

字段：

- `schema_version`：固定为 `task-profile-audit-sample/v1`。
- `id`：样本编号。
- `gap_id`：采集模板写入 `GAP-WORKFLOW-TASK-PROFILE-AUDIT`；旧样本缺省时由该 ledger 默认归属补齐。
- `source_type`：`real-task`、`synthetic-regression` 或 `manual-review`。
- `outcome`：`accepted`、`pending` 或 `rejected`。
- `profile`：`simple`、`medium`、`complex`、`0-1-stage` 或 `recovery-dispute`。
- `task_summary`：任务摘要。
- `read_files`：实际读取或明确继承的上下文文件。
- `changed_files`：任务实际改动文件。
- `verification_commands`：本轮用于证明完成的命令。
- `requirement_ids` / `workstream_ids`：适用时填写；不适用时用 `traceability_note` 说明。
- `traceability_note`：非需求任务可写 `not-applicable: ...`，避免伪造 REQ/WS。
- `false_positive`：该 profile 选择或读面检查是否被判为误报。
- `process_tax_note`：记录治理读面 / 验证面的成本和收益判断。
- `evidence_refs`：必须指向存在的 repo-relative 共享治理文档、测试或命令引用；可带 markdown anchor、pytest node id 或 JSONL 行号 selector；不得引用 `.codex/runtime/*`。

## 当前规则

- 所有 profile 至少应保留 `docs/ai/index.md` 和 `docs/ai/working-context.md` 的短链路锚点。
- `simple` 任务不应默认读取 `docs/requirements/`、ADR、handoff 或 archive 等重治理面。
- `complex` 任务必须有 traceability closure：读过 traceability matrix、记录 REQ/WS，或明确 `not-applicable`。
- governance docs 变更必须带 `check_ai_governance.py` 验证。
- requirements 变更必须带 `check_requirements_shape.py` 验证。
- `0-1-stage` 任务必须读取 requirements index、traceability matrix、plan、stage status 和 workstream surface。
- `recovery-dispute` 任务必须读取 runtime 或 handoff recovery surface。
- raw transcript、prompt、cwd、完整工具输出和 `.codex/runtime/*` 路径不得进入共享样本。
- synthetic 样本只证明 schema 和 regression 覆盖，不计入真实 burn-in。
- accepted real samples 会按 profile 计数；starter 默认只带 synthetic regression 样本，不预置任何 accepted real burn-in 结论。新项目采集真实任务后再讨论升级。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_task_profile_audit.py
python3 tests/test_task_profile_audit.py
```

## 边界

- 该检查只校验显式记录的 audit artifact，不从完整 transcript 自动推断所有读取动作。
- 默认 CI 验证样本格式、真实 / synthetic 样本计数和规则可运行；真实任务样本仍需继续积累。
- 该检查保持 advisory；升级前必须先积累真实样本、误报率和修复路径。
