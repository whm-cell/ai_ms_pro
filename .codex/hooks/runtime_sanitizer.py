from __future__ import annotations

import re
from typing import Any


DEFAULT_MAX_LENGTH = 300

SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        "[REDACTED_PRIVATE_KEY]",
    ),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_ACCESS_KEY]"),
    (
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
        "[REDACTED_JWT]",
    ),
    (
        re.compile(
            r"(?i)\b(authorization)\s*[:=]\s*(bearer|basic)\s+[A-Za-z0-9._~+/=-]{12,}"
        ),
        r"\1: [REDACTED_AUTH_HEADER]",
    ),
    (
        re.compile(
            r"(?i)\b(password|passwd|pwd|token|api[_-]?key|secret|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*([^\s'\"`,;]+)"
        ),
        r"\1=[REDACTED_SECRET]",
    ),
    (
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "[REDACTED_EMAIL]",
    ),
    (
        re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)"),
        "[REDACTED_PHONE]",
    ),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "[REDACTED_PHONE]"),
)

PATH_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"/Users/[^/\s]+"), "/Users/[REDACTED_USER]"),
    (re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+"), r"C:\\Users\\[REDACTED_USER]"),
)


def compact_text(value: Any, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    if not isinstance(value, str):
        return ""
    compact = normalize_space(redact_sensitive_text(value))
    return compact[:max_length].strip()


def compact_transcript_path(value: Any, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    if not isinstance(value, str):
        return ""
    compact = normalize_space(redact_sensitive_text(value))
    tail = transcript_tail(compact)
    if tail:
        compact = f"[REDACTED_PATH]/{tail}"
    return compact[:max_length].strip()


def redact_sensitive_text(value: str) -> str:
    redacted = value
    for pattern, replacement in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    for pattern, replacement in PATH_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def transcript_tail(value: str) -> str:
    if "/" not in value and "\\" not in value:
        return ""
    parts = re.split(r"[\\/]", value)
    return parts[-1].strip()
