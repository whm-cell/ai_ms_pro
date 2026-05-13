import { LEVELS, PICKUP_DEFS, REQUIREMENT_IDS, STRINGS, WORKSTREAM_IDS } from "./content.js";

const SMOKE_MODE = new URLSearchParams(window.location.search).has("smoke");
const STORAGE_KEY = "pixel-freeze-platformer:v1";
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const dom = {
  title: document.getElementById("title"),
  subtitle: document.getElementById("subtitle"),
  overlay: document.getElementById("overlay"),
  overlayTitle: document.getElementById("overlay-title"),
  overlayDetail: document.getElementById("overlay-detail"),
  start: document.getElementById("start"),
  pause: document.getElementById("pause"),
  retry: document.getElementById("retry"),
  next: document.getElementById("next"),
  resetProgress: document.getElementById("reset-progress"),
  language: document.getElementById("language"),
  level: document.getElementById("level"),
  lives: document.getElementById("lives"),
  score: document.getElementById("score"),
  combo: document.getElementById("combo"),
  time: document.getElementById("time"),
  enemies: document.getElementById("enemies"),
  exit: document.getElementById("exit"),
  rank: document.getElementById("rank"),
  best: document.getElementById("best"),
};

const labelIds = ["level", "lives", "score", "combo", "time", "enemies", "exit", "rank", "language", "best"];
const keys = new Set();

const state = {
  mode: "playing",
  paused: false,
  levelIndex: 0,
  lives: 3,
  score: 0,
  levelStartScore: 0,
  combo: 0,
  bestCombo: 0,
  rank: "Pending",
  timeLeft: 0,
  exitUnlocked: false,
  damageTaken: false,
  player: null,
  enemies: [],
  pickups: [],
  projectiles: [],
  balls: [],
  effects: [],
  buffs: {},
  elapsed: 0,
  lastFrame: 0,
};

let save = loadSave();

function defaultSave() {
  return { locale: "en", unlockedLevel: 0, bestScore: 0 };
}

function loadSave() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? { ...defaultSave(), ...JSON.parse(raw) } : defaultSave();
  } catch {
    return defaultSave();
  }
}

function writeSave() {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(save));
  } catch {
    // localStorage may be unavailable in restricted browser contexts.
  }
}

function t(key) {
  const locale = save.locale in STRINGS ? save.locale : "en";
  return STRINGS[locale][key] || STRINGS.en[key] || key;
}

function currentLevel() {
  return LEVELS[state.levelIndex];
}

function cloneEnemy(enemy) {
  return {
    ...enemy,
    baseY: enemy.y,
    dir: enemy.type === "shield" ? -1 : 1,
    state: "active",
    freezeProgress: 0,
    splitDone: false,
    phase: Math.random() * Math.PI,
  };
}

function clonePickup(pickup) {
  return { ...pickup, collected: false };
}

function startCampaign() {
  state.score = 0;
  state.lives = 3;
  startLevel(0, { keepRunScore: true });
}

function startLevel(index, options = {}) {
  const nextIndex = Math.max(0, Math.min(LEVELS.length - 1, index));
  const level = LEVELS[nextIndex];
  state.levelIndex = nextIndex;
  state.mode = "playing";
  state.paused = false;
  state.levelStartScore = options.keepRunScore ? state.score : 0;
  if (!options.keepRunScore) {
    state.score = 0;
    state.lives = 3;
  }
  state.combo = 0;
  state.bestCombo = 0;
  state.rank = t("ready");
  state.timeLeft = level.timeLimit;
  state.exitUnlocked = false;
  state.damageTaken = false;
  state.elapsed = 0;
  state.player = {
    x: level.playerStart.x,
    y: level.playerStart.y,
    vx: 0,
    vy: 0,
    w: 30,
    h: 40,
    facing: 1,
    grounded: false,
    invuln: 0,
    attackCooldown: 0,
  };
  state.enemies = level.enemies.map(cloneEnemy);
  state.pickups = (level.pickups || []).map(clonePickup);
  state.projectiles = [];
  state.balls = [];
  state.effects = [];
  state.buffs = { rapid: 0, boots: 0, shield: 0, magnet: 0 };
  syncHud();
  draw();
  return getSnapshot();
}

