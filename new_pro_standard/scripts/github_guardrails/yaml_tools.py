from __future__ import annotations

import re


def simple_yaml_top_map(text: str, key: str) -> dict[str, str]:
    lines = text.splitlines()
    values: dict[str, str] = {}
    in_block = False
    for line in lines:
        if not in_block:
            in_block = line.strip() == f"{key}:"
            continue
        if line and not line.startswith(" "):
            break
        match = re.match(r"\s{2}([A-Za-z0-9_-]+):\s*(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip("'\"")
    return values


def simple_yaml_jobs(text: str) -> set[str]:
    lines = text.splitlines()
    jobs: set[str] = set()
    in_jobs = False
    for line in lines:
        if not in_jobs:
            in_jobs = line.strip() == "jobs:"
            continue
        if line and not line.startswith(" "):
            break
        match = re.match(r"\s{2}([A-Za-z0-9_-]+):\s*$", line)
        if match:
            jobs.add(match.group(1))
    return jobs


def has_top_key(text: str, key: str) -> bool:
    return any(line.strip() == f"{key}:" for line in text.splitlines())


def has_event_trigger(text: str, event: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("on:") and event in stripped:
            return True
        if stripped != "on:":
            continue
        for nested in lines[index + 1:]:
            if nested and not nested.startswith(" "):
                break
            if re.match(rf"\s{{2}}{re.escape(event)}\s*:", nested):
                return True
    return False
