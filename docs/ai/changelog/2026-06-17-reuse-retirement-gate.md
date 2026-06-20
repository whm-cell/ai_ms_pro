# Reuse And Retirement Gate

日期：2026-06-17

## 新增功能

- 新增 `[reuse_retirement]` 配置段，用于开启代码复用候选和旧路径退场候选审计。
- 新增 `scripts/check_reuse_retirement.py`，默认输出 review-required 报告并退出 0；`--strict` 仅供人工或 burn-in 后手动验证。
- 新增 `docs/ai/standards/reuse-retirement-boundary.md`，明确复用、退场、no-write 和人工复核边界。

## 行为变化

- `.codex/harness.toml`、代码根目录、checker、测试或 standard 变更会触发 reuse-retirement follow-up 提示。
- Tool contract registry 记录该 checker 的 read-only / git-read 权限、危险 flag 和验证命令。
- Starter 默认配置包含同一 review-required gate，新项目可直接获得“先查复用、再判断退场”的审计信号。

## 修复问题

- 降低新增 harness 或业务路径时复制相似代码、保留旧 mock/smoke/legacy 路径而无人复核的风险。
- 把“是否应复用现有代码”和“旧路径是否应退场”从口头约束变成可运行的 bounded review。

## 破坏性变更

- 无。默认不是 blocking check，不自动修改业务代码、不删除旧文件。

## 边界

- 不证明候选文件是死代码。
- 不处理动态入口、CLI、hook、test fixture 或文档引用的完整可达性。
- 不替代 `check_code_shape.py`、代码审查或业务测试。

## 验证范围

- `scripts/check_reuse_retirement.py`
- `tests/test_reuse_retirement.py`
- `scripts/check_change_triggered_followups.py`
- `scripts/check_tool_contracts.py`
- `scripts/check_ai_governance.py`
- `scripts/check_context_budget.py`

## 关联文档

- [Reuse And Retirement Boundary](../standards/reuse-retirement-boundary.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
