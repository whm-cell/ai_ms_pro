# Three.js Snake

Zero-build static snake game built with Three.js and browser ES modules.

This app is the active capability-test sample for WS-01. It validates a small but real loop: requirement metadata, an executable game surface, deterministic smoke hooks, and black-box browser behavior.

## Run

Serve the repository root with any static server, for example:

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

## Smoke Checks

Run the repo-level browser smoke flows:

```bash
python3 scripts/threejs_snake_smoke.py
python3 scripts/threejs_snake_blackbox_smoke.py
```

The deterministic smoke path opens `apps/threejs-snake/?smoke=1` and uses `window.__THREEJS_SNAKE_TEST__` to verify load, food pickup, wall collision, metadata, and restart behavior.

If the current runner cannot bind a local port, start the static server outside that runner and pass the URL:

```bash
python3 scripts/threejs_snake_smoke.py --no-server --url http://127.0.0.1:8000/apps/threejs-snake/?smoke=1
python3 scripts/threejs_snake_blackbox_smoke.py --no-server --url http://127.0.0.1:8000/apps/threejs-snake/
```
