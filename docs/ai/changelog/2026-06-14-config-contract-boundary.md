# Config Contract Boundary

更新时间：2026-06-14
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 Config Contract Boundary 标准，固定配置分类、入库 / 不入库边界、typed registry、env template、本机 env 和 runtime artifact 的职责。
- 新增 `[config_contracts]` harness 配置，用于声明 env template、本机 env、registry、扫描根、allowed literal paths、secret key pattern、config key pattern 和 literal pattern。
- 新增 `scripts/check_config_contract.py`，以配置驱动方式检查 secret-like key、配置 key、模型 ID、endpoint 或其它 literal 是否散落到未允许路径。
- 新增 `scripts/check_env_template_sync.py` 和 SessionStart hook，只比较 env key 集合并提示本机漂移，不读取、不打印、不覆盖 env 值。

## 修复问题

- 把 `demo_txt_t_proto` 中 provider 配置边界的做法抽象成通用机制，避免把 `qwen`、`wanx`、`DASHSCOPE_*`、`BAILIAN_*` 等 provider-specific 规则写死在通用 checker。
- 补齐 changed-file follow-up，让 env template、provider registry、deployment env template、hook config、workflow 和 config contract 标准改动会提示对应检查。

## 行为变化

- `.codex/hooks.json` 的 SessionStart 链路新增 env template drift warning hook；无 env template 配置时该检查为 no-op。
- `.gitignore` 明确忽略 `.env` / `.env.*`，保留 `.env.example`。

## 破坏性变更

- 无。新检查初始为 review-required，不升级 blocking，不改变 WS-01 / WS-02 active validation。

## 验证范围

- `python3 tests/test_harness_config.py`
- `python3 tests/test_config_contract.py`
- `python3 tests/test_env_template_sync.py`
- `python3 tests/test_hooks_config_sync.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_config_contract.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_env_template_sync.py --warning-only`
- `.codex/hooks/run_with_repo_python.sh scripts/sync_hooks_config.py --check`

## 关联文档

- [Config Contract Boundary](../standards/config-contract-boundary.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [AI 文档入口索引](../index.md)