function resetProgress() {
  save = defaultSave();
  writeSave();
  startLevel(0);
  return getSnapshot();
}

function retryLevel() {
  return startLevel(state.levelIndex, { keepRunScore: true });
}

function nextLevel() {
  if (state.mode !== "levelComplete") {
    return getSnapshot();
  }
  return startLevel(state.levelIndex + 1, { keepRunScore: true });
}

function pauseToggle(force) {
  if (!["playing", "paused"].includes(state.mode)) {
    return getSnapshot();
  }
  state.paused = typeof force === "boolean" ? force : !state.paused;
  state.mode = state.paused ? "paused" : "playing";
  syncHud();
  draw();
  return getSnapshot();
}

function activeEnemies() {
  return state.enemies.filter((enemy) => ["active", "affected", "packed"].includes(enemy.state));
}

function playerRect() {
  const player = state.player;
  return { x: player.x - player.w / 2, y: player.y - player.h, w: player.w, h: player.h };
}

function rectsOverlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function enemyRect(enemy) {
  const size = enemy.type === "flyer" ? 30 : 34;
  return { x: enemy.x - size / 2, y: enemy.y - size, w: size, h: size };
}

function platformUnder(rect, previousBottom) {
  const platforms = currentLevel().platforms || [];
  for (const platform of platforms) {
    const wasAbove = previousBottom <= platform.y + 4;
    const isCrossing = rect.y + rect.h >= platform.y && rect.y + rect.h <= platform.y + 28;
    const overlapsX = rect.x + rect.w > platform.x + 4 && rect.x < platform.x + platform.w - 4;
    if (wasAbove && isCrossing && overlapsX) {
      return platform;
    }
  }
  return null;
}

function fireProjectile() {
  if (state.mode !== "playing" || state.player.attackCooldown > 0) {
    return getSnapshot();
  }
  const cooldown = state.buffs.rapid > 0 ? 0.12 : 0.2;
  state.player.attackCooldown = cooldown;
  state.projectiles.push({
    x: state.player.x + state.player.facing * 22,
    y: state.player.y - 25,
    vx: state.player.facing * 390,
    ttl: 0.55,
  });
  addEffect(state.player.x + state.player.facing * 32, state.player.y - 36, "ice");
  return getSnapshot();
}

function freezeEnemyById(id, power = 99) {
  const enemy = state.enemies.find((item) => item.id === id);
  if (!enemy || enemy.state === "cleared") {
    return getSnapshot();
  }
  applyFreeze(enemy, power);
  syncHud();
  draw();
  return getSnapshot();
}

function applyFreeze(enemy, power = 1) {
  if (!["active", "affected", "packed"].includes(enemy.state)) {
    return;
  }
  enemy.freezeProgress = Math.min(enemy.freeze, enemy.freezeProgress + power);
  enemy.state = enemy.freezeProgress >= enemy.freeze ? "packed" : "affected";
  addEffect(enemy.x, enemy.y - 42, enemy.state === "packed" ? "packed" : "freeze");
}

function nearestPackedEnemy() {
  const packed = state.enemies.filter((enemy) => enemy.state === "packed");
  packed.sort((a, b) => Math.abs(a.x - state.player.x) - Math.abs(b.x - state.player.x));
  return packed[0] || null;
}

function kickNearestPacked() {
  const enemy = nearestPackedEnemy();
  if (!enemy) {
    return getSnapshot();
  }
  return throwPackedEnemyById(enemy.id);
}

