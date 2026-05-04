# Harness Evidence Checks Handoff

更新时间：2026-05-04
阶段：stage-00
任务：harness-evidence-checks
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务是 harness verification 能力增强，不新增 requirements canonical mapping

## 本任务目标

- 增加 repo-local skill discoverability 检查
- 增加 PRD / requirements 导入质量检查
- 增加 Candidate skill with/without eval 登记与检查
- 增加 GitHub guardrails 本地/远端可运行检查

## 已完成内容

- 新增 `scripts/check_repo_skills.py`
- 新增 `scripts/check_requirements_shape.py`
- 新增 `scripts/check_skill_usage_samples.py`
- 新增 `scripts/check_github_guardrails.py`
- 新增 `docs/ai/skill-usage-samples.md`
- 新增 `docs/ai/skill-evals/README.md`
- 将 repo skills 迁到 `.agents/skills`，并修正 `agents/openai.yaml` 为 `policy.allow_implicit_invocation`
- 同步 `docs/ai/index.md`、status、open-items、working-context、changelog 和使用细节

## 修改文件

- [check_repo_skills.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_repo_skills.py)
- [check_requirements_shape.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_requirements_shape.py)
- [check_skill_usage_samples.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_skill_usage_samples.py)
- [check_github_guardrails.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_github_guardrails.py)
- [Candidate Skill Usage Samples](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/skill-usage-samples.md)
- [Candidate Skill Eval Protocol](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/skill-evals/README.md)
- [PRD 长文到 Harness 与 Skill 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/PRD长文到Harness与Skill使用细节.md)

## 关键实现决策

- 四个新检查默认 warning-only，不接 Stop hook，不自动升级 Candidate skill。
- `check_repo_skills.py` 结构错误会失败；`repo-local only` 是事实输出，`.agents/skills` 才标为 Codex discoverable。
- `check_requirements_shape.py` 对缺失 `REQ` matrix 行失败，对 source / WS 覆盖缺口和技术假设启发式提示保持 warning。
- `check_skill_usage_samples.py` 默认只报告 with/without eval 样本不足；只有 `--strict` 才把缺少样本视为失败。
- `check_github_guardrails.py` 对未登录、缺权限或远端不可达输出 `UNKNOWN` 并退出 0，避免把不可证明项伪装成 OK。

## 行为护栏摘要

- Assumptions：当前两个 workflow skills 仍是 Candidate。
- Scope Boundary：不全局安装 skill，不改业务功能，不把新检查接入 blocking hook。
- Success Criteria：能列出 repo-local/global skill 状态，能检查 requirements 链路，能记录 Candidate skill 样本缺口。
- Verification：运行四个新检查、governance check、context budget check。

## 已验证有效的路线

- 将证据检查做成独立脚本，避免继续加厚 `check_ai_governance.py`。
- 用 `docs/ai/skill-usage-samples.md` 和 `docs/ai/skill-evals/` 保存 promotion evidence，而不是把样本塞进 skill 本体。

## 已验证无效的路线

- 把 `repo-local only` 当成错误会误伤当前显式调用策略。
- 在没有真实样本前把 Candidate skill 升级为 always-on 会制造流程税风险。

## 尚未尝试但建议的路线

- 在下一个真实 PRD 导入任务中记录 `prd-to-project-skills` 样本。
- 在下一个非平凡功能实现任务中记录 `progressive-feature-development` 样本。
- 后续如样本稳定，再考虑是否同步到 CI 或全局 skill 安装流程。

## 当前未完成项

- `prd-to-project-skills` 仍为 0/2 accepted with/without eval samples。
- `progressive-feature-development` 仍为 0/2 accepted with/without eval samples。
- 新检查尚未同步进远端 CI required checks。

## 已知风险与注意事项

- `check_requirements_shape.py` 的技术假设识别是启发式，不替代人工判断。
- 真实样本不足是当前事实，不应为了通过检查伪造样本。
- 全局安装 skill 前必须确认不会把当前项目规则误用到其他项目。

## 下一位 Agent 的第一步动作

- 若处理 PRD 或非平凡功能，先运行对应新检查并在 `docs/ai/skill-usage-samples.md` 记录样本结果。

## 建议同步更新

- 当前已同步 `index`、`working-context`、`status`、`harness-open-items`、changelog 和使用细节。
