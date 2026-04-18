import * as THREE from "https://unpkg.com/three@0.164.1/build/three.module.js";

const GRID_SIZE = 16;
const CELL_SIZE = 1;
const MOVE_INTERVAL_MS = 150;
const STORAGE_KEY = "threejs-snake-best-score";
const SMOKE_MODE = new URLSearchParams(window.location.search).has("smoke");

const canvas = document.getElementById("game");
const scoreEl = document.getElementById("score");
const bestEl = document.getElementById("best");
const overlayEl = document.getElementById("overlay");
const titleEl = document.getElementById("title");
const messageEl = document.getElementById("message");
const restartButton = document.getElementById("restart");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x07111f);
scene.fog = new THREE.Fog(0x07111f, 14, 34);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: false,
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
camera.position.set(0, 18, 18);
camera.lookAt(0, 0, 0);

const ambientLight = new THREE.AmbientLight(0xbdd7ff, 1.0);
scene.add(ambientLight);

const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(-8, 16, 12);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -14;
sun.shadow.camera.right = 14;
sun.shadow.camera.top = 14;
sun.shadow.camera.bottom = -14;
scene.add(sun);

const accent = new THREE.PointLight(0x55d9ff, 35, 24, 2);
accent.position.set(0, 6, 0);
scene.add(accent);

const boardGroup = new THREE.Group();
scene.add(boardGroup);

const boardGeometry = new THREE.PlaneGeometry(GRID_SIZE, GRID_SIZE);
const boardMaterial = new THREE.MeshStandardMaterial({
  color: 0x0e1728,
  roughness: 0.92,
  metalness: 0.02,
});
const board = new THREE.Mesh(boardGeometry, boardMaterial);
board.rotation.x = -Math.PI / 2;
board.receiveShadow = true;
boardGroup.add(board);

const borderGeometry = new THREE.BoxGeometry(GRID_SIZE + 0.45, 0.32, GRID_SIZE + 0.45);
const borderMaterial = new THREE.MeshStandardMaterial({
  color: 0x12213a,
  roughness: 0.7,
  metalness: 0.12,
});
const border = new THREE.Mesh(borderGeometry, borderMaterial);
border.position.y = -0.16;
border.receiveShadow = true;
boardGroup.add(border);

const grid = new THREE.GridHelper(GRID_SIZE, GRID_SIZE, 0x406080, 0x22334d);
grid.position.y = 0.01;
boardGroup.add(grid);

const cellGeometry = new THREE.BoxGeometry(CELL_SIZE * 0.88, 0.7, CELL_SIZE * 0.88);

const snakeMaterial = new THREE.MeshStandardMaterial({
  color: 0x5fffd7,
  emissive: 0x113b36,
  roughness: 0.35,
  metalness: 0.1,
});

const headMaterial = new THREE.MeshStandardMaterial({
  color: 0xc9fff4,
  emissive: 0x1d665d,
  roughness: 0.2,
  metalness: 0.15,
});

const foodMaterial = new THREE.MeshStandardMaterial({
  color: 0xff7a7a,
  emissive: 0x5e1111,
  roughness: 0.22,
  metalness: 0.24,
});

const snakeMeshes = [];
let foodMesh = null;

const state = {
  running: false,
  gameOver: false,
  score: 0,
  best: Number(localStorage.getItem(STORAGE_KEY) || 0),
  direction: { x: 1, z: 0 },
  queuedDirection: { x: 1, z: 0 },
  snake: [],
  food: { x: 0, z: 0 },
  lastMoveAt: 0,
};

bestEl.textContent = String(state.best);

function cellToWorld(x, z) {
  const half = (GRID_SIZE - 1) / 2;
  return {
    x: (x - half) * CELL_SIZE,
    z: (z - half) * CELL_SIZE,
  };
}

