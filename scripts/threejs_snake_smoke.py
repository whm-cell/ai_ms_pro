#!/usr/bin/env python3
from __future__ import annotations

import argparse
import functools
import http.server
import os
import shutil
import socket
import socketserver
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
APP_URL_PATH = "/apps/threejs-snake/?smoke=1"
PLAYWRIGHT_BROWSER_VERSION = os.environ.get("PLAYWRIGHT_VERSION", "1.59.1")
PLAYWRIGHT_CLI_VERSION = os.environ.get("PLAYWRIGHT_CLI_VERSION", "0.1.13")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a lightweight browser smoke test against apps/threejs-snake.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface for the local static server. Default: 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port for the local static server. Default: auto-select a free port.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Launch the browser in headed mode for manual observation.",
    )
    parser.add_argument(
        "--url",
        default="",
        help="Use an already-served app URL instead of starting a local static server.",
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Require --url and do not bind a local static server.",
    )
    args = parser.parse_args()
    if args.no_server and not args.url:
        parser.error("--no-server requires --url.")
    if args.url and not args.url.startswith(("http://", "https://")):
        parser.error("--url must be an http:// or https:// URL.")
    return args


def find_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return int(sock.getsockname()[1])


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def start_static_server(host: str, port: int) -> tuple[socketserver.TCPServer, threading.Thread, int]:
    handler_cls = functools.partial(QuietHandler, directory=str(REPO_ROOT))
    server = socketserver.TCPServer((host, port), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, int(server.server_address[1])


def wait_for_server(host: str, port: int, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    url = f"http://{host}:{port}/apps/threejs-snake/index.html"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"Static server did not become ready in time: {url}")


def wait_for_url(url: str, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as response:
                if 200 <= response.status < 400:
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"External app URL did not become ready in time: {url}")


def run_command(cmd: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def ensure_npx() -> None:
    if shutil.which("npx"):
        return
    raise RuntimeError("npx is required to run this smoke test.")


def run_pw(command: str, *args: str, env: dict[str, str]) -> None:
    cmd = [
        "npx",
        "--yes",
        "--package",
        f"@playwright/cli@{PLAYWRIGHT_CLI_VERSION}",
        "playwright-cli",
        "--session",
        env["PLAYWRIGHT_CLI_SESSION"],
        command,
        *args,
    ]
    result = run_command(cmd, env=env)
    if result.returncode == 0:
        return

    details = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    help_note = (
        "\nOne-time browser install may be required: "
        f"`npx --yes --package=playwright@{PLAYWRIGHT_BROWSER_VERSION} playwright install chromium`"
    )
    raise RuntimeError(f"Playwright CLI command failed: {' '.join(cmd)}\n{details}{help_note}")


def run_browser_code(source: str, env: dict[str, str]) -> None:
    run_pw(
        "run-code",
        source.strip(),
        env=env,
    )


def verify_initial_state(env: dict[str, str]) -> None:
    run_browser_code(
        """
await page.waitForLoadState("domcontentloaded");
await page.waitForFunction(() => Boolean(window.__THREEJS_SNAKE_TEST__));
const snapshot = await page.evaluate(() => window.__THREEJS_SNAKE_TEST__.restart());
if (!snapshot.running || snapshot.gameOver || !snapshot.overlayHidden || snapshot.score !== 0) {
  throw new Error(`Unexpected initial snapshot: ${JSON.stringify(snapshot)}`);
}
if (snapshot.paused || snapshot.status !== "Running") {
  throw new Error(`Expected running status in initial snapshot, got ${JSON.stringify(snapshot)}`);
}
if (!snapshot.requirementIds.includes("REQ-001") || !snapshot.workstreamIds.includes("WS-01")) {
  throw new Error(`Expected WS-01 metadata in snapshot, got ${JSON.stringify(snapshot)}`);
}
        """,
        env=env,
    )


def verify_pause_resume(env: dict[str, str]) -> None:
    run_browser_code(
        """
const paused = await page.evaluate(() => window.__THREEJS_SNAKE_TEST__.pause());
if (!paused.paused || paused.running || paused.overlayHidden || paused.title !== "Paused" || paused.restartLabel !== "Resume") {
  throw new Error(`Expected pause state, got ${JSON.stringify(paused)}`);
}
const resumed = await page.evaluate(() => window.__THREEJS_SNAKE_TEST__.resume());
if (resumed.paused || !resumed.running || !resumed.overlayHidden || resumed.status !== "Running") {
  throw new Error(`Expected resume state, got ${JSON.stringify(resumed)}`);
}
        """,
        env=env,
    )


def verify_food_pickup(env: dict[str, str]) -> None:
    run_browser_code(
        """
const afterEat = await page.evaluate(() => {
  window.__THREEJS_SNAKE_TEST__.placeFoodAhead();
  return window.__THREEJS_SNAKE_TEST__.step(1);
});
if (afterEat.score !== 1 || afterEat.best !== 1 || !afterEat.running || afterEat.gameOver) {
  throw new Error(`Expected a successful food pickup, got ${JSON.stringify(afterEat)}`);
}
        """,
        env=env,
    )


def verify_reset_best(env: dict[str, str]) -> None:
    run_browser_code(
        """
const afterResetBest = await page.evaluate(() => window.__THREEJS_SNAKE_TEST__.resetBestScore());
if (afterResetBest.best !== 0 || afterResetBest.resetBestLabel !== "Reset Best") {
  throw new Error(`Expected best score reset, got ${JSON.stringify(afterResetBest)}`);
}
        """,
        env=env,
    )


def verify_crash(env: dict[str, str]) -> None:
    run_browser_code(
        """
const afterCrash = await page.evaluate(() => window.__THREEJS_SNAKE_TEST__.step(9));
if (!afterCrash.gameOver || afterCrash.running || afterCrash.title !== "Game Over") {
  throw new Error(`Expected a wall collision game over, got ${JSON.stringify(afterCrash)}`);
}
        """,
        env=env,
    )


def verify_restart(env: dict[str, str]) -> None:
    run_browser_code(
        """
await page.locator("#restart").click();
const afterRestart = await page.evaluate(() => window.__THREEJS_SNAKE_TEST__.getSnapshot());
if (!afterRestart.running || afterRestart.gameOver || afterRestart.score !== 0 || !afterRestart.overlayHidden) {
  throw new Error(`Expected restart to reset the game, got ${JSON.stringify(afterRestart)}`);
}
        """,
        env=env,
    )


def smoke_steps(url: str, headed: bool, env: dict[str, str]) -> None:
    open_args = [url]
    if headed:
        open_args.append("--headed")

    run_pw("open", *open_args, env=env)
    verify_initial_state(env)
    verify_pause_resume(env)
    verify_food_pickup(env)
    verify_reset_best(env)
    verify_crash(env)
    verify_restart(env)


def main() -> int:
    args = parse_args()
    ensure_npx()

    host = args.host
    server = None
    thread = None
    if args.url:
        bound_port = args.port
        url = args.url
    else:
        port = args.port or find_free_port(host)
        server, thread, bound_port = start_static_server(host, port)
        url = f"http://{host}:{bound_port}{APP_URL_PATH}"
    session_name = f"snake-{os.getpid()}-{int(time.time())}"
    env = os.environ.copy()
    env["PLAYWRIGHT_CLI_SESSION"] = session_name

    if server is None:
        print(f"[smoke] using external app URL {url}")
    else:
        print(f"[smoke] serving {REPO_ROOT} on {host}:{bound_port}")
    print(f"[smoke] opening {url}")

    try:
        if server is None:
            wait_for_url(url)
        else:
            wait_for_server(host, bound_port)
        smoke_steps(url, args.headed, env)
        print("[smoke] PASS threejs-snake: load -> pause -> resume -> reset best -> game over -> restart")
        return 0
    finally:
        try:
            run_pw("close", env=env)
        except Exception:
            pass
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=1.0)
        shutil.rmtree(REPO_ROOT / ".playwright-cli", ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[smoke] FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
