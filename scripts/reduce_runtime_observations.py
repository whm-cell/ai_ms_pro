#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OBSERVATION_DIR = ROOT / ".codex" / "runtime" / "observations"
EXCLUDE_PREFIXES = (
    ".codex/runtime/",
    "mysjzhishidian/",
)
DEFAULT_LIMIT = 20
MAX_SECTION_ITEMS = 8


def main() -> int:
    args = parse_args()
    observation_file = resolve_observation_file(args.input)
    entries = load_observations(observation_file)
    selected = select_entries(entries, args.limit)
    markdown = render_handoff_draft(
        observation_file=observation_file,
        entries=entries,
        selected=selected,
        stage=args.stage,
        task=args.task,
        title=args.title,
    )

    if args.output:
        output_path = Path(args.output).expanduser()
        if not output_path.is_absolute():
            output_path = (ROOT / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reduce runtime observations into a handoff-first markdown draft."
    )
    parser.add_argument(
        "--input",
        help="Path to a JSONL observation file. Defaults to the latest file in .codex/runtime/observations/.",
    )
    parser.add_argument(
        "--output",
        help="Optional markdown output path. If omitted, the reducer prints to stdout.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"How many most recent observations to consider after promotion filtering. Default: {DEFAULT_LIMIT}.",
    )
    parser.add_argument(
        "--stage",
        default="stage-00",
        help="Stage label to include in the draft metadata. Default: stage-00.",
    )
    parser.add_argument(
        "--task",
        default="runtime-observation-reducer-draft",
        help="Task label to include in the draft metadata.",
    )
    parser.add_argument(
        "--title",
        default="Runtime Observation Reducer Draft",
        help="Markdown title for the generated draft.",
    )
    return parser.parse_args()


def resolve_observation_file(value: str | None) -> Path:
    if value:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if not path.exists():
            raise SystemExit(f"Observation file not found: {path}")
        return path

    candidates = observation_candidates()
    if not candidates:
        raise SystemExit(
            "No observation files found under .codex/runtime/observations/. "
            "Capture runtime observations first or pass --input."
        )
    return candidates[-1]


def observation_candidates() -> list[Path]:
    if not OBSERVATION_DIR.exists():
        return []
    files: list[Path] = []
    for path in sorted(OBSERVATION_DIR.glob("*.jsonl")):
        if path.name.startswith("_"):
            continue
        files.append(path)
    return files


def load_observations(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def select_entries(entries: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    promotable = [entry for entry in entries if entry.get("needs_governance_promotion") is True]
    source = promotable if promotable else entries
    if limit <= 0:
        return source
    return source[-limit:]


def render_handoff_draft(
    observation_file: Path,
    entries: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    stage: str,
    task: str,
    title: str,
) -> str:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    selected_sessions = unique_strings(selected, "session_id")
    shared_paths = count_shared_paths(selected)
    prompt_previews = ordered_unique_texts(selected, "prompt_preview")
    promotion_reasons = ordered_unique_texts(selected, "promotion_reason")
    runtime_only_count = sum(1 for entry in selected if entry.get("runtime_only_changes") is True)
    promotable_count = sum(1 for entry in entries if entry.get("needs_governance_promotion") is True)
    top_paths = [path for path, _ in shared_paths.most_common(MAX_SECTION_ITEMS)]
    repeated_paths = [path for path, count in shared_paths.items() if count > 1]

    content = "\n".join(
        [
            f"# {title}",
            "",
            f"更新时间：{now}",
            f"阶段：{stage}",
            f"任务：{task}",
            "状态：草稿",
            "",
            "## 本任务目标",
            "",
            "- 基于 runtime observations 提炼需要进入 repo 共享治理层的候选结论",
            "- 默认先产出 handoff 草稿，再由主 Agent 判断是否继续压缩到 status 或 ADR",
            "- 保持 reducer 为显式触发工具，而不是 hook 自动发布 canonical 文档",
            "",
            "## 已完成内容",
            "",
            f"- 已从 `{display_path(observation_file)}` 读取 {len(entries)} 条 observation 记录",
            f"- 已选取 {len(selected)} 条 observation 作为本次 handoff 草稿输入，其中 {promotable_count} 条显式标记为需要共享治理层提升",
            f"- 已覆盖 {len(selected_sessions)} 个 session，识别出 {len(top_paths)} 个共享层候选修改文件",
            bullet(
                prefixed_preview("提取到的主要 prompt 线索", prompt_previews, 3),
                "未从 observations 中提取到稳定的 prompt 线索",
            ),
            "",
            "## 修改文件",
            "",
            bullets_or_fallback(top_paths, "- 暂未从 observations 中提取到共享层修改文件"),
            "",
            "## 关键实现决策",
            "",
            "- reducer 是显式运行的脚本，不在 `Stop` hook 中自动执行",
            "- reducer 的默认输出顺序是 `observations -> handoff draft -> 主 Agent 审核 -> status/ADR`",
            "- 只有 observations 中的共享层线索才应进入 canonical 文档；runtime-only 记录继续停留在本地层",
            bullet(
                prefixed_preview("当前 observation 提升理由聚类", promotion_reasons, 2),
                "当前样本中尚未形成稳定的提升理由聚类",
            ),
            "",
            "## 当前未完成项",
            "",
            "- 需要主 Agent 审核本草稿，确认是否应该发布或更新 canonical handoff",
            "- 若同类 observation 已跨多次 session 稳定出现，再决定是否压缩到 status 或 ADR",
            "- 尚未把 reducer 输出接入 requirement/workstream metadata",
            "",
            "## 已知风险与注意事项",
            "",
            "- observations 来自 best-effort Stop hook，字段可能随上游 payload 变化而不完整",
            "- `changed_paths` 反映的是当前工作区可见改动，不保证严格等价于单次会话内的最小变更集",
            f"- 本次 reducer 输入中有 {runtime_only_count} 条 runtime-only observation，它们不应直接升格为共享真相",
            "",
            "## 已验证有效的路线",
            "",
            bullet(
                prefixed_preview("observations 中重复出现的共享层文件", repeated_paths, 3),
                "先从 observations 中出现频率更高的共享层文件入手，适合作为 handoff 审核起点",
            ),
            "- 先生成 handoff 草稿、再由主 Agent 决定是否发布 canonical 文档，符合 repo-first 治理边界",
            "",
            "## 已验证无效的路线",
            "",
            "- 仅凭 runtime-only observations 直接发布 canonical handoff、status 或 ADR，不符合当前治理模型",
            "- 让 reducer 自动改写共享治理文档会越过主 Agent 的语义判断边界",
            "",
            "## 尚未尝试但建议的路线",
            "",
            "- 将本草稿与相关 session 文件、active handoff 和 working-context 一起对读，再决定是否发布 canonical handoff",
            "- 如果同类 observation 在多个 session 中重复出现，可增加 status 或 ADR 候选压缩",
            "- 后续可在 reducer 中接入 requirement/workstream metadata，以提高追踪能力",
            "",
            "## 下一位 Agent 的第一步动作",
            "",
            f"- 先复核 `{display_path(observation_file)}` 的最近 observation，与当前 active handoff 和 `working-context.md` 对照，判断是否需要落地新的 canonical handoff",
            "",
            "## 建议同步更新",
            "",
            "- 若本草稿被采纳，更新 `docs/ai/index.md` 与 `working-context.md`",
            "- 若 reducer 输出已经形成长期稳定工作流结论，补充或更新 ADR",
        ]
    ) + "\n"
    return content


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


def compact_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip()


def string_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