function throwPackedEnemyById(id) {
  const enemy = state.enemies.find((item) => item.id === id);
  if (!enemy || enemy.state === "cleared") {
    return getSnapshot();
  }
  const direction = state.player.x <= enemy.x ? 1 : -1;
  clearEnemy(enemy, 1, "throw");
  state.balls.push({
    x: enemy.x,
    y: enemy.y - 18,
    vx: direction * 310,
    ttl: 1.5,
    chain: 1,
  });
  checkExitUnlock();
  syncHud();
  draw();
  return getSnapshot();
}

function clearEnemy(enemy, chain = 1, reason = "hit") {
  if (!enemy || enemy.state === "cleared") {
    return;
  }
  enemy.state = "cleared";
  state.combo += 1;
  state.bestCombo = Math.max(state.bestCombo, state.combo);
  const typeBonus = enemy.type === "shield" || enemy.type === "splitter" ? 60 : 0;
  const value = 120 * chain + typeBonus;
  state.score += value;
  addEffect(enemy.x, enemy.y - 46, `+${value}`);
  if (enemy.type === "splitter" && !enemy.splitDone && reason !== "split-child") {
    enemy.splitDone = true;
    spawnSplitlings(enemy);
  }
}

function spawnSplitlings(enemy) {
  const left = {
    id: `${enemy.id}-left`,
    type: "walker",
    x: enemy.x - 38,
    y: enemy.y,
    patrol: [Math.max(40, enemy.x - 115), enemy.x + 16],
    freeze: 1,
  };
  const right = {
    id: `${enemy.id}-right`,
    type: "walker",
    x: enemy.x + 38,
    y: enemy.y,
    patrol: [enemy.x - 16, Math.min(920, enemy.x + 115)],
    freeze: 1,
  };
  state.enemies.push(cloneEnemy(left), cloneEnemy(right));
}

function checkExitUnlock() {
  if (activeEnemies().length === 0) {
    state.exitUnlocked = true;
    addEffect(currentLevel().exit.x + 28, currentLevel().exit.y - 10, t("open"));
  }
}

function enterExit() {
  if (!state.exitUnlocked || state.mode !== "playing") {
    return getSnapshot();
  }
  const level = currentLevel();
  const timeBonus = Math.max(0, Math.floor(state.timeLeft * 8));
  const noHitBonus = state.damageTaken ? 0 : 260;
  const comboBonus = state.bestCombo * 95;
  state.score += timeBonus + noHitBonus + comboBonus;
  const levelScore = state.score - state.levelStartScore;
  state.rank = calculateRank(levelScore, level.rankTargets);
  save.bestScore = Math.max(save.bestScore, state.score);
  save.unlockedLevel = Math.max(save.unlockedLevel, Math.min(LEVELS.length - 1, state.levelIndex + 1));
  writeSave();
  state.mode = state.levelIndex === LEVELS.length - 1 ? "campaignComplete" : "levelComplete";
  syncHud();
  draw();
  return getSnapshot();
}

function calculateRank(score, targets) {
  if (score >= targets.s) return "S";
  if (score >= targets.a) return "A";
  if (score >= targets.b) return "B";
  return "C";
}

function damagePlayer() {
  if (state.player.invuln > 0 || state.mode !== "playing") {
    return;
  }
  if (state.buffs.shield > 0) {
    state.buffs.shield = 0;
    state.player.invuln = 1.0;
    addEffect(state.player.x, state.player.y - 48, "guard");
    return;
  }
  state.damageTaken = true;
  state.lives -= 1;
  state.player.invuln = 1.3;
  addEffect(state.player.x, state.player.y - 48, "-1");
  if (state.lives <= 0) {
    state.mode = "gameOver";
  } else {
    state.player.x = currentLevel().playerStart.x;
    state.player.y = currentLevel().playerStart.y;
    state.player.vx = 0;
    state.player.vy = 0;
  }
  syncHud();
}

