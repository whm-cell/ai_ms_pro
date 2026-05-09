# Security Policy

更新时间：2026-05-09

本仓库是 private repo。安全报告和敏感证据必须走私有渠道；不要把 secret、token、credential、完整环境变量值或未脱敏日志贴到 issue、PR、commit message、聊天记录或治理文档里。

## 报告路径

请通过仓库管理员或团队私有安全渠道报告安全问题。

- 仓库管理员：`<repo-admin-or-security-owner>`
- 私有安全渠道：`<private-security-channel>`
- 可公开记录在 issue / PR 的内容只限脱敏摘要、影响范围、修复状态和验证结论。

如果报告涉及正在泄漏的 secret，先通过私有渠道通知管理员；不要为了证明问题而复制 secret 原文。

## 处理原则

### Secret 泄漏

- 立即停止传播：删除或编辑包含 secret 的未合并 PR 评论、issue 正文、日志附件或文档片段；git 历史清理另行确认，不自动执行。
- 立即轮换：将泄漏值视为已失效，使用对应 secret manager / GitHub secret / 外部服务后台轮换。
- 保留脱敏证据：记录 secret 类型、作用域、暴露位置、发现时间、处置人和验证结果，不记录真实值。
- 复查影响：检查 CI、部署、第三方服务、runtime/local artifacts 和相关依赖配置是否仍引用旧值。

### 依赖漏洞

- 先确认漏洞是否影响当前仓库实际使用路径、运行环境和发布边界。
- 高危或可利用漏洞优先升级、替换、禁用入口或记录临时缓解措施。
- 暂不能修复时，必须记录原因、临时缓解、owner 和复查时间。
- Dependency Review、SBOM、CodeQL 和 Scorecard 发现当前仍按 advisory evidence 处理；是否阻断合并按仓库治理文档和当前阶段决策执行。

## 披露边界

- 本仓库不在 public security advisory 流程内时，默认使用私有渠道完成 triage、修复和验证。
- 对外披露、发布公告、创建 release、签名或 artifact attestation 都属于高影响动作，需要明确人工确认。
- AI/Agent 可以帮助整理脱敏摘要、影响面和验证命令，但不得要求用户粘贴 secret 原文。

## 相关文档

- [Security Evidence Triage](docs/ai/security/security-evidence-triage.md)
- [Supply Chain And Provenance Plan](docs/ai/security/supply-chain-provenance-plan.md)
