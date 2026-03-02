// =============================================================================
// Snake Game — game.js
// Pure vanilla JS, no dependencies. See docs/adr.md for architecture details.
// =============================================================================

// ---------------------------------------------------------------------------
// T-003: Constants, State, Initialization
// ---------------------------------------------------------------------------

const GRID_SIZE = 20; // pixels per grid cell
const INITIAL_SNAKE_LENGTH = 3;

// Colors (ADR section 3.4)
const COLORS = {
    background: '#1a1a2e',
    snake: '#00ff88',
    snakeHead: '#00cc6a',
    food: '#ff4757',
    foodGlow: 'rgba(255, 71, 87, 0.4)',
    text: '#ffffff',
    textDim: '#888888'
};

// Speed tiers (ADR section 5)
const SPEED_TIERS = [
    { threshold: 0, speed: 150 },
    { threshold: 5, speed: 130 },
    { threshold: 10, speed: 110 },
    { threshold: 20, speed: 90 }
];

// Canvas and context references
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Overlay references
const startOverlay = document.getElementById('start-overlay');
const gameoverOverlay = document.getElementById('gameover-overlay');
const pauseOverlay = document.getElementById('pause-overlay');
const finalScoreEl = document.getElementById('final-score');
const finalHighScoreEl = document.getElementById('final-high-score');

// Grid dimensions (set by resize)
let cols = 0;
let rows = 0;

// Game state (ADR section 3.1)
let state = {
    snake: [],
    direction: { x: 1, y: 0 },
    nextDirection: { x: 1, y: 0 },
    food: { x: 0, y: 0 },
    score: 0,
    highScore: 0,
    gameOver: false,
    paused: false,
    started: false,
    speed: 150
};

// Loop control
let lastTick = 0;
let animFrameId = null;

/**
 * Resize canvas to fit viewport, aligned to grid.
 */
function resize() {
    const maxWidth = Math.min(window.innerWidth - 20, 800);
    const maxHeight = Math.min(window.innerHeight - 20, 600);

    cols = Math.floor(maxWidth / GRID_SIZE);
    rows = Math.floor(maxHeight / GRID_SIZE);

    canvas.width = cols * GRID_SIZE;
    canvas.height = rows * GRID_SIZE;
}

/**
 * Place food on a random grid cell not occupied by the snake.
 * Uses Set-based lookup for O(1) collision checks against long snakes.
 */
function spawnFood() {
    const occupied = new Set(state.snake.map(seg => seg.y * cols + seg.x));
    const totalCells = cols * rows;

    // Safety: if snake fills the entire grid, no room for food
    if (occupied.size >= totalCells) {
        return;
    }

    let pos;
    do {
        pos = {
            x: Math.floor(Math.random() * cols),
            y: Math.floor(Math.random() * rows)
        };
    } while (occupied.has(pos.y * cols + pos.x));
    state.food = pos;
}

/**
 * Get current speed based on score.
 */
function getSpeed(score) {
    let speed = SPEED_TIERS[0].speed;
    for (const tier of SPEED_TIERS) {
        if (score >= tier.threshold) {
            speed = tier.speed;
        }
    }
    return speed;
}

/**
 * Initialize / reset game state. Does not start the loop.
 */
function init() {
    const centerX = Math.floor(cols / 2);
    const centerY = Math.floor(rows / 2);

    state.snake = [];
    for (let i = 0; i < INITIAL_SNAKE_LENGTH; i++) {
        state.snake.push({ x: centerX - i, y: centerY });
    }

    state.direction = { x: 1, y: 0 };
    state.nextDirection = { x: 1, y: 0 };
    state.score = 0;
    state.gameOver = false;
    state.paused = false;
    state.speed = SPEED_TIERS[0].speed;

    spawnFood();
}

// ---------------------------------------------------------------------------
// T-004: Input Handling
// ---------------------------------------------------------------------------

/**
 * Map key events to direction changes, pause, restart.
 * Direction is buffered in nextDirection to prevent 180-degree reversal.
 */
function handleInput(event) {
    const key = event.key;

    // Direction mappings
    const directionMap = {
        'ArrowUp': { x: 0, y: -1 },
        'ArrowDown': { x: 0, y: 1 },
        'ArrowLeft': { x: -1, y: 0 },
        'ArrowRight': { x: 1, y: 0 },
        'w': { x: 0, y: -1 },
        's': { x: 0, y: 1 },
        'a': { x: -1, y: 0 },
        'd': { x: 1, y: 0 },
        'W': { x: 0, y: -1 },
        'S': { x: 0, y: 1 },
        'A': { x: -1, y: 0 },
        'D': { x: 1, y: 0 }
    };

    // Prevent default for arrow keys (stop page scroll)
    if (key.startsWith('Arrow')) {
        event.preventDefault();
    }

    // Start game on first direction input
    if (!state.started && directionMap[key]) {
        state.started = true;
        startOverlay.classList.add('hidden');
        state.nextDirection = directionMap[key];
        state.direction = directionMap[key];
        lastTick = performance.now();
        gameLoop();
        return;
    }

    // Restart on Enter when game over
    if (state.gameOver && key === 'Enter') {
        gameoverOverlay.classList.add('hidden');
        init();
        state.started = true;
        lastTick = performance.now();
        gameLoop();
        return;
    }

    // Pause/unpause on Space
    if (key === ' ' && state.started && !state.gameOver) {
        event.preventDefault();
        state.paused = !state.paused;
        if (state.paused) {
            pauseOverlay.classList.remove('hidden');
            if (animFrameId) {
                cancelAnimationFrame(animFrameId);
                animFrameId = null;
            }
        } else {
            pauseOverlay.classList.add('hidden');
            lastTick = performance.now();
            gameLoop();
        }
        return;
    }

    // Buffer direction change (prevent 180-degree reversal)
    if (directionMap[key] && !state.paused && !state.gameOver && state.started) {
        const newDir = directionMap[key];
        // Only allow if not reversing current direction
        if (newDir.x !== -state.direction.x || newDir.y !== -state.direction.y) {
            state.nextDirection = newDir;
        }
    }
}

