from __future__ import annotations

import re
from pathlib import Path


TECH_ASSUMPTION_HEADING_RE = re.compile(r"^(#+)\s+.*(技术假设|技术栈|技术选型|框架选型|数据库选型|架构事实)")
TECH_ASSUMPTION_LABEL_RE = re.compile(r"(技术假设|技术栈假设|技术选型|框架选型|数据库选型|架构事实)")
TECH_STATUS_RE = re.compile(
    r"\b(accepted|proposed|rejected|deferred)\b|(状态\s*[：:]\s*)?(已采纳|已接受|候选|拟议|提议|已拒绝|拒绝|暂缓|推迟)",
    re.IGNORECASE,
)
WEAK_STATUS_RE = re.compile(r"(待确认|待澄清|未确认|待定|需要决定|需要确认)")
VERIFICATION_METHOD_RE = re.compile(
    r"\bverification method\b|验证方式|验证方法|验收方式|验收方法|测试方式|测试方法|验证命令|测试命令|\b(smoke|test|pytest|go test|pnpm test|npm test|manual review|code review|pending)\b|待验证|待确认",
    re.IGNORECASE,
)


def is_candidate_assumption_line(raw_line: str, in_assumption_section: bool) -> bool:
    stripped = raw_line.strip()
    if not stripped or (stripped.startswith("|") and re.fullmatch(r"[\s|:-]+", stripped)):
        return False
    if stripped.startswith("|"):
        return bool(in_assumption_section or TECH_ASSUMPTION_LABEL_RE.search(stripped))
    if stripped.startswith(("-", "*", "+")):
        return bool(in_assumption_section or TECH_ASSUMPTION_LABEL_RE.search(stripped))
    return bool(TECH_ASSUMPTION_LABEL_RE.search(stripped))


def technical_assumption_record(raw_line: str) -> str:
    stripped = raw_line.strip()
    if stripped.startswith("|"):
        cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
        normalized = [cell.lower() for cell in cells]
        if {"claim", "status"}.issubset(set(normalized)) or {"技术假设", "状态"}.issubset(set(cells)):
            return ""
        return " | ".join(cells)
    return stripped.lstrip("-*+").strip()


def check_technical_assumption_record(
    path: Path,
    number: int,
    line: str,
    warnings: list[str],
    root: Path,
) -> None:
    record = technical_assumption_record(line)
    if not record:
        return
    location = f"{path.relative_to(root).as_posix()}:{number}"
    if not TECH_STATUS_RE.search(record):
        if WEAK_STATUS_RE.search(record):
            warnings.append(
                f"technical assumption has unresolved status, use accepted/proposed/rejected/deferred: {location}: {record}"
            )
        else:
            warnings.append(
                f"technical assumption missing status accepted/proposed/rejected/deferred: {location}: {record}"
            )
    if not VERIFICATION_METHOD_RE.search(record):
        warnings.append(f"technical assumption missing verification method: {location}: {record}")


def check_technical_assumption_lines(paths: list[Path], warnings: list[str], *, root: Path) -> None:
    for path in paths:
        in_assumption_section = False
        section_level = 0
        for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = raw_line.strip()
            heading = re.match(r"^(#+)\s+", stripped)
            if heading:
                level = len(heading.group(1))
                matched = bool(TECH_ASSUMPTION_HEADING_RE.search(stripped))
                if matched:
                    in_assumption_section = True
                    section_level = level
                elif in_assumption_section and level <= section_level:
                    in_assumption_section = False
                continue
            if is_candidate_assumption_line(raw_line, in_assumption_section):
                check_technical_assumption_record(path, number, raw_line, warnings, root)