function collectPickup(pickup) {
  pickup.collected = true;
  if (pickup.type === "rapid") state.buffs.rapid = 10;
  if (pickup.type === "boots") state.buffs.boots = 10;
  if (pickup.type === "shield") state.buffs.shield = 1;
  if (pickup.type === "time") state.timeLeft += 12;
  if (pickup.type === "magnet") {
    state.buffs.magnet = 12;
    state.score += 160;
  }
  const def = PICKUP_DEFS[pickup.type];
  addEffect(pickup.x, pickup.y - 26, def ? def.label[save.locale] || def.label.en : pickup.type);
}

function addEffect(x, y, text) {
  state.effects.push({ x, y, text, ttl: 0.8 });
}

function update(delta) {
  if (state.mode !== "playing") {
    return;
  }
  state.elapsed += delta;
  state.timeLeft = Math.max(0, state.timeLeft - delta);
  if (state.timeLeft <= 0) {
    state.mode = "gameOver";
    syncHud();
    return;
  }
  updateBuffs(delta);
  updatePlayer(delta);
  updateEnemies(delta);
  updateProjectiles(delta);
  updateBalls(delta);
  updatePickups();
  updateEffects(delta);
  checkExitUnlock();
  syncHud();
}

function updateBuffs(delta) {
  for (const key of Object.keys(state.buffs)) {
    if (state.buffs[key] > 1) {
      state.buffs[key] = Math.max(0, state.buffs[key] - delta);
    }
  }
  state.player.attackCooldown = Math.max(0, state.player.attackCooldown - delta);
  state.player.invuln = Math.max(0, state.player.invuln - delta);
}

function updatePlayer(delta) {
  const player = state.player;
  const left = keys.has("ArrowLeft") || keys.has("KeyA");
  const right = keys.has("ArrowRight") || keys.has("KeyD");
  const speed = state.buffs.rapid > 0 ? 190 : 165;
  const jump = state.buffs.boots > 0 ? -395 : -345;
  if (left) {
    player.vx = -speed;
    player.facing = -1;
  } else if (right) {
    player.vx = speed;
    player.facing = 1;
  } else {
    player.vx *= 0.84;
  }
  player.vy += 980 * delta;
  const previousBottom = player.y;
  player.x = Math.max(24, Math.min(canvas.width - 24, player.x + player.vx * delta));
  player.y += player.vy * delta;
  const rect = playerRect();
  const platform = platformUnder(rect, previousBottom);
  player.grounded = false;
  if (platform) {
    player.y = platform.y;
    player.vy = 0;
    player.grounded = true;
  }
  if ((keys.has("Space") || keys.has("ArrowUp") || keys.has("KeyW")) && player.grounded) {
    player.vy = jump;
    player.grounded = false;
  }
  for (const hazard of currentLevel().hazards || []) {
    if (rectsOverlap(playerRect(), hazard)) {
      damagePlayer();
    }
  }
  if (state.exitUnlocked && rectsOverlap(playerRect(), currentLevel().exit)) {
    enterExit();
  }
}

function updateEnemies(delta) {
  for (const enemy of state.enemies) {
    if (!["active", "affected"].includes(enemy.state)) {
      continue;
    }
    if (enemy.state === "affected") {
      enemy.freezeProgress = Math.max(0, enemy.freezeProgress - delta * 0.15);
      if (enemy.freezeProgress <= 0) enemy.state = "active";
      continue;
    }
    const speed = enemy.type === "charger" ? 75 : enemy.type === "jumper" ? 48 : 40;
    enemy.x += enemy.dir * speed * delta;
    if (enemy.x < enemy.patrol[0] || enemy.x > enemy.patrol[1]) {
      enemy.dir *= -1;
      enemy.x = Math.max(enemy.patrol[0], Math.min(enemy.patrol[1], enemy.x));
    }
    if (enemy.type === "flyer") {
      enemy.y = enemy.baseY + Math.sin(state.elapsed * 2.5 + enemy.phase) * 18;
    }
    if (rectsOverlap(playerRect(), enemyRect(enemy))) {
      damagePlayer();
    }
  }
}

