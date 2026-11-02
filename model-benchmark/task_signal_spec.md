# Hard Benchmark — "Alien Signal Strings"

A fully specified, objectively checkable problem. Give the spec below (and only
`task_signal_spec.md` + `signal_expected_public.json`) to the model under test.
Hidden test answers and the reference solution stay sealed.

## Problem

An alien beacon transmits strings over an alphabet of `A` letters
(`'a'`, `'b'`, …, the first `A` lowercase letters). A string is **valid** if it
contains **none** of `F` forbidden patterns as a contiguous substring.

Count the number of valid strings of length exactly `N`, modulo `1_000_000_007`.

## Input (stdin)

```
A F N
pattern_1
pattern_2
...
pattern_F
```

- `2 <= A <= 26`
- `0 <= F <= 50`
- `0 <= N <= 10^18`      ← N can be astronomically large; you cannot iterate it
- each pattern is a non-empty string of up to 20 letters from the first `A` letters
- total length of all patterns <= 200
- `N = 0` means the empty string (length 0); it is valid iff no pattern is empty
  (patterns are never empty, so the empty string is always valid → answer 1)

## Output

A single integer: the count of valid length-`N` strings, taken `mod 1_000_000_007`.

## Why this is hard

- `N` up to `10^18` rules out any per-length DP or simulation. The intended
  solution recognises this as walks on an automaton and uses **fast matrix
  exponentiation** (O(S^3 log N), S = automaton size).
- Patterns overlap and share prefixes/suffixes, so correctness requires a proper
  **Aho-Corasick** automaton (suffix/fail links and terminal propagation), not a
  naive per-pattern check. Getting the fail links or terminal inheritance slightly
  wrong produces answers that look plausible but are wrong on the hidden seeds.
- Modular arithmetic throughout; off-by-one on `N` (states vs transitions) is a
  classic failure.

A partial solution that only handles small `N` by direct DP will pass the public
cases and fail every hidden case. That is the point.

## Checking

```
python3 signal_check.py "python3 your_solution.py"
# or, for a compiled binary:
python3 signal_check.py ./your_solution
```

Pass = every public AND every hidden case correct, byte-for-byte on the integer.
