#!/usr/bin/env python3
"""germdfs_check.py -- independent re-implementation of germdfs.c (slow; for
cross-checking small complexity bounds).

Enumerates the half-line germs below anti-diagonal M with at most K
neighbourhoods besides (L,L,L) that never fire, never put L at the front and
satisfy PUMP(n,n') for 4 <= n < n' <= NP, with auxiliary states introduced in
increasing order along the anti-diagonal order of the cells.  The pumping
cones are taken from pumping.py (breadth-first search), not hard-coded.

usage: germdfs_check.py K [M] [NP]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pumping  # noqa: E402

sys.setrecursionlimit(100000)
K = int(sys.argv[1])
M = int(sys.argv[2]) if len(sys.argv) > 2 else 78
NP = int(sys.argv[3]) if len(sys.argv) > 3 else 40
WSTATES = ['L', 'G', 'A', 'B']
AUX = ['A', 'B']

# cells in anti-diagonal order, t increasing within an anti-diagonal
ORDER = [(m - i, i) for m in range(2, M + 1) for i in range(m - 1, 0, -1) if i <= (m - i) + 1]
ORDER.sort(key=lambda c: (c[0] + c[1], c[0]))
# pumping checks: after the last cell of anti-diagonal 2n'-2
CONES = {n: pumping.cone(n) for n in range(4, NP)}
CHECK_AFTER = {}
for idx, (t, i) in enumerate(ORDER):
    m = t + i
    if m % 2 == 0 and (m + 2) // 2 <= NP:
        CHECK_AFTER[m] = idx          # last index with this anti-diagonal (overwritten)


def input_cells(n, cone):
    out = []
    for (kk, d) in cone:
        out.append(pumping.input_cell(n, kk, d))
    return out


INPUT = {}
for n2 in range(5, NP + 1):
    for n in range(4, n2):
        INPUT[(n, n2)] = [(pumping.input_cell(n, kk, d), pumping.input_cell(n2, kk, d)) for (kk, d) in CONES[n]]

val = {}
tab = {('L', 'L', 'L'): 'L'}
germs = []
nodes = 0


def cell(t, i):
    if i == 0:
        return '*'
    if t == 0:
        return 'G' if i == 1 else 'L'
    if i > t + 1:
        return 'L'
    return val[(t, i)]


def pump_ok(n2):
    for n in range(4, n2):
        if all(cell(*a) == cell(*b) for (a, b) in INPUT[(n, n2)]):
            return False
    return True


def dfs(idx, used, maxaux):
    global nodes
    nodes += 1
    while idx < len(ORDER):
        t, i = ORDER[idx]
        e = (cell(t - 1, i - 1), cell(t - 1, i), cell(t - 1, i + 1))
        front = (i == t + 1)
        if e in tab:
            v = tab[e]
            if front and v == 'L':
                return
            val[(t, i)] = v
        else:
            if used >= K:
                return
            for v in WSTATES:
                if front and v == 'L':
                    continue
                if v in AUX and AUX.index(v) > maxaux + 1:
                    continue
                tab[e] = v
                val[(t, i)] = v
                nm = max(maxaux, AUX.index(v)) if v in AUX else maxaux
                if after_cell(idx):
                    dfs(idx + 1, used + 1, nm)
                del tab[e]
            return
        if not after_cell(idx):
            return
        idx += 1
    germs.append(sorted((k, v) for k, v in tab.items() if k != ('L', 'L', 'L')))


def after_cell(idx):
    t, i = ORDER[idx]
    m = t + i
    if CHECK_AFTER.get(m) == idx:
        return pump_ok((m + 2) // 2)
    return True


dfs(0, 0, -1)
print("K=%d M=%d NP=%d nodes=%d germs=%d" % (K, M, NP, nodes, len(germs)))
for g in germs:
    print("GERM " + " ".join("%s%s%s>%s" % (e[0], e[1], e[2], v) for e, v in g))
