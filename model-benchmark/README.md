# Model Benchmark — a genuinely hard, self-checking challenge

A problem on the hard end of what frontier ("laboratory") models can do, with an
objective checker. Weaker models typically pass the public cases and fail the
hidden ones; that gap is the signal.

## How to run the test on your model

1. Give your model **only** these two files:
   - `task_signal_spec.md`
   - `signal_expected_public.json`
   Ask it to produce a program that reads the described stdin and prints the answer.
2. Save its program (e.g. `your_solution.py`).
3. Grade it:
   ```
   python3 signal_check.py "python3 your_solution.py"
   ```
   The checker runs 3 public + 8 hidden cases. `PASS` requires all of them.

## Why it discriminates

- Hidden cases use `N` up to 10^18 — any per-length loop/DP cannot finish.
  The intended solution needs an Aho-Corasick automaton + matrix exponentiation
  (`O(S^3 log N)`). A demonstrably-correct naive DP passes public and stalls on
  every hidden case.
- Overlapping patterns require correct suffix/fail links and terminal
  propagation; small mistakes give plausible-but-wrong answers on hidden seeds.

## Integrity

- `sealed/` holds the reference solution and hidden answers. Do **not** show
  `sealed/` to the model under test.
- The reference was validated against an independent brute-force counter on 200
  random small instances (`A<=3, N<=7`) before generating any vector.
- Public answers are real but few; hidden seeds prevent hard-coding.

## Files

| File | Purpose |
|------|---------|
| `task_signal_spec.md` | The problem statement (give to the model) |
| `signal_expected_public.json` | 3 public test vectors (give to the model) |
| `signal_check.py` | Grader; runs public + hidden cases |
| `sealed/reference_signal.py` | Reference solution (keep hidden) |
| `sealed/signal_expected_hidden.json` | Hidden answers (keep hidden) |
