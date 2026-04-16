#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AI_DIR = ROOT / "docs" / "ai"
REQ_DIR = ROOT / "docs" / "requirements"

PLACEHOLDER_MARKERS = [
    "待补充",
    "TODO",
    "TBD",
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


def check_placeholder_markers(path: Path, warnings: list[str]) -> None:
    text = load_text(path)
    for marker in PLACEHOLDER_MARKERS:
        if marker in text:
            warnings.append(f"Placeholder marker '{marker}' found in {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    required_section_map: dict[Path, list[str]] = {
        AI_DIR / "working-context.md": [
            "## 当前主目标",
            "## 当前活跃队列",
            "## 当前风险与阻塞",
            "## 下一次会话先读",
            "## 更新规则",
        ],
    }

    for path, sections in required_section_map.items():
        if not path.exists():
            errors.append(f"Required quality-controlled document missing: {path.relative_to(ROOT)}")
            continue
        check_required_sections(path, sections, errors)

    for path in iter_docs(AI_DIR / "handoffs" / "active"):
        check_required_sections(
            path,
            [
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
            ],
            errors,
        )
        check_placeholder_markers(path, warnings)

    template_path = AI_DIR / "handoffs" / "active" / "_template.md"
    if template_path.exists():
        check_required_sections(
            template_path,
            [
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
            ],
            errors,
        )

    for path in iter_docs(AI_DIR / "status"):
        check_required_sections(
            path,
            [
                "## 当前阶段目标",
                "## 当前完成度",
                "## 本阶段关键成果",
                "## 风险与阻塞",
                "## 下一阶段重点",
                "## 验收判断",
            ],
            errors,
        )
        check_placeholder_markers(path, warnings)

    for path in iter_docs(AI_DIR / "changelog"):
        check_required_sections(
            path,
            [
                "## 新增功能",
                "## 修复问题",
                "## 行为变化",
                "## 破坏性变更",
                "## 验证范围",
            ],
            errors,
        )
        check_placeholder_markers(path, warnings)

    for path in iter_docs(AI_DIR / "adr"):
        check_required_sections(
            path,
            [
                "## 背景",
                "## 决策",
                "## 备选方案",
                "## 决策理由",
                "## 影响",
            ],
            errors,
        )
        check_placeholder_markers(path, warnings)

    for path in iter_docs(REQ_DIR / "normalized"):
        check_required_sections(
            path,
            [
                "## 背景",
                "## 目标",
                "## 范围",
                "## 验收条件",
                "## 依赖与前置条件",
            ],
            errors,
        )
        check_placeholder_markers(path, warnings)

    for path in iter_docs(REQ_DIR / "workstreams"):
        check_required_sections(
            path,
            [
                "## 业务目标",
                "## 覆盖需求",
                "## 主要模块",
                "## 阶段拆分建议",
                "## 验收重点",
            ],
            errors,
        )
        check_placeholder_markers(path, warnings)

    check_placeholder_markers(AI_DIR / "working-context.md", warnings)

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


if __name__ == "__main__":
    raise SystemExit(main())
