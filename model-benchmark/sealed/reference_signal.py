#!/usr/bin/env python3
"""Reference: count length-N strings over an A-letter alphabet containing NONE of the
forbidden patterns as a contiguous substring, modulo 1e9+7.
Method: Aho-Corasick automaton over surviving states + matrix exponentiation.
SEALED — do not show to the model under test."""
import sys
MOD = 1_000_000_007

def solve(A, N, patterns):
    # Build Aho-Corasick trie. Node 0 = root.
    goto = [dict()]
    fail = [0]
    bad = [False]  # node corresponds to end of a forbidden pattern (or inherits one via fail)
    def new_node():
        goto.append(dict()); fail.append(0); bad.append(False); return len(goto)-1
    for p in patterns:
        cur = 0
        for ch in p:
            c = ord(ch) - 97
            if c not in goto[cur]:
                goto[cur][c] = new_node()
            cur = goto[cur][c]
        bad[cur] = True
    # BFS to build fail links and a full transition table `go`
    from collections import deque
    go = [[0]*A for _ in range(len(goto))]
    dq = deque()
    for c in range(A):
        if c in goto[0]:
            v = goto[0][c]; fail[v] = 0; go[0][c] = v; dq.append(v)
        else:
            go[0][c] = 0
    while dq:
        u = dq.popleft()
        if bad[fail[u]]:
            bad[u] = True
        for c in range(A):
            if c in goto[u]:
                v = goto[u][c]; fail[v] = go[fail[u]][c]; go[u][c] = v; dq.append(v)
            else:
                go[u][c] = go[fail[u]][c]
    # Surviving (non-bad) states
    survivors = [i for i in range(len(goto)) if not bad[i]]
    idx = {s:i for i,s in enumerate(survivors)}
    S = len(survivors)
    # Transfer matrix: M[i][j] = #letters taking survivor i -> survivor j (skipping bad targets)
    M = [[0]*S for _ in range(S)]
    for s in survivors:
        i = idx[s]
        for c in range(A):
            t = go[s][c]
            if not bad[t]:
                M[i][idx[t]] += 1
    # vector v = e_root ; answer = sum of (v * M^N)
    def matmul(X, Y):
        n=len(X); m=len(Y[0]); k=len(Y)
        Z=[[0]*m for _ in range(n)]
        for a in range(n):
            Xa=X[a]; Za=Z[a]
            for b in range(k):
                x=Xa[b]
                if x:
                    Yb=Y[b]
                    for d in range(m):
                        Za[d]=(Za[d]+x*Yb[d])%MOD
        return Z
    # exponentiate M^N applied to row vector (root)
    vec=[[0]*S]; vec[0][idx[0]]=1
    base=M; e=N
    while e>0:
        if e&1:
            vec=matmul(vec, base)
        e>>=1
        if e>0:
            base=matmul(base, base)
    return sum(vec[0])%MOD

def brute(A, N, patterns):
    # O(A^N) direct count, only for tiny N — used to validate the reference.
    import itertools
    cnt=0
    for tup in itertools.product(range(A), repeat=N):
        s=''.join(chr(97+c) for c in tup)
        if not any(p in s for p in patterns):
            cnt+=1
    return cnt%MOD

def main():
    data=sys.stdin.read().split('\n')
    first=data[0].split()
    A=int(first[0]); F=int(first[1]); N=int(first[2])
    pats=[data[1+i].strip() for i in range(F)]
    pats=[p for p in pats if p!='']
    print(solve(A,N,pats))

if __name__=='__main__':
    main()
