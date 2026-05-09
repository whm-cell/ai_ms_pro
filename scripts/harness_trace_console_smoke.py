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
APP_URL_PATH = "/apps/harness-trace-console/?smoke=1"
PLAYWRIGHT_BROWSER_VERSION = os.environ.get("PLAYWRIGHT_VERSION", "1.59.1")
PLAYWRIGHT_CLI_VERSION = os.environ.get("PLAYWRIGHT_CLI_VERSION", "0.1.13")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a lightweight browser smoke test against apps/harness-trace-console.",
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
    return parser.parse_args()


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
    url = f"http://{host}:{port}/apps/harness-trace-console/index.html"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"Static server did not become ready in time: {url}")


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


def smoke_steps(url: str, headed: bool, env: dict[str, str]) -> None:
    open_args = [url]
    if headed:
      open_args.append("--headed")

    run_pw("open", *open_args, env=env)

    run_pw(
        "run-code",
        """
await page.waitForLoadState("domcontentloaded");
await page.waitForFunction(() => window.__HARNESS_TRACE_CONSOLE_TEST__?.getSnapshot().loadState === "ready");
const snapshot = await page.evaluate(() => window.__HARNESS_TRACE_CONSOLE_TEST__.getSnapshot());
if (snapshot.totalRows !== 6 || snapshot.summary.workstreamCount !== 2) {
  throw new Error(`Unexpected initial snapshot: ${JSON.stringify(snapshot)}`);
}
if (!snapshot.workstreams.includes("WS-01") || !snapshot.workstreams.includes("WS-02")) {
  throw new Error(`Expected WS-01 and WS-02 to be present: ${JSON.stringify(snapshot)}`);
}
        """.strip(),
        env=env,
    )

    run_pw(
        "run-code",
        """
const afterWorkstream = await page.evaluate(() => window.__HARNESS_TRACE_CONSOLE_TEST__.setWorkstreamFilter("WS-02"));
if (afterWorkstream.rowCount !== 3 || afterWorkstream.visibleRequirements.join(",") !== "REQ-004,REQ-005,REQ-006") {
  throw new Error(`Unexpected WS-02 filter snapshot: ${JSON.stringify(afterWorkstream)}`);
}
        """.strip(),
        env=env,
    )

    run_pw(
        "run-code",
        """
const afterSearch = await page.evaluate(() => window.__HARNESS_TRACE_CONSOLE_TEST__.setSearch("REQ-006"));
if (afterSearch.rowCount !== 1 || afterSearch.visibleRequirements[0] !== "REQ-006") {
  throw new Error(`Unexpected REQ-006 search snapshot: ${JSON.stringify(afterSearch)}`);
}
        """.strip(),
        env=env,
    )

    run_pw(
        "run-code",
        """
const afterSelect = await page.evaluate(() => window.__HARNESS_TRACE_CONSOLE_TEST__.selectRequirement("REQ-006"));
if (afterSelect.selectedRequirement !== "REQ-006") {
  throw new Error(`Expected REQ-006 to be selected, got ${JSON.stringify(afterSelect)}`);
}
        """.strip(),
        env=env,
    )

    run_pw(
        "run-code",
        """
const afterClear = await page.evaluate(() => window.__HARNESS_TRACE_CONSOLE_TEST__.clearFilters());
const afterStatus = await page.evaluate(() => window.__HARNESS_TRACE_CONSOLE_TEST__.setStatusFilter("已完成"));
if (afterClear.rowCount !== 6 || afterStatus.rowCount !== 6) {
  throw new Error(`Unexpected clear/status snapshot: ${JSON.stringify({ afterClear, afterStatus })}`);
}
        """.strip(),
        env=env,
    )


def main() -> int:
    args = parse_args()
    ensure_npx()

    host = args.host
    port = args.port or find_free_port(host)
    server, thread, bound_port = start_static_server(host, port)
    session_name = f"htc-{os.getpid()}-{int(time.time())}"
    env = os.environ.copy()
    env["PLAYWRIGHT_CLI_SESSION"] = session_name
    url = f"http://{host}:{bound_port}{APP_URL_PATH}"

    print(f"[smoke] serving {REPO_ROOT} on {host}:{bound_port}")
    print(f"[smoke] opening {url}")

    try:
        wait_for_server(host, bound_port)
        smoke_steps(url, args.headed, env)
        print("[smoke] PASS harness-trace-console: load -> WS-02 filter -> REQ-006 search -> completed status")
        return 0
    finally:
        try:
            run_pw("close", env=env)
        except Exception:
            pass
        server.shutdown()
        server.server_close()
        thread.join(timeout=1.0)
        shutil.rmtree(REPO_ROOT / ".playwright-cli", ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[smoke] FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
