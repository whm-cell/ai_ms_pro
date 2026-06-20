# Reuse And Retirement Boundary

更新时间：2026-06-17
状态：review-required

## 目的

新增代码不应默认堆叠成第二套实现；被新路径替代的旧 smoke、mock、legacy 或 v1 路径也不应无限期留在 runtime / harness 面里。

本标准把“先找可复用代码”和“标记旧路径退场”变成 no-write / review-required 审计信号。

## 配置

```toml
[reuse_retirement]
enabled = true
scan_roots = [".codex/hooks", "app", "apps", "components", "lib", "packages", "pages", "scripts", "src"]
new_file_min_lines = 80
reuse_score_threshold = 4
max_candidates = 5
retirement_markers = ["demo", "deprecated", "dev", "fixture", "legacy", "mock", "old", "seed", "smoke", "v1"]
```

## 检查内容

- 新增或大改代码文件如果与现有文件的路径 token、函数名或 class 名高度相似，输出 `reuse-review-candidate`。
- 变更文件如果可能替代带 `legacy / old / mock / smoke / fixture / v1` 等 marker 的旧路径，输出 `retirement-review-candidate`。
- 每条 finding 只要求 reviewer 明确判断：复用、抽取、保留并说明原因、立即退场、或记录后续退场条件。

## 边界

- 不自动删除代码。
- 不证明候选文件一定未使用；动态 import、CLI entrypoint、hook、test fixture 和文档引用仍需人工复核。
- 不替代 `check_code_shape.py`；code-shape 管大小和结构，本检查管复用/退场候选。
- 默认退出 0；只有人工显式使用 `--strict` 时才在 finding/error 上非零退出。

## 推荐处理

- `reuse-review-candidate`：优先复用现有 helper / adapter / checker；若不复用，写清差异原因。
- `retirement-review-candidate`：选择 `retire_now`、`keep_with_reason` 或 `replace_by <path>`，避免旧路径长期漂浮。
- 对风险高的退场动作，先删除引用、补测试，再删除文件；不要让 checker 自动改代码。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_reuse_retirement.py
python3 tests/test_reuse_retirement.py
```
