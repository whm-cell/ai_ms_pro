from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOOK_DIR = ROOT / ".codex" / "hooks"
sys.path.insert(0, str(HOOK_DIR))

from runtime_sanitizer import compact_text  # noqa: E402

EXCLUDE_PREFIXES = (".codex/runtime/", "mysjzhishidian/")
MAX_SECTION_ITEMS = 8


@dataclass(frozen=True)
class HandoffRenderContext:
    now: str
    observation_file: Path
    entries: list[dict[str, Any]]
    selected: list[dict[str, Any]]
    stage: str
    task: str
    title: str
    selected_sessions: list[str]
    prompt_previews: list[str]
    promotion_reasons: list[str]
    merged_requirement_ids: list[str]
    merged_workstream_ids: list[str]
    runtime_only_count: int
    promotable_count: int
    top_paths: list[str]
    repeated_paths: list[str]


def render_handoff_draft(
    observation_file: Path,
    entries: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    stage: str,
    task: str,
    title: str,
    requirement_ids: list[str],
    workstream_ids: list[str],
) -> str:
    context = build_render_context(
        observation_file=observation_file,
        entries=entries,
        selected=selected,
        stage=stage,
        task=task,
        title=title,
        requirement_ids=requirement_ids,
        workstream_ids=workstream_ids,
    )
    return "\n".join(render_handoff_lines(context)) + "\n"


def build_render_context(
    observation_file: Path,
    entries: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    stage: str,
    task: str,
    title: str,
    requirement_ids: list[str],
    workstream_ids: list[str],
) -> HandoffRenderContext:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    selected_sessions = unique_strings(selected, "session_id")
    shared_paths = count_shared_paths(selected)
    prompt_previews = ordered_unique_texts(selected, "prompt_preview")
    promotion_reasons = ordered_unique_texts(selected, "promotion_reason")
    observed_requirement_ids = aggregate_identifier_lists(selected, "requirement_ids")
    observed_workstream_ids = aggregate_identifier_lists(selected, "workstream_ids")
    merged_requirement_ids = merge_identifier_lists(requirement_ids, observed_requirement_ids)
    merged_workstream_ids = merge_identifier_lists(workstream_ids, observed_workstream_ids)
    runtime_only_count = sum(1 for entry in selected if entry.get("runtime_only_changes") is True)
    promotable_count = sum(1 for entry in entries if entry.get("needs_governance_promotion") is True)
    top_paths = [path for path, _ in shared_paths.most_common(MAX_SECTION_ITEMS)]
    repeated_paths = [path for path, count in shared_paths.items() if count > 1]
    return HandoffRenderContext(
        now=now,
        observation_file=observation_file,
        entries=entries,
        selected=selected,
        stage=stage,
        task=task,
        title=title,
        selected_sessions=selected_sessions,
        prompt_previews=prompt_previews,
        promotion_reasons=promotion_reasons,
        merged_requirement_ids=merged_requirement_ids,
        merged_workstream_ids=merged_workstream_ids,
        runtime_only_count=runtime_only_count,
        promotable_count=promotable_count,
        top_paths=top_paths,
        repeated_paths=repeated_paths,
    )


def render_handoff_lines(context: HandoffRenderContext) -> list[str]:
    return (
        render_header_lines(context)
        + render_progress_lines(context)
        + render_decision_lines(context)
        + render_risk_and_route_lines(context)
        + render_followup_lines(context)
    )


def render_header_lines(context: HandoffRenderContext) -> list[str]:
    return [
        f"# {context.title}",
        "",
        f"更新时间：{context.now}",
        f"阶段：{context.stage}",
        f"任务：{context.task}",
        "状态：草稿",
        "",
        "## 需求与工作流标识",
        "",
        f"- Requirement IDs：{format_identifiers(context.merged_requirement_ids)}",
        f"- Workstream IDs：{format_identifiers(context.merged_workstream_ids)}",
        "- 若已绑定，应与 `docs/requirements/traceability-matrix.md` 和相关 workstream 文档保持一致",
        "",
        "## 本任务目标",
        "",
        "- 基于 runtime observations 提炼需要进入 repo 共享治理层的候选结论",
        "- 默认先产出 handoff 草稿，再由主 Agent 判断是否继续压缩到 status 或 ADR",
        "- 保持 reducer 为显式触发工具，而不是 hook 自动发布 canonical 文档",
        "",
    ]


def render_progress_lines(context: HandoffRenderContext) -> list[str]:
    return [
        "## 已完成内容",
        "",
        f"- 已从 `{display_path(context.observation_file)}` 读取 {len(context.entries)} 条 observation 记录",
        f"- 已选取 {len(context.selected)} 条 observation 作为本次 handoff 草稿输入，其中 {context.promotable_count} 条显式标记为需要共享治理层提升",
        f"- 已覆盖 {len(context.selected_sessions)} 个 session，识别出 {len(context.top_paths)} 个共享层候选修改文件",
        bullet(
            prefixed_preview("提取到的主要 prompt 线索", context.prompt_previews, 3),
            "未从 observations 中提取到稳定的 prompt 线索",
        ),
        "",
        "## 修改文件",
        "",
        bullets_or_fallback(context.top_paths, "- 暂未从 observations 中提取到共享层修改文件"),
        "",
    ]


