#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AI_DIR = ROOT / "docs" / "ai"
REQ_DIR = ROOT / "docs" / "requirements"
RUNTIME_SESSION_TEMPLATE = ROOT / ".codex" / "runtime" / "sessions" / "_template.md"

PLACEHOLDER_MARKERS = [
    "待补充",
    "TODO",
    "TBD",
]

CORE_REQUIRED_SECTION_MAP: dict[Path, list[str]] = {
    AI_DIR / "plan.md": [
        "## 使用边界",
        "## 项目目标",
        "## 范围定义",
        "## 阶段规划",
    ],
    AI_DIR / "working-context.md": [
        "## 同步元数据",
        "## 当前主目标",
        "## 当前活跃队列",
        "## 当前风险与阻塞",
        "## 下一次会话先读",
        "## 更新规则",
    ],
}

HANDOFF_REQUIRED_SECTIONS = [
    "## 需求与工作流标识",
    "## 本任务目标",
    "## 已完成内容",
    "## 修改文件",
    "## 关键实现决策",
    "## 当前未完成项",
    "## 已知风险与注意事项",
    "## 已验证有效的路线",
    "## 已验证无效的路线",
    "## 尚未尝试但建议的路线",
    "## 下一位 Agent 的第一步动作",
]

STATUS_REQUIRED_SECTIONS = [
    "## 需求与工作流标识",
    "## 当前阶段目标",
    "## 当前完成度",
    "## 本阶段关键成果",
    "## 风险与阻塞",
    "## 下一阶段重点",
    "## 验收判断",
]

RUNTIME_SESSION_REQUIRED_SECTIONS = [
    "## 需求与工作流标识",
    "## 当前目标",
    "## 会话范围与触发背景",
    "## 已做动作",
    "## 触碰文件",
    "## 当前 Open Loops",
    "## 需提升到共享治理层的内容",
    "## 下次 Resume 提示",
    "## 是否需要提升为 Handoff",
]

CHANGELOG_REQUIRED_SECTIONS = [
    "## 新增功能",
    "## 修复问题",
    "## 行为变化",
    "## 破坏性变更",
    "## 验证范围",
]

ADR_REQUIRED_SECTIONS = [
    "## 背景",
    "## 决策",
    "## 备选方案",
    "## 决策理由",
    "## 影响",
]

NORMALIZED_REQUIREMENT_SECTIONS = [
    "## 背景",
    "## 目标",
    "## 范围",
    "## 验收条件",
    "## 依赖与前置条件",
]

WORKSTREAM_SECTION_CHOICES = [
    ["## 使用边界"],
    ["## 业务目标"],
    ["## 覆盖需求"],
    ["## 主要模块"],
    ["## 阶段拆分建议"],
    ["## 验收模型", "## 验收重点"],
]


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_docs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    files: list[Path] = []
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        if path.name == "README.md":
            continue
        files.append(path)
    return files


def check_required_sections(path: Path, sections: list[str], errors: list[str]) -> None:
    text = load_text(path)
    for section in sections:
        if section not in text:
            errors.append(f"Missing section in {path.relative_to(ROOT)}: {section}")


def check_required_section_choices(path: Path, section_choices: list[list[str]], errors: list[str]) -> None:
    text = load_text(path)
    for choices in section_choices:
        if any(section in text for section in choices):
            continue
        rendered = " | ".join(choices)
        errors.append(f"Missing one of sections in {path.relative_to(ROOT)}: {rendered}")


def check_placeholder_markers(path: Path, warnings: list[str]) -> None:
    text = load_text(path)
    for marker in PLACEHOLDER_MARKERS:
        if marker in text:
            warnings.append(f"Placeholder marker '{marker}' found in {path.relative_to(ROOT)}")


def check_required_documents(errors: list[str]) -> None:
    for path, sections in CORE_REQUIRED_SECTION_MAP.items():
        if not path.exists():
            errors.append(f"Required quality-controlled document missing: {path.relative_to(ROOT)}")
            continue
        check_required_sections(path, sections, errors)


def check_section_collection(
    directory: Path,
    sections: list[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    for path in iter_docs(directory):
        check_required_sections(path, sections, errors)
        check_placeholder_markers(path, warnings)


def check_optional_template(path: Path, sections: list[str], errors: list[str]) -> None:
    if path.exists():
        check_required_sections(path, sections, errors)


def check_workstream_docs(errors: list[str], warnings: list[str]) -> None:
    for path in iter_docs(REQ_DIR / "workstreams"):
        check_required_section_choices(path, WORKSTREAM_SECTION_CHOICES, errors)
        check_placeholder_markers(path, warnings)


def run_quality_checks(errors: list[str], warnings: list[str]) -> None:
    check_required_documents(errors)
    check_section_collection(AI_DIR / "handoffs" / "active", HANDOFF_REQUIRED_SECTIONS, errors, warnings)
    check_optional_template(AI_DIR / "handoffs" / "active" / "_template.md", HANDOFF_REQUIRED_SECTIONS, errors)
    check_section_collection(AI_DIR / "status", STATUS_REQUIRED_SECTIONS, errors, warnings)
    check_optional_template(AI_DIR / "status" / "_template.md", STATUS_REQUIRED_SECTIONS, errors)
    check_optional_template(RUNTIME_SESSION_TEMPLATE, RUNTIME_SESSION_REQUIRED_SECTIONS, errors)
    check_section_collection(AI_DIR / "changelog", CHANGELOG_REQUIRED_SECTIONS, errors, warnings)
    check_section_collection(AI_DIR / "adr", ADR_REQUIRED_SECTIONS, errors, warnings)
    check_section_collection(REQ_DIR / "normalized", NORMALIZED_REQUIREMENT_SECTIONS, errors, warnings)
    check_workstream_docs(errors, warnings)
    check_placeholder_markers(AI_DIR / "working-context.md", warnings)


def print_result(errors: list[str], warnings: list[str]) -> int:
    if errors:
        print("AI docs quality check: FAILED")
        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARN: {message}")
        return 1

    print("AI docs quality check: OK")
    for message in warnings:
        print(f"WARN: {message}")
    return 0


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    run_quality_checks(errors, warnings)
    return print_result(errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
