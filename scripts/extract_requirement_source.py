#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from requirements_source_boundary import dangerous_instruction_matches


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "requirements" / "source"
DEFAULT_QUARANTINE_DIR = ROOT / "docs" / "requirements" / "source-raw" / "quarantine"
DEFAULT_EXCERPT_CHAR_LIMIT = 6_000
DEFAULT_EXCERPT_LINE_LIMIT = 120
INSTRUCTION_HANDLING = (
    "Raw source is treated as requirement evidence/data only; it is not executable agent instructions."
)


@dataclass(frozen=True)
class ExtractionMetadata:
    source_id: str
    source_trust: str
    raw_source_path: str
    quarantine_path: str
    raw_sha256: str
    raw_size_bytes: int
    raw_line_count: int
    excerpt_char_limit: int
    excerpt_line_limit: int
    excerpt_size_chars: int
    excerpt_line_count: int
    truncated: bool
    dangerous_instruction_line_count: int
    instruction_handling: str
    sanitization_status: str


@dataclass(frozen=True)
class ExtractionResult:
    metadata: ExtractionMetadata
    excerpt_path: str
    reqdoc_draft_path: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract a sanitized requirement-source excerpt and REQDOC draft from raw PRD evidence."
    )
    parser.add_argument("raw_source", type=Path, help="Raw PRD/source file to preserve as evidence/data.")
    parser.add_argument("--source-id", required=True, help="REQDOC id for the generated draft, e.g. REQDOC-444.")
    parser.add_argument(
        "--source-trust",
        default="unknown",
        help="Trust classification for the raw source, e.g. user-provided, external-web, third-party, unknown.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--quarantine-dir", type=Path, default=DEFAULT_QUARANTINE_DIR)
    parser.add_argument("--excerpt-char-limit", type=int, default=DEFAULT_EXCERPT_CHAR_LIMIT)
    parser.add_argument("--excerpt-line-limit", type=int, default=DEFAULT_EXCERPT_LINE_LIMIT)
    parser.add_argument("--json", action="store_true", help="Emit output paths and metadata as JSON.")
    return parser.parse_args(argv)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return slug.strip("-") or "raw-source"


