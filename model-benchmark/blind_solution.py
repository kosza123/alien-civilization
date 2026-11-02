#!/usr/bin/env python3
"""Count length-N strings over an A-letter alphabet avoiding all forbidden patterns.

Approach:
  1. Build an Aho-Corasick automaton (goto + fail links, with terminal status
     propagated along fail links) and drop every terminal state.
  2. The number of valid strings of length n is a_n = (number of walks of
     length n from the root in the pruned automaton).  By Cayley-Hamilton this
     sequence satisfies a linear recurrence of order <= S (S = #states).
  3. Compute a_0 .. a_{2S+1} by direct DP (cheap), recover the minimal recurrence
     with Berlekamp-Massey over GF(p), and evaluate a_N with Kitamasa
     (x^N mod characteristic polynomial), O(S^2 log N).
"""
import sys

MOD = 1_000_000_007


def build_automaton(A, patterns):
    goto = [[-1] * A]
    fail = [0]
    term = [False]
    for p in patterns:
        s = 0
        for ch in p:
            c = ord(ch) - 97
            if goto[s][c] == -1:
                goto[s][c] = len(goto)
                goto.append([-1] * A)
                fail.append(0)
                term.append(False)
            s = goto[s][c]
        term[s] = True
    # BFS to fill fail links and complete transitions
    from collections import deque
    q = deque()
    for c in range(A):
        nxt = goto[0][c]
        if nxt == -1:
            goto[0][c] = 0
        else:
            fail[nxt] = 0
            q.append(nxt)
    while q:
        s = q.popleft()
        term[s] = term[s] or term[fail[s]]
        for c in range(A):
            nxt = goto[s][c]
            if nxt == -1:
                goto[s][c] = goto[fail[s]][c]
            else:
                fail[nxt] = goto[fail[s]][c]
                q.append(nxt)
    return goto, term


def sequence_terms(goto, term, A, count):
    """a_0 .. a_{count-1}: number of valid strings of each length."""
    S = len(goto)
    live = [s for s in range(S) if not term[s]]
    # Pre-compute, for each live state, the list of live successors (with multiplicity).
    succ = {}
    for s in live:
        lst = []
        for c in range(A):
            t = goto[s][c]
            if not term[t]:
                lst.append(t)
        succ[s] = lst
    vec = [0] * S
    vec[0] = 1
    out = []
    for _ in range(count):
        out.append(sum(vec) % MOD)
        nv = [0] * S
        for s in live:
            v = vec[s]
            if v:
                for t in succ[s]:
                    nv[t] += v
        vec = [x % MOD for x in nv]
    return out


def berlekamp_massey(seq):
    """Return c = [c_1..c_L] with a_n = sum c_i a_{n-i} (mod p) for n >= L."""
    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1
    for n in range(len(seq)):
        d = seq[n]
        for i in range(1, L + 1):
            d = (d + C[i] * seq[n - i]) % MOD
        if d == 0:
            m += 1
            continue
        T = C[:]
        coef = d * pow(b, MOD - 2, MOD) % MOD
        if len(C) < len(B) + m:
            C.extend([0] * (len(B) + m - len(C)))
        for i in range(len(B)):
            C[i + m] = (C[i + m] - coef * B[i]) % MOD
        if 2 * L <= n:
            L = n + 1 - L
            B = T
            b = d
            m = 1
        else:
            m += 1
    # C[0] = 1, a_n + C[1] a_{n-1} + ... + C[L] a_{n-L} = 0
    return [(-C[i]) % MOD for i in range(1, L + 1)]


def kitamasa(rec, init, n):
    """n-th term of recurrence a_k = sum rec[i-1] * a_{k-i}, given a_0..a_{L-1}."""
    L = len(rec)
    if L == 0:
        return 0
    if n < L:
        return init[n] % MOD

    def mulmod(p, q):
        # polynomial product reduced modulo x^L - rec[0] x^{L-1} - ... - rec[L-1]
        res = [0] * (2 * L - 1)
        for i, pi in enumerate(p):
            if pi:
                for j, qj in enumerate(q):
                    res[i + j] += pi * qj
        for i in range(2 * L - 2, L - 1, -1):
            coef = res[i] % MOD
            if coef:
                for j in range(L):
                    res[i - 1 - j] += coef * rec[j]
        return [x % MOD for x in res[:L]]

    # compute x^n mod charpoly via binary exponentiation
    result = [1] + [0] * (L - 1)
    base = ([0, 1] + [0] * (L - 2)) if L > 1 else [rec[0] % MOD]
    e = n
    while e:
        if e & 1:
            result = mulmod(result, base)
        e >>= 1
        if e:
            base = mulmod(base, base)
    return sum(result[i] * init[i] for i in range(L)) % MOD


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    A = int(data[0])
    F = int(data[1])
    N = int(data[2])
    patterns = data[3:3 + F]

    if N == 0:
        print(1)
        return

    goto, term = build_automaton(A, patterns)
    S = len(goto)
    count = 2 * S + 2
    terms = sequence_terms(goto, term, A, count)
    if N < count:
        print(terms[N] % MOD)
        return
    rec = berlekamp_massey(terms)
    L = len(rec)
    print(kitamasa(rec, terms[:L], N) % MOD)


if __name__ == "__main__":
    main()
