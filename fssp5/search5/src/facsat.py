#!/usr/bin/env python3
"""
facsat.py -- is some k-state rule a local image (factor) of a given minimal-time solution M?

    c_n(t, i) = pi( window of M_n around (t, i) ),   window = cells i-r..i+r at time t
                                                      (and, with --past q, cells i-q..i+q at time t-1)
The image diagrams must be the diagrams of ONE k-state rule delta with c_n(0, .) = G L ... L that puts every
cell in state F at time 2n-2 and not before.  The constraints only depend on which windows occur next to each
other, so they are collected once from the lines n0..N of the target; if every such configuration of the target
has been seen, a solution is a k-state minimal-time solution for every length that the target synchronizes,
and unsatisfiability means that no such image exists.

usage: facsat.py K N R [--past Q] [--target mazoyer6.txt] [--n0 3] [--time SEC] [--solver kissat]
"""
import argparse, itertools, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simlib import load, sim, ok
from mcopy import run_solver, NAMES

ap = argparse.ArgumentParser()
ap.add_argument('k', type=int); ap.add_argument('N', type=int); ap.add_argument('r', type=int)
ap.add_argument('--past', type=int, default=-1); ap.add_argument('--target', default='mazoyer6.txt')
ap.add_argument('--n0', type=int, default=3); ap.add_argument('--time', type=int, default=3000)
ap.add_argument('--solver', default='kissat'); ap.add_argument('--out'); ap.add_argument('--cnf')
ap.add_argument('--lrat', action='store_true')
a = ap.parse_args()
kt, ttab = load(a.target)
k, W, F = a.k, list(range(a.k - 1)), a.k - 1
r, q = a.r, a.past

wid = {}
def window(rows, n, t, i):
    w = tuple(rows[t][j - 1] if 1 <= j <= n else '*' for j in range(i - r, i + r + 1))
    if q >= 0:
        w += ('|',) + (tuple(rows[t - 1][j - 1] if 1 <= j <= n else '*' for j in range(i - q, i + q + 1)) if t >= 1 else ('^',) * (2 * q + 1))
    return wid.setdefault(w, len(wid))

cons, init = set(), {}
seen_at = {}
for n in range(a.n0, a.N + 1):
    rows = sim(ttab, n)
    assert len(rows) - 1 == 2 * n - 2 and set(rows[-1]) == {'F'}, n
    before = len(cons)
    ws = [[window(rows, n, t, i) for i in range(1, n + 1)] for t in range(2 * n - 2)]
    for i in range(n):
        v = 1 if i == 0 else 0
        assert init.setdefault(ws[0][i], v) == v
    for t in range(2 * n - 2):
        for i in range(n):
            nb = (ws[t][i - 1] if i >= 1 else '*', ws[t][i], ws[t][i + 1] if i + 1 < n else '*')
            cons.add(nb + (('F',) if t + 1 == 2 * n - 2 else (ws[t + 1][i],)))
    seen_at[n] = len(cons) - before
last_new = max(n for n in seen_at if seen_at[n])
print('lines %d..%d: %d windows, %d distinct constraints; the last new constraint appears at n = %d' % (
    a.n0, a.N, len(wid), len(cons), last_new), flush=True)

nv, cl = 0, []
def new():
    global nv
    nv += 1
    return nv
def exactly_one(vs):
    cl.append(list(vs))
    for x, y in itertools.combinations(vs, 2):
        cl.append([-x, -y])
P = {w: [new() for _ in W] for w in wid.values()}
for vs in P.values():
    exactly_one(vs)
T = {}
side = ['*'] + W
for l in side:
    for c in W:
        for rr in side:
            if l == '*' and rr == '*':
                continue
            T[(l, c, rr)] = [new() for _ in range(k)]
            exactly_one(T[(l, c, rr)])
cl.append([T[(0, 0, 0)][0]])
cl.append([T[(0, 0, '*')][0]])
for w, v in init.items():
    cl.append([P[w][v]])
dom = lambda w: [('*', None)] if w == '*' else [(s, P[w][s]) for s in W]
for (w1, w2, w3, w4) in sorted(cons, key=str):
    for (x, vx), (y, vy), (z, vz) in itertools.product(dom(w1), dom(w2), dom(w3)):
        lits = [-v for v in (vx, vy, vz) if v is not None]
        if w4 == 'F':
            cl.append(lits + [T[(x, y, z)][F]])
        else:
            for d in W:
                cl.append(lits + [-P[w4][d], T[(x, y, z)][d]])
# symmetry: auxiliary values are first used in increasing order along the windows (in order of first occurrence)
order = sorted(wid.values())
for s in range(2, k - 2):
    prev = None
    for w in order:
        if prev is None:
            cl.append([-P[w][s + 1]])
        else:
            cl.append([-P[w][s + 1], prev])
        cur = new()
        cl.append([-cur, P[w][s]] + ([prev] if prev is not None else []))
        prev = cur
print('k=%d radius %d%s: %d variables, %d clauses' % (k, r, '' if q < 0 else ' + past radius %d' % q, nv, len(cl)), flush=True)
import tempfile
cnf = a.cnf or os.path.join(tempfile.gettempdir(), 'fac_%d_%d_%d_%d_%d.cnf' % (k, a.N, r, q, os.getpid()))
with open(cnf, 'w') as f:
    f.write('p cnf %d %d\n' % (nv, len(cl)))
    f.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in cl))
t1 = time.time()
status, model = run_solver(a.solver, cnf, a.time)
print('%s %s (%.1f s)' % (a.solver, status, time.time() - t1), flush=True)
if status == 'SATISFIABLE':
    pos = set(v for v in model if v > 0)
    nm = lambda s: '*' if s == '*' else ('F' if s == F else NAMES[s])
    tab = {(nm(l), nm(c), nm(rr)): nm(next(d for d in range(k) if vs[d] in pos)) for (l, c, rr), vs in T.items()}
    out = a.out or cnf[:-4] + '.rule.txt'
    with open(out, 'w') as f:
        f.write('# facsat.py %s\nk %d\n' % (' '.join(sys.argv[1:]), k))
        for (l, c, rr), d in tab.items():
            f.write('%s %s %s %s\n' % (l, c, rr, d))
    good = [n for n in range(2, 3 * a.N) if ok(tab, n)]
    print('rule written to', out)
    print('pi:', ' '.join('%s>%s' % (''.join(w), NAMES[next(s for s in W if P[i][s] in pos)]) for w, i in sorted(wid.items(), key=lambda x: x[1])))
    print('synchronized lengths up to %d: %s' % (3 * a.N - 1, good))
if not a.cnf:
    os.remove(cnf)
