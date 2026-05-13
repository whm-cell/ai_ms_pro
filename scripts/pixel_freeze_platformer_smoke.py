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


APP_URL_PATH = "/apps/pixel-freeze-platformer/?smoke=1"
APP_READY_PATH = "/apps/pixel-freeze-platformer/index.html"


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
    verify_initial_state(env)
    verify_playable_controls(env)
    verify_level_flow(env)
    verify_campaign_flow(env)
    verify_locale_and_reset(env)


def verify_initial_state(env: dict[str, str]) -> None:
    run_pw(
        "run-code",
        """
await page.waitForLoadState("domcontentloaded");
await page.waitForFunction(() => Boolean(window.__PIXEL_FREEZE_PLATFORMER_TEST__));
const api = window.__PIXEL_FREEZE_PLATFORMER_TEST__;
const validation = await page.evaluate(() => window.__PIXEL_FREEZE_PLATFORMER_TEST__.validateContent());
if (
  !validation.ok ||
  validation.levelCount < 3 ||
  validation.localeCount < 2 ||
  validation.enemyTypes.length < 3 ||
  validation.pickupTypes.length < 3 ||
  validation.assetBoundary !== "original-placeholder-canvas"
) {
  throw new Error(`Invalid content schema: ${JSON.stringify(validation)}`);
}
for (const id of ["REQ-010", "REQ-011", "REQ-012", "REQ-013"]) {
  if (!validation.requirementIds.includes(id)) {
    throw new Error(`Missing requirement id ${id}: ${JSON.stringify(validation)}`);
  }
}
if (!validation.workstreamIds.includes("WS-04")) {
  throw new Error(`Missing WS-04 metadata: ${JSON.stringify(validation)}`);
}
const initial = await page.evaluate(() => api.resetProgress());
if (initial.levelIndex !== 0 || initial.remainingEnemies < 3 || initial.score !== 0 || initial.mode !== "playing") {
  throw new Error(`Unexpected initial state: ${JSON.stringify(initial)}`);
}
        """.strip(),
        env=env,
    )


def verify_playable_controls(env: dict[str, str]) -> None:
    run_pw(
        "run-code",
        """
const api = window.__PIXEL_FREEZE_PLATFORMER_TEST__;
const start = await page.evaluate(() => api.resetAll({ levelIndex: 0 }));
await page.evaluate(() => api.simulateInput([], 0.45));
const moved = await page.evaluate(() => api.simulateInput(["ArrowRight"], 0.28));
if (moved.playerX <= start.playerX) {
  throw new Error(`Expected right movement: ${JSON.stringify({ start, moved })}`);
}
const jumped = await page.evaluate(() => api.simulateInput(["Space"], 0.08));
if (jumped.playerVy >= 0 || jumped.playerY >= moved.playerY) {
  throw new Error(`Expected jump impulse: ${JSON.stringify({ moved, jumped })}`);
}
const fired = await page.evaluate(() => api.simulateAction("KeyJ"));
if (fired.projectileCount < 1) {
  throw new Error(`Expected attack projectile: ${JSON.stringify(fired)}`);
}
        """.strip(),
        env=env,
    )


def verify_level_flow(env: dict[str, str]) -> None:
    run_pw(
        "run-code",
        """
const api = window.__PIXEL_FREEZE_PLATFORMER_TEST__;
const cleared = await page.evaluate(() => api.clearCurrentLevelWithCombo());
if (!cleared.exitUnlocked || cleared.remainingEnemies !== 0 || cleared.combo < 3 || cleared.score <= 0) {
  throw new Error(`Expected cleared level: ${JSON.stringify(cleared)}`);
}
const complete = await page.evaluate(() => api.enterExit());
if (complete.mode !== "levelComplete" || !["S", "A", "B", "C"].includes(complete.rank) || complete.unlockedLevel < 1) {
  throw new Error(`Expected level complete: ${JSON.stringify(complete)}`);
}
const next = await page.evaluate(() => api.nextLevel());
if (next.levelIndex !== 1 || next.mode !== "playing" || next.remainingEnemies < 4) {
  throw new Error(`Expected next level: ${JSON.stringify(next)}`);
}
        """.strip(),
        env=env,
    )


def verify_campaign_flow(env: dict[str, str]) -> None:
    run_pw(
        "run-code",
        """
const complete = await page.evaluate(() => window.__PIXEL_FREEZE_PLATFORMER_TEST__.completeCampaignFast());
if (
  complete.mode !== "campaignComplete" ||
  complete.levelIndex !== 2 ||
  complete.unlockedLevel !== 2 ||
  complete.bestScore <= 0 ||
  !complete.exitUnlocked
) {
  throw new Error(`Expected completed campaign: ${JSON.stringify(complete)}`);
}
        """.strip(),
        env=env,
    )


def verify_locale_and_reset(env: dict[str, str]) -> None:
    run_pw(
        "run-code",
        """
const api = window.__PIXEL_FREEZE_PLATFORMER_TEST__;
const zh = await page.evaluate(() => api.setLocale("zh"));
const title = await page.locator("#label-lives").textContent();
if (zh.locale !== "zh" || title !== "生命") {
  throw new Error(`Expected Chinese locale: ${JSON.stringify({ zh, title })}`);
}
const reset = await page.evaluate(() => api.resetProgress());
if (
  reset.locale !== "en" ||
  reset.levelIndex !== 0 ||
  reset.unlockedLevel !== 0 ||
  reset.bestScore !== 0 ||
  reset.score !== 0
) {
  throw new Error(`Expected reset progress: ${JSON.stringify(reset)}`);
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
    session_name = f"pfp-{os.getpid()}-{int(time.time())}"
    env = os.environ.copy()
    env["PLAYWRIGHT_CLI_SESSION"] = session_name
    url = f"http://{host}:{bound_port}{APP_URL_PATH}"

    print(f"[smoke] serving {REPO_ROOT} on {host}:{bound_port}")
    print(f"[smoke] opening {url}")

    try:
        wait_for_app(host, bound_port)
        smoke_steps(url, args.headed, env)
        print(
            "[smoke] PASS pixel-freeze-platformer: "
            "load -> validate content -> controls -> clear level -> next level -> campaign complete -> locale/reset"
        )
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
