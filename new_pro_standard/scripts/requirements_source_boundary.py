from __future__ import annotations

import re
from pathlib import Path


SOURCE_TRUST_PREFIXES = ("来源可信度：", "来源可信度:", "Source trust:", "Source Trust:")
INSTRUCTION_HANDLING_PREFIXES = ("指令处理：", "指令处理:", "Instruction handling:", "Instruction Handling:")
SANITIZATION_STATUS_PREFIXES = ("清洗状态：", "清洗状态:", "Sanitization status:", "Sanitization Status:")
SOURCE_EVIDENCE_TYPE_PREFIXES = ("文档类型：", "文档类型:", "Document type:", "Document Type:")
REVIEW_REQUIRED_SOURCE_TRUSTS = ("external-web", "third-party", "unknown")
QUARANTINE_MARKERS = ("quarantine", "quarantined", "隔离")
RAW_EVIDENCE_MARKERS = ("raw", "source-evidence", "raw-prd-evidence", "原始证据", "原始附件", "原文")
PENDING_SANITIZATION_RE = re.compile(r"\bpending\b|待清洗|未清洗|待处理", re.IGNORECASE)
SANITIZED_OR_EXCERPTED_RE = re.compile(
    r"summari[sz]ed|excerpted|saniti[sz]ed|redacted|cleaned|curated|摘要|摘录|清洗|脱敏",
    re.IGNORECASE,
)
INSTRUCTION_AS_DATA_RE = re.compile(r"(证据|数据|evidence|data)", re.IGNORECASE)
INSTRUCTION_NOT_EXECUTABLE_RE = re.compile(
    r"(不得|不应|不能|不可|不是|not|never|must not|non-executable).*(指令|instructions?)|"
    r"(指令|instructions?).*(不得|不应|不能|不可|不是|not|never|must not|non-executable)",
    re.IGNORECASE,
)
DANGEROUS_INSTRUCTION_RE = re.compile(
    r"\bSYSTEM_OVERRIDE\b|\bADMIN_INSTRUCTION\b|ignore (all )?(previous|prior) instructions?|"
    r"disregard (all )?(previous|prior) instructions?|disable safety filters?|"
    r"turn off safety|developer mode|jailbreak|reveal (the )?system prompt|"
    r"override (the )?system|忽略(之前|先前|以上).*指令|系统覆盖|管理员指令|"
    r"禁用安全|关闭安全|绕过安全|泄露系统提示",
    re.IGNORECASE,
)
LARGE_SOURCE_WARNING_BYTES = 60_000


def is_review_required_source_trust(value: str | None) -> bool:
    normalized = (value or "").lower()
    return any(source_trust in normalized for source_trust in REVIEW_REQUIRED_SOURCE_TRUSTS)


def has_marker(value: str | None, markers: tuple[str, ...]) -> bool:
    normalized = (value or "").lower()
    return any(marker in normalized for marker in markers)


def is_quarantined_or_raw_evidence(
    trust: str | None,
    sanitization: str | None,
    doc_type: str | None,
) -> bool:
    return (
        has_marker(trust, QUARANTINE_MARKERS)
        or has_marker(sanitization, QUARANTINE_MARKERS)
        or has_marker(doc_type, QUARANTINE_MARKERS)
        or has_marker(sanitization, RAW_EVIDENCE_MARKERS)
        or has_marker(doc_type, RAW_EVIDENCE_MARKERS)
    )


def is_summarized_excerpted_or_sanitized(value: str | None) -> bool:
    return bool(SANITIZED_OR_EXCERPTED_RE.search(value or ""))


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


def dangerous_instruction_matches(text: str) -> list[tuple[int, str]]:
    matches: list[tuple[int, str]] = []
    for number, raw_line in enumerate(text.splitlines(), start=1):
        match = DANGEROUS_INSTRUCTION_RE.search(raw_line)
        if match:
            matches.append((number, match.group(0)))
    return matches


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
        doc_type = prefixed_value(text, SOURCE_EVIDENCE_TYPE_PREFIXES)
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
        quarantined_or_raw = is_quarantined_or_raw_evidence(trust, sanitization, doc_type)
        sanitized_or_excerpted = is_summarized_excerpted_or_sanitized(sanitization)
        if review_required_source and PENDING_SANITIZATION_RE.search(sanitization or ""):
            warnings.append(
                f"external content boundary sanitization status is pending for {trust}; review required before using as implementation basis: {location}"
            )
        if quarantined_or_raw and not sanitized_or_excerpted:
            warnings.append(
                f"external content boundary classified as quarantined/raw evidence and is not summarized/excerpted/sanitized; review required before implementation basis: {location}"
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
        for line_number, phrase in dangerous_instruction_matches(text):
            suffix = "; quarantine before use" if (review_required_source or quarantined_or_raw) else ""
            warnings.append(
                f"external content boundary dangerous instruction-like content '{phrase}' at line {line_number}{suffix}: {location}"
            )
        if path.stat().st_size > LARGE_SOURCE_WARNING_BYTES and not sanitized_or_excerpted:
            warnings.append(
                f"external content boundary large source is not marked summarized/excerpted/sanitized ({path.stat().st_size} bytes): {location}"
            )
