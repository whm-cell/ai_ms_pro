from __future__ import annotations

import re
from pathlib import Path


SOURCE_TRUST_PREFIXES = ("来源可信度：", "来源可信度:", "Source trust:", "Source Trust:")
INSTRUCTION_HANDLING_PREFIXES = ("指令处理：", "指令处理:", "Instruction handling:", "Instruction Handling:")
SANITIZATION_STATUS_PREFIXES = ("清洗状态：", "清洗状态:", "Sanitization status:", "Sanitization Status:")
REVIEW_REQUIRED_SOURCE_TRUSTS = ("external-web", "third-party", "unknown")
PENDING_SANITIZATION_RE = re.compile(r"\bpending\b|待清洗|未清洗|待处理", re.IGNORECASE)
INSTRUCTION_AS_DATA_RE = re.compile(r"(证据|数据|evidence|data)", re.IGNORECASE)
INSTRUCTION_NOT_EXECUTABLE_RE = re.compile(
    r"(不得|不应|不能|不可|不是|not|never|must not|non-executable).*(指令|instructions?)|"
    r"(指令|instructions?).*(不得|不应|不能|不可|不是|not|never|must not|non-executable)",
    re.IGNORECASE,
)


def is_review_required_source_trust(value: str | None) -> bool:
    normalized = (value or "").lower()
    return any(source_trust in normalized for source_trust in REVIEW_REQUIRED_SOURCE_TRUSTS)


def prefixed_value(text: str, prefixes: tuple[str, ...]) -> str | None:
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        for prefix in prefixes:
            if stripped.startswith(prefix):
                return stripped[len(prefix):].strip()
    return None


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def check_external_content_boundary_metadata(
    source_docs: dict[str, Path],
    warnings: list[str],
    *,
    root: Path | None = None,
) -> None:
    repo_root = root or Path.cwd()
    for source_id, path in source_docs.items():
        text = path.read_text(encoding="utf-8")
        trust = prefixed_value(text, SOURCE_TRUST_PREFIXES)
        instruction_handling = prefixed_value(text, INSTRUCTION_HANDLING_PREFIXES)
        sanitization = prefixed_value(text, SANITIZATION_STATUS_PREFIXES)
        missing = [
            label
            for label, value in (
                ("source trust", trust),
                ("instruction handling", instruction_handling),
                ("sanitization status", sanitization),
            )
            if not value
        ]
        location = f"{source_id} ({relative(path, repo_root)})"
        if missing:
            warnings.append(
                f"external content boundary metadata missing {', '.join(missing)}; review required: {location}"
            )
            continue
        review_required_source = is_review_required_source_trust(trust)
        if review_required_source and PENDING_SANITIZATION_RE.search(sanitization or ""):
            warnings.append(
                f"external content boundary sanitization status is pending for {trust}; review required before using as implementation basis: {location}"
            )
        if not INSTRUCTION_AS_DATA_RE.search(instruction_handling or ""):
            suffix = "; review required" if review_required_source else ""
            warnings.append(
                f"external content boundary instruction handling should say source content is evidence/data{suffix}: {location}"
            )
        if not INSTRUCTION_NOT_EXECUTABLE_RE.search(instruction_handling or ""):
            suffix = "; review required" if review_required_source else ""
            warnings.append(
                f"external content boundary instruction handling should say source content is not executable agent instructions{suffix}: {location}"
            )
