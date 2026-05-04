# PRD 长文到 Harness 与 Skill 使用细节

更新时间：2026-05-04

## 这是什么

本文件说明当项目拿到一份万字 PRD / 长 Markdown 需求文档时，如何使用当前 harness 与 repo-local skills。

核心原则：

- PRD 原文是需求来源，不直接变成执行计划。
- `docs/requirements/*` 承载“做什么、为什么做、怎么验收”的 canonical truth。
- `.agents/skills/*` 承载“以后反复怎么做”的 Codex repo-local 按需方法，不保存当前状态和验收进度。
- `docs/ai/*` 承载“现在做到哪、下一步是什么、哪些决策已稳定”的共享治理真相。

## 推荐处理链路

### 1. 原文入库

把万字 PRD 原样保存到：

```text
docs/requirements/source/REQDOC-XXX-<short-name>.md
```

原文入库时只做必要的标题、来源、更新时间补充，不要边导入边改写需求。

### 2. 标准化需求

从原文拆出多个 normalized requirement：

```text
docs/requirements/normalized/REQ-XXX-<short-name>.md
```

每个 `REQ` 应尽量回答：

- 用户或业务目标是什么
- 功能行为是什么
- 验收标准是什么
- 非目标是什么
- 技术假设有哪些
- 需要人工确认的问题有哪些

PRD 中“不精准的技术栈”不要直接当成架构事实。先写成 `技术假设`、`待确认` 或 `ADR 候选`。

### 3. 拆成 workstream

把多个 `REQ` 组合成可开发切片：

```text
docs/requirements/workstreams/WS-XX-<short-name>.md
```

一个 `WS` 应该能指导一次阶段化实现或一个垂直切片，而不是简单复制 PRD 章节。

### 4. 更新追踪矩阵

更新：

```text
docs/requirements/traceability-matrix.md
```

保持链路清楚：

```text
REQDOC -> REQ -> WS -> STAGE -> 验收/测试
```

如果当前还没有阶段或实现，写真实状态，不要伪造完成度。

### 5. 调用 `$prd-to-project-skills`

在 PRD / requirements / workstream 中出现稳定可复用模式时，再调用：

```text
$prd-to-project-skills
```

它负责分类，不负责实现功能。

输出应拆成：

- `Keep In Requirements`：产品行为、验收标准、业务规则、traceability、当前状态
- `Candidate Skill Content`：稳定模块模式、API 约定、测试方式、依赖使用规则
- `Promote To ADR / Status / Check`：长期架构决策、阶段执行策略、可自动检查规则
- `Reject Skillization`：一次性需求、不可靠技术栈、当前进度、未验证想法、重复治理规则

### 6. 开发具体功能时调用 `$progressive-feature-development`

当进入某个非平凡功能、跨模块改动、API / storage / architecture / testing strategy 改动时，再调用：

```text
$progressive-feature-development
```

它应先生成技术方案，再进入实现。

输出至少包含：

- Task Classification
- Requirement IDs / Workstream IDs
- Minimum Context Read
- Selected Skills
- Technical Plan
- Plan Gate Result
- Implementation Boundary
- Verification Commands
- Document Promotion Decision

简单任务、局部 typo、单文件窄修复、单条验证命令不应触发完整流程。

## 推荐 Prompt

### PRD 导入与分类

```text
请基于 docs/requirements/source/REQDOC-XXX-<short-name>.md 做 PRD 标准化。
先不要写业务代码。

输出：
1. 建议拆出的 REQ 列表
2. 建议拆出的 WS 列表
3. PRD 中不可靠或需要确认的技术栈假设
4. 应保留在 requirements 的内容
5. 可能进入 $prd-to-project-skills 的候选模式
6. 应升级到 ADR/status/check 的内容
7. 拒绝 skill 化的内容和原因
```

### 候选 skill 分类

```text
请调用 $prd-to-project-skills，处理 REQ-XXX / WS-XX 中的稳定开发模式。
不要实现功能。

固定输出：
- Candidate Sources
- Stability Assessment
- Keep In Requirements
- Candidate Skill Content
- Promote To ADR / Status / Check
- Reject Skillization
- Governance Updates Needed
```