function updateProjectiles(delta) {
  for (const projectile of state.projectiles) {
    projectile.x += projectile.vx * delta;
    projectile.ttl -= delta;
    const projectileRect = { x: projectile.x - 7, y: projectile.y - 5, w: 14, h: 10 };
    for (const enemy of activeEnemies()) {
      if (rectsOverlap(projectileRect, enemyRect(enemy))) {
        applyFreeze(enemy, 1);
        projectile.ttl = 0;
        break;
      }
    }
  }
  state.projectiles = state.projectiles.filter((projectile) => projectile.ttl > 0);
}

function updateBalls(delta) {
  for (const ball of state.balls) {
    ball.x += ball.vx * delta;
    ball.ttl -= delta;
    if (ball.x < 26 || ball.x > canvas.width - 26) {
      ball.vx *= -1;
      ball.x = Math.max(26, Math.min(canvas.width - 26, ball.x));
    }
    const ballRect = { x: ball.x - 18, y: ball.y - 18, w: 36, h: 36 };
    for (const enemy of activeEnemies()) {
      if (rectsOverlap(ballRect, enemyRect(enemy))) {
        ball.chain += 1;
        clearEnemy(enemy, ball.chain, "chain");
      }
    }
  }
  state.balls = state.balls.filter((ball) => ball.ttl > 0);
}

function updatePickups() {
  const rect = playerRect();
  for (const pickup of state.pickups) {
    if (!pickup.collected && rectsOverlap(rect, { x: pickup.x - 13, y: pickup.y - 13, w: 26, h: 26 })) {
      collectPickup(pickup);
    }
  }
}

function updateEffects(delta) {
  state.effects = state.effects
    .map((effect) => ({ ...effect, y: effect.y - 18 * delta, ttl: effect.ttl - delta }))
    .filter((effect) => effect.ttl > 0);
}

function syncHud() {
  const level = currentLevel();
  dom.title.textContent = t("title");
  dom.subtitle.textContent = t("subtitle");
  dom.start.textContent = t("start");
  dom.pause.textContent = state.mode === "paused" ? t("resume") : t("pause");
  dom.retry.textContent = t("retry");
  dom.next.textContent = t("next");
  dom.resetProgress.textContent = t("resetProgress");
  for (const id of labelIds) {
    const label = document.getElementById(`label-${id}`);
    if (label) label.textContent = t(id);
  }
  dom.language.value = save.locale;
  dom.level.textContent = `${state.levelIndex + 1}/${LEVELS.length}`;
  dom.lives.textContent = String(state.lives);
  dom.score.textContent = String(state.score);
  dom.combo.textContent = String(state.combo);
  dom.time.textContent = String(Math.ceil(state.timeLeft));
  dom.enemies.textContent = String(activeEnemies().length);
  dom.exit.textContent = state.exitUnlocked ? t("open") : t("locked");
  dom.rank.textContent = state.rank;
  dom.best.textContent = String(save.bestScore);
  updateOverlay(level);
}

function updateOverlay(level) {
  const modeTitle = {
    paused: t("paused"),
    levelComplete: `${level.name[save.locale] || level.name.en} ${t("complete")}`,
    campaignComplete: t("campaignComplete"),
    gameOver: t("gameOver"),
  }[state.mode];
  if (!modeTitle) {
    dom.overlay.classList.add("hidden");
    return;
  }
  dom.overlayTitle.textContent = modeTitle;
  dom.overlayDetail.textContent = `${t("rank")}: ${state.rank} | ${t("score")}: ${state.score}`;
  dom.overlay.classList.remove("hidden");
}

