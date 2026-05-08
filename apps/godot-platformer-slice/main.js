const SMOKE_MODE = new URLSearchParams(window.location.search).has("smoke");
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const comboEl = document.getElementById("combo");
const enemiesEl = document.getElementById("enemies");
const exitEl = document.getElementById("exit");
const rankEl = document.getElementById("rank");
const resetButton = document.getElementById("reset");
const completionBanner = document.getElementById("completion-banner");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;
const GROUND_Y = 440;
const GRAVITY = 0.85;
const MOVE_SPEED = 4.2;
const JUMP_SPEED = -15;
const FRICTION = 0.78;

const keys = new Set();

const initialEnemies = [
  { id: "guard-left", x: 380, y: GROUND_Y - 28, state: "active", freeze: 0 },
  { id: "guard-right", x: 610, y: GROUND_Y - 28, state: "active", freeze: 0 },
];

const state = {
  running: true,
  complete: false,
  score: 0,
  combo: 0,
  rank: "Pending",
  exitUnlocked: false,
  player: { x: 140, y: GROUND_Y - 34, vx: 0, vy: 0, grounded: true, facing: 1 },
  enemies: [],
  effects: [],
};

function cloneEnemies() {
  return initialEnemies.map((enemy) => ({ ...enemy }));
}

function resetGame() {
  state.running = true;
  state.complete = false;
  state.score = 0;
  state.combo = 0;
  state.rank = "Pending";
  state.exitUnlocked = false;
  state.player = { x: 140, y: GROUND_Y - 34, vx: 0, vy: 0, grounded: true, facing: 1 };
  state.enemies = cloneEnemies();
  state.effects = [];
  completionBanner.classList.add("hidden");
  syncHud();
  draw();
  return getSnapshot();
}

function activeEnemies() {
  return state.enemies.filter((enemy) => enemy.state !== "cleared");
}

function nearestEnemy() {
  const candidates = activeEnemies();
  candidates.sort((a, b) => Math.abs(a.x - state.player.x) - Math.abs(b.x - state.player.x));
  return candidates[0] || null;
}

function freezeNearestEnemy() {
  const enemy = nearestEnemy();
  if (!enemy || enemy.state === "cleared") {
    return getSnapshot();
  }

  enemy.state = "frozen";
  enemy.freeze = 100;
  state.effects.push({ x: enemy.x, y: enemy.y - 30, text: "Frozen", ttl: 45 });
  syncHud();
  draw();
  return getSnapshot();
}

function throwFrozenEnemy() {
  const enemy = state.enemies.find((item) => item.state === "frozen");
  if (!enemy) {
    return getSnapshot();
  }

  enemy.state = "cleared";
  enemy.freeze = 0;
  state.combo += 1;
  const bonus = 100 * state.combo;
  state.score += bonus;
  state.effects.push({ x: enemy.x, y: enemy.y - 34, text: `+${bonus}`, ttl: 50 });
  if (activeEnemies().length === 0) {
    state.exitUnlocked = true;
    state.effects.push({ x: 820, y: GROUND_Y - 95, text: "Exit open", ttl: 80 });
  }
  syncHud();
  draw();
  return getSnapshot();
}

function enterExit() {
  if (!state.exitUnlocked) {
    return getSnapshot();
  }

  state.complete = true;
  state.running = false;
  state.score += 250;
  state.rank = calculateRank();
  completionBanner.classList.remove("hidden");
  syncHud();
  draw();
  return getSnapshot();
}

function syncHud() {
  scoreEl.textContent = String(state.score);
  comboEl.textContent = String(state.combo);
  enemiesEl.textContent = String(activeEnemies().length);
  exitEl.textContent = state.exitUnlocked ? "Open" : "Locked";
  rankEl.textContent = state.rank;
}

function calculateRank() {
  if (state.score >= 550 && state.combo >= 2) {
    return "A";
  }
  if (state.score >= 450) {
    return "B";
  }
  return "C";
}

function handleInput() {
  if (!state.running) {
    return;
  }

  const player = state.player;
  const left = keys.has("ArrowLeft") || keys.has("KeyA");
  const right = keys.has("ArrowRight") || keys.has("KeyD");

  if (left) {
    player.vx = -MOVE_SPEED;
    player.facing = -1;
  } else if (right) {
    player.vx = MOVE_SPEED;
    player.facing = 1;
  } else {
    player.vx *= FRICTION;
  }

  if ((keys.has("ArrowUp") || keys.has("KeyW") || keys.has("Space")) && player.grounded) {
    player.vy = JUMP_SPEED;
    player.grounded = false;
  }
}

function updatePlayer() {
  const player = state.player;
  player.vy += GRAVITY;
  player.x += player.vx;
  player.y += player.vy;
  player.x = Math.max(42, Math.min(900, player.x));

  if (player.y >= GROUND_Y - 34) {
    player.y = GROUND_Y - 34;
    player.vy = 0;
    player.grounded = true;
  }

  if (state.exitUnlocked && player.x > 790 && player.y >= GROUND_Y - 50) {
    enterExit();
  }
}

