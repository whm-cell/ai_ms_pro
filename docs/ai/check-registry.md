# Check Registry

更新时间：2026-05-13
状态：已确认

## 作用

本文件记录 harness checks 的治理等级，避免把所有提醒都升级为 blocking，也避免只靠口头约定判断哪些检查必须跑。

## 等级定义

- `advisory`：只提示风险或压缩机会，不阻断。
- `review-required`：需要 PR 作者或 reviewer 明确看过；是否阻断由当前阶段决定。
- `blocking-candidate`：具备升级为 blocking 的候选条件，但必须先满足真实样本、误报率和修复路径要求。
- `blocking`：CI、hook 或远端规则已经强制；失败必须修复或显式记录例外。

## 当前分级

| Check | Level | CI coverage | 升级条件 |
| --- | --- | --- | --- |
| `check_ai_governance.py` | `blocking` | governance job / Stop hook | 已强制，继续保持 |
| `check_code_shape.py` | `blocking-candidate` | governance job uses `--all`; hooks use `--staged` | 新增大文件误报可控后保持或收紧 |
| Ruff Python linter / whitespace | `blocking` | governance job installs `.codex/requirements.txt`, runs `git diff --check`, then runs `python3 -m ruff check .codex/hooks scripts tests`; scope is `E9` plus Pyflakes `F` | 先观察 P0 误报和修复成本；后续再决定是否扩大到 style / import sorting / complexity 或纳入 hooks |
| `check_pr_touch_conflicts.py` | `blocking-candidate` | PR job blocks confirmed high-risk overlap; GitHub API `UNKNOWN` stays visible but non-blocking during burn-in | 两次真实多人 PR 样本证明收益后收紧 |
| `check_github_guardrails.py` | `review-required` | manual / PR review evidence | private Free 下只证明本地/CI evidence 与 plan-limited `UNKNOWN`；升级 plan 或改 public 后再考虑 required-check 阻断 |
| `check_branch_hygiene.py` | `blocking` | PR summary runs `--strict --current-pr`; main push summary runs `--strict`; manual cleanup commands remain explicit; Actions token 无法读取 check rollup 时 failed-open-PR 审计降级为 NOTE | active PR 预算、failed open PR、stale branch 持续稳定后再考虑调整阈值 |
| WS-01 / WS-02 / WS-03 browser smoke | `blocking` | smoke job runs `threejs_snake_smoke.py`, `threejs_snake_blackbox_smoke.py`, `harness_trace_console_smoke.py`, `harness_trace_console_blackbox_smoke.py`, and `godot_platformer_slice_smoke.py` | 已强制；Playwright browser install 与 CLI package 版本继续固定 |
| `check_requirements_shape.py` | `blocking-candidate` | manual / follow-up summary | PRD 导入、raw evidence / source quarantine、`pending` source boundary 和 external-web / third-party / unknown 样本证明误报可控后升级；`source-evidence/raw-prd-evidence` 不作为 canonical REQDOC，缺 trust/instruction/sanitization metadata 为 review-required |
| `check_agent_trace_schema.py` | `blocking-candidate` | governance job; runtime stop-hook tests validate producer output against the schema; local export adapter runs against the sample | Stop producer 与本地 adapter 已接入；后续若扩大到真实 trace-file batch validation，再根据误报率决定是否升级为 blocking |
| `export_agent_trace.py` | `advisory` | governance job runs local sample export | 本地 `local-otel-json` adapter 只证明转换层；OpenAI / OTLP / MCP / A2A 真实互通需要单独 contract 和 ADR |
| `export_agent_trace.py --format otlp-http-json` | `advisory` | local/unit tests cover explicit endpoint send; default CI path remains no-network | OTLP HTTP JSON pilot 只证明显式 endpoint + `network_exported` 证据链；外部 collector / OpenAI / MCP / A2A 仍需单独 ADR |
| `check_agent_eval_dataset.py` | `advisory` | governance job | 已包含 skill-harness 回归样本；真实 eval 执行、误报率、CI 成本和模型质量结论需要后续样本 |
| `run_agent_eval_dataset.py` | `advisory` | governance job runs `--dry-run`; selected local evals are manual | deterministic grader 已落地；真实 eval 执行、误报率、CI 成本和模型质量结论需要后续样本 |
| `check_tool_contracts.py` | `blocking-candidate` | governance job | MCP-like tools 或高影响工具 contract 增多后，根据误报率和 automation mode 使用情况升级 |
| `collect_harness_sample_gaps.py` | `advisory` | governance job runs collector | 只列出 security / guardrail / workflow 真实样本缺口；不自动生成证据，不升级 blocking |
| `check_change_triggered_followups.py` | `advisory` | PR / main push summary；包含 high-impact-agent-actions review-required advisory | 不直接升级；只驱动其他 checks 与人工确认 |
| `check_context_budget.py` | `blocking` | governance job / pre-commit / `check_ai_governance.py`; Stop hook inherits through governance check | 默认面、skill catalog、raw source、static task packet 达到 90% 压缩触发线或硬预算超限时阻断；`--warning-only` 仅保留人工审计输出 |
| `check_archive_candidates.py` | `advisory` | manual | 不自动归档；保持主 Agent 语义判断 |
| `check_skill_usage_samples.py` | `advisory` | manual | 只证明 skill 样本是否足够，不阻断业务 |
| `check_repo_skills.py` | `review-required` | manual / starter validation | skill 结构频繁变更后再考虑 CI |
| `check_skill_catalog.py` | `review-required` | governance job / starter validation | `.codex/skills` vendor/proxy/lock 与 `--check-output` 样本证明误报可控后再考虑升级为 blocking |
| Scorecard / CodeQL / SBOM / dependency review / secret scanning advisory | `advisory` | single `security-evidence` job with artifacts; dependency review PR job; secret scanning only when external evidence or plan supports it; 首轮 PR + main push evidence 已通过，CodeQL code-scanning 上传注解按 triage 处理 | 按 `docs/ai/security/security-evidence-triage.md` burn-in 后依据严重度、误报率、owner 和修复路径逐项升级 |
| `agentic-control-matrix.md` | `review-required` | manual / security review evidence | 只做 OWASP / NIST 风格控制映射；真实样本、owner、误报率和修复路径满足后才推动具体 check 升级 |

## 升级规则

- 一个 advisory 或 review-required check 不能直接升为 blocking。
- 升级前必须至少有两次真实样本，且记录误报、修复路径、CI 成本和 reviewer 负担。
- 升级决策进入 `status` 或 `ADR`；`AGENTS.md` 只补触发句，不展开完整执行细节。