function draw() {
  const level = currentLevel();
  drawBackground(level);
  for (const platform of level.platforms) drawPlatform(platform, level.theme);
  for (const hazard of level.hazards || []) drawHazard(hazard);
  drawExit(level.exit);
  for (const pickup of state.pickups) if (!pickup.collected) drawPickup(pickup);
  for (const enemy of state.enemies) drawEnemy(enemy);
  for (const projectile of state.projectiles) drawProjectile(projectile);
  for (const ball of state.balls) drawBall(ball);
  drawPlayer();
  drawEffects();
}

function drawBackground(level) {
  const palette = {
    ice: ["#151d2b", "#1e3d5c", "#5ce1e6"],
    wind: ["#171a2a", "#273d62", "#8dd7ff"],
    forge: ["#1b1519", "#4b2635", "#ff9f68"],
  }[level.theme] || ["#141824", "#263044", "#5ce1e6"];
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = palette[0];
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = palette[1];
  ctx.fillRect(0, 0, canvas.width, 136);
  ctx.fillStyle = "rgba(255,255,255,0.08)";
  for (let x = 30; x < canvas.width; x += 84) {
    ctx.fillRect(x, 58 + (x % 3) * 8, 42, 4);
  }
  ctx.fillStyle = palette[2];
  ctx.fillRect(18, 18, 124, 5);
}

function drawPlatform(platform, theme) {
  const fill = theme === "forge" ? "#4e3840" : theme === "wind" ? "#334667" : "#2a5063";
  ctx.fillStyle = fill;
  ctx.fillRect(platform.x, platform.y, platform.w, platform.h);
  ctx.fillStyle = "rgba(255,255,255,0.16)";
  ctx.fillRect(platform.x, platform.y, platform.w, 4);
}

function drawHazard(hazard) {
  ctx.fillStyle = "#ff5da2";
  for (let x = hazard.x; x < hazard.x + hazard.w; x += 18) {
    ctx.beginPath();
    ctx.moveTo(x, hazard.y + hazard.h);
    ctx.lineTo(x + 9, hazard.y);
    ctx.lineTo(x + 18, hazard.y + hazard.h);
    ctx.closePath();
    ctx.fill();
  }
}

function drawExit(exit) {
  ctx.fillStyle = state.exitUnlocked ? "#5ce1e6" : "#3c4652";
  ctx.fillRect(exit.x, exit.y, exit.w, exit.h);
  ctx.fillStyle = state.exitUnlocked ? "#101116" : "#aeb8c5";
  ctx.fillRect(exit.x + 18, exit.y + 30, 18, exit.h - 30);
}

function drawPlayer() {
  const player = state.player;
  const flicker = player.invuln > 0 && Math.floor(state.elapsed * 16) % 2 === 0;
  if (flicker) return;
  ctx.fillStyle = "#f4f7fb";
  ctx.fillRect(player.x - 15, player.y - 36, 30, 36);
  ctx.fillStyle = state.buffs.shield > 0 ? "#b388ff" : "#5ce1e6";
  ctx.fillRect(player.x - 10 + player.facing * 8, player.y - 46, 20, 12);
  ctx.fillStyle = "#101116";
  ctx.fillRect(player.x + player.facing * 12, player.y - 42, 4, 4);
}

function drawEnemy(enemy) {
  if (enemy.state === "cleared") return;
  const rect = enemyRect(enemy);
  const colors = {
    walker: ["#f6d365", "#8f6b2a"],
    jumper: ["#ff9f68", "#8d4635"],
    flyer: ["#8dd7ff", "#315d8f"],
    shield: ["#b388ff", "#563a7d"],
    charger: ["#ff5da2", "#7d294c"],
    splitter: ["#f4f7fb", "#596170"],
  }[enemy.type] || ["#f6d365", "#8f6b2a"];
  ctx.fillStyle = enemy.state === "packed" ? "#bff7ff" : enemy.state === "affected" ? "#8dd7ff" : colors[0];
  ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
  ctx.fillStyle = enemy.state === "packed" ? "#3a7892" : colors[1];
  ctx.fillRect(rect.x + 6, rect.y - 8, rect.w - 12, 10);
  if (enemy.state !== "packed") {
    ctx.fillStyle = "#101116";
    ctx.fillRect(rect.x + 8, rect.y + 12, 4, 4);
    ctx.fillRect(rect.x + rect.w - 12, rect.y + 12, 4, 4);
  }
}

