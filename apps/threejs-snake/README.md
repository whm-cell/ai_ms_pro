# Three.js Snake

Minimal zero-build static snake game built with three.js and browser ES modules.

## Run

Serve this folder with any static server, for example:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/apps/threejs-snake/
```

## Controls

- Arrow keys or `WASD` to move
- `Enter` or the restart button to restart after game over

## Smoke Check

Run the repo-level browser smoke flow:

```bash
python3 scripts/threejs_snake_smoke.py
```

The smoke script:

- starts a temporary static server
- opens `apps/threejs-snake/?smoke=1` with `playwright-cli`
- uses a namespaced `window.__THREEJS_SNAKE_TEST__` helper to verify deterministic score, game-over, and restart behavior
- removes temporary `.playwright-cli/` artifacts before exit
