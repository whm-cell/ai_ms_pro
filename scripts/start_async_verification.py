#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / ".codex" / "runtime" / "async-verification"


@dataclass(frozen=True)
class CommandSpec:
    label: str
    args: tuple[str, ...]


@dataclass(frozen=True)
class CommandResult:
    label: str
    exit_code: int
    started_at: str
    finished_at: str


PRESETS: dict[str, tuple[CommandSpec, ...]] = {
    "active-browser-smoke": (
        CommandSpec("threejs-snake-smoke", (sys.executable, "scripts/threejs_snake_smoke.py")),
        CommandSpec(
            "threejs-snake-blackbox-smoke",
            (sys.executable, "scripts/threejs_snake_blackbox_smoke.py"),
        ),
        CommandSpec(
            "harness-trace-console-smoke",
            (sys.executable, "scripts/harness_trace_console_smoke.py"),
        ),
        CommandSpec(
            "harness-trace-console-blackbox-smoke",
            (sys.executable, "scripts/harness_trace_console_blackbox_smoke.py"),
        ),
    ),
    "active-static-contracts": (
        CommandSpec("threejs-snake-contract", (sys.executable, "scripts/check_threejs_snake_contract.py")),
        CommandSpec("ai-governance", (sys.executable, "scripts/check_ai_governance.py")),
        CommandSpec("context-budget", (sys.executable, "scripts/check_context_budget.py")),
    ),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start bounded local async verification presets.")
    parser.add_argument("preset", nargs="?", help="Verification preset name.")
    parser.add_argument("run_id", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--list", action="store_true", help="List preset names.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them.")
    parser.add_argument("--foreground", action="store_true", help="Run synchronously and stream output.")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_id_for(preset: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    return f"{stamp}-{preset}"


def run_dir_for(run_id: str) -> Path:
    return RUNTIME_ROOT / run_id


def status_path(run_dir: Path) -> Path:
    return run_dir / "status.json"


def log_path(run_dir: Path) -> Path:
    return run_dir / "verification.log"


def status_payload(
    *,
    preset: str,
    run_id: str,
    state: str,
    started_at: str | None,
    finished_at: str | None,
    command_results: list[CommandResult] | None = None,
    error: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "async-verification/v1",
        "preset": preset,
        "run_id": run_id,
        "state": state,
        "started_at": started_at,
        "finished_at": finished_at,
        "command_results": [asdict(result) for result in command_results or []],
    }
    if error:
        payload["error"] = error
    return payload


def write_status(run_dir: Path, payload: dict[str, object]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    status_path(run_dir).write_text(f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n", encoding="utf-8")


def append_log(run_dir: Path, text: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    with log_path(run_dir).open("a", encoding="utf-8") as handle:
        handle.write(text)


def dry_run(preset: str) -> int:
    commands = PRESETS.get(preset)
    if commands is None:
        print(f"Unknown async verification preset: {preset}", file=sys.stderr)
        return 1
    for command in commands:
        print(f"{command.label}: {' '.join(command.args)}")
    return 0


def run_command(command: CommandSpec, run_dir: Path, *, foreground: bool) -> CommandResult:
    started_at = utc_now()
    append_log(run_dir, f"\n$ {' '.join(command.args)}\n")
    env = os.environ.copy()
    env["AI_MS_PRO_ASYNC_VERIFICATION_RUN_DIR"] = str(run_dir)
    process = subprocess.run(
        list(command.args),
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = process.stdout or ""
    append_log(run_dir, output)
    if foreground and output:
        print(output, end="")
    finished_at = utc_now()
    append_log(run_dir, f"\n[{command.label}] exit={process.returncode}\n")
    return CommandResult(
        label=command.label,
        exit_code=process.returncode,
        started_at=started_at,
        finished_at=finished_at,
    )


def run_preset(preset: str, run_id: str, *, foreground: bool) -> int:
    commands = PRESETS.get(preset)
    if commands is None:
        print(f"Unknown async verification preset: {preset}", file=sys.stderr)
        return 1

    run_dir = run_dir_for(run_id)
    started_at = utc_now()
    results: list[CommandResult] = []
    write_status(run_dir, status_payload(preset=preset, run_id=run_id, state="running", started_at=started_at, finished_at=None))
    append_log(run_dir, f"Async verification {run_id}\nPreset: {preset}\nStarted: {started_at}\n")
    try:
        for command in commands:
            result = run_command(command, run_dir, foreground=foreground)
            results.append(result)
            write_status(
                run_dir,
                status_payload(
                    preset=preset,
                    run_id=run_id,
                    state="running",
                    started_at=started_at,
                    finished_at=None,
                    command_results=results,
                ),
            )
            if result.exit_code != 0:
                finished_at = utc_now()
                write_status(
                    run_dir,
                    status_payload(
                        preset=preset,
                        run_id=run_id,
                        state="failed",
                        started_at=started_at,
                        finished_at=finished_at,
                        command_results=results,
                    ),
                )
                return result.exit_code
        finished_at = utc_now()
        write_status(
            run_dir,
            status_payload(
                preset=preset,
                run_id=run_id,
                state="passed",
                started_at=started_at,
                finished_at=finished_at,
                command_results=results,
            ),
        )
        append_log(run_dir, f"\nCompleted: {finished_at}\n")
        return 0
    except Exception as exc:
        finished_at = utc_now()
        write_status(
            run_dir,
            status_payload(
                preset=preset,
                run_id=run_id,
                state="error",
                started_at=started_at,
                finished_at=finished_at,
                command_results=results,
                error=str(exc),
            ),
        )
        append_log(run_dir, f"\nERROR: {exc}\n")
        return 1


def start_detached(preset: str, run_id: str) -> Path:
    run_dir = run_dir_for(run_id)
    write_status(run_dir, status_payload(preset=preset, run_id=run_id, state="queued", started_at=None, finished_at=None))
    subprocess.Popen(  # noqa: S603 - argv-only self invocation, no shell.
        [sys.executable, str(Path(__file__).resolve()), "--worker", preset, run_id],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=(os.name != "nt"),
    )
    return run_dir


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list:
        print("\n".join(sorted(PRESETS)))
        return 0
    if not args.preset:
        print("Missing preset. Use --list to see available presets.", file=sys.stderr)
        return 1
    if args.dry_run:
        return dry_run(args.preset)
    if args.worker:
        if not args.run_id:
            print("Worker mode requires run_id.", file=sys.stderr)
            return 1
        return run_preset(args.preset, args.run_id, foreground=False)
    run_id = run_id_for(args.preset)
    if args.foreground:
        return run_preset(args.preset, run_id, foreground=True)
    run_dir = start_detached(args.preset, run_id)
    print(f"Started async verification {run_id}")
    print(f"Status: {status_path(run_dir).relative_to(ROOT)}")
    print(f"Log: {log_path(run_dir).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
