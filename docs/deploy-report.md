# Deployment Report

**Phase:** 7 — Deployment
**Date:** 2026-03-02
**Status:** DEPLOYED (local)

## Deliverable

```
game/
  index.html    43 lines    1.3 KB   Entry point
  style.css     81 lines    1.5 KB   Styling
  game.js      422 lines   12.0 KB   Game logic
  tests.html   266 lines   10.6 KB   Test suite
  ─────────────────────────────────────────
  Total:       812 lines   25.4 KB
```

## Deployment Verification

| Check | Result |
|-------|--------|
| All files present | 4/4 files in game/ |
| JS syntax valid | node --check passes |
| HTML well-formed | Parser validates OK |
| Zero external dependencies | No http/https refs, no import/require |
| Self-contained directory | game/ has no references outside itself |
| File:// protocol compatible | All paths are relative (style.css, game.js) |

## How to Play

1. Open `game/index.html` in any modern browser (Chrome, Firefox, Safari, Edge)
2. The start screen shows: "Press any arrow key to start"
3. Use arrow keys or WASD to control the snake
4. Eat the red food dots to grow and score points
5. The snake speeds up at scores 5, 10, and 20
6. Avoid hitting walls or your own body
7. Press Space to pause, Enter to restart after game over

## Alternative Deployment Options

- **GitHub Pages:** Push `game/` directory and enable Pages on the repo
- **Static hosting:** Copy `game/` to Netlify, Vercel, S3, or any static file server
- **Local server (optional):** `python3 -m http.server 8000 -d game/` then visit localhost:8000
