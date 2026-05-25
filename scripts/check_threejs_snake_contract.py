#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "apps" / "threejs-snake"
INDEX_PATH = APP_ROOT / "index.html"
MAIN_PATH = APP_ROOT / "main.js"
STYLE_PATH = APP_ROOT / "style.css"

REQUIRED_IDS = {
    "game",
    "score",
    "best",
    "overlay",
    "title",
    "message",
    "restart",
}
REQUIRED_SMOKE_METHODS = {"getSnapshot", "restart", "placeFoodAhead", "step"}
REQUIRED_REQUIREMENTS = {"REQ-001", "REQ-002", "REQ-003"}
REQUIRED_WORKSTREAMS = {"WS-01"}


@dataclass(frozen=True)
class HtmlSummary:
    ids: set[str]
    classes: set[str]
    scripts: list[dict[str, str]]
    importmaps: list[str]


class AppHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.classes: set[str] = set()
        self.scripts: list[dict[str, str]] = []
        self.importmaps: list[str] = []
        self._inside_importmap = False
        self._importmap_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        if element_id := attr_map.get("id"):
            self.ids.add(element_id)
        for class_name in attr_map.get("class", "").split():
            self.classes.add(class_name)
        if tag == "script":
            self.scripts.append(attr_map)
            if attr_map.get("type") == "importmap":
                self._inside_importmap = True
                self._importmap_parts = []

    def handle_data(self, data: str) -> None:
        if self._inside_importmap:
            self._importmap_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._inside_importmap:
            self.importmaps.append("".join(self._importmap_parts))
            self._inside_importmap = False
            self._importmap_parts = []


def parse_html(text: str) -> HtmlSummary:
    parser = AppHtmlParser()
    parser.feed(text)
    return HtmlSummary(
        ids=parser.ids,
        classes=parser.classes,
        scripts=parser.scripts,
        importmaps=parser.importmaps,
    )


def find_smoke_methods(main_js: str) -> set[str]:
    api_match = re.search(
        r"window\.__THREEJS_SNAKE_TEST__\s*=\s*Object\.freeze\(\{(?P<body>.*?)\n\s*\}\);",
        main_js,
        flags=re.S,
    )
    if api_match is None:
        return set()
    return set(re.findall(r"^\s*([A-Za-z]\w*)\(", api_match.group("body"), flags=re.M))


def validate_importmap(summary: HtmlSummary, errors: list[str]) -> None:
    if not summary.importmaps:
        errors.append("index.html must define a browser importmap for Three.js.")
        return

    try:
        importmap = json.loads(summary.importmaps[0])
    except json.JSONDecodeError as exc:
        errors.append(f"index.html importmap is invalid JSON: {exc.msg}")
        return

    imports = importmap.get("imports")
    if not isinstance(imports, dict):
        errors.append("index.html importmap must contain an imports object.")
        return

    three_url = imports.get("three")
    if not isinstance(three_url, str) or "three@" not in three_url or not three_url.endswith("/build/three.module.js"):
        errors.append("index.html importmap must pin the `three` browser module URL.")


def validate_html(summary: HtmlSummary, errors: list[str]) -> None:
    missing_ids = sorted(REQUIRED_IDS - summary.ids)
    if missing_ids:
        errors.append(f"index.html missing required DOM ids: {', '.join(missing_ids)}")

    if "hint" not in summary.classes:
        errors.append("index.html must include the .hint element used by blackbox smoke.")

    module_scripts = [script for script in summary.scripts if script.get("type") == "module"]
    if not any(script.get("src") == "./main.js" for script in module_scripts):
        errors.append("index.html must load ./main.js as a module script.")

    validate_importmap(summary, errors)


def validate_main_js(main_js: str, errors: list[str]) -> None:
    if 'import * as THREE from "three";' not in main_js:
        errors.append('main.js must import Three.js through the importmap alias: import * as THREE from "three";')

    for requirement_id in sorted(REQUIRED_REQUIREMENTS):
        if requirement_id not in main_js:
            errors.append(f"main.js missing requirement metadata: {requirement_id}")

    for workstream_id in sorted(REQUIRED_WORKSTREAMS):
        if workstream_id not in main_js:
            errors.append(f"main.js missing workstream metadata: {workstream_id}")

    if "new THREE.WebGLRenderer" not in main_js:
        errors.append("main.js must instantiate THREE.WebGLRenderer.")

    if "SMOKE_MODE" not in main_js or "window.__THREEJS_SNAKE_TEST__" not in main_js:
        errors.append("main.js must expose the namespaced smoke API only for smoke mode.")

    missing_methods = sorted(REQUIRED_SMOKE_METHODS - find_smoke_methods(main_js))
    if missing_methods:
        errors.append(f"main.js smoke API missing methods: {', '.join(missing_methods)}")

    if "overlayHidden" not in main_js or "restartLabel" not in main_js:
        errors.append("main.js smoke snapshot must include UI state fields used by smoke tests.")


def validate() -> list[str]:
    errors: list[str] = []
    for path in (INDEX_PATH, MAIN_PATH, STYLE_PATH):
        if not path.exists():
            errors.append(f"required app file missing: {path.relative_to(ROOT)}")
    if errors:
        return errors

    validate_html(parse_html(INDEX_PATH.read_text(encoding="utf-8")), errors)
    validate_main_js(MAIN_PATH.read_text(encoding="utf-8"), errors)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Three.js Snake contract check: FAILED")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Three.js Snake contract check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