function drawPickup(pickup) {
  const def = PICKUP_DEFS[pickup.type] || { color: "#f4f7fb" };
  ctx.fillStyle = def.color;
  ctx.fillRect(pickup.x - 10, pickup.y - 10, 20, 20);
  ctx.fillStyle = "#101116";
  ctx.fillRect(pickup.x - 4, pickup.y - 4, 8, 8);
}

function drawProjectile(projectile) {
  ctx.fillStyle = "#5ce1e6";
  ctx.fillRect(projectile.x - 7, projectile.y - 5, 14, 10);
}

function drawBall(ball) {
  ctx.fillStyle = "#bff7ff";
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, 18, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#3a7892";
  ctx.fillRect(ball.x - 10, ball.y - 3, 20, 6);
}

function drawEffects() {
  ctx.font = "700 18px Inter, sans-serif";
  ctx.textAlign = "center";
  for (const effect of state.effects) {
    ctx.fillStyle = String(effect.text).startsWith("+") ? "#f6d365" : "#f4f7fb";
    ctx.fillText(effect.text, effect.x, effect.y);
  }
}

function validateContent() {
  const errors = [];
  const enemyTypes = new Set();
  const pickupTypes = new Set();
  if (LEVELS.length < 3) errors.push("expected at least 3 levels");
  for (const level of LEVELS) {
    for (const key of ["id", "name", "timeLimit", "playerStart", "exit", "rankTargets"]) {
      if (!(key in level)) errors.push(`${level.id || "unknown"} missing ${key}`);
    }
    if (!Array.isArray(level.platforms) || level.platforms.length === 0) errors.push(`${level.id} missing platforms`);
    if (!Array.isArray(level.enemies) || level.enemies.length === 0) errors.push(`${level.id} missing enemies`);
    for (const enemy of level.enemies || []) {
      if (!enemy.id || !enemy.type || !enemy.patrol || !enemy.freeze) errors.push(`${level.id} invalid enemy`);
      if (enemy.type) enemyTypes.add(enemy.type);
    }
    for (const pickup of level.pickups || []) {
      if (!pickup.id || !pickup.type || !(pickup.type in PICKUP_DEFS)) errors.push(`${level.id} invalid pickup`);
      if (pickup.type) pickupTypes.add(pickup.type);
    }
  }
  if (enemyTypes.size < 3) errors.push("expected at least 3 enemy behavior types");
  if (pickupTypes.size < 3) errors.push("expected at least 3 pickup types");
  return {
    ok: errors.length === 0,
    errors,
    levelCount: LEVELS.length,
    enemyTypes: [...enemyTypes].sort(),
    pickupTypes: [...pickupTypes].sort(),
    localeCount: Object.keys(STRINGS).length,
    requirementIds: REQUIREMENT_IDS,
    workstreamIds: WORKSTREAM_IDS,
    assetBoundary: "original-placeholder-canvas",
  };
}

function getSnapshot() {
  const level = currentLevel();
  return {
    mode: state.mode,
    levelIndex: state.levelIndex,
    levelId: level.id,
    levelName: level.name[save.locale] || level.name.en,
    lives: state.lives,
    score: state.score,
    combo: state.combo,
    bestCombo: state.bestCombo,
    timeLeft: Math.ceil(state.timeLeft),
    playerX: Math.round(state.player.x),
    playerY: Math.round(state.player.y),
    playerVy: Math.round(state.player.vy),
    projectileCount: state.projectiles.length,
    ballCount: state.balls.length,
    remainingEnemies: activeEnemies().length,
    packedEnemies: state.enemies.filter((enemy) => enemy.state === "packed").length,
    clearedEnemies: state.enemies.filter((enemy) => enemy.state === "cleared").length,
    exitUnlocked: state.exitUnlocked,
    rank: state.rank,
    locale: save.locale,
    unlockedLevel: save.unlockedLevel,
    bestScore: save.bestScore,
    requirementIds: REQUIREMENT_IDS,
    workstreamIds: WORKSTREAM_IDS,
  };
}

