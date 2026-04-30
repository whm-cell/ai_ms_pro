#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from runtime_traceability import resolve_runtime_traceability


ROOT = Path(__file__).resolve().parents[2]
SESSION_DIR = ROOT / ".codex" / "runtime" / "sessions"
WORKING_CONTEXT_PATH = ROOT / "docs" / "ai" / "working-context.md"
MAX_FIELD_LENGTH = 300
SESSION_ID_KEYS = (
    "session_id",
    "sessionId",
)
TEXT_KEYS = (
    "user_prompt",
    "prompt",
    "message",
    "text",
    "content",
    "input",
)
TRANSCRIPT_KEYS = (
    "transcript_path",
    "transcriptPath",
)
REQUIREMENT_ID_KEYS = (
    "requirement_ids",
    "requirementIds",
    "requirement_id",
    "requirementId",
)
WORKSTREAM_ID_KEYS = (
    "workstream_ids",
    "workstreamIds",
    "workstream_id",
    "workstreamId",
)
RESUME_KEYS = (
    "resumed",
    "is_resume",
    "resume",
)
SUBAGENT_KEYS = (
    "subagent",
    "is_subagent",
    "agent_type",
    "agentType",
)
ENV_SESSION_ID_KEYS = (
    "CODEX_SESSION_ID",
    "SESSION_ID",
)
ENV_REQUIREMENT_ID_KEYS = (
    "CODEX_REQUIREMENT_IDS",
    "REQUIREMENT_IDS",
)
ENV_WORKSTREAM_ID_KEYS = (
    "CODEX_WORKSTREAM_IDS",
    "WORKSTREAM_IDS",
)
ENV_AGENT_KEYS = (
    "CODEX_AGENT_TYPE",
    "AGENT_TYPE",
)


def main() -> int:
    payload = load_payload()
    try:
        write_session_snapshot(payload)
    except Exception:
        # Runtime session persistence is best-effort and must never block Stop.
        return 0
    return 0


def load_payload() -> dict[str, Any]:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_session_snapshot(payload: dict[str, Any]) -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    session_id = first_value(payload, SESSION_ID_KEYS) or first_env_value(ENV_SESSION_ID_KEYS) or "unknown-session"
    agent_label = infer_agent_label(payload)
    branch_or_thread = infer_branch_or_thread(payload, session_id)
    session_file = find_or_create_session_file(session_id, agent_label, branch_or_thread)

    session_type = infer_session_type(payload, session_file)
    prompt_preview = compact_text(first_value(payload, TEXT_KEYS))
    transcript_path = compact_text(first_value(payload, TRANSCRIPT_KEYS))
    changed_paths = git_status_paths()
    payload_requirement_ids = collect_identifier_values(payload, REQUIREMENT_ID_KEYS)
    payload_workstream_ids = collect_identifier_values(payload, WORKSTREAM_ID_KEYS)
    env_requirement_ids = [] if payload_requirement_ids else collect_env_identifiers(ENV_REQUIREMENT_ID_KEYS)
    env_workstream_ids = [] if payload_workstream_ids else collect_env_identifiers(ENV_WORKSTREAM_ID_KEYS)
    requirement_ids, workstream_ids, traceability_source = resolve_runtime_traceability(
        payload_requirement_ids,
        payload_workstream_ids,
        env_requirement_ids,
        env_workstream_ids,
        changed_paths,
    )
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")

    field_text = "\n".join(f"- `{path}`" for path in changed_paths[:20]) or "- 暂无检测到当前工作区变更"
    promote = should_promote(changed_paths)
    promote_reason = infer_promotion_reason(promote, changed_paths)

    content = "\n".join(
        [
            "# Runtime Session 记录",
            "",
            f"更新时间：{now}",
            f"Agent：{agent_label}",
            f"Session 类型：{session_type}",
            f"分支或线程：{branch_or_thread}",
            f"Session ID：{session_id}",
            "",
            "## 需求与工作流标识",
            "",
            f"- Requirement IDs：{format_identifiers(requirement_ids)}",
            f"- Workstream IDs：{format_identifiers(workstream_ids)}",
            f"- Traceability Source：{traceability_source}",
            "- 若已绑定，应与 `docs/requirements/traceability-matrix.md` 保持一致",
            "",
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
            "",
            "## 是否需要提升为 Handoff",
            "",
            f"- {'是' if promote else '否'}",
            f"- 原因：{promote_reason}",
            "- 若为“是”，至少同步：任务目标、已完成内容、修改文件、关键实现决策、有效路线、无效路线、候选路线、未完成项、风险、下一步动作",
            "",
            "## Hook 元数据",
            "",
            bullet(transcript_path, "未检测到 transcript_path"),
            bullet(compact_text(str(WORKING_CONTEXT_PATH)), "未检测到 working-context 路径"),
            bullet(traceability_source, "未检测到 traceability source"),
        ]
    ) + "\n"

    session_file.write_text(content, encoding="utf-8")


