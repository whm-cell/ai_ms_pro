# Logging / Redaction Boundary

更新时间：2026-06-14
状态：review-required standard

## 作用

本标准约束 repo 内日志、诊断输出、trace metadata、telemetry 和 checker/report 输出的敏感信息边界。它不声明 SIEM、DLP、生产 observability 平台、日志采集管线、集中脱敏服务或远端告警治理已完成。

## 分类

- Safe metadata：可输出，例如规则名、状态码、路径、行号、非敏感枚举、耗时、计数和 bounded id。
- Sensitive value：不得输出，例如 secret、token、cookie、password、API key、数据库 URL、session、authorization header、env value。
- User / business payload：默认不输出原文；需要时只输出摘要、长度、hash、类型、字段名或人工确认后的 display-safe 内容。
- Provider / external payload：默认不输出 raw request/response；只输出 request id、provider code、状态和 display-safe 摘要。
- Runtime artifact：不进入共享 docs；如需诊断，保留在本地 runtime artifact 并写 bounded summary。

## 契约规则

- 日志和 checker 输出必须先判断 audience：developer-local、CI、user-facing、shared governance doc 或 external telemetry。
- 共享输出只能包含 key 名、规则名、路径、行号、状态和摘要，不包含 secret value、raw prompt、raw provider payload 或完整用户输入。
- 读取 env 时不得打印 env value；只能打印 key 名或缺失状态。
- 错误日志不得把 exception、request body、headers、cookies 或 provider raw payload 无过滤地 `JSON.stringify` / dump。
- 新增 logging helper 时要保留 redaction / allowlist 入口；不要让调用方手写分散脱敏逻辑。

## 等级边界

- 当前等级是 review-required。
- 本标准不证明生产日志系统已脱敏，不证明外部 telemetry 安全，不替代 secret scanning。
- 对安全、权限、账号、支付、provider、runtime trace 或用户内容路径的日志变更，应优先人工复核输出样本。

## 未来 Checker 升级条件

- 有至少 2-3 个真实变更样本证明常见风险模式稳定。
- 误报率、修复路径、CI 成本和 reviewer 负担已记录。
- 候选检查可先覆盖 `console.log/error`、logger 调用、`JSON.stringify(req|headers|process.env|error)`、env value 输出和 raw provider payload 输出。

## 验证建议

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```
