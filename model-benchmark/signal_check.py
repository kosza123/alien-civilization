#!/usr/bin/env python3
"""Checker for the Alien Signal Strings benchmark.
Usage: python3 signal_check.py "<command to run the candidate program>"
The command receives the test on stdin and must print one integer on stdout."""
import sys, json, subprocess, shlex, os

HERE = os.path.dirname(os.path.abspath(__file__))

def load(path):
    with open(path) as f:
        return json.load(f)

def run_case(cmd, case):
    stdin = f"{case['A']} {len(case['patterns'])} {case['N']}\n" + "".join(p + "\n" for p in case['patterns'])
    try:
        out = subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT (>30s)"
    txt = out.stdout.strip()
    if not txt:
        return None, "no output / stderr: " + out.stderr.strip()[:200]
    try:
        return int(txt.split()[0]), None
    except ValueError:
        return None, "non-integer output: " + txt[:80]

def main():
    if len(sys.argv) < 2:
        print("usage: python3 signal_check.py \"<run command>\"")
        sys.exit(2)
    cmd = shlex.split(sys.argv[1])
    public = load(os.path.join(HERE, "signal_expected_public.json"))
    hidden_path = os.path.join(HERE, "sealed", "signal_expected_hidden.json")
    hidden = load(hidden_path) if os.path.exists(hidden_path) else []
    total = 0; passed = 0
    for label, cases in (("public", public), ("hidden", hidden)):
        for i, case in enumerate(cases):
            total += 1
            got, err = run_case(cmd, case)
            exp = case["answer"]
            if err:
                print(f"[{label} {i}] ERROR: {err}")
            elif got == exp:
                passed += 1
                print(f"[{label} {i}] OK   (N={case['N']}, A={case['A']}, F={len(case['patterns'])})")
            else:
                print(f"[{label} {i}] WRONG: got {got}, expected {exp}  (N={case['N']}, patterns={case['patterns']})")
    print(f"\n{passed}/{total} cases passed.", "PASS" if passed == total and total > 0 else "FAIL")
    sys.exit(0 if passed == total and total > 0 else 1)

if __name__ == "__main__":
    main()
