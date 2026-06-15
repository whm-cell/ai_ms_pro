# Config Contract Boundary

更新时间：2026-06-14
状态：review-required mechanism

## 作用

本标准把“配置文件约定俗成”变成可审计的 harness 契约。它不提供生产配置中心、secret manager、Kubernetes / CI secret 接入或远端部署验证；它只约束 repo 内配置声明、模板、registry 和生产代码之间的边界。

## 配置分类

- Mechanism config：入库，例如 `.codex/harness.toml`、`.codex/hooks.json`、workflow、package scripts 和 checker 配置。
- Typed registry：入库，例如 provider/model/endpoint/env key 的唯一声明面。
- Env template：入库，只放 key、空值、非敏感示例值和说明。
- Local / deploy secret：不入库，例如 `.env`、`.env.local`、真实 token、密码、数据库 URL。
- Runtime artifact：不入库且不是 canonical truth，例如 `.codex/runtime/*`。

## 契约规则

- `.codex/harness.toml` 的 `[config_contracts]` 声明 env template、本机 env、registry、扫描根、允许出现配置字面量的路径、敏感 key pattern、配置 key pattern 和 literal pattern。
- `scripts/check_config_contract.py` 从配置读取规则，检查 secret-like key、配置 key、模型 ID、endpoint 或其它 literal 是否只出现在 registry / allowed paths / env template 中。
- `scripts/check_env_template_sync.py` 只比较 env template 与本机 env 的 key 集合，不读取、不打印、不覆盖任何值。
- `.codex/hooks/session_start_env_template_sync.py` 只在 SessionStart 提示本机 env 缺失 key；该提示 warning-only，不把 `.env` 变成共享 truth。
- Provider-specific 规则必须进入 `[config_contracts]`，不得硬编码在通用 checker 中。

## 等级边界

- `check_env_template_sync.py` 是 review-required / warning-only 运行面，适合提醒本机运行配置滞后。
- `check_config_contract.py` 初始为 review-required；项目可在真实样本、误报率、修复路径和 CI 成本明确后再讨论 blocking-candidate 或 blocking。
- 检查输出只能包含规则组、路径、行号和 key 名；不得输出 env value、secret、raw prompt、runtime transcript 或 `.codex/runtime/*` 原料。

## 可迁移示例

`demo_txt_t_proto` 的 provider boundary 可用以下配置形态表达，而不需要把 Bailian / DashScope / qwen / wanx 写死进通用脚本：

```toml
[config_contracts]
enabled = true
env_template_paths = [".env.example"]
local_env_paths = [".env", ".env.local"]
registry_paths = ["lib/xhs/ai/providerConfig.ts"]
scan_roots = ["app", "components", "lib", "services"]
allowed_literal_paths = ["lib/xhs/ai/providerConfig.ts"]
secret_key_patterns = ["DASHSCOPE_API_KEY"]
config_key_patterns = ["DASHSCOPE_[A-Z_]+", "BAILIAN_[A-Z_]+"]
literal_patterns = ["qwen[0-9A-Za-z_.-]+", "wanx[0-9A-Za-z_.-]+"]
```

当前 `ai_ms_pro` 只启用通用机制，尚未声明项目特定 provider pattern。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_config_contract.py
.codex/hooks/run_with_repo_python.sh scripts/check_env_template_sync.py --warning-only
python3 tests/test_config_contract.py
python3 tests/test_env_template_sync.py
```
