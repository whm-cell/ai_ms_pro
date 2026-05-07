# Godot Platformer First Slice

Repo-native browser slice for `REQDOC-003`.

This is not a Godot project. It is a small playable spike that keeps the root repository focused on harness research while validating the PRD's first gameplay loop:

```text
move / jump -> freeze enemies -> throw to clear -> unlock exit -> complete
```

## Run

Serve the repository root with any static server:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/apps/godot-platformer-slice/
```

## Controls

- Arrow keys or `A` / `D` to move
- `W`, `ArrowUp`, or `Space` to jump
- `J` to freeze the nearest enemy
- `K` to throw a frozen enemy
- `R` or the reset button to restart

## Smoke Check

Run the repo-level smoke flow:

```bash
python3 scripts/godot_platformer_slice_smoke.py
```

The smoke script opens `apps/godot-platformer-slice/?smoke=1` and verifies:

- initial traceability metadata
- enemy freeze
- frozen enemy throw
- full clear and exit unlock
- level completion
- reset
