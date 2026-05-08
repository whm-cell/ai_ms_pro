from __future__ import annotations

from typing import Any


def render_session_snapshot(snapshot: dict[str, Any]) -> str:
    sections = [
        render_header(snapshot),
        render_traceability(snapshot),
        render_body(snapshot),
        render_promotion(snapshot),
        render_hook_metadata(snapshot),
    ]
    return "\n".join(sections) + "\n"


def render_header(snapshot: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Runtime Session 记录",
            "",
            f"更新时间：{snapshot['now']}",
            f"Agent：{snapshot['agent_label']}",
            f"Session 类型：{snapshot['session_type']}",
            f"分支或线程：{snapshot['branch_or_thread']}",
            f"Session ID：{snapshot['session_id']}",
        ]
    )


def render_traceability(snapshot: dict[str, Any]) -> str:
    lines = [
        "## 需求与工作流标识",
        "",
        f"- Requirement IDs：{format_identifiers(snapshot['requirement_ids'])}",
        f"- Workstream IDs：{format_identifiers(snapshot['workstream_ids'])}",
    ]
    if snapshot.get("traceability_source"):
        lines.append(f"- Traceability Source：{snapshot['traceability_source']}")
    lines.append("- 若已绑定，应与 `docs/requirements/traceability-matrix.md` 保持一致")
    return "\n".join(lines)


def render_body(snapshot: dict[str, Any]) -> str:
    field_text = "\n".join(f"- `{path}`" for path in snapshot["changed_paths"][:20])
    if not field_text:
        field_text = "- 暂无检测到当前工作区变更"
    prompt_preview = snapshot["prompt_preview"]
    transcript_path = snapshot["transcript_path"]

    return "\n".join(
        [
            "## 当前目标",
            "",
            bullet(prompt_preview, "待主 Agent 基于本次 Stop 事件补充当前目标"),
            "",
            "## 会话范围与触发背景",
            "",
            bullet(
                transcript_path,
                "由 Stop hook 自动刷新；如需更完整背景，请结合工作区状态和共享治理文档判断",
            ),
            "",
            "## 行为护栏快照",
            "",
            "- Assumptions：待主 Agent 补充本次实现前明确采用的假设",
            "- Scope Boundary：待主 Agent 补充本次只改什么、不顺手改什么",
            "- Success Criteria：待主 Agent 补充可验证的完成条件",
            "- Verification Plan：待主 Agent 补充收尾前应运行的检查、测试或 smoke",
            "",
            "## 已做动作",
            "",
            "- Stop hook 已刷新本地 runtime session 快照",
            "- 已记录当前工作区变更文件与最佳努力 prompt/transcript 元数据",
            "",
            "## 触碰文件",
            "",
            field_text,
            "",
            "## 已验证有效的路线",
            "",
            "- 待主 Agent 从本次会话内容提炼",
            "",
            "## 已验证无效的路线",
            "",
            "- 待主 Agent 从本次会话内容提炼",
            "",
            "## 当前 Open Loops",
            "",
            "- Stop hook 无法可靠推断全部开放问题，需主 Agent 按需补充",
            "",
            "## 需提升到共享治理层的内容",
            "",
            bullet(
                prompt_preview,
                "若本次 session 已形成共享结论，请提升到 handoff、status、ADR、plan 或 requirements",
            ),
            "",
            "## 下次 Resume 提示",
            "",
            "- 先读 `docs/ai/index.md`、`docs/ai/working-context.md` 和相关 ADR",
            bullet(
                transcript_path,
                "若需要还原更细的会话轨迹，优先结合 transcript 路径或当前 session 文件判断",
            ),
        ]
    )


def render_promotion(snapshot: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## 是否需要提升为 Handoff",
            "",
            f"- {'是' if snapshot['promote'] else '否'}",
            f"- 原因：{snapshot['promote_reason']}",
            "- 若为“是”，至少同步：任务目标、已完成内容、修改文件、关键实现决策、有效路线、无效路线、候选路线、未完成项、风险、下一步动作",
        ]
    )


def render_hook_metadata(snapshot: dict[str, Any]) -> str:
    lines = [
        "## Hook 元数据",
        "",
        bullet(snapshot["transcript_path"], "未检测到 transcript_path"),
        bullet(snapshot["working_context_path"], "未检测到 working-context 路径"),
    ]
    if snapshot.get("traceability_source"):
        lines.append(bullet(snapshot["traceability_source"], "未检测到 traceability source"))
    return "\n".join(lines)


def format_identifiers(values: list[str]) -> str:
    return ", ".join(values) if values else "未绑定"


def bullet(value: str, fallback: str) -> str:
    return f"- {value or fallback}"
