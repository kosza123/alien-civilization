#!/usr/bin/env python3
"""Reference implementation of task1_spec.md. DO NOT show this to the model under test."""
import sys

W, H, T = 12, 12, 300
MASK = (1 << 64) - 1


class Rng:
    def __init__(self, seed):
        self.state = seed & MASK

    def next(self):
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) & MASK
        return self.state

    def below(self, n):
        return (self.next() >> 33) % n


def run(seed):
    rng = Rng(seed)
    fert = [[0] * W for _ in range(H)]
    res = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            f = rng.below(10)
            fert[y][x] = f
            res[y][x] = f * 10
    colonies = {}          # id -> dict
    occ = {}               # (x,y) -> id
    next_id = 0
    for _ in range(4):
        x = rng.below(W)
        y = rng.below(H)
        if (x, y) in occ:
            continue
        colonies[next_id] = {"id": next_id, "x": x, "y": y, "pop": 10, "tech": 0}
        occ[(x, y)] = next_id
        next_id += 1

    def kill(cid):
        c = colonies.pop(cid)
        del occ[(c["x"], c["y"])]

    for _ in range(T):
        for y in range(H):
            for x in range(W):
                res[y][x] = min(res[y][x] + fert[y][x], fert[y][x] * 10)
        order = sorted(colonies)
        for cid in order:
            if cid not in colonies:
                continue
            c = colonies[cid]
            x, y = c["x"], c["y"]
            h = min(res[y][x], c["pop"])
            res[y][x] -= h
            if h >= c["pop"]:
                c["pop"] = c["pop"] + c["pop"] // 4 + 1
            else:
                c["pop"] = c["pop"] - (c["pop"] - h + 1) // 2
            if c["pop"] >= 20 and c["tech"] < 5:
                c["tech"] += 1
            if c["pop"] > 30 + 10 * c["tech"]:
                d = rng.below(4)
                tx, ty = x, y
                if d == 0:
                    ty = (y - 1) % H
                elif d == 1:
                    tx = (x + 1) % W
                elif d == 2:
                    ty = (y + 1) % H
                else:
                    tx = (x - 1) % W
                m = c["pop"] // 2
                if (tx, ty) not in occ:
                    colonies[next_id] = {"id": next_id, "x": tx, "y": ty, "pop": m, "tech": c["tech"]}
                    occ[(tx, ty)] = next_id
                    next_id += 1
                    c["pop"] -= m
                else:
                    dcol = colonies[occ[(tx, ty)]]
                    a = m + 5 * c["tech"] + rng.below(10)
                    b = dcol["pop"] + 5 * dcol["tech"] + rng.below(10)
                    if a > b:
                        kill(dcol["id"])
                        colonies[next_id] = {"id": next_id, "x": tx, "y": ty, "pop": m, "tech": c["tech"]}
                        occ[(tx, ty)] = next_id
                        next_id += 1
                        c["pop"] -= m
                    else:
                        c["pop"] -= m
            if c["pop"] <= 0:
                kill(cid)

    total = sum(c["pop"] for c in colonies.values())
    chk = 0
    for y in range(H):
        for x in range(W):
            chk += res[y][x] * (x + 1) * (y + 1)
    for c in colonies.values():
        chk += c["pop"] * (c["id"] + 1) + c["tech"] * 1000 * (c["id"] + 1)
    return total, len(colonies), chk % 1000003


if __name__ == "__main__":
    t, n, chk = run(int(sys.argv[1]))
    print(t)
    print(n)
    print(chk)
