#!/usr/bin/env python3

from __future__ import annotations

import textwrap


def render_ai_index(project_name: str, stage_label: str) -> str:
    return textwrap.dedent(
        f"""\
        # AI 文档入口索引

        更新时间：YYYY-MM-DD
        当前状态：待导入首个真实场景
        当前阶段：{stage_label}

        ## 入口说明

        本文件是 `docs/ai/` 的稳定路由层，面向 AI 与人类执行者。

        这里只保留共享治理控制面的默认入口，不在这里重复展开完整阶段目录。

        `.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入默认共享阅读面，也不作为项目共享真相。

        ## 默认短链路

        1. [项目规则 AGENTS.md](../../AGENTS.md)
        2. [当前工作上下文](./working-context.md)

        任务进入哪个更深入口，由 `AGENTS.md` 的 Task Discovery Protocol 判断。简单任务默认停在短链路；requirements、plan、handoff、ADR 与 archive 都是按需入口。

        用户通常不需要手动标注任务类型。`按简单任务处理`、`按复杂任务处理`、`这是 0-1 阶段任务`、`不要读 archive`、`需要深挖历史` 只是可选覆盖指令，用来纠正或收窄 Agent 的默认判断。

        ## 按需深入入口

        - [需求文档入口索引](../requirements/index.md)：需求驱动、traceability 或 0-1 stage 任务再进入
        - [项目计划](./plan.md)：阶段目标、范围与验收框架需要确认时再进入
        - [Harness 可迁移清单](./harness-portability-guide.md)
        - [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)
        - [传统项目接入 Harness 的标准起手式](./traditional-project-harness-kickoff.md)
        - [handoffs/active](./handoffs/active)
        - [status](./status)
        - [changelog](./changelog)
        - [adr](./adr)
        - 默认 active handoff 预算由 `.codex/harness.toml` 的 `context_surface.active_handoff_budget` 控制，初始值为 `5`。达到预算时优先压缩到 `status` 或归档，而不是继续扩张默认恢复面。

        ## 当前阶段占位

        - 暂无阶段 `status`
        - 暂无活跃 `handoff`
        - 暂无阶段 `changelog`
        - 暂无正式 `adr`

        ## 活跃目录

        - [handoffs/active](./handoffs/active)
        - [status](./status)
        - [changelog](./changelog)
        - [adr](./adr)

        ## 归档入口

        - [handoffs/archive](./handoffs/archive)
        - [archive](./archive)

        ## 维护规则

        - 本文件只做稳定路由，不维护第二套“当前阶段总表”或“下一次会话先读”的完整展开版。
        - 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，更新这里的稳定入口与占位状态。
        - 当某个完成型 `handoff` 已被 `status` 或 `adr` 吸收且不再有默认恢复价值时，将其移入 `handoffs/archive`。
        - 本地 runtime harness 文件不应加入本索引。
        """
    )


def render_working_context(project_name: str, stage_label: str) -> str:
    return textwrap.dedent(
        f"""\
        # 当前工作上下文

        更新时间：YYYY-MM-DD
        当前阶段：{stage_label}
        当前模式：Codex-first harness engineering

        ## 作用

        本文件只保留当前开发阶段最需要被下一次会话立即继承的增量真相。

        它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

        ## 同步元数据

        - Current Stage: {stage_label}
        - Active Status Source: 未绑定
        - Active Handoff Sources: 未绑定
        - Requirement IDs: 未绑定
        - Workstream IDs: 未绑定
        - Last Synced From: bootstrap
        - Last Synced At: YYYY-MM-DD

        ## 当前主目标

        - 为 `{project_name}` 建立最小可用的共享治理控制面
        - 导入首个真实需求并形成第一个 workstream
        - 让第一条垂直切片跑通 `requirements -> implementation -> runtime memory -> handoff/status`

        ## 当前活跃队列

        1. 初始化 `docs/ai/` 和 `docs/requirements/` 控制面
        2. 导入首个 `REQDOC / REQ / WS`
        3. 实现第一个可验证的垂直切片
        4. 跑通 runtime observation / session / reducer / handoff-status 链路
        5. 默认将共享恢复面保持在 `index -> working-context -> status -> configured active handoff budget`

        ## 当前风险与阻塞

        - 首个真实场景尚未导入，当前还不能证明 traceability 链路可用
        - 若把旧项目共享真相直接复制过来，会污染新项目控制面
        - 若未先初始化 index / plan / working-context / traceability-matrix，Stop hook 可能在首轮工作后直接给出治理失败
        - active handoff 默认预算由 `.codex/harness.toml` 控制；被 `status` 吸收后的完成型 handoff 应进入 `archive`，否则默认恢复面会再次膨胀

        ## 下一次会话先读

        1. [AI 文档入口索引](./index.md)
        2. [当前工作上下文](./working-context.md)
        3. [需求文档入口索引](../requirements/index.md)
        4. [项目计划](./plan.md)
        5. [Harness 可迁移清单](./harness-portability-guide.md)
        6. [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)

        ## 最近已固化的决策

        - 项目采用 `AGENTS.md + Codex Stop hook + 校验脚本` 的治理方式
        - 项目采用 `docs/requirements/` 与 `docs/ai/` 分层管理需求与执行上下文
        - `.codex/runtime/` 只保存本地 session/observation 原料，不替代 `docs/ai/` 共享治理文档
        - 默认共享恢复面保持轻量：`index -> working-context -> status -> configured active handoff budget`
        - `plan` 与 `workstream` 属于 projection surface，不应重复承载快速变化的当前状态
        - `.agents/skills/repo-governed-coding/` 是可选行为护栏，默认显式调用，不替代 `AGENTS.md`、共享治理文档或检查脚本
        - `.agents/skills/harness-maintenance/` 是可选 harness 维护能力，只在修改 runtime、hooks、reducers、compression、verification、GitHub guardrails 或 code-shape checks 时按需调用
        - `.agents/skills/requirements-traceability-maintenance/` 是可选 requirements 维护能力，只在 PRD 导入、`REQDOC / REQ / WS`、traceability matrix 或技术假设变化时按需调用

        ## 更新规则

        - 只保留当前阶段仍然有效的增量真相
        - 当阶段切换、主目标变化或 `status/handoff` 完成压缩后优先更新本文件
        - 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在默认恢复面里
        """
    )