def find_or_create_session_file(session_id: str, agent_label: str, branch_or_thread: str) -> Path:
    existing = sorted(SESSION_DIR.glob(f"*_{session_id}.md"))
    if existing:
        return existing[-1]

    stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    safe_branch = slugify(branch_or_thread)
    safe_agent = slugify(agent_label)
    safe_session = slugify(session_id)
    return SESSION_DIR / f"{stamp}_{safe_agent}_{safe_branch}_{safe_session}.md"


def infer_session_type(payload: dict[str, Any], session_file: Path) -> str:
    resumed = first_value(payload, RESUME_KEYS)
    if isinstance(resumed, bool) and resumed:
        return "resume"
    if session_file.exists():
        return "pause-before-exit"
    return "new"


def infer_agent_label(payload: dict[str, Any]) -> str:
    env_label = first_env_value(ENV_AGENT_KEYS)
    if env_label:
        return "subagent" if "sub" in env_label.lower() else "main"

    value = first_value(payload, SUBAGENT_KEYS)
    if isinstance(value, bool):
        return "subagent" if value else "main"
    if isinstance(value, str):
        lowered = value.lower()
        if "sub" in lowered or "worker" in lowered:
            return "subagent"
    return "main"


def infer_branch_or_thread(payload: dict[str, Any], session_id: str) -> str:
    branch = git_branch()
    if branch:
        return branch
    thread = first_value(payload, ("thread_id", "threadId"))
    if isinstance(thread, str) and thread.strip():
        return thread.strip()
    return session_id


def git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def git_status_paths() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.append(path_text)
    return paths


def should_promote(changed_paths: list[str]) -> bool:
    if not changed_paths:
        return False
    for path_text in changed_paths:
        if path_text.startswith(".codex/runtime/"):
            continue
        if path_text.startswith("mysjzhishidian/"):
            continue
        return True
    return False


def infer_promotion_reason(promote: bool, changed_paths: list[str]) -> str:
    if not promote:
        return "当前仅检测到本地 runtime 或参考草稿层改动，暂不强制提升"
    return (
        "检测到除 runtime/参考草稿之外的仓库级改动；主 Agent 应判断是否需要发布 canonical handoff"
    )


def first_env_value(keys: tuple[str, ...]) -> str:
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    return ""


def first_value(data: Any, keys: tuple[str, ...]) -> Any:
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if is_meaningful(value):
                return value
        for value in data.values():
            found = first_value(value, keys)
            if is_meaningful(found):
                return found
    elif isinstance(data, list):
        for item in data:
            found = first_value(item, keys)
            if is_meaningful(found):
                return found
    return None


def collect_identifier_values(data: Any, keys: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()

    def add(candidate: str) -> None:
        normalized = candidate.strip()
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        values.append(normalized)

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in keys:
                    extract_from_value(value)
                else:
                    visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    def extract_from_value(value: Any) -> None:
        if isinstance(value, str):
            for piece in value.split(","):
                add(piece)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    add(item)
        elif isinstance(value, dict):
            visit(value)

    visit(data)
    return values


def collect_env_identifiers(keys: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for key in keys:
        raw = os.environ.get(key, "")
        if not raw:
            continue
        for piece in raw.split(","):
            normalized = piece.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            values.append(normalized)
    return values


def is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def compact_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    compact = " ".join(value.split())
    return compact[:MAX_FIELD_LENGTH].strip()


def format_identifiers(values: list[str]) -> str:
    if not values:
        return "未绑定"
    return ", ".join(values)


def bullet(value: str, fallback: str) -> str:
    text = value or fallback
    return f"- {text}"


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    slug = re.sub(r"[^a-z0-9._-]+", "-", lowered)
    return slug.strip("-") or "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
