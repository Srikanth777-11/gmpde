# Architecture Decision Record

**Project:** Browser-Based Interactive Game — Snake
**Phase:** 2 — Design
**Date:** 2026-03-02
**Status:** PROPOSED

## 1. Game Selection: Snake

Adopting the research recommendation. Snake provides the best ratio of gameplay richness to implementation complexity. It is real-time (showcasing interactive UI), universally understood (learnable in seconds), and naturally fits a canvas-based rendering approach.

## 2. File Structure

```
game/
  index.html      — Entry point, contains canvas element and UI overlay
  style.css       — Layout, colors, fonts, game-over overlay styling
  game.js         — All game logic: state, loop, rendering, input
```

Three files, one directory. The `index.html` file links to `style.css` and `game.js`. No build step. User opens `index.html` in any modern browser and plays immediately.

**Rationale for 3-file split over single HTML file:** Separation of concerns aids readability and makes Phase 5 implementation tasks naturally parallelizable. The overhead is negligible (two extra HTTP requests for local files).

## 3. Component Architecture

### 3.1 Game State Object
```
state = {
  snake: [{x, y}, ...],    // Array of grid cells, head is index 0
  direction: {x, y},       // Current movement vector
  nextDirection: {x, y},   // Buffered input (prevents 180-degree reversal)
  food: {x, y},            // Current food position
  score: 0,
  highScore: 0,            // Session-best (stored in variable, not persisted)
  gameOver: false,
  paused: false,
  speed: 150               // Milliseconds per tick (lower = faster)
}
```

### 3.2 Game Loop
- Uses `setTimeout` + `requestAnimationFrame` hybrid pattern:
  - `setTimeout` controls game tick speed (snake moves every `state.speed` ms)
  - `requestAnimationFrame` handles rendering at screen refresh rate
- This separates game logic speed from render speed, allowing smooth visuals.

### 3.3 Core Functions

| Function | Responsibility |
|----------|---------------|
| `init()` | Reset state, place snake at center, spawn food, start loop |
| `update()` | Move snake, check collisions, check food eaten, update score |
| `draw()` | Clear canvas, draw grid (optional), draw snake, draw food, draw score |
| `handleInput(event)` | Map arrow keys / WASD to direction changes, buffer input |
| `spawnFood()` | Random grid cell not occupied by snake |
| `checkCollision()` | Head vs walls, head vs body |
| `gameOverScreen()` | Show overlay with final score and "Press Enter to restart" |
| `resize()` | Adjust canvas to fit viewport while maintaining grid alignment |