document.addEventListener('keydown', handleInput);

// ---------------------------------------------------------------------------
// T-005: Game Loop and Update Logic
// ---------------------------------------------------------------------------

/**
 * Check if head position collides with walls or snake body.
 * Returns true if collision detected.
 */
function checkCollision(head) {
    // Wall collision
    if (head.x < 0 || head.x >= cols || head.y < 0 || head.y >= rows) {
        return true;
    }
    // Self collision (check against body, not head — head is not yet in snake array when called)
    for (let i = 0; i < state.snake.length; i++) {
        if (state.snake[i].x === head.x && state.snake[i].y === head.y) {
            return true;
        }
    }
    return false;
}

/**
 * Advance game state by one tick.
 * Moves snake, checks collisions, handles food, updates score and speed.
 */
function update() {
    // Apply buffered direction
    state.direction = { ...state.nextDirection };

    // Calculate new head position
    const head = state.snake[0];
    const newHead = {
        x: head.x + state.direction.x,
        y: head.y + state.direction.y
    };

    // Check collision before moving
    if (checkCollision(newHead)) {
        state.gameOver = true;
        if (state.score > state.highScore) {
            state.highScore = state.score;
        }
        // Show game over overlay
        finalScoreEl.textContent = state.score;
        finalHighScoreEl.textContent = state.highScore;
        gameoverOverlay.classList.remove('hidden');
        return;
    }

    // Move snake: add new head
    state.snake.unshift(newHead);

    // Check food
    if (newHead.x === state.food.x && newHead.y === state.food.y) {
        state.score++;
        state.speed = getSpeed(state.score);
        spawnFood();
        // Don't pop tail — snake grows
    } else {
        // Pop tail — snake moves without growing
        state.snake.pop();
    }
}

/**
 * Main game loop using setTimeout + requestAnimationFrame hybrid.
 * setTimeout controls tick rate, rAF handles rendering.
 */
function gameLoop() {
    if (state.gameOver || state.paused) {
        return;
    }

    const now = performance.now();
    const elapsed = now - lastTick;

    if (elapsed >= state.speed) {
        update();
        lastTick = now;
    }

    draw();

    if (!state.gameOver && !state.paused) {
        animFrameId = requestAnimationFrame(gameLoop);
    }
}

// ---------------------------------------------------------------------------
// T-006: Rendering
// ---------------------------------------------------------------------------

/**
 * Draw a rounded rectangle on the canvas.
 */
function roundRect(x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fill();
}

/**
 * Render the current game state to the canvas.
 * Reads state, does not mutate it.
 */
function draw() {
    // Clear canvas
    ctx.fillStyle = COLORS.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw subtle grid lines (batched into a single path for performance)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    for (let x = 0; x <= cols; x++) {
        ctx.moveTo(x * GRID_SIZE, 0);
        ctx.lineTo(x * GRID_SIZE, canvas.height);
    }
    for (let y = 0; y <= rows; y++) {
        ctx.moveTo(0, y * GRID_SIZE);
        ctx.lineTo(canvas.width, y * GRID_SIZE);
    }
    ctx.stroke();

    // Draw food (circle with glow)
    const foodCenterX = state.food.x * GRID_SIZE + GRID_SIZE / 2;
    const foodCenterY = state.food.y * GRID_SIZE + GRID_SIZE / 2;
    const foodRadius = GRID_SIZE / 2 - 2;

    ctx.save();
    ctx.shadowColor = COLORS.foodGlow;
    ctx.shadowBlur = 15;
    ctx.fillStyle = COLORS.food;
    ctx.beginPath();
    ctx.arc(foodCenterX, foodCenterY, foodRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Draw snake segments
    const gap = 2; // gap between edge and segment for rounded look
    for (let i = 0; i < state.snake.length; i++) {
        const seg = state.snake[i];
        const isHead = i === 0;

        ctx.fillStyle = isHead ? COLORS.snakeHead : COLORS.snake;

        roundRect(
            seg.x * GRID_SIZE + gap,
            seg.y * GRID_SIZE + gap,
            GRID_SIZE - gap * 2,
            GRID_SIZE - gap * 2,
            4
        );
    }

    // Draw score (top-left)
    ctx.fillStyle = COLORS.text;
    ctx.font = '16px "Segoe UI", Tahoma, Geneva, Verdana, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Score: ' + state.score, 10, 24);

    // Draw high score (top-right)
    ctx.textAlign = 'right';
    ctx.fillStyle = COLORS.textDim;
    ctx.fillText('Best: ' + state.highScore, canvas.width - 10, 24);
}

// ---------------------------------------------------------------------------
// T-007: UI Overlays and Game Flow
// ---------------------------------------------------------------------------

/**
 * Set up the game on page load.
 * Sizes canvas, initializes state, shows start overlay, draws initial frame.
 */
function setup() {
    resize();
    init();
    draw(); // Draw initial frame behind start overlay
}

// Handle window resize
window.addEventListener('resize', () => {
    resize();
    // Re-initialize if game hasn't started (snake position depends on grid size)
    if (!state.started) {
        init();
    }
    draw();
});

// Start everything
setup();
