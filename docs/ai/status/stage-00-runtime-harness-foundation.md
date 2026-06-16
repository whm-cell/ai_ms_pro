# Stage-00 Runtime Harness Foundation Status

更新时间：2026-06-16
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

- 2026-06-03 至 06-08 已完成 capability state/evidence 聚合、bounded vnext、external decisions、`default_permission` 和 opt-in Prototype Design Brief；外部副作用与能力宣称仍由 activation gates 阻断。
- 2026-06-12 至 06-14 已新增 evidence-based coding standards、Agent Productization Readiness、mixed-stack code-shape scope、Config Contract Boundary 和 `$enterprise-code-boundary-maintenance` Candidate skill；这些均保持 review-required / blocking-candidate 边界，不声明生产配置、secret manager、远端部署、生产观测或新 lint blocking 完成。
- 2026-06-15 已修复 WS-01 / WS-02 Playwright smoke 在 Windows 下直接调用 `npx` 找不到 `.cmd` 启动器的问题；macOS / Linux 继续使用 plain `npx`，并保持 `shell=False`。
- 2026-06-15 已将公共 harness 机制增量同步到 `new_pro_standard`，并过滤为 starter-safe 边界；本 repo 的 REQ/WS、accepted samples、runtime artifacts 和 demo apps 不复制。
- 2026-06-16 已新增 Coding Agent / Browser Harness Selection、Bounded Loop Triage 与 Mock Data Boundary：前者 source-backed 地调整 comparator/transport 默认口径，后者把 capability summary 与 sample queue 汇总为 operator-reviewed next-action candidates，mock-data boundary 早期发现页面/组件中的大型 inline mock；三者都不新增 runtime claim。

## 本阶段关键成果

- `requirements -> implementation -> smoke -> runtime promotion -> status` 已跑通；CI blocking smoke 仍只覆盖 WS-01 / WS-02。
- GitHub、agentic standards、tool contracts、sample gaps、runtime compression、context budget、code-shape、prototype brief、coding/config/mock-data/enterprise/productization/loop triage 均已进入 bounded checks / references；细则不放回默认上下文。
- Capability 聚合保持 local-first：runtime artifact 是本地恢复材料；verified remote、hosted trace、MCP/A2A、native sandbox、外部 collector、真实 CI agent workflow 和生产原型能力均未声明完成。
- External decisions / default permission / execution wrapper 只覆盖 source-backed、bounded local/no-effect 改进；wrapper report 显式显示 `native sandbox: false`。
- Coding/browser selection 与 bounded loop triage 只改变选择口径和候选排序，不创建 scheduler、MCP/A2A、native sandbox、hosted eval/trace 或真实 CI agent workflow。
- Config Contract Boundary 只把 env template、typed registry、scan roots、allowed literal paths 和 pattern 变成可审计契约；provider-specific 规则必须在 `.codex/harness.toml` 配置，不写死在通用 checker。
- WS-01 / WS-02 Playwright smoke 的 `npx` 解析已集中到共享 helper；直接 smoke 与 blackbox smoke 均可在 Windows 通过，且不改变验证范围或外部能力声明。
- `new_pro_standard` 已同步 hook/runtime、sample-gap、burn-in、productization readiness、config/enterprise boundary、eval、tool-contract、checkpoint 和 code-shape 公共逻辑；模板内相关 ledger 均为 empty / deferred / pending starter state。

## 风险与阻塞

- GitHub remote required checks / review / 禁直推在 private Free 下仍是 `UNKNOWN`。
- Remote interop、cross-task resume、multi-agent、loop triage、external decisions、高影响动作、runtime drift、guardrail/security/runtime token pressure、coding/enterprise/product readiness 都仍缺真实样本、误报率、修复路径或 owner evidence；不得升级为完成或 blocking。
- 产品级 agent readiness 当前只是缺口雷达；未来新增产品 agent 必须新增 target assessment。
- Config Contract Boundary 不能被写成生产配置管理完成；它不验证外部部署 secret、不保存本机 `.env`、不证明远端环境已同步。
- Context budget 仍需压缩；legacy code-shape 大文件按独立小切片处理。

## 本轮收敛

- `.codex/runtime/*` tracked verification artifacts 已从 canonical change surface 移除，生成目录改为 ignore。
- Default context surface 降到预算线以下；ADR-002/003 已归档，当前 ADR 数低于预算。
- 记录 1 条 bounded high-impact confirmation real sample；cross-task resume 仍因缺真实非 harness 任务样本保持 open。
- `.codex/hooks.json` 已改为 portable hook launcher，Windows 进入 PowerShell runner，macOS / Linux 进入 POSIX runner，避免 `.py` 文件关联弹窗并消除跨宿主同步漂移。

## 下一阶段重点

- 提交前收敛 canonical change surface，`.codex/runtime/*` 不作为 canonical artifact。
- 继续观察 capability summary；指标只支持决策，不自动升级 claim。
- 对 cross-task resume、remote interop 和 high-impact guardrail 只采集真实 bounded sample；synthetic 或 local-only 证据不得冒充 accepted remote / cross-task proof。
- 下一轮优先补真实 cross-task resume sample、ADR-017 允许的 remote endpoint pilot，以及 code-quality / product-agent / high-impact guardrail 的真实样本；所有升级仍按 check registry 的样本、误报率、修复路径、CI 成本和 owner 要求执行。
- 后续 coding-agent 或 browser harness 对比先按 Coding Agent / Browser Harness Selection 做默认选择；偏离 `mini-swe-agent` comparator 或 CLI / skills-first browser smoke 口径时，需要写明 source-backed reason 和不新增能力 claim。
- 若后续项目需要 provider / model / endpoint 边界，先把 pattern 和 registry path 写入 `[config_contracts]`，再运行 `check_config_contract.py`；不要把 provider-specific literal 写进通用 checker。
- 若后续页面需要样例数据，优先放入 `[mock_data_boundary]` 声明的 fixture / scenario surface；产品 runtime path 中的大型 inline mock 和 mock-like import 先按 `check_mock_data_boundary.py` 输出做 review-required 处理，不自动删除旧代码。
- 压缩完成型 handoff / status 细节，合并或 supersede 旧 ADR，避免默认面超过 context gate。
- legacy code-shape 大文件按独立维护小切片拆分，避免和 capability schema 改动混合。

## Next Best Work Review

- Planned next work：继续 Stage-00 harness 维护小切片。
- Decision：continue
- Reason：当前优化是稳定、降噪和证据补强，不改变 stage goal、REQ/WS 范围或 blocking policy。
- User confirmation required：no

## 验收判断

- 本轮优化完成后，context budget 应低于 warning threshold，ADR count 应低于预算，code-shape legacy warning 应消失。
- High-impact confirmation 只能计为 local repo governance cleanup sample；cross-task resume、verified remote 和 external collector 仍不得声明完成。
- Task outcome eval 的 warn/review 语义仍是本地 deterministic signal；bounded loop triage、CI agent contract、local wrapper 和 multi-agent sample 也只是 bounded harness evidence，不是平台完成证明。
- External harness decision audit 通过只能证明四类 source-backed operator decision 与 default-permitted local/no-effect scope 当前一致；不能证明任何外部运行面或托管能力。

## 关联文档

- [Harness Remaining Work](../harness-open-items.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Harness Capability Model](../harness-capability-model.md)
- [Coding Agent And Browser Harness Selection](../standards/coding-agent-browser-harness-selection.md)
- [Mock Data Boundary](../standards/mock-data-boundary.md)
- [Agentic Control Matrix](../security/agentic-control-matrix.md)
- [Tool Contracts](../tool-contracts/README.md)
