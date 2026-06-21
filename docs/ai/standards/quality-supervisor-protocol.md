# Quality Supervisor Protocol

更新时间：2026-06-21
状态：candidate / disabled by default
标准 ID：`quality-supervisor-protocol/v1`

## 作用

本标准吸收 `demo_txt_t_proto` 的质量监督子代理做法，但在本项目保持 bounded：它只定义当前任务的只读复核协议，不创建自动编排，不证明 hooks 可以启动 subagent，也不声明 scheduler、A2A、hosted eval 或真实 CI agent workflow。

## 配置

`.codex/harness.toml` 的 `[quality_supervisor]` 目前默认：

- `enabled = false`
- `default_scope = "material-task"`
- `supervisor_role = "quality-supervisor"`

开启前必须同步 `AGENTS.md`、本标准、`check-registry.md`、`docs/ai/index.md` 与适用验证路由，并明确跳过条件。开启后仍然是主 Agent 显式调用可用工具；hooks cannot spawn subagents。

## 协议边界

- Quality supervisor 默认只读，检查 scope fit、REQ/WS 绑定、文档影响、验证覆盖、secret 暴露、runtime artifact 边界和能力宣称是否过度。
- Main agent owns canonical writes to `docs/ai/*`, `docs/requirements/*`, `AGENTS.md`, harness config, checks, and final user-facing claims.
- 跳过原因必须可解释，例如 direct answer、single-command、explicit user opt-out、tool unavailable、privacy or secret boundary。
- Supervisor output 是 review input，不是 canonical truth；稳定结论仍需主 Agent 提升到 status、handoff、ADR、requirements、traceability、check registry 或 changelog。

## 检查

`scripts/check_quality_supervisor_protocol.py` 读取 `[quality_supervisor]`：

- disabled 时只确认配置可解析并输出 skip / OK。
- enabled 时要求本标准、AGENTS、check registry 和 index 存在必要 token，防止配置、文档和能力边界漂移。

该检查为 `review-required`。它不证明某次任务实际启动了 subagent，不替代人工判断，不自动写 canonical docs。

## 验证

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_quality_supervisor_protocol.py
python3 tests/test_quality_supervisor_protocol.py
```

治理面变更时仍需运行：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
git diff --check
```
