# new_pro_standard Harness Starter Sync

更新时间：2026-05-26
阶段或版本：stage-00
状态：已确认

## 新增功能

- `new_pro_standard` 同步 starter-safe runtime hook 能力：PreToolUse preflight、Stop runtime token pressure、Stop loop/scope monitor、runtime sanitizer、traceability resolver 和 local trace producer。
- `new_pro_standard` 同步 starter-safe verification gates：context-budget pre-commit、Ruff / whitespace CI、`.agents/skills` code-shape 覆盖和复制卫生 `.gitignore`。
- `new_pro_standard` 新增空样本闭环：`GAP-STARTER-*` gap catalog、空 sample-gap ledger、pending candidate template 和 no-write sample evidence checker。

## 修复问题

- 修正 starter checked-in `.codex/hooks.json` 的平台默认值，使 macOS / Linux 复制后不再保留 Windows-only PowerShell hook command。
- 补齐 starter `runtime_token_budget` 配置，避免 Stop token-pressure hook 只能依赖脚本内默认阈值。
- 补充 starter 复制卫生，避免 `.DS_Store`、`__pycache__`、`.ruff_cache`、runtime tool-output 等本地材料进入新项目共享 truth。

## 行为变化

- `scripts/bootstrap_harness.py` 会渲染包含 PreToolUse / Stop warning hooks 的 `.codex/hooks.json`，并保留 Windows PowerShell runner 配置。
- starter 的 sample evidence 机制只接受新项目真实 bounded evidence；synthetic、placeholder、runtime JSONL、raw transcript、secret 和旧项目 ledger rows 不能作为 accepted real evidence。
- starter 显式保留 `runtime_token_budget` 配置，Stop token-pressure warning 可以由新项目调整阈值。

## 破坏性变更

- 无。当前项目真实 REQ/WS、accepted sample rows、upgrade decision 结论、runtime artifacts 和 WS-01 / WS-02 demo apps 仍不复制进 starter。

## 验证范围

- 在 `new_pro_standard` 下运行 `python -m unittest discover -s tests`：160 tests passed。
- 运行 `check_ai_governance.py`、`check_context_budget.py`、`check_requirements_shape.py`、`check_code_shape.py --all`。
- 运行 `ruff check .codex/hooks scripts tests`、`git diff --check -- new_pro_standard`。
- 运行 `collect_harness_sample_gaps.py --include-future --json`、`check_harness_sample_gap_evidence.py`、`plan_harness_sample_collection.py --gap-id GAP-STARTER-HIGH-IMPACT-ACTION --sample-template`。
- 运行 PreToolUse / Stop token pressure / Stop loop-scope hook smoke 和 Windows hook renderer smoke。

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [new_pro_standard README](/Volumes/usd/codes/go_projects/ai_ms_pro/new_pro_standard/README.md)