function updateEnemies() {
  for (const enemy of state.enemies) {
    if (enemy.state !== "active") {
      continue;
    }
    const drift = enemy.id === "guard-left" ? -0.55 : 0.55;
    enemy.x += drift;
    if (enemy.x < 330 || enemy.x > 660) {
      enemy.x -= drift * 2;
    }
  }
}

function updateEffects() {
  state.effects = state.effects
    .map((effect) => ({ ...effect, y: effect.y - 0.3, ttl: effect.ttl - 1 }))
    .filter((effect) => effect.ttl > 0);
}

function tick() {
  handleInput();
  if (state.running) {
    updatePlayer();
    updateEnemies();
    updateEffects();
  }
  draw();
  requestAnimationFrame(tick);
}

function drawPlatform(x, y, width, height, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, width, height);
  ctx.fillStyle = "rgba(255,255,255,0.12)";
  ctx.fillRect(x, y, width, 4);
}

function drawPlayer() {
  const player = state.player;
  ctx.fillStyle = "#e8fff7";
  ctx.fillRect(player.x - 18, player.y - 30, 36, 34);
  ctx.fillStyle = "#53f3c3";
  ctx.fillRect(player.x + player.facing * 7, player.y - 38, 18, 12);
  ctx.fillStyle = "#07100f";
  ctx.fillRect(player.x + player.facing * 16, player.y - 34, 4, 4);
}

function drawEnemy(enemy) {
  if (enemy.state === "cleared") {
    return;
  }

  ctx.fillStyle = enemy.state === "frozen" ? "#a7e6ff" : "#f7c86b";
  ctx.fillRect(enemy.x - 22, enemy.y - 26, 44, 32);
  ctx.fillStyle = enemy.state === "frozen" ? "#4ea3c1" : "#9d6831";
  ctx.fillRect(enemy.x - 14, enemy.y - 36, 28, 12);
  ctx.fillStyle = "#07100f";
  ctx.fillRect(enemy.x - 9, enemy.y - 20, 5, 5);
  ctx.fillRect(enemy.x + 5, enemy.y - 20, 5, 5);
}

function drawExit() {
  ctx.fillStyle = state.exitUnlocked ? "#53f3c3" : "#334a46";
  ctx.fillRect(805, GROUND_Y - 92, 56, 92);
  ctx.fillStyle = state.exitUnlocked ? "#07100f" : "#9ec5ba";
  ctx.fillRect(823, GROUND_Y - 58, 20, 58);
}

function drawEffects() {
  ctx.font = "700 20px Inter, sans-serif";
  ctx.textAlign = "center";
  for (const effect of state.effects) {
    ctx.fillStyle = effect.text.startsWith("+") ? "#53f3c3" : "#e8fff7";
    ctx.fillText(effect.text, effect.x, effect.y);
  }
}

function draw() {
  ctx.clearRect(0, 0, WIDTH, HEIGHT);
  ctx.fillStyle = "#0c1d1b";
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  ctx.fillStyle = "#14312d";
  ctx.fillRect(0, 0, WIDTH, 130);
  drawPlatform(0, GROUND_Y, WIDTH, 100, "#1f3f38");
  drawPlatform(180, 320, 210, 22, "#274e46");
  drawPlatform(555, 300, 180, 22, "#274e46");
  drawExit();
  for (const enemy of state.enemies) {
    drawEnemy(enemy);
  }
  drawPlayer();
  drawEffects();
}

function getSnapshot() {
  return {
    running: state.running,
    complete: state.complete,
    score: state.score,
    combo: state.combo,
    rank: state.rank,
    exitUnlocked: state.exitUnlocked,
    remainingEnemies: activeEnemies().length,
    frozenEnemies: state.enemies.filter((enemy) => enemy.state === "frozen").length,
    clearedEnemies: state.enemies.filter((enemy) => enemy.state === "cleared").length,
    requirementIds: ["REQ-007", "REQ-008", "REQ-009"],
    workstreamIds: ["WS-03"],
    title: completionBanner.classList.contains("hidden") ? "Platformer First Slice" : "Slice Complete",
  };
}

document.addEventListener("keydown", (event) => {
  keys.add(event.code);
  if (event.code === "KeyJ") {
    freezeNearestEnemy();
  }
  if (event.code === "KeyK") {
    throwFrozenEnemy();
  }
  if (event.code === "KeyR") {
    resetGame();
  }
});

document.addEventListener("keyup", (event) => {
  keys.delete(event.code);
});

resetButton.addEventListener("click", resetGame);

window.__GODOT_PLATFORMER_SLICE_TEST__ = {
  reset: resetGame,
  getSnapshot,
  freezeNearestEnemy,
  throwFrozenEnemy,
  enterExit,
};

resetGame();
if (!SMOKE_MODE) {
  requestAnimationFrame(tick);
} else {
  draw();
}
