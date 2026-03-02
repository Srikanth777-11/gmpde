# Research Brief

**Project:** Browser-Based Interactive Game
**Phase:** 1 — Research
**Date:** 2026-03-02

## Feasibility Assessment

Building a simple browser game in pure HTML/CSS/JS is fully feasible and well-trodden territory. The HTML5 Canvas API provides hardware-accelerated 2D rendering. `requestAnimationFrame` enables smooth 60fps game loops. Keyboard/mouse event listeners handle input. No dependencies are needed.

## Game Genre Evaluation

### Candidate 1: Snake
- **Complexity:** Low. Grid-based movement, collision detection against self and walls.
- **Learnability:** Instant — arrow keys to move, eat food, grow longer.
- **Win/Lose:** Lose on collision. Score = length. No fixed "win" — high-score chasing.
- **Visual appeal:** Moderate. Simple but satisfying with smooth movement.
- **Implementation effort:** ~200-300 lines of JS.

### Candidate 2: Breakout (Brick Breaker)
- **Complexity:** Low-medium. Ball physics (angle reflection), paddle control, brick grid.
- **Learnability:** Instant — move paddle, bounce ball, break bricks.
- **Win/Lose:** Win by clearing all bricks. Lose when ball falls past paddle (lives system).
- **Visual appeal:** High. Colorful brick grid, satisfying brick-breaking feedback.
- **Implementation effort:** ~300-400 lines of JS.

### Candidate 3: 2048
- **Complexity:** Medium. Grid merge logic, tile spawning, win/lose detection.
- **Learnability:** 30 seconds — slide tiles, match numbers.
- **Win/Lose:** Win at 2048 tile. Lose when no moves remain.
- **Visual appeal:** High. Clean tile-based UI with color progression.
- **Implementation effort:** ~300-400 lines of JS. DOM-based (no canvas needed).

### Candidate 4: Minesweeper
- **Complexity:** Medium. Flood-fill reveal, mine placement, flag system.
- **Learnability:** Moderate — requires understanding of number clues.
- **Win/Lose:** Win by revealing all safe cells. Lose by clicking mine.
- **Visual appeal:** Moderate. Grid-based, iconic.
- **Implementation effort:** ~350-450 lines of JS.

## Recommendation

**Snake** is the strongest candidate. Rationale:
1. Lowest implementation complexity while still being a "real" game
2. Universally known — zero learning curve
3. Canvas-based rendering demonstrates interactive graphics well
4. Real-time gameplay (continuous game loop) showcases browser interactivity better than turn-based alternatives
5. Clean scope: no edge cases around merge logic (2048) or flood-fill (Minesweeper)
6. Easy to make visually appealing with minimal CSS

**Breakout** is the strong runner-up if the architect wants slightly richer mechanics (ball physics, lives system).

## Technical Approach

- **Rendering:** HTML5 Canvas API (`<canvas>` element, 2D context)
- **Game loop:** `requestAnimationFrame` for smooth 60fps updates
- **Input:** `keydown`/`keyup` event listeners for arrow keys
- **Structure:** Single `index.html` with embedded or linked CSS/JS (architect decides file split)
- **State management:** Simple JS object holding grid state, snake position, direction, score

---

# v1.1 — Realistic Snake Rendering Research

**Phase:** 1 — Research
**Date:** 2026-03-02

## Canvas 2D Techniques for Snake Anatomy

### 1. Head Rendering (within 20x20px cell)

**Shape**: Use `ctx.ellipse()` or a combination of `ctx.arc()` and `ctx.lineTo()` to create a rounded, slightly elongated head shape. The head should be drawn as an oval (~18x16px) oriented in the movement direction.

**Rotation technique**: Use `ctx.save()`, `ctx.translate(centerX, centerY)`, `ctx.rotate(angle)`, then draw relative to origin, then `ctx.restore()`. Angle derived from `state.direction`: right=0, down=PI/2, left=PI, up=-PI/2.

**Eyes**: Two small `ctx.arc()` circles for the sclera (white, radius ~2.5px), positioned symmetrically on the head. Pupils are smaller filled `ctx.arc()` circles (dark, radius ~1.5px) offset slightly in the movement direction to give a "looking forward" effect.

**Forked tongue**: Two short `ctx.lineTo()` segments forming a V-shape extending from the front of the head. Use `ctx.strokeStyle` with red color, `ctx.lineWidth = 1`. Animate the tongue by toggling extension length using a frame counter (e.g., extend every 15 frames for a flicker effect). A simple modulo on a global tick counter avoids adding state fields.

### 2. Body Rendering (scale pattern + gradient)

**Gradient along body length**: Compute a color for each segment based on its index relative to total length. Use a linear interpolation from a richer green (near head) to a darker green (near tail). This can be done with simple RGB math -- no need for `createLinearGradient()` per segment.

**Per-segment gradient (3D effect)**: Use `ctx.createRadialGradient()` within each 20x20 cell. Center a lighter color in the middle, darker at edges. This creates a "rounded tube" illusion. Since each gradient object is cheap to create and the snake rarely exceeds 50 segments, this is well within 60fps budget.

**Scale pattern**: Draw 2-3 small `ctx.arc()` or `ctx.ellipse()` shapes per segment in a slightly darker shade to simulate scales. Position them in a staggered pattern (alternating odd/even segments). Each arc is ~3-4px radius, partially overlapping the segment edge. Keep to 2-3 arcs max per segment for performance.

**Segment connection**: Draw segments as circles (radius ~9px) rather than rectangles. Overlapping circles create a smooth, connected body appearance without gaps. This is a common technique in snake games.

### 3. Tail Rendering (taper)

**Taper shape**: Draw the tail segment as a triangle or narrow ellipse pointing away from the previous segment. Use `ctx.beginPath()`, `ctx.moveTo()`, `ctx.lineTo()` to create a pointed shape. The base width matches the body segment width (~16px), tapering to ~2px at the tip.

**Direction calculation**: Compute tail direction from the vector between the last segment and the second-to-last segment. Use `Math.atan2(dy, dx)` for the angle, then rotate+translate like the head.

**Gradient**: Apply the same body gradient scheme but at the darkest end of the spectrum.

### 4. Performance Considerations

- `ctx.save()/restore()` pairs are cheap (~0.01ms each)
- `ctx.createRadialGradient()` is the most expensive call but at <50 segments, total overhead is <1ms per frame
- Avoid creating `new` objects in the draw loop -- reuse color strings via template literals or pre-computed arrays
- A frame counter for tongue animation can use a simple module-level variable incremented in `draw()`, no state changes needed
- Total additional draw calls per frame: ~3-5 per body segment + ~10 for head + ~3 for tail = well under 300 calls for a 50-segment snake

### 5. Recommended Approach

1. Replace the single `roundRect` loop with three specialized functions: `drawSnakeHead()`, `drawSnakeBody()`, `drawSnakeTail()`
2. Use `ctx.translate/rotate` for directional orientation of head and tail
3. Use circular segments with radial gradients for the body
4. Use `ctx.arc()` for eyes and small scale marks
5. Use `ctx.stroke()` lines for the forked tongue with frame-counter animation
6. Add ~6 new color constants to COLORS (eyeWhite, pupil, tongue, scaleLight, scaleDark, tailTip)