### 3.4 Rendering Details
- **Canvas size:** Dynamically calculated. Grid cells are 20x20 pixels. Canvas fills available space rounded down to nearest multiple of 20.
- **Colors:** Dark background (#1a1a2e), green snake (#00ff88), red food (#ff4757), white text. Clean, high-contrast palette.
- **Snake style:** Rounded rectangles for each segment. Head slightly different shade.
- **Food:** Circular dot with subtle glow effect (shadow blur on canvas).
- **Score:** Rendered on canvas top-left. High score top-right.

### 3.5 Input Handling
- Arrow keys AND WASD supported for movement
- Enter key to restart after game over
- Space bar to pause/unpause
- Direction buffer prevents 180-degree turns (e.g., pressing Left while moving Right)
- `event.preventDefault()` on arrow keys to prevent page scrolling

## 4. UI Overlay

A minimal HTML/CSS overlay for:
- **Start screen:** Game title + "Press any arrow key to start"
- **Game-over screen:** "Game Over" + final score + "Press Enter to restart"
- Overlay fades in/out using CSS transitions. Game canvas is always visible behind it.

## 5. Speed Progression

Snake speeds up as score increases:
- Score 0-4: 150ms/tick
- Score 5-9: 130ms/tick
- Score 10-19: 110ms/tick
- Score 20+: 90ms/tick

This provides increasing difficulty, making high scores feel earned.

## 6. API Contracts (Internal)

No external APIs. Internal contract between functions:

- `update()` mutates `state` and returns void. `draw()` reads `state` and renders.
- `handleInput()` only writes to `state.nextDirection`. `update()` reads it and applies.
- `init()` is the only function that resets `state` entirely.

## 7. Deployment

The `game/` directory is self-contained. Deployment options:
1. **Local:** Open `game/index.html` in a browser (file:// protocol works)
2. **GitHub Pages:** Push `game/` and serve via Pages
3. **Any static host:** Copy directory to Netlify, Vercel, S3, etc.

No build step. No environment variables. No configuration.

---

# v1.1 — Realistic Snake Rendering ADR

**Phase:** 2 — Design
**Date:** 2026-03-02
**Status:** PROPOSED

## 1. Overview

Replace the uniform rounded-rectangle snake rendering (game/game.js lines 368-383) with anatomically-inspired rendering using three specialized functions. The existing `draw()` function structure is preserved -- only the snake-drawing loop is replaced.

## 2. New Color Constants

Add to the COLORS object (game/game.js lines 14-22):

```
snakeBodyLight: '#00ff88'    // Bright green (segment center, near head)
snakeBodyDark:  '#008844'    // Dark green (segment edge, near tail)
eyeWhite:      '#ffffff'     // Sclera
pupil:         '#1a1a2e'     // Pupil (matches background for contrast)
tongue:        '#ff2222'     // Red tongue
scaleAccent:   '#00cc6a'     // Darker marks for scale texture
```

## 3. Module-Level State for Animation

Add one module-level variable (NOT in state object):

```
let tongueFrameCounter = 0;  // Incremented each draw() call
```

Tongue is extended when `tongueFrameCounter % 20 < 10` (50% duty cycle, flickers ~3x/sec at 60fps).

## 4. Direction-to-Angle Utility

```
function directionAngle(dir) → number
```
Maps state.direction {x,y} to radians:
- {1,0} right = 0
- {0,1} down = PI/2
- {-1,0} left = PI
- {0,-1} up = -PI/2

Used by head and tail drawing for rotation.

## 5. Function: drawSnakeHead(seg, direction)

**Parameters:** `seg` = {x,y} grid position, `direction` = {x,y} movement vector

**Algorithm:**
1. Compute center: `cx = seg.x * 20 + 10`, `cy = seg.y * 20 + 10`
2. `ctx.save()`, translate to center, rotate by `directionAngle(direction)`
3. **Head shape**: Draw a filled ellipse (horizontal radius 9, vertical radius 8) using `ctx.ellipse()`. Fill with radial gradient (center: snakeHead color, edge: snakeBodyDark).
4. **Eyes**: Two white circles (radius 2.5) at positions (-3, -5) and (-3, +5) relative to center. Pupils (radius 1.5) offset +1px in the forward direction (positive x in local coords).
5. **Tongue**: If tongue is extended (frame counter check): two red lines from (8, 0) to (12, -2) and (12, +2), lineWidth 1.5, strokeStyle = COLORS.tongue. If retracted, draw shorter lines from (8, 0) to (10, -1) and (10, +1).
6. `ctx.restore()`

## 6. Function: drawSnakeBody(seg, index, totalLength, prevSeg, nextSeg)

**Parameters:** `seg` = {x,y}, `index` = segment index (1-based from head), `totalLength` = snake length, `prevSeg` = segment closer to head, `nextSeg` = segment closer to tail (or null for segment before tail)

**Algorithm:**
1. Compute center: `cx = seg.x * 20 + 10`, `cy = seg.y * 20 + 10`
2. **Body color gradient along length**: Interpolate RGB from snakeBodyLight (index=1) to snakeBodyDark (index=totalLength-2). Factor `t = index / (totalLength - 1)`.
3. **Radial gradient per segment**: Create radial gradient from (cx, cy, 0) to (cx, cy, 9). Inner stop = interpolated color (lighter), outer stop = same color darkened ~30%.
4. **Draw circle**: `ctx.arc(cx, cy, 9, 0, 2*PI)`, fill with gradient.
5. **Scale marks**: Draw 2 small arcs (radius 3px) in scaleAccent color at staggered positions. Odd-index segments: marks at top-left and bottom-right. Even-index: marks at top-right and bottom-left. Use `ctx.globalAlpha = 0.3` for subtlety, restore after.

## 7. Function: drawSnakeTail(seg, prevSeg)

**Parameters:** `seg` = {x,y} tail position, `prevSeg` = second-to-last segment

**Algorithm:**
1. Compute center: `cx = seg.x * 20 + 10`, `cy = seg.y * 20 + 10`
2. Compute direction from prevSeg toward seg: `dx = seg.x - prevSeg.x`, `dy = seg.y - prevSeg.y`. Angle = `Math.atan2(dy, dx)`.
3. `ctx.save()`, translate to center, rotate by angle.
4. **Taper shape**: A filled triangle/kite shape. Base at (-8, -7) to (-8, +7), tip at (9, 0). Fill with the darkest body gradient color.
5. Apply radial gradient (lighter center, darker edges) for 3D consistency.
6. `ctx.restore()`

## 8. Modified draw() Snake Loop

Replace lines 368-383 with:

```
tongueFrameCounter++;
for (let i = state.snake.length - 1; i >= 0; i--) {
    const seg = state.snake[i];
    if (i === 0) {
        drawSnakeHead(seg, state.direction);
    } else if (i === state.snake.length - 1 && state.snake.length > 1) {
        drawSnakeTail(seg, state.snake[i - 1]);
    } else {
        drawSnakeBody(seg, i, state.snake.length,
                      state.snake[i - 1],
                      state.snake[i + 1]);
    }
}
```

Drawing back-to-front (tail first, head last) ensures the head overlaps body segments and the tongue renders on top.

## 9. Performance Budget

| Operation | Per Segment | Max Segments (50) | Budget |
|-----------|-------------|-------------------|--------|
| Radial gradient creation | ~0.02ms | 1ms | OK |
| Arc fill | ~0.01ms | 0.5ms | OK |
| Scale marks (2 arcs) | ~0.02ms | 1ms | OK |
| Head (ellipse + eyes + tongue) | ~0.15ms | 1x = 0.15ms | OK |
| Tail (path + gradient) | ~0.08ms | 1x = 0.08ms | OK |
| **Total new rendering** | | **~2.7ms** | **Well under 16.6ms frame budget** |

## 10. Files Modified

Only `game/game.js`:
- Lines 14-22: Add new color constants to COLORS
- New module-level variable: `tongueFrameCounter`
- New function: `directionAngle(dir)`
- New function: `drawSnakeHead(seg, direction)`
- New function: `drawSnakeBody(seg, index, totalLength, prevSeg, nextSeg)`
- New function: `drawSnakeTail(seg, prevSeg)`
- Lines 368-383: Replace snake drawing loop

No changes to index.html, style.css, game logic, input handling, overlays, or state structure.
