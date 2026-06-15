# Runtime Side Effect Boundary

更新时间：2026-06-14
状态：review-required standard

## 作用

本标准约束网络、数据库、文件系统、队列、外部 provider、进程执行和部署环境访问等 runtime side effect 的代码边界。它不声明 service mesh、远端 side-effect 审计、生产 sandbox、集中 egress policy 或完整 distributed transaction 机制已完成。

## 分类

- Pure domain logic：不直接访问网络、DB、文件系统、queue、env 或 provider。
- Adapter / client：封装外部系统调用，负责 timeout、retry、auth、redaction 和错误映射。
- Repository / persistence：封装 DB、migration、transaction 和 schema 边界。
- Runtime harness / script：执行本地验证、hook、smoke 或 tooling；必须明确本地/远端、副作用和输出边界。
- External effect：任何会影响远端系统、费用、权限、发布、部署或持久数据的动作。

## 契约规则

- 业务核心层不应直接散落 `fetch`、DB client、`fs`、`process.env`、queue producer 或 provider SDK；优先通过 adapter / repository / config registry。
- 外部调用必须声明 timeout、失败映射、重试/幂等策略和 redaction 边界；没有策略时应显式记录为 review 风险。
- 写入型 API、任务创建、支付/权限/发布/部署类动作必须考虑 idempotency 或重复提交行为。
- 本地脚本和 smoke 必须区分 local-only、fake provider、pilot remote 和 verified remote；不能把 local runner 说成生产部署。
- 任何外部副作用、高费用动作、权限变更或部署动作都需要显式用户确认或已有 repo gate。

## 等级边界

- 当前等级是 review-required。
- 本标准不阻止所有直接 side effect；它要求高风险路径有清晰边界和复核。
- 现有 legacy 散落调用不自动成为本轮重构范围；只处理当前任务触达的 changed surface。

## 未来 Checker 升级条件

- 有真实样本证明 direct side-effect 扫描能有效发现问题，且不会大量误报测试、smoke、adapter 和 harness 脚本。
- 可先从 changed-file advisory 开始，扫描 `fetch(`、DB client、`fs`、queue/provider SDK、`child_process` 和 `process.env`。
- 升级 blocking 前必须有例外配置、允许路径、修复路径和 CI 成本记录。

## 验证建议

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```
