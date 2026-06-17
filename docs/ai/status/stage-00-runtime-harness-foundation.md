# Stage-00 Runtime Harness Foundation Status

更新时间：2026-06-17
阶段：stage-00
状态：进行中

## 需求与工作流标识

- Requirement IDs：REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs：WS-01, WS-02
- Active validation：WS-01 Three.js Snake 与 WS-02 Harness Trace Console。

## 当前阶段目标

- Runtime / Governance / Verification 三层 harness 已可用；当前阶段从 closeout 转为 bounded capability 增量建设。
- 新增能力限定为 `runtime durability`、`bounded observability / interop`、`task-quality eval` 和 bounded loop triage，不转向通用云端 agent platform。

## 当前完成度

- 2026-06-03 至 06-17 已完成 capability 聚合、bounded vnext、external decisions、productization/config/mock-data/data-activation/coding-browser/loop triage 与 optimization defaults 等增量；这些只改善选择、证据、运行指标和 review-required 可见性，外部副作用与能力宣称仍由 activation gates 阻断。
- 2026-06-15 已修复 WS-01 / WS-02 Playwright smoke 的跨平台 `npx` 解析，并把公共 harness 机制 starter-safe 同步到 `new_pro_standard`；不复制本 repo 的 REQ/WS、accepted samples、runtime artifacts 或 demo apps。

## 本阶段关键成果

- `requirements -> implementation -> smoke -> runtime promotion -> status` 已跑通；CI blocking smoke 仍只覆盖 WS-01 / WS-02。
- GitHub、agentic standards、tool contracts、sample gaps、runtime compression、context budget、code-shape、prototype/config/mock-data/enterprise/productization/optimization defaults 均已进入 bounded checks / references；细则不放回默认上下文。
- Real Data Activation Gate 已把新项目 smoke/mock 退场固化为 `[data_activation].mode` 审计信号；`smoke`、`shadow-real`、`real` 只改变 review-required 检查强度，不迁移数据、不删除 fixture、不声明真实数据质量。
- Starter bootstrap Python runtime 解析已支持父级 `.env` allowlisted Python selector 与 pyenv 版本回退，降低新项目 `.codex/.venv` 初始化落到系统 Python 3.9 的概率；该能力不复制 `.env`，不读取任意 secret，不提交 `.codex/.venv`。
- Capability 聚合保持 local-first：runtime artifact 是本地恢复材料；verified remote、hosted trace/eval、MCP/A2A、native sandbox、外部 collector、真实 CI agent workflow 和生产原型能力均未声明完成。
- External decisions、coding/browser selection、bounded loop triage、optimization defaults 与 execution wrapper 只覆盖 source-backed local/no-effect 改进；`native_sandbox=false`、`model_usage=none` 和 cost=0 都是边界元数据，不是平台能力证明。

## 风险与阻塞

- GitHub remote required checks / review / 禁直推在 private Free 下仍是 `UNKNOWN`。
- Remote interop、cross-task resume、multi-agent、loop triage、external decisions、高影响动作、runtime drift、guardrail/security/runtime token pressure、coding/enterprise/product readiness 都仍缺足量真实样本、误报率、修复路径或 owner evidence；不得升级为完成或 blocking。
- 产品级 agent readiness 当前只是缺口雷达；未来新增产品 agent 必须新增 target assessment。
- Config Contract Boundary 不能被写成生产配置管理完成；它不验证外部部署 secret、不保存本机 `.env`、不证明远端环境已同步。
- Context budget 仍需压缩；legacy code-shape 大文件按独立小切片处理。

## 本轮收敛

- `.codex/runtime/*` tracked verification artifacts 已从 canonical change surface 移除，生成目录改为 ignore。
- Default context surface 降到预算线以下；ADR-002/003 已归档，当前 ADR 数低于预算。
- 记录 1 条 bounded high-impact confirmation real sample；PreToolUse 已收集 2/2 accepted real warning samples（含 1 个 sensitive-output false positive）并记录 `keep-advisory` 决策；cross-task resume 仍因缺真实非 harness 任务样本保持 open。
- `.codex/hooks.json` 已改为 portable hook launcher，Windows 进入 PowerShell runner，macOS / Linux 进入 POSIX runner，避免 `.py` 文件关联弹窗并消除跨宿主同步漂移。

## 下一阶段重点

- 提交前收敛 canonical change surface，`.codex/runtime/*` 不作为 canonical artifact。
- 继续观察 capability summary；指标只支持决策，不自动升级 claim。
- 对 cross-task resume、remote interop、PreToolUse warning 和 high-impact guardrail 只采集真实 bounded sample；synthetic、placeholder 或 local-only 证据不得冒充 accepted remote / cross-task proof；PreToolUse 已达升级讨论门槛但保持 advisory。
- 下一轮优先补真实 cross-task resume sample、ADR-017 允许的 remote endpoint pilot，以及 code-quality / product-agent / high-impact guardrail 的真实样本；所有升级仍按 check registry 的样本、误报率、修复路径、CI 成本和 owner 要求执行。
- 后续产品级 agent、sandbox、CI coding-agent、hosted eval 或 MCP/A2A 方向先走 Harness Optimization Decision Defaults：comparison-only / task-shape gated / explicit confirmation，不从趋势报告直接升级 runtime。
- 后续 coding-agent/browser、provider/model/endpoint、mock-data 或 product-agent 方向分别按对应 standard / config route 处理；偏离默认口径时写明 source-backed reason 和不新增 capability claim。
- 压缩完成型 handoff / status 细节，合并或 supersede 旧 ADR，避免默认面超过 context gate。
- legacy code-shape 大文件按独立维护小切片拆分，避免和 capability schema 改动混合。

## Next Best Work Review

- Planned next work：继续 Stage-00 harness 维护小切片，优先补真实 evidence 与 run metrics。
- Decision：continue
- Reason：当前优化是稳定、降噪、运行指标补强和默认决策收敛，不改变 stage goal、REQ/WS 范围或 blocking policy。
- User confirmation required：no

## 验收判断

- High-impact confirmation 只能计为 local repo governance cleanup sample；cross-task resume、verified remote 和 external collector 仍不得声明完成。
- Task outcome eval、bounded loop triage、CI agent contract、local wrapper、run metrics 和 multi-agent sample 都只是 bounded harness evidence，不是平台完成证明。

## 关联文档

- [Harness Remaining Work](../harness-open-items.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Harness Capability Model](../harness-capability-model.md)
- [Harness Optimization Decision Defaults](../standards/harness-optimization-decision-defaults.md)
- [Coding Agent And Browser Harness Selection](../standards/coding-agent-browser-harness-selection.md)
- [Mock Data Boundary](../standards/mock-data-boundary.md)
- [Agentic Control Matrix](../security/agentic-control-matrix.md)
- [Tool Contracts](../tool-contracts/README.md)
