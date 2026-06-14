# Error Contract Boundary

更新时间：2026-06-14
状态：review-required standard

## 作用

本标准约束错误分类、错误码、HTTP 状态映射、用户可见文案和内部诊断信息之间的边界。它不声明全局错误码平台、跨服务 error registry、SLO/incident 平台或生产告警闭环已完成。

## 分类

- User-visible error：给用户或前端展示，必须稳定、可翻译、无内部实现细节。
- API contract error：对外响应契约，包含稳定 code、HTTP status、safe message 和必要上下文。
- Internal diagnostic：仅供开发/运维定位，可包含 bounded metadata，但不得泄露敏感值。
- Provider / dependency error：外部系统错误映射到本项目 code；不得直接透出 raw provider message。
- Programmer error：断言、不可恢复 bug 或 invariant violation，不应伪装成用户可修复错误。

## 契约规则

- API 或 service 边界不得直接返回 `error.message`、stack trace、raw exception、raw provider response 或数据库错误。
- 新增用户可见失败态时，必须明确 code、HTTP status、safe message、重试/修复语义和是否可归因于用户输入。
- 外部 provider / DB / queue / auth 错误必须映射为本项目错误分类；原始错误只能进入受控诊断摘要。
- 错误码和状态枚举应集中在已有 schema、registry、adapter 或标准文档中；不要在多个 API route 分散创造同义 code。
- 测试或 smoke 应覆盖主要失败路径，尤其是 permission denied、missing config、provider unavailable、timeout、invalid input 和 partial failure。

## 等级边界

- 当前等级是 review-required。
- 本标准不证明全仓库已有统一错误平台，也不要求一次性重构 legacy error handling。
- 涉及权限、安全、数据写入、外部 provider、部署或用户可见 API 的错误变更应优先复核。

## 未来 Checker 升级条件

- 有真实样本证明某些模式能稳定自动识别，例如 API response 直接使用 `error.message`、返回 stack、或 provider raw message。
- 升级前必须记录误报率、允许例外、修复模板和 CI 成本。
- 可先做 changed-file advisory，而不是直接 blocking。

## 验证建议

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```