### 单个 workstream 技术方案

```text
请基于 WS-XX 和 REQ-XXX/REQ-YYY 调用 $progressive-feature-development。
先不要实现。

技术方案必须包含：
- assumptions
- NOT Building
- affected modules
- interfaces / data flow
- implementation boundary
- verification commands
- doc promotion decision
- 需要我人工确认的问题
```

## Codex 是否默认知道 repo-local skills

当前结论：本 repo 的 skills 已迁到 `.agents/skills/*`，应按 Codex repo-local skill 路径处理；但这仍不等同于已安装到全局 `$CODEX_HOME/skills`。

当前 repo 做到的是：

- skill 文件存在于 `.agents/skills/<name>/SKILL.md`
- `AGENTS.md` 和 `docs/ai/index.md` 写了何时按需进入这些 skill
- `scripts/check_repo_skills.py` 会标注 `codex_discoverable`、`repo-local only` 或 `globally installed`
- `scripts/check_context_budget.py` 会扫描 repo-local skill 的大小和描述预算
- skill 结构可用 `skill-creator/scripts/quick_validate.py` 验证

这属于 repo-local native skill，不是全局安装。

如果要让 Codex 在所有项目中默认发现某个 skill，通常需要把它安装或同步到 `$CODEX_HOME/skills`，例如：

```text
/Users/coolm/.codex/skills/<skill-name>/SKILL.md
```

但把项目 skill 全局安装有风险：

- 可能把当前项目的治理约束误用到其他项目
- 可能让简单任务更容易触发不必要流程
- 可能让 skill 变成隐藏 truth，绕过 `docs/requirements` 和 `docs/ai`

因此当前策略是：项目专属 workflow skill 先保留在 `.agents/skills`，并通过 `AGENTS.md + docs/ai/index.md` 明确触发；只有经过多个真实项目验证后，再考虑做成全局安装或 always-on 能力。

## 已落地的 evidence checks

### 1. Repo-local skill discoverability

当前检查：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py
```

它会：

- 列出 repo-local skills
- 验证 `SKILL.md` 结构
- 检查 `agents/openai.yaml`
- 对比 `$CODEX_HOME/skills`
- 明确标注 `repo-local only` / `globally installed`

### 2. PRD 导入质量检查

当前检查：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py
```

它会检查：

- `REQDOC` 是否被 `requirements/index.md` 引用
- `REQ` 是否都有来源
- `WS` 是否绑定了 `REQ`
- `traceability-matrix.md` 是否覆盖所有新 `REQ/WS`
- 技术假设是否被误写成已采纳架构事实

### 3. Candidate skill usage samples

`$progressive-feature-development` 与 `$prd-to-project-skills` 当前是 Candidate。

当前登记面：

```text
docs/ai/skill-usage-samples.md
```

当前检查：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py
```

它会观察：

- 是否减少上下文读取量
- 是否减少返工
- 是否能阻止 PRD 当前状态被塞进 skill
- 是否让简单任务产生流程税

没有真实样本前，不应升级为 always-on。当前两个 workflow skills 都是 0/2 accepted real-task samples。

## 当前 harness 仍可继续改进的点

### 1. projection docs 漂移仍是长期风险

`plan.md` 和 `workstreams/*.md` 是 projection surface，容易与 `working-context`、`status`、`traceability-matrix` 产生新旧状态漂移。

当前治理规则已定义边界，但 checker 还不是完整 dependency-graph aware。后续可以增加“投影文档 freshness warning”，先提示不阻断。

### 2. 远端 GitHub 守门仍需确认

本地 harness 已经可用，但远端 branch protection / ruleset / dependency review / required checks 是否真正生效，仍需要 GitHub 侧确认。

这不是 repo 内文档能完全证明的事项。

## 复查命令

```bash
python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/prd-to-project-skills
python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/progressive-feature-development
.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py
.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py
.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```
