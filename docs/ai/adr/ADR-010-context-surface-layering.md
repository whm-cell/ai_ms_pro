# Context Surface Layering

更新时间：2026-04-30
编号：ADR-010
标题：配置化默认上下文面与归档候选提醒
状态：已采纳

## 背景

- 默认入口如果持续承载阶段细节，会让简单开发任务继承过多历史上下文。
- 本仓库已经采用 `index -> working-context -> status -> active handoff` 的轻量恢复链路，但 active handoff 预算和归档候选阈值仍分散在脚本和文案中。
- 归档判断需要语义确认，不能交给 hook 或 reducer 自动移动共享文档。

## 决策

- 在 `.codex/harness.toml` 增加 `[context_surface]`，统一配置 active handoff 预算、archive candidate 最低分和是否达到预算即提醒。
- `check_ai_governance.py` 和 `check_archive_candidates.py` 读取同一配置；CLI 参数可临时覆盖 archive monitor 的预算与最低分。
- 保持 warning-only：脚本只提示候选和原因，不移动 handoff、不更新 `index` / `working-context` / `status`。
- `new_pro_standard` 同步同一机制，starter 生成文档也使用“configured budget”表述，避免重新写死阈值。

## 备选方案

- 方案 A：继续在脚本和文档中分别硬编码预算。
- 方案 B：将 archive candidate monitor 接入 Stop hook。
- 方案 C：让脚本自动归档完成型 handoff。

## 决策理由

- 配置化预算能让 root、starter 和 bootstrap 模板保持同一语义，减少后续漂移。
- Stop hook 默认提醒会增加简单任务噪音，违背小默认上下文目标。
- 自动归档需要判断 handoff 的未完成项、下一步动作和风险是否已经进入 `status` / backlog / ADR，仍应由主 Agent 人工确认。

## 影响

- 默认上下文治理链路明确为：小默认上下文 -> 按需加载细节 -> 阶段压缩 -> 阈值候选提醒 -> 人工语义归档。
- active handoff 达到配置预算时 governance check 会给 warning，但不阻断任务。
- archive candidate monitor 输出会包含配置预算、最低分和是否达到预算，便于压缩前审查。
- 跨平台 Python 与 hook renderer 的现有回归需要继续作为相关脚本变更的必跑项。

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [ADR-007 Governance Surface Budget](./ADR-007-governance-surface-budget.md)