def render_decision_lines(context: HandoffRenderContext) -> list[str]:
    return [
        "## 关键实现决策",
        "",
        "- reducer 是显式运行的脚本，不在 `Stop` hook 中自动执行",
        "- reducer 的默认输出顺序是 `observations -> handoff draft -> 主 Agent 审核 -> status/ADR`",
        "- 只有 observations 中的共享层线索才应进入 canonical 文档；runtime-only 记录继续停留在本地层",
        bullet(
            prefixed_preview("当前 observation 提升理由聚类", context.promotion_reasons, 2),
            "当前样本中尚未形成稳定的提升理由聚类",
        ),
        bullet(
            prefixed_preview("从 observation 中聚合到的 Requirement IDs", context.merged_requirement_ids, 4),
            "当前 observations 尚未绑定 Requirement IDs",
        ),
        bullet(
            prefixed_preview("从 observation 中聚合到的 Workstream IDs", context.merged_workstream_ids, 4),
            "当前 observations 尚未绑定 Workstream IDs",
        ),
        "",
        "## 当前未完成项",
        "",
        "- 需要主 Agent 审核本草稿，确认是否应该发布或更新 canonical handoff",
        "- 若同类 observation 已跨多次 session 稳定出现，再决定是否压缩到 status 或 ADR",
        "- 若当前任务已正式绑定需求或 workstream，需要把同一组 IDs 同步回 traceability matrix 和相关 workstream 文档",
        "",
    ]


def render_risk_and_route_lines(context: HandoffRenderContext) -> list[str]:
    return [
        "## 已知风险与注意事项",
        "",
        "- observations 来自 best-effort Stop hook，字段可能随上游 payload 变化而不完整",
        "- `changed_paths` 反映的是当前工作区可见改动，不保证严格等价于单次会话内的最小变更集",
        f"- 本次 reducer 输入中有 {context.runtime_only_count} 条 runtime-only observation，它们不应直接升格为共享真相",
        "",
        "## 已验证有效的路线",
        "",
        bullet(
            prefixed_preview("observations 中重复出现的共享层文件", context.repeated_paths, 3),
            "先从 observations 中出现频率更高的共享层文件入手，适合作为 handoff 审核起点",
        ),
        "- 先生成 handoff 草稿、再由主 Agent 决定是否发布 canonical 文档，符合 repo-first 治理边界",
        "",
        "## 已验证无效的路线",
        "",
        "- 仅凭 runtime-only observations 直接发布 canonical handoff、status 或 ADR，不符合当前治理模型",
        "- 让 reducer 自动改写共享治理文档会越过主 Agent 的语义判断边界",
        "",
    ]


def render_followup_lines(context: HandoffRenderContext) -> list[str]:
    return [
        "## 尚未尝试但建议的路线",
        "",
        "- 将本草稿与相关 session 文件、active handoff 和 working-context 一起对读，再决定是否发布 canonical handoff",
        "- 如果同类 observation 在多个 session 中重复出现，可增加 status 或 ADR 候选压缩",
        "- 若真实项目需求已经导入，运行 reducer 时显式补齐 `--requirement-id` / `--workstream-id`，减少后续追踪断点",
        "",
        "## Next Best Work Review",
        "- Planned next work / Decision / Reason / User confirmation required：由主 Agent 发布前填写；Decision：continue | re-scope | split | pivot | park | cancel | ask-user",
        "## 下一位 Agent 的第一步动作",
        "",
        f"- 先复核 `{display_path(context.observation_file)}` 的最近 observation，与当前 active handoff 和 `working-context.md` 对照，判断是否需要落地新的 canonical handoff",
        "",
        "## 建议同步更新",
        "",
        "- 若本草稿被采纳，更新 `docs/ai/index.md` 与 `working-context.md`",
        "- 若 reducer 输出已经形成长期稳定工作流结论，补充或更新 ADR",
    ]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def unique_strings(entries: list[dict[str, Any]], key: str) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        value = string_value(entry.get(key))
        if not value or value in seen:
            continue
        ordered.append(value)
        seen.add(value)
    return ordered


def ordered_unique_texts(entries: list[dict[str, Any]], key: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        value = compact_text(entry.get(key))
        if not value or value in seen:
            continue
        values.append(value)
        seen.add(value)
    return values


def aggregate_identifier_lists(entries: list[dict[str, Any]], key: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        raw = entry.get(key)
        if not isinstance(raw, list):
            continue
        for item in raw:
            if not isinstance(item, str):
                continue
            normalized = item.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            values.append(normalized)
    return values


def merge_identifier_lists(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            normalized = item.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            merged.append(normalized)
    return merged


def count_shared_paths(entries: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for entry in entries:
        raw_paths = entry.get("changed_paths")
        if not isinstance(raw_paths, list):
            continue
        for raw_path in raw_paths:
            path_text = string_value(raw_path)
            if not path_text or is_excluded_path(path_text):
                continue
            counter[path_text] += 1
    return counter


def is_excluded_path(path_text: str) -> bool:
    for prefix in EXCLUDE_PREFIXES:
        if path_text.startswith(prefix):
            return True
    return False


def join_preview(values: list[str], limit: int) -> str:
    if not values:
        return ""
    return "；".join(values[:limit])


def prefixed_preview(prefix: str, values: list[str], limit: int) -> str:
    preview = join_preview(values, limit)
    if not preview:
        return ""
    return f"{prefix}：{preview}"


def bullets_or_fallback(values: list[str], fallback: str) -> str:
    if not values:
        return fallback
    return "\n".join(f"- `{value}`" for value in values)


def bullet(value: str, fallback: str) -> str:
    text = value or fallback
    return f"- {text}"


def format_identifiers(values: list[str]) -> str:
    if not values:
        return "未绑定"
    return ", ".join(values)


def string_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""