function clearCurrentLevelWithCombo() {
  let guard = 0;
  while (activeEnemies().length > 0 && guard < 60) {
    const enemy = activeEnemies()[0];
    freezeEnemyById(enemy.id, 99);
    throwPackedEnemyById(enemy.id);
    guard += 1;
  }
  checkExitUnlock();
  syncHud();
  draw();
  return getSnapshot();
}

function completeCampaignFast() {
  startCampaign();
  for (let index = 0; index < LEVELS.length; index += 1) {
    if (state.levelIndex !== index) startLevel(index, { keepRunScore: true });
    clearCurrentLevelWithCombo();
    enterExit();
    if (index < LEVELS.length - 1) nextLevel();
  }
  return getSnapshot();
}

function setLocale(locale) {
  if (locale in STRINGS) {
    save.locale = locale;
    writeSave();
    syncHud();
    draw();
  }
  return getSnapshot();
}

function simulateInput(codes = [], duration = 0.16) {
  keys.clear();
  for (const code of codes) keys.add(code);
  const total = Math.max(0.016, Number(duration) || 0.16);
  const steps = Math.max(1, Math.ceil(total / 0.016));
  const delta = total / steps;
  for (let step = 0; step < steps; step += 1) {
    update(delta);
  }
  keys.clear();
  syncHud();
  draw();
  return getSnapshot();
}

function simulateAction(code) {
  if (code === "KeyJ") return fireProjectile();
  if (code === "KeyK") return kickNearestPacked();
  if (code === "KeyP") return pauseToggle();
  if (code === "KeyR") return retryLevel();
  return getSnapshot();
}

function frame(timestamp) {
  const delta = Math.min(0.033, (timestamp - state.lastFrame) / 1000 || 0);
  state.lastFrame = timestamp;
  update(delta);
  draw();
  requestAnimationFrame(frame);
}

document.addEventListener("keydown", (event) => {
  keys.add(event.code);
  if (event.repeat) return;
  if (event.code === "KeyJ") fireProjectile();
  if (event.code === "KeyK") kickNearestPacked();
  if (event.code === "KeyP") pauseToggle();
  if (event.code === "KeyR") retryLevel();
  if (event.code === "Enter" && state.mode === "levelComplete") nextLevel();
});

document.addEventListener("keyup", (event) => {
  keys.delete(event.code);
});

dom.start.addEventListener("click", startCampaign);
dom.pause.addEventListener("click", () => pauseToggle());
dom.retry.addEventListener("click", retryLevel);
dom.next.addEventListener("click", nextLevel);
dom.resetProgress.addEventListener("click", resetProgress);
dom.language.addEventListener("change", (event) => setLocale(event.target.value));

if (SMOKE_MODE) {
  window.__PIXEL_FREEZE_PLATFORMER_TEST__ = {
    validateContent,
    resetAll: (options = {}) => startLevel(options.levelIndex || 0),
    startCampaign,
    startLevel,
    getSnapshot,
    setLocale,
    freezeEnemyById,
    throwPackedEnemyById,
    clearCurrentLevelWithCombo,
    enterExit,
    nextLevel,
    completeCampaignFast,
    resetProgress,
    simulateInput,
    simulateAction,
  };
}

setLocale(save.locale);
startLevel(save.unlockedLevel || 0);
if (!SMOKE_MODE) {
  requestAnimationFrame(frame);
}
