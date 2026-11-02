# Task 1 — Implement the Micro-Civilization Simulator from spec

Write a program (any language) that implements the simulation below **exactly**.
It is run as:

    <your-program> SEED

and must print exactly three lines to stdout:

    <total population of all alive colonies>
    <number of alive colonies>
    <checksum>

after running `T = 300` ticks with the given integer `SEED`.
All arithmetic is on integers. "a // b" is floor division. "a % b" is the
non-negative modulo (Python semantics). Values are unbounded integers except
the PRNG state, which is 64-bit unsigned.

## 1. PRNG

    state = SEED  (as unsigned 64-bit, SEED is 0 <= SEED < 2^32)

    next():
        state = (state * 6364136223846793005 + 1442695040888963407) mod 2^64
        return state

    rand_below(n):          # n >= 1
        return (next() >> 33) % n

There is exactly one global PRNG. Every call to `rand_below` advances it once.
Nothing else advances it. The *order* of calls described below is normative.

## 2. World

- Grid width `W = 12`, height `H = 12`, toroidal (wraps in both axes).
- Coordinates: `x` in `0..W-1` (columns), `y` in `0..H-1` (rows).
- Each cell has `fertility` (0..9) and `resource` (integer >= 0).
- A cell holds at most one colony.

Directions: `0 = North (y-1)`, `1 = East (x+1)`, `2 = South (y+1)`, `3 = West (x-1)`,
with wrap-around.

## 3. Initialisation (in this exact order)

1. For each cell in row-major order (for y in 0..H-1, for x in 0..W-1):
   `fertility = rand_below(10)`, `resource = fertility * 10`.
2. `next_id = 0`.
3. Repeat 4 times:
   `x = rand_below(W)`, then `y = rand_below(H)` (two draws, x first).
   If cell `(x, y)` already has a colony: do nothing more (the draws are still consumed).
   Otherwise create a colony `{id = next_id, x, y, pop = 10, tech = 0}` and `next_id += 1`.

## 4. One tick

Run steps 4.1 and 4.2 in order, `T = 300` times.

### 4.1 Regrowth (no randomness)

For every cell: `resource = min(resource + fertility, fertility * 10)`.

### 4.2 Colony phase

Let `order` be the list of colonies alive **at the start of step 4.2**, sorted by `id`
ascending. Colonies created during this step are **not** in `order` and are not
processed until the next tick. A colony in `order` that was destroyed earlier in the
same step (by conflict) is **skipped**.

For each colony `C` in `order` that is still alive, do the following sub-steps in order:

**(a) Harvest.** `h = min(resource of C's cell, C.pop)`; `resource -= h`.

**(b) Growth.**
- if `h >= C.pop`: `C.pop = C.pop + C.pop // 4 + 1`
- else:           `C.pop = C.pop - (C.pop - h + 1) // 2`

**(c) Tech.** if `C.pop >= 20` and `C.tech < 5`: `C.tech += 1`.

**(d) Migration.** Only if `C.pop > 30 + 10 * C.tech`:
- `d = rand_below(4)`; target cell = C's cell moved one step in direction `d` (wrapping).
- `m = C.pop // 2` (migrants). Compute `m` once, before any change to `C.pop`.
- If the target cell has **no** colony:
  create `{id = next_id, x, y of target, pop = m, tech = C.tech}`, `next_id += 1`,
  and `C.pop -= m`.
- If the target cell has a colony `D` (conflict):
  `a = m + 5 * C.tech + rand_below(10)` (attacker roll drawn **first**),
  `b = D.pop + 5 * D.tech + rand_below(10)` (defender roll drawn **second**).
  - if `a > b`: `D` is destroyed (removed from the world). Then create a new colony
    on that cell `{id = next_id, pop = m, tech = C.tech}`, `next_id += 1`, and `C.pop -= m`.
  - else: `C.pop -= m` (the migrants are lost; nothing is created; `D` is unchanged).

**(e) Death.** if `C.pop <= 0`: `C` is removed from the world.

(A colony created in (d) is never processed in the same tick, even if its `id` is larger.)

## 5. Output after T ticks

    line 1: sum of pop over alive colonies
    line 2: number of alive colonies
    line 3: checksum = ( sum over all cells of resource * (x + 1) * (y + 1)
                        + sum over alive colonies of pop * (id + 1) + tech * 1000 * (id + 1)
                      ) mod 1000003

Numbers only, no extra text, newline-terminated.

## Public test vectors

See `task1_expected_public.json` (seeds 1, 2, 3). The checker also uses hidden seeds,
so hard-coding outputs will not pass.

## Checking

    python3 task1_check.py path/to/your_program   # must be executable, or pass "python3 file.py"

A pass is 3/3 public seeds AND all hidden seeds matching, byte-for-byte.
