#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
import time

from harness_trace_console_smoke import (
    REPO_ROOT,
    ensure_npx,
    find_free_port,
    parse_args,
    run_pw,
    start_static_server,
    wait_for_server,
)


APP_URL_PATH = "/apps/harness-trace-console/"
BLACKBOX_ASSERTION_SCRIPT = """
await page.waitForLoadState("domcontentloaded");
await page.locator("#row-count").waitFor();
await page.waitForFunction(() => document.querySelectorAll(".matrix-card").length >= 1);

const selectors = ["#search-input", "#workstream-filter", "#status-filter", "#detail-title"];
for (const selector of selectors) {
  await page.locator(selector).waitFor();
}

const initialCards = page.locator(".matrix-card");
const initialCount = await initialCards.count();
if (initialCount < 2) {
  throw new Error(`Expected at least two visible rows on load, got ${initialCount}`);
}

const initialDetailTitle = (await page.locator("#detail-title").textContent() || "").trim();
if (!initialDetailTitle || initialDetailTitle === "No row selected") {
  throw new Error(`Expected an initial detail selection, got ${JSON.stringify(initialDetailTitle)}`);
}

const workstreamOptions = await page.locator("#workstream-filter option").allTextContents();
if (!workstreamOptions.includes("WS-02")) {
  throw new Error(`Expected WS-02 option, got ${JSON.stringify(workstreamOptions)}`);
}

await page.selectOption("#workstream-filter", "WS-02");
const filteredCards = page.locator(".matrix-card");
const filteredCount = await filteredCards.count();
if (filteredCount < 1 || filteredCount >= initialCount) {
  throw new Error(
    `Expected WS-02 filter to reduce visible rows while keeping at least one result: ${JSON.stringify({ initialCount, filteredCount })}`,
  );
}

const filteredTexts = await filteredCards.allTextContents();
if (!filteredTexts.every((text) => text.includes("WS-02"))) {
  throw new Error(`Expected filtered rows to stay inside WS-02: ${JSON.stringify(filteredTexts)}`);
}

await page.fill("#search-input", "REQ-006");
const searchCards = page.locator(".matrix-card");
const searchCount = await searchCards.count();
if (searchCount !== 1) {
  throw new Error(`Expected a single REQ-006 search result, got ${searchCount}`);
}

const onlyTitle = (await searchCards.locator(".card-title").first().textContent() || "").trim();
if (onlyTitle !== "REQ-006") {
  throw new Error(`Expected REQ-006 card title, got ${JSON.stringify(onlyTitle)}`);
}

await searchCards.first().click();
const detailTitle = (await page.locator("#detail-title").textContent() || "").trim();
if (detailTitle !== "REQ-006") {
  throw new Error(`Expected REQ-006 detail title, got ${JSON.stringify(detailTitle)}`);
}

const detailText = await page.locator("#detail-body").innerText();
if (!detailText.includes("Workstream") || !detailText.includes("WS-02")) {
  throw new Error(`Expected WS-02 detail content, got ${JSON.stringify(detailText)}`);
}
if (!detailText.includes("Canonical Status") || !detailText.includes("已完成")) {
  throw new Error(`Expected completed canonical status, got ${JSON.stringify(detailText)}`);
}

await page.fill("#search-input", "");
await page.selectOption("#workstream-filter", "all");
const resetCount = await page.locator(".matrix-card").count();
if (resetCount <= filteredCount) {
  throw new Error(
    `Expected clearing filters to restore more rows: ${JSON.stringify({ filteredCount, resetCount })}`,
  );
}
""".strip()


def smoke_steps(url: str, headed: bool, env: dict[str, str]) -> None:
    open_args = [url]
    if headed:
        open_args.append("--headed")

    run_pw("open", *open_args, env=env)
    run_pw("run-code", BLACKBOX_ASSERTION_SCRIPT, env=env)


def main() -> int:
    args = parse_args()
    ensure_npx()

    host = args.host
    port = args.port or find_free_port(host)
    server, thread, bound_port = start_static_server(host, port)
    session_name = f"htc-blackbox-{os.getpid()}-{int(time.time())}"
    env = os.environ.copy()
    env["PLAYWRIGHT_CLI_SESSION"] = session_name
    url = f"http://{host}:{bound_port}{APP_URL_PATH}"

    print(f"[smoke] serving {REPO_ROOT} on {host}:{bound_port}")
    print(f"[smoke] opening {url}")

    try:
        wait_for_server(host, bound_port)
        smoke_steps(url, args.headed, env)
        print("[smoke] PASS harness-trace-console blackbox: load -> WS-02 filter -> REQ-006 search -> detail")
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