function createCellMesh(material) {
  const mesh = new THREE.Mesh(cellGeometry, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function ensureSnakeMeshes(length) {
  while (snakeMeshes.length < length) {
    const mesh = createCellMesh(snakeMaterial);
    scene.add(mesh);
    snakeMeshes.push(mesh);
  }

  while (snakeMeshes.length > length) {
    const mesh = snakeMeshes.pop();
    scene.remove(mesh);
  }
}

function ensureFoodMesh() {
  if (foodMesh) {
    return;
  }

  const geometry = new THREE.SphereGeometry(0.34, 24, 16);
  foodMesh = new THREE.Mesh(geometry, foodMaterial);
  foodMesh.castShadow = true;
  foodMesh.receiveShadow = true;
  scene.add(foodMesh);
}

function randomCell() {
  return Math.floor(Math.random() * GRID_SIZE);
}

function isOccupied(x, z) {
  return state.snake.some((part) => part.x === x && part.z === z);
}

function spawnFood() {
  let candidate;
  do {
    candidate = { x: randomCell(), z: randomCell() };
  } while (isOccupied(candidate.x, candidate.z));

  state.food = candidate;
  ensureFoodMesh();
  const foodPos = cellToWorld(candidate.x, candidate.z);
  foodMesh.position.set(foodPos.x, 0.45, foodPos.z);
}

function resetGame() {
  state.snake = [
    { x: 6, z: 8 },
    { x: 5, z: 8 },
    { x: 4, z: 8 },
  ];
  state.direction = { x: 1, z: 0 };
  state.queuedDirection = { x: 1, z: 0 };
  state.score = 0;
  state.gameOver = false;
  state.running = true;
  state.lastMoveAt = performance.now();

  ensureSnakeMeshes(state.snake.length);
  spawnFood();
  syncHud();
  overlayEl.classList.add("hidden");
  titleEl.textContent = "Snake";
  messageEl.textContent = "Eat the glowing food, avoid walls and yourself.";
  restartButton.textContent = "Restart";
}

function endGame() {
  state.gameOver = true;
  state.running = false;
  overlayEl.classList.remove("hidden");
  titleEl.textContent = "Game Over";
  messageEl.textContent = `Score ${state.score}. Press Enter or click restart to play again.`;
}

function syncHud() {
  scoreEl.textContent = String(state.score);
  bestEl.textContent = String(state.best);
}

function setDirection(next) {
  const current = state.direction;
  const reversing = next.x + current.x === 0 && next.z + current.z === 0;
  if (reversing) {
    return;
  }

  state.queuedDirection = next;
}

function handleMove() {
  if (!state.running) {
    return;
  }

  state.direction = state.queuedDirection;
  const head = state.snake[0];
  const next = {
    x: head.x + state.direction.x,
    z: head.z + state.direction.z,
  };

  const hitWall = next.x < 0 || next.x >= GRID_SIZE || next.z < 0 || next.z >= GRID_SIZE;
  const tailWillMove = next.x !== state.food.x || next.z !== state.food.z;
  const bodyToCheck = tailWillMove ? state.snake.slice(0, -1) : state.snake;
  const hitSelf = bodyToCheck.some((part) => part.x === next.x && part.z === next.z);

  if (hitWall || hitSelf) {
    if (state.score > state.best) {
      state.best = state.score;
      localStorage.setItem(STORAGE_KEY, String(state.best));
    }
    syncHud();
    endGame();
    return;
  }

  state.snake.unshift(next);

  if (next.x === state.food.x && next.z === state.food.z) {
    state.score += 1;
    if (state.score > state.best) {
      state.best = state.score;
      localStorage.setItem(STORAGE_KEY, String(state.best));
    }
    spawnFood();
    syncHud();
    ensureSnakeMeshes(state.snake.length);
  } else {
    state.snake.pop();
  }

  ensureSnakeMeshes(state.snake.length);
}

function updateSnakeMeshes() {
  ensureSnakeMeshes(state.snake.length);

  state.snake.forEach((part, index) => {
    const mesh = snakeMeshes[index];
    const pos = cellToWorld(part.x, part.z);
    mesh.position.set(pos.x, 0.35, pos.z);
    mesh.material = index === 0 ? headMaterial : snakeMaterial;
    mesh.scale.y = index === 0 ? 1.08 : 1;
    mesh.rotation.y = index === 0 ? 0.12 : 0;
  });
}

function updateCamera(timeMs) {
  const t = timeMs * 0.0005;
  const snakeHead = state.snake[0] ?? { x: GRID_SIZE / 2, z: GRID_SIZE / 2 };
  const headWorld = cellToWorld(snakeHead.x, snakeHead.z);
  const targetX = THREE.MathUtils.lerp(camera.position.x, headWorld.x, 0.05);
  const targetZ = THREE.MathUtils.lerp(camera.position.z, headWorld.z + 10, 0.03);
  camera.position.x = targetX + Math.sin(t) * 0.35;
  camera.position.z = targetZ;
  camera.position.y = 18 + Math.cos(t * 0.8) * 0.2;
  camera.lookAt(headWorld.x, 0, headWorld.z);
}

function updateFoodAnimation(timeMs) {
  if (!foodMesh) {
    return;
  }

  const pulse = 1 + Math.sin(timeMs * 0.006) * 0.08;
  foodMesh.scale.setScalar(pulse);
  foodMesh.rotation.y += 0.015;
}

function render(timeMs) {
  requestAnimationFrame(render);

  if (state.running && timeMs - state.lastMoveAt >= MOVE_INTERVAL_MS) {
    const moves = Math.floor((timeMs - state.lastMoveAt) / MOVE_INTERVAL_MS);
    state.lastMoveAt += moves * MOVE_INTERVAL_MS;
    for (let i = 0; i < moves; i += 1) {
      handleMove();
      if (!state.running) {
        break;
      }
    }
  }

  updateSnakeMeshes();
  updateCamera(timeMs);
  updateFoodAnimation(timeMs);

  renderer.render(scene, camera);
}

function resize() {
  const width = canvas.clientWidth || window.innerWidth;
  const height = canvas.clientHeight || window.innerHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function getSmokeSnapshot() {
  return {
    running: state.running,
    gameOver: state.gameOver,
    score: state.score,
    best: state.best,
    direction: { ...state.direction },
    snake: state.snake.map((part) => ({ ...part })),
    food: { ...state.food },
    overlayHidden: overlayEl.classList.contains("hidden"),
    title: titleEl.textContent,
    message: messageEl.textContent,
    restartLabel: restartButton.textContent,
  };
}

function installSmokeApi() {
  if (!SMOKE_MODE) {
    return;
  }

  window.__THREEJS_SNAKE_TEST__ = Object.freeze({
    getSnapshot() {
      return getSmokeSnapshot();
    },
    restart() {
      resetGame();
      updateSnakeMeshes();
      return getSmokeSnapshot();
    },
    placeFoodAhead() {
      const head = state.snake[0];
      const next = {
        x: head.x + state.direction.x,
        z: head.z + state.direction.z,
      };
      const outside = next.x < 0 || next.x >= GRID_SIZE || next.z < 0 || next.z >= GRID_SIZE;

      if (outside || isOccupied(next.x, next.z)) {
        throw new Error("Cannot place smoke-test food ahead of the snake.");
      }

      state.food = next;
      ensureFoodMesh();
      const foodPos = cellToWorld(next.x, next.z);
      foodMesh.position.set(foodPos.x, 0.45, foodPos.z);
      return getSmokeSnapshot();
    },
    step(moves = 1) {
      const totalMoves = Math.max(0, Math.floor(Number(moves) || 0));

      for (let i = 0; i < totalMoves; i += 1) {
        handleMove();
        if (!state.running) {
          break;
        }
      }

      updateSnakeMeshes();
      return getSmokeSnapshot();
    },
  });
}

window.addEventListener("resize", resize);
window.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (key === "arrowup" || key === "w") {
    event.preventDefault();
    setDirection({ x: 0, z: -1 });
  } else if (key === "arrowdown" || key === "s") {
    event.preventDefault();
    setDirection({ x: 0, z: 1 });
  } else if (key === "arrowleft" || key === "a") {
    event.preventDefault();
    setDirection({ x: -1, z: 0 });
  } else if (key === "arrowright" || key === "d") {
    event.preventDefault();
    setDirection({ x: 1, z: 0 });
  } else if (key === "enter" || key === " ") {
    event.preventDefault();
    if (!state.running) {
      resetGame();
    }
  }
});

restartButton.addEventListener("click", () => {
  resetGame();
});

resize();
installSmokeApi();
resetGame();
requestAnimationFrame(render);
