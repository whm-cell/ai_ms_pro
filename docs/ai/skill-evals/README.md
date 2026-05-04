# Candidate Skill Eval Protocol

更新时间：2026-05-04
状态：P0 对照实验规范

## 作用

本目录保存 Candidate repo-local skills 的详细 with/without 对照实验材料。

`docs/ai/skill-usage-samples.md` 是索引级登记表；本目录用于放更长的任务记录、对照细节、原始验证摘要或复盘。这里的内容仍不是 canonical current-state truth，长期结论必须提升到 `status`、`handoff`、ADR、requirements 或检查脚本。

## 最小 eval 字段

每个 accepted eval 必须能回溯以下字段：

- `baseline_without_skill`: 不使用 skill 时的基线流程、读取面、预计或实际返工、风险和流程税。
- `run_with_skill`: 使用 skill 时的触发理由、读取面、执行路径、产出和治理回写。
- `delta`: 相对 baseline 的上下文、返工、质量、速度或流程税变化。
- `acceptance`: 是否计入升级证据，以及原因。
- `verification`: 实际运行的测试、smoke、治理检查或人工复核。

## 判定规则

- `accepted` 只表示该样本可计入 Candidate skill 升级证据，不表示该 skill 已稳定化。
- 每个 Candidate skill 仍至少需要 2 个 accepted real-task eval samples。
- 如果 with/without 对照显示 skill 增加了简单任务流程税，应记录为 `rejected` 或负向 `pending` 样本。
- 不得为了满足样本数量伪造 accepted；样本不足时保持 warning-only 事实。

## 文件建议

详细 eval 文件建议使用：

```text
docs/ai/skill-evals/SAMPLE-XXX-short-name.md
```

文件内容应包含任务背景、样本字段、验证命令输出摘要和是否需要提升到共享 truth surface。
