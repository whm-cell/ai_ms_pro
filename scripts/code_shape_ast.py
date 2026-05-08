from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class DefinitionShape:
    qualname: str
    lines: int


class ShapeVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.stack: list[str] = []
        self.functions: list[DefinitionShape] = []
        self.classes: list[DefinitionShape] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append(DefinitionShape(self._qualname(node.name), self._lines(node)))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.append(DefinitionShape(self._qualname(node.name), self._lines(node)))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.functions.append(DefinitionShape(self._qualname(node.name), self._lines(node)))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def _qualname(self, name: str) -> str:
        return ".".join([*self.stack, name]) if self.stack else name

    @staticmethod
    def _lines(node: ast.AST) -> int:
        start = getattr(node, "lineno", 0)
        end = getattr(node, "end_lineno", start)
        return end - start + 1


def collect_python_shapes(text: str) -> tuple[list[DefinitionShape], list[DefinitionShape]]:
    tree = ast.parse(text)
    visitor = ShapeVisitor()
    visitor.visit(tree)
    return visitor.functions, visitor.classes


def summarize(items: list[DefinitionShape], limit: int) -> str:
    offenders = [item for item in items if item.lines > limit]
    offenders.sort(key=lambda item: item.lines, reverse=True)
    preview = ", ".join(f"{item.qualname} ({item.lines})" for item in offenders[:3])
    if len(offenders) > 3:
        preview += f", +{len(offenders) - 3} more"
    return preview
