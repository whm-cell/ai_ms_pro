主要问题


repo-local skill 路径可能不符合当前 Codex 官方发现路径。

当前脚本扫描 .codex/skills 和 .agents/skills，但 OpenAI Codex 文档写的是 repo skills 扫描 .agents/skills，而不是 .codex/skills。check_repo_skills.py (line 14) 现在只能证明“repo 内有 skill 文件”，不能证明 Codex 原生会加载 .codex/skills。建议：把 root 和 starter 的 skills 镜像/迁移到 .agents/skills，或让 check_repo_skills.py 明确标注 codex-discoverable / repo-documented-only。



agents/openai.yaml 的 invocation policy 结构可能不被 Codex 识别。

OpenAI 文档示例是 policy.allow_implicit_invocation: false，不是当前这些 skill 里使用的 openai.allow_implicit_invocation 形态。官方说明 allow_implicit_invocation=false 会阻止隐式触发，但前提是 metadata 被正确解析。OpenAI Codex Skills 建议把所有 skill 的 agents/openai.yaml 改成官方 schema。



默认上下文已经接近预算上限。

本地 check_context_budget.py 输出是 8444 / 8500，虽然无 warning，但余量很薄。研究也不是单向支持“越多 repo context 越好”：一篇 2026 arXiv 论文发现 AGENTS.md 可能降低成功率并增加超过 20% 推理成本，结论是人写 context 应只描述最小要求；另一篇论文则观察到 AGENTS.md 可能降低运行时间和输出 token。两者合起来说明：规则有用，但必须薄。arXiv 2602.11988, arXiv 2601.20404 建议把 root 默认预算降回更保守区间，或者把 stage 状态再压缩。



Candidate skill 样本机制还不够“实验化”。

当前 skill-usage-samples.md (line 16) 只有 0/2 样本门槛，但没有强制 with-skill / without-skill 对照、token delta、duration delta、pass rate、人工评审结论。建议新增 docs/ai/skill-evals/<skill>/iteration-N/ 或 .codex/skills/<skill>/evals/，至少保存 prompt、expected output、with/without 结果、评分。



PRD 导入检查还偏轻。

check_requirements_shape.py (line 21) 已检查 ID 和 matrix 覆盖，但还没有强制 source baseline、owner、verification method、assumption state。Jama 明确说 RTM 应连接 source、design、tests、verification evidence，并持续维护；Atlassian 明确要求 assumptions 包括 technology/business/user behavior 并持续复查。建议把技术栈从普通文本拆成 Assumption Status: proposed | validated | rejected | ADR-linked。



远端 GitHub 守门仍是未闭环风险。

本地 status 已承认 branch protection / ruleset / security analysis 还需人工确认：stage status (line 48)。GitHub 官方建议 required reviews、required status checks、conversation resolution；Actions 安全建议最小权限和 third-party action pin 到 full SHA。GitHub protected branches, GitHub Actions security 建议新增一个 scripts/check_github_remote_guardrails.py，用 gh 或 API 输出“本地文件已配置 / 远端实际生效 / 缺口”。



优先级建议

P0：迁移或镜像 .codex/skills 到 .agents/skills，并修正 agents/openai.yaml schema。否则 skill 机制可能只是文档机制，不是 Codex 原生技能机制。
P0：把 Candidate skill eval 从样本登记升级为 with/without 对照实验，避免凭感觉升级 always-on。
P1：扩展 PRD 导入检查，尤其是技术假设状态和 verification method。
P1：远端 GitHub guardrails 做成可运行检查。
P2：继续压缩默认上下文，避免 Stage-00 历史变成长期流程税。