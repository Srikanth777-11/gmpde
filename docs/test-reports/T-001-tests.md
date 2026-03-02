# Test Report: Automated Unit Tests

**Phase:** 6 — Testing
**Date:** 2026-03-02
**Test File:** game/tests.html

## Test Coverage

| Function | Tests | Coverage Notes |
|----------|-------|---------------|
| `getSpeed()` | 8 tests | All 4 tiers tested + boundary values |
| `checkCollision()` | 9 tests | All 4 walls, boundary edges, self-collision, empty space |
| `spawnFood()` | 4 tests | Valid range, not-on-snake (1-seg), not-on-snake (10-seg) |
| `init()` | 10 tests | Score reset, highScore preserved, gameOver/paused reset, snake position/length, direction, speed |
| Direction buffer | 4 tests | 180-degree rejection (right->left, down->up), perpendicular acceptance (right->up, down->left) |
| `update()` | 5 tests | Movement (head position, length), eating (growth, score), game over on wall collision |

**Total: 40 tests across 6 function groups.**

## How to Run
Open `game/tests.html` in any browser. Results display inline with PASS/FAIL indicators and a summary count. Console also logs `TEST RESULTS: N/N passed`.

## Limitations
- Tests run in the browser (not Node.js) because game.js depends on DOM elements (canvas, overlays)
- Rendering (`draw()`) is not tested programmatically -- covered by manual visual QA
- Window resize behavior is not tested -- covered by manual QA
