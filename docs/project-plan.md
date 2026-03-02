# Project Plan

**Project:** Browser-Based Snake Game
**Phase:** 3 — Planning
**Date:** 2026-03-02

## Task Breakdown

Tasks are ordered by dependency. Each is atomic and estimable.

### T-001: Create project structure and HTML entry point
**File:** `game/index.html`
**Scope:** Create `game/` directory. Write `index.html` with:
- HTML5 boilerplate, viewport meta tag
- `<canvas id="gameCanvas">` element
- Start screen overlay div and game-over overlay div
- Links to `style.css` and `game.js`
**Dependencies:** None
**Estimate:** Small

### T-002: Implement base styling
**File:** `game/style.css`
**Scope:** Write CSS for:
- Page reset (margin, padding, box-sizing)
- Canvas centering (flexbox on body)
- Dark background color (#1a1a2e)
- Overlay positioning (absolute, centered, semi-transparent backdrop)
- Overlay text styling (title, score, instructions)
- CSS transitions for overlay fade in/out
- Basic responsive behavior (canvas block, max-width)
**Dependencies:** T-001 (needs HTML structure to style)
**Estimate:** Small

### T-003: Implement game state and initialization
**File:** `game/game.js` (first section)
**Scope:** Write:
- Constants: GRID_SIZE (20), colors, speed tiers
- `state` object per ADR section 3.1
- `init()` function: reset state, place snake at center, call `spawnFood()`
- `spawnFood()` function: random cell not on snake
- `resize()` function: fit canvas to viewport, align to grid
**Dependencies:** T-001 (needs canvas element)
**Estimate:** Medium

### T-004: Implement input handling
**File:** `game/game.js` (input section)
**Scope:** Write:
- `handleInput(event)`: map arrow keys + WASD to direction vectors
- Direction buffer logic (prevent 180-degree reversal)
- Enter key for restart, Space for pause
- `event.preventDefault()` on arrow keys
- Register `keydown` event listener
**Dependencies:** T-003 (needs state object and init function)
**Estimate:** Small

### T-005: Implement game loop and update logic
**File:** `game/game.js` (loop section)
**Scope:** Write:
- `update()`: move snake head, check wall collision, check self collision, check food eaten, grow snake or pop tail, update score, apply speed progression
- `gameLoop()`: setTimeout + requestAnimationFrame hybrid per ADR section 3.2
- `checkCollision()`: head vs boundaries, head vs body segments
- Game-over state transition
**Dependencies:** T-003, T-004 (needs state, init, input, spawnFood)
**Estimate:** Medium

### T-006: Implement rendering
**File:** `game/game.js` (rendering section)
**Scope:** Write:
- `draw()`: clear canvas, draw snake segments (rounded rects, head highlight), draw food (circle with glow), draw score text and high score
- Color constants applied per ADR section 3.4
**Dependencies:** T-003, T-005 (needs state and game loop to call draw)
**Estimate:** Medium

### T-007: Implement UI overlays and game flow
**File:** `game/game.js` (overlay section) + minor updates to `game/index.html`
**Scope:** Write:
- Show/hide start screen overlay on game start
- Show game-over overlay with final score on death
- "Press Enter to restart" handling
- Pause overlay on Space
- Wire up `init()` call on page load to show start screen
**Dependencies:** T-002 (overlay CSS), T-005 (game loop), T-006 (rendering)
**Estimate:** Small

## Execution Order

```
T-001 (HTML) ──> T-002 (CSS) ──> T-003 (State/Init) ──> T-004 (Input)
                                       |
                                       v
                                 T-005 (Loop/Update) ──> T-006 (Rendering)
                                                              |
                                                              v
                                                       T-007 (Overlays/Flow)
```

## Testing Strategy (Phase 6)
- Manual browser testing for gameplay
- Automated tests for pure functions: `spawnFood`, `checkCollision`, direction buffer logic
- Visual QA: overlay transitions, canvas sizing, color accuracy

---

# v1.1 — Realistic Snake Rendering Task Breakdown

**Phase:** 3 — Planning
**Date:** 2026-03-02

## Shared Setup (included in T-008 as foundation)

Before any rendering function is implemented, T-008 will add the shared infrastructure:
- New color constants to COLORS object (ADR v1.1 section 2)
- `tongueFrameCounter` module-level variable (ADR v1.1 section 3)
- `directionAngle(dir)` utility function (ADR v1.1 section 4)
- Modified snake drawing loop in `draw()` that dispatches to the three new functions (ADR v1.1 section 8)

## Task Breakdown

### T-008: Head rendering with eyes and tongue
**File:** `game/game.js`
**Scope:**
- Add new COLORS entries: eyeWhite, pupil, tongue, scaleAccent, snakeBodyLight, snakeBodyDark
- Add `tongueFrameCounter` variable near other module-level vars (after line 45)
- Add `directionAngle(dir)` utility function
- Implement `drawSnakeHead(seg, direction)` per ADR v1.1 section 5:
  - Elliptical head shape with radial gradient
  - Two eyes with white sclera and dark pupils
  - Forked tongue with frame-counter flicker animation
- Replace snake drawing loop (lines 368-383) with the back-to-front dispatch loop per ADR v1.1 section 8
- Temporarily use simple circle fill for body and tail segments as placeholders until T-009 and T-010 are implemented
**Dependencies:** None (first v1.1 task)
**Estimate:** Medium
**Verification:** Head rotates correctly in all 4 directions; eyes and tongue visible; no rendering errors for body/tail placeholders

### T-009: Body scale pattern and gradient
**File:** `game/game.js`
**Scope:**
- Implement `drawSnakeBody(seg, index, totalLength, prevSeg, nextSeg)` per ADR v1.1 section 6:
  - Color interpolation from snakeBodyLight to snakeBodyDark based on segment index
  - Radial gradient per segment for 3D tube illusion
  - Circle-based segment (radius 9px) instead of rounded rectangle
  - Scale marks (2 small arcs per segment) in staggered pattern with alpha transparency
- Replace the placeholder body rendering from T-008
**Dependencies:** T-008 (needs COLORS, directionAngle, draw loop structure)
**Estimate:** Medium
**Verification:** Body shows color gradient from bright (near head) to dark (near tail); each segment has visible radial shading; scale marks visible but subtle

### T-010: Tail taper rendering
**File:** `game/game.js`
**Scope:**
- Implement `drawSnakeTail(seg, prevSeg)` per ADR v1.1 section 7:
  - Compute direction from prevSeg to seg using Math.atan2
  - Draw tapered triangle/kite shape with base matching body width and tip at point
  - Apply darkest body gradient color with radial shading
- Replace the placeholder tail rendering from T-008
- Handle edge case: snake length = 1 (no tail, only head)
**Dependencies:** T-008 (needs COLORS, draw loop), T-009 (body gradient color scheme must be consistent)
**Estimate:** Small
**Verification:** Tail points away from body; taper is visible; colors match the dark end of body gradient

## Execution Order

```
T-008 (Head + shared setup) ──> T-009 (Body scales) ──> T-010 (Tail taper)
```

Strictly sequential: each task builds on the rendering infrastructure from the previous one.

## Testing Strategy (Phase 6)
- Visual QA in browser: verify all 4 directions, various snake lengths (1, 3, 10, 30+ segments)
- Performance check: confirm 60fps with 50+ segment snake
- Regression check: food rendering, score display, overlays all unchanged