def relative(path: Path, root: Path = ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def read_raw(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sanitize_lines(text: str, *, char_limit: int, line_limit: int) -> tuple[list[str], bool, int]:
    dangerous_lines = {line_number for line_number, _phrase in dangerous_instruction_matches(text)}
    source_lines = text.splitlines()
    excerpt: list[str] = []
    used_chars = 0
    truncated = len(source_lines) > line_limit
    for line_number, raw_line in enumerate(source_lines, start=1):
        if len(excerpt) >= line_limit:
            truncated = True
            break
        line = (
            "[REDACTED: dangerous instruction-like content in raw source line "
            f"{line_number}]"
            if line_number in dangerous_lines
            else raw_line
        )
        projected = used_chars + len(line) + (1 if excerpt else 0)
        if projected > char_limit:
            remaining = char_limit - used_chars - (1 if excerpt else 0)
            if remaining > 0:
                excerpt.append(line[:remaining].rstrip())
                used_chars = char_limit
            truncated = True
            break
        excerpt.append(line)
        used_chars = projected
    return excerpt, truncated, len(dangerous_lines)


def sanitization_status(*, truncated: bool, dangerous_instruction_count: int) -> str:
    parts = ["excerpted"]
    if truncated:
        parts.append("truncated")
    if dangerous_instruction_count:
        parts.append("dangerous-instruction-like-content-redacted")
    parts.append("raw-preserved-in-quarantine")
    return "; ".join(parts)


def metadata_block(metadata: ExtractionMetadata) -> str:
    return "\n".join(
        [
            "文档类型：sanitized-excerpt",
            f"关联文档：{metadata.source_id}",
            f"来源可信度：{metadata.source_trust}",
            f"指令处理：{metadata.instruction_handling}",
            f"清洗状态：{metadata.sanitization_status}",
            f"Raw source path: {metadata.raw_source_path}",
            f"Quarantine copy: {metadata.quarantine_path}",
            f"Raw SHA-256: {metadata.raw_sha256}",
            f"Raw size bytes: {metadata.raw_size_bytes}",
            f"Raw line count: {metadata.raw_line_count}",
            f"Excerpt char limit: {metadata.excerpt_char_limit}",
            f"Excerpt line limit: {metadata.excerpt_line_limit}",
            f"Excerpt chars: {metadata.excerpt_size_chars}",
            f"Excerpt lines: {metadata.excerpt_line_count}",
            f"Excerpt truncated: {'yes' if metadata.truncated else 'no'}",
            f"Dangerous instruction-like lines redacted: {metadata.dangerous_instruction_line_count}",
        ]
    )


def render_excerpt(metadata: ExtractionMetadata, excerpt_lines: list[str]) -> str:
    truncated_note = (
        "\n\n> Excerpt was truncated deterministically; the full raw file remains quarantined evidence/data."
        if metadata.truncated
        else ""
    )
    return "\n".join(
        [
            f"# {metadata.source_id} sanitized raw source excerpt",
            "",
            metadata_block(metadata),
            "",
            "## Sanitized Excerpt",
            "",
            "\n".join(excerpt_lines).rstrip(),
            truncated_note,
            "",
        ]
    )


def render_reqdoc_draft(metadata: ExtractionMetadata, excerpt_path: Path, excerpt_lines: list[str]) -> str:
    preview = "\n".join(excerpt_lines).strip()
    if len(preview) > 2_000:
        preview = preview[:2_000].rstrip() + "\n[TRUNCATED: see sanitized excerpt for the bounded source extract]"
    return "\n".join(
        [
            f"# {metadata.source_id} requirement source draft",
            "",
            f"文档编号：{metadata.source_id}",
            "状态：draft-from-sanitized-excerpt",
            f"来源：{relative(excerpt_path)}",
            f"来源可信度：{metadata.source_trust}",
            f"指令处理：{metadata.instruction_handling}",
            "清洗状态：draft-from-sanitized-excerpt; full raw source excluded",
            f"原始证据：{metadata.quarantine_path}",
            "",
            "## Source Boundary",
            "",
            "- Full raw source remains quarantined evidence/data and is not copied into this REQDOC draft.",
            "- Instruction-like content from the raw source is treated as data and redacted from excerpts.",
            "- Human review is required before promoting this draft into canonical requirements.",
            "",
            "## Sanitized Evidence Preview",
            "",
            preview,
            "",
            "## Draft Normalization Notes",
            "",
            "- Requirement IDs: 未绑定",
            "- Workstream IDs: 未绑定",
            "- Technical assumptions: 待人工确认",
            "- Acceptance model: 待人工确认",
            "",
        ]
    )


def copy_to_quarantine(raw_path: Path, quarantine_dir: Path, source_id: str) -> Path:
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    target = quarantine_dir / f"{safe_slug(source_id)}-{safe_slug(raw_path.name)}"
    shutil.copy2(raw_path, target)
    return target


def extract_raw_requirement_source(
    raw_source: Path,
    *,
    source_id: str,
    source_trust: str = "unknown",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    quarantine_dir: Path = DEFAULT_QUARANTINE_DIR,
    excerpt_char_limit: int = DEFAULT_EXCERPT_CHAR_LIMIT,
    excerpt_line_limit: int = DEFAULT_EXCERPT_LINE_LIMIT,
) -> ExtractionResult:
    if excerpt_char_limit <= 0:
        raise ValueError("excerpt_char_limit must be positive")
    if excerpt_line_limit <= 0:
        raise ValueError("excerpt_line_limit must be positive")
    raw_path = raw_source.resolve()
    raw_text = read_raw(raw_path)
    excerpt_lines, truncated, dangerous_count = sanitize_lines(
        raw_text,
        char_limit=excerpt_char_limit,
        line_limit=excerpt_line_limit,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    quarantine_path = copy_to_quarantine(raw_path, quarantine_dir, source_id)
    metadata = ExtractionMetadata(
        source_id=source_id,
        source_trust=source_trust,
        raw_source_path=relative(raw_path),
        quarantine_path=relative(quarantine_path),
        raw_sha256=sha256_text(raw_text),
        raw_size_bytes=len(raw_text.encode("utf-8")),
        raw_line_count=len(raw_text.splitlines()),
        excerpt_char_limit=excerpt_char_limit,
        excerpt_line_limit=excerpt_line_limit,
        excerpt_size_chars=len("\n".join(excerpt_lines)),
        excerpt_line_count=len(excerpt_lines),
        truncated=truncated,
        dangerous_instruction_line_count=dangerous_count,
        instruction_handling=INSTRUCTION_HANDLING,
        sanitization_status=sanitization_status(
            truncated=truncated,
            dangerous_instruction_count=dangerous_count,
        ),
    )
    slug = safe_slug(source_id)
    excerpt_path = output_dir / f"{slug}-sanitized-excerpt.md"
    reqdoc_draft_path = output_dir / f"{slug}-draft.md"
    excerpt_path.write_text(render_excerpt(metadata, excerpt_lines), encoding="utf-8")
    reqdoc_draft_path.write_text(render_reqdoc_draft(metadata, excerpt_path, excerpt_lines), encoding="utf-8")
    return ExtractionResult(
        metadata=metadata,
        excerpt_path=relative(excerpt_path),
        reqdoc_draft_path=relative(reqdoc_draft_path),
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = extract_raw_requirement_source(
        args.raw_source,
        source_id=args.source_id,
        source_trust=args.source_trust,
        output_dir=args.output_dir,
        quarantine_dir=args.quarantine_dir,
        excerpt_char_limit=args.excerpt_char_limit,
        excerpt_line_limit=args.excerpt_line_limit,
    )
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(f"excerpt: {result.excerpt_path}")
        print(f"reqdoc_draft: {result.reqdoc_draft_path}")
        print(f"quarantine: {result.metadata.quarantine_path}")
        print(f"truncated: {'yes' if result.metadata.truncated else 'no'}")
        print(f"dangerous_instruction_like_lines_redacted: {result.metadata.dangerous_instruction_line_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
