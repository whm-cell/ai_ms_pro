#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
import time
import urllib.request

from threejs_snake_smoke import (
    REPO_ROOT,
    ensure_npx,
    find_free_port,
    parse_args,
    run_pw,
    start_static_server,
)


APP_URL_PATH = "/apps/godot-platformer-slice/?smoke=1"
APP_READY_PATH = "/apps/godot-platformer-slice/index.html"


def wait_for_app(host: str, port: int, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    url = f"http://{host}:{port}{APP_READY_PATH}"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"Static server did not become ready in time: {url}")


def smoke_steps(url: str, headed: bool, env: dict[str, str]) -> None:
    open_args = [url]
    if headed:
        open_args.append("--headed")

    run_pw("open", *open_args, env=env)

    run_pw(
        "run-code",
        """
await page.waitForLoadState("domcontentloaded");
await page.waitForFunction(() => Boolean(window.__GODOT_PLATFORMER_SLICE_TEST__));
const initial = await page.evaluate(() => window.__GODOT_PLATFORMER_SLICE_TEST__.reset());
if (initial.remainingEnemies !== 2 || initial.exitUnlocked || initial.complete) {
  throw new Error(`Unexpected initial state: ${JSON.stringify(initial)}`);
}
if (!initial.requirementIds.includes("REQ-007") || !initial.workstreamIds.includes("WS-03")) {
  throw new Error(`Missing traceability metadata: ${JSON.stringify(initial)}`);
}
        """.strip(),
        env=env,
    )

    run_pw(
        "run-code",
        """
const frozen = await page.evaluate(() => window.__GODOT_PLATFORMER_SLICE_TEST__.freezeNearestEnemy());
if (frozen.frozenEnemies !== 1 || frozen.remainingEnemies !== 2) {
  throw new Error(`Expected one frozen enemy: ${JSON.stringify(frozen)}`);
}
const firstThrow = await page.evaluate(() => window.__GODOT_PLATFORMER_SLICE_TEST__.throwFrozenEnemy());
if (firstThrow.clearedEnemies !== 1 || firstThrow.remainingEnemies !== 1 || firstThrow.exitUnlocked) {
  throw new Error(`Expected one cleared enemy and locked exit: ${JSON.stringify(firstThrow)}`);
}
        """.strip(),
        env=env,
    )

    run_pw(
        "run-code",
        """
await page.evaluate(() => window.__GODOT_PLATFORMER_SLICE_TEST__.freezeNearestEnemy());
const secondThrow = await page.evaluate(() => window.__GODOT_PLATFORMER_SLICE_TEST__.throwFrozenEnemy());
if (secondThrow.clearedEnemies !== 2 || secondThrow.remainingEnemies !== 0 || !secondThrow.exitUnlocked) {
  throw new Error(`Expected all enemies cleared and exit unlocked: ${JSON.stringify(secondThrow)}`);
}
const complete = await page.evaluate(() => window.__GODOT_PLATFORMER_SLICE_TEST__.enterExit());
if (!complete.complete || complete.running || complete.title !== "Slice Complete") {
  throw new Error(`Expected completed slice: ${JSON.stringify(complete)}`);
}
        """.strip(),
        env=env,
    )

    run_pw(
        "run-code",
        """
await page.locator("#reset").click();
const afterReset = await page.evaluate(() => window.__GODOT_PLATFORMER_SLICE_TEST__.getSnapshot());
if (!afterReset.running || afterReset.complete || afterReset.score !== 0 || afterReset.remainingEnemies !== 2) {
  throw new Error(`Expected reset state: ${JSON.stringify(afterReset)}`);
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
    session_name = f"gps-{os.getpid()}-{int(time.time())}"
    env = os.environ.copy()
    env["PLAYWRIGHT_CLI_SESSION"] = session_name
    url = f"http://{host}:{bound_port}{APP_URL_PATH}"

    print(f"[smoke] serving {REPO_ROOT} on {host}:{bound_port}")
    print(f"[smoke] opening {url}")

    try:
        wait_for_app(host, bound_port)
        smoke_steps(url, args.headed, env)
        print("[smoke] PASS godot-platformer-slice: load -> freeze -> throw -> unlock exit -> complete -> reset")
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
