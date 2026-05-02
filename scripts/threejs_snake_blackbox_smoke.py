#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
import time

from threejs_snake_smoke import (
    REPO_ROOT,
    ensure_npx,
    find_free_port,
    parse_args,
    run_pw,
    start_static_server,
    wait_for_server,
)


APP_URL_PATH = "/apps/threejs-snake/"


def smoke_steps(url: str, headed: bool, env: dict[str, str]) -> None:
    open_args = [url]
    if headed:
        open_args.append("--headed")

    run_pw("open", *open_args, env=env)
    run_pw(
        "run-code",
        """
await page.waitForLoadState("domcontentloaded");
await page.locator("#game").waitFor();
await page.locator("#score").waitFor();
await page.locator("#best").waitFor();
await page.locator(".hint").waitFor();

const canvasBox = await page.locator("#game").boundingBox();
if (!canvasBox || canvasBox.width < 100 || canvasBox.height < 100) {
  throw new Error(`Expected visible game canvas, got ${JSON.stringify(canvasBox)}`);
}

await page.waitForFunction(() => document.querySelector("#overlay")?.classList.contains("hidden"));
const initialScore = (await page.locator("#score").textContent() || "").trim();
if (initialScore !== "0") {
  throw new Error(`Expected initial score 0, got ${JSON.stringify(initialScore)}`);
}

await page.keyboard.press("ArrowDown");
await page.waitForFunction(
  () => (document.querySelector("#title")?.textContent || "").trim() === "Game Over",
  null,
  { timeout: 6000 },
);

const gameOverMessage = await page.locator("#message").innerText();
if (!gameOverMessage.includes("Score")) {
  throw new Error(`Expected game over score message, got ${JSON.stringify(gameOverMessage)}`);
}

await page.keyboard.press("Enter");
await page.waitForFunction(() => document.querySelector("#overlay")?.classList.contains("hidden"));
const restartedTitle = (await page.locator("#title").textContent() || "").trim();
const restartedScore = (await page.locator("#score").textContent() || "").trim();
if (restartedTitle !== "Snake" || restartedScore !== "0") {
  throw new Error(`Expected Enter restart to reset title and score, got ${JSON.stringify({ restartedTitle, restartedScore })}`);
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
    session_name = f"snake-blackbox-{os.getpid()}-{int(time.time())}"
    env = os.environ.copy()
    env["PLAYWRIGHT_CLI_SESSION"] = session_name
    url = f"http://{host}:{bound_port}{APP_URL_PATH}"

    print(f"[smoke] serving {REPO_ROOT} on {host}:{bound_port}")
    print(f"[smoke] opening {url}")

    try:
        wait_for_server(host, bound_port)
        smoke_steps(url, args.headed, env)
        print("[smoke] PASS threejs-snake blackbox: load -> keyboard turn -> game over -> enter restart")
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
