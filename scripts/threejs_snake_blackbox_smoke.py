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
await page.locator("#status").waitFor();
await page.locator("#reset-best").waitFor();
await page.locator(".hint").waitFor();

await page.evaluate(() => localStorage.setItem("threejs-snake-best-score", "7"));
await page.reload({ waitUntil: "domcontentloaded" });
await page.locator("#reset-best").waitFor();

const canvasBox = await page.locator("#game").boundingBox();
if (!canvasBox || canvasBox.width < 100 || canvasBox.height < 100) {
  throw new Error(`Expected visible game canvas, got ${JSON.stringify(canvasBox)}`);
}

await page.waitForFunction(() => document.querySelector("#overlay")?.classList.contains("hidden"));
const seededBest = (await page.locator("#best").textContent() || "").trim();
if (seededBest !== "7") {
  throw new Error(`Expected seeded best score 7, got ${JSON.stringify(seededBest)}`);
}
await page.locator("#reset-best").click();
await page.waitForFunction(() => (document.querySelector("#best")?.textContent || "").trim() === "0");

const initialScore = (await page.locator("#score").textContent() || "").trim();
if (initialScore !== "0") {
  throw new Error(`Expected initial score 0, got ${JSON.stringify(initialScore)}`);
}
const initialStatus = (await page.locator("#status").textContent() || "").trim();
if (initialStatus !== "Running") {
  throw new Error(`Expected initial status Running, got ${JSON.stringify(initialStatus)}`);
}

await page.keyboard.press("p");
await page.waitForFunction(() => (document.querySelector("#title")?.textContent || "").trim() === "Paused");
const pausedStatus = (await page.locator("#status").textContent() || "").trim();
const resumeLabel = (await page.locator("#restart").textContent() || "").trim();
if (pausedStatus !== "Paused" || resumeLabel !== "Resume") {
  throw new Error(`Expected pause UI, got ${JSON.stringify({ pausedStatus, resumeLabel })}`);
}

await page.keyboard.press(" ");
await page.waitForFunction(() => document.querySelector("#overlay")?.classList.contains("hidden"));
const resumedStatus = (await page.locator("#status").textContent() || "").trim();
if (resumedStatus !== "Running") {
  throw new Error(`Expected resumed status Running, got ${JSON.stringify(resumedStatus)}`);
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
    server = None
    thread = None
    if args.url:
        bound_port = args.port
        url = args.url
    else:
        port = args.port or find_free_port(host)
        server, thread, bound_port = start_static_server(host, port)
        url = f"http://{host}:{bound_port}{APP_URL_PATH}"
    session_name = f"snake-blackbox-{os.getpid()}-{int(time.time())}"
    env = os.environ.copy()
    env["PLAYWRIGHT_CLI_SESSION"] = session_name

    if server is None:
        print(f"[smoke] using external app URL {url}")
    else:
        print(f"[smoke] serving {REPO_ROOT} on {host}:{bound_port}")
    print(f"[smoke] opening {url}")

    try:
        if server is None:
            from threejs_snake_smoke import wait_for_url

            wait_for_url(url)
        else:
            wait_for_server(host, bound_port)
        smoke_steps(url, args.headed, env)
        print("[smoke] PASS threejs-snake blackbox: load -> reset best -> keyboard turn -> game over -> enter restart")
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
