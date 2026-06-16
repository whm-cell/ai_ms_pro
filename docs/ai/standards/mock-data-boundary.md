# Mock Data Boundary

更新时间：2026-06-16
状态：review-required mechanism

## 作用

本标准把“页面里先塞一大份 mock 数据”改成可审计的 harness 边界。目标是让产品页面、组件和 runtime code 尽早依赖真实 adapter / API、network handler、scenario factory 或受控 fixture，而不是把大型样例数组长期留在页面文件里。

它不自动清理旧代码、不替换业务数据层、不生成后端 API，也不把所有 mock 都视为错误。开发样例、story、测试和显式 fixture 仍允许存在。

## 边界规则

- `.codex/harness.toml` 的 `[mock_data_boundary]` 声明扫描根、fixture 路径、允许消费 mock 的路径、runtime import denied paths、scenario manifest paths 和 inline 阈值。
- `scripts/check_mock_data_boundary.py` 默认扫描 `app`、`apps`、`components`、`pages`、`src`，并额外检查声明为 manifest-required 的 fixture roots。
- 大型 mock-like inline 数组、mock-like `Array.from({ length })`、runtime 路径中的 mock/fixture import、未登记大型 fixture 和未固定 seed 的 fixture factory 输出 `REVIEW:`。
- `fixtures`、`mocks`、`mock-data`、`tests/fixtures`、`stories/fixtures`、`dev-seeds` 等声明路径是允许的大型样例数据存放面。
- `*.test.*`、`*.spec.*`、`*.stories.*` 和 `tests/**` 可以消费 mock-like module；产品 runtime path 应改走 adapter、scenario factory 或真实边界。
- 推荐落点顺序：真实 adapter / API -> network handler -> scenario factory -> fixture。

## Scenario Manifest

大型 fixture 应绑定到 `mock-data-scenario/v1` JSONL manifest。默认 manifest 路径：

- `mock-data/scenarios.jsonl`
- `mocks/scenarios.jsonl`

每行必须包含：

- `schema="mock-data-scenario/v1"`
- `id`
- `data_paths`
- `surface`：`dev | test | story | demo | contract-sample`
- `source_truth`
- `adapter`：`fixture | scenario-factory | msw-handler | playwright-route | openapi-example | manual-seed`
- `owner`
- `expires_at`

checker 会校验 data path 存在、manifest id 不重复、同一 data path 不被多个 active row 绑定。当前只校验 repo-local manifest 语义，不安装 MSW、Prism、Playwright，不从 OpenAPI 生成 mock。

## 等级边界

- 默认检查是 no-write / review-required；发现问题时退出码仍为 0，避免首轮误报阻断开发。
- `--strict` 只在项目经过真实样本、误报率和迁移路径 burn-in 后才适合接入 blocking。
- 检查只报告路径、行号、finding code、suggested layer、suggested path 和边界建议，不读取 runtime transcript、不外发、不修改项目文件。
- 旧代码不会被自动删除；需要主 Agent 或 reviewer 明确确认后，按业务上下文迁移到 fixture / factory / adapter。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_mock_data_boundary.py
.codex/hooks/run_with_repo_python.sh scripts/check_mock_data_boundary.py --json
python3 tests/test_mock_data_boundary.py
```
