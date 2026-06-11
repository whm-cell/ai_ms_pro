# Agentic Red-Team Samples

更新时间：2026-05-25
状态：v1 / advisory burn-in

## 作用

本文件定义 G6/G7 red-team / surface-control 的 bounded 样本账本，用来记录 prompt injection、tool-output injection、skill squatting、memory poisoning、handoff / A2A confusion、cascade autonomy、human confirmation 和 sandbox overclaim 等风险的真实或可复跑证据。

默认样本文件是 `agentic-red-team-samples.jsonl`，由 `scripts/check_agentic_red_team_samples.py` 校验。

当前账本已有 8 个 accepted local-replay 样本覆盖全部 8 类 red-team risk family，并有 2 个 `sandbox-claim-honesty` accepted real incidents；其它 risk family 的 real incident 仍需 burn-in。

## 样本类型

- `local-replay`：可由本仓库测试或 checker 复跑的本地样本。
- `synthetic-regression`：只证明 schema / regression 覆盖，不计入 replay-or-real burn-in。
- `real-incident`：真实外部攻击、真实第三方工具 / skill、真实 handoff / sandbox 争议等事件。
- `manual-review`：人工审计记录，必须继续补 replay 或 real evidence 才能支撑升级。

## 字段

- `schema_version`：固定为 `agentic-red-team-sample/v1`。
- `control_ids`：映射到 `agentic-control-matrix.md` 的 `AC-xx`。
- `risk_family`：`prompt-injection`、`tool-output-injection`、`skill-squatting`、`memory-poisoning`、`a2a-handoff-confusion`、`cascade-autonomy`、`human-confirmation` 或 `sandbox-claim-honesty`。
- `source_type` / `outcome`：记录样本来源与处理结果。
- `local_only` / `no_external_claim`：accepted 样本必须为 `true`，避免把本地 replay 说成外部互通或真实攻击。
- `false_positive_rule`：每个样本必须说明何时可判为误报。
- `replay_commands`：`local-replay` 样本必须给出可复跑命令。
- `evidence_refs` / `checker_refs`：`evidence_refs` 必须指向存在的 repo-relative 共享文档、脚本或测试，可带 markdown anchor、pytest node id 或 JSONL 行号 selector；不引用 raw runtime。

## 边界

- 不存 prompt、transcript、cwd、raw tool output 或 `.codex/runtime/*` 路径。
- 本地 replay 可以证明规则可复跑，不能证明真实外部攻击、真实 MCP / A2A / OpenAI hosted interop 或 native sandbox provider。
- `upgrade_signal=candidate` 只能用于 `real-incident` 样本；本地 replay 只能给 `none` 或 `weak`。
- 该检查保持 advisory，不自动改变 `agentic-control-matrix.md` 的 control level。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_agentic_red_team_samples.py
python3 tests/test_agentic_red_team_samples.py
```

相关 replay 命令：

```bash
python3 tests/test_requirements_shape.py
python3 tests/test_skill_catalog.py
.codex/hooks/run_with_repo_python.sh tests/test_workspace_sandbox.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/handoffs/active/demo.md
.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/security/agentic-control-matrix.md
.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/security/agent-action-guardrails.md
.codex/hooks/run_with_repo_python.sh scripts/check_skill_catalog.py
.codex/hooks/run_with_repo_python.sh scripts/check_workspace_sandbox.py
```
