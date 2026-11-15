#!/usr/bin/env python3
"""ftime.py -- k-state rules that synchronize the lines 2..N at SOME time (not necessarily minimal).

For every line n the firing time tau(n) is chosen by the solver in [2n-2, tmax(n)], tmax(n) = a*n + b
(--tmax a b), or is fixed to c*n + d with --exact c d.  Requirements: the line starts from G L ... L, no cell
is in state F before tau(n), all cells are in state F at tau(n); delta(L,L,L) = delta(L,L,*) = L.
With --mono, tau(n) < tau(n+1).  A model is re-simulated; the lengths up to --test that it synchronizes
(at any time below --cap times n) are printed with their firing times.

usage: ftime.py K N [--tmax a b | --exact c d] [--mono] [--time SEC] [--solver kissat|cadical] [--out FILE]
"""
import argparse, itertools, os, subprocess, sys, time
ap = argparse.ArgumentParser()
ap.add_argument('k', type=int); ap.add_argument('N', type=int)
ap.add_argument('--tmax', type=int, nargs=2, default=(3, 2)); ap.add_argument('--exact', type=int, nargs=2)
ap.add_argument('--mono', action='store_true'); ap.add_argument('--time', type=int, default=600)
ap.add_argument('--solver', default='kissat'); ap.add_argument('--out'); ap.add_argument('--n0', type=int, default=2)
ap.add_argument('--test', type=int, default=120); ap.add_argument('--cap', type=int, default=8)
ap.add_argument('--lines', default='', help='additional lines, comma-separated')
ap.add_argument('--cnf'); ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args()
k = a.k; W = list(range(k - 1)); F = k - 1; BND = -1
NAMES = 'LGABCDE'[:k - 1] + 'F'
import shutil
nv = 0; cl = []
def new():
    global nv
    nv += 1; return nv
def exactly_one(vs):
    cl.append(list(vs))
    for x, y in itertools.combinations(vs, 2):
        cl.append([-x, -y])
T = {}
side = [BND] + W
for l in side:
    for c in W:
        for r in side:
            if l == BND and r == BND:
                continue
            T[(l, c, r)] = [new() for _ in range(k)]
            exactly_one(T[(l, c, r)])
cl.append([T[(0, 0, 0)][0]]); cl.append([T[(0, 0, BND)][0]])
lines = list(range(a.n0, a.N + 1)) + [int(x) for x in a.lines.split(',') if x]
tau = {}
for n in lines:
    tmin = 2 * n - 2
    tmx = a.exact[0] * n + a.exact[1] if a.exact else max(tmin, a.tmax[0] * n + a.tmax[1])
    if a.exact:
        tmin = tmx
    D = {t: new() for t in range(tmin, tmx + 1)}
    exactly_one(list(D.values()))
    tau[n] = D
    # alive[t]: the line fires at a time > t   (true for t < tmin, false for t >= tmx)
    alive = {}
    for t in range(tmx, -1, -1):
        if t >= tmx:
            alive[t] = False
        elif t < tmin:
            alive[t] = True
        else:
            v = new(); alive[t] = v
            nxt = alive[t + 1]
            # v <-> D[t+1] or alive[t+1]
            cl.append([-v, D[t + 1]] + ([nxt] if nxt is not False else []))
            cl.append([v, -D[t + 1]])
            if nxt is not False:
                cl.append([v, -nxt])
    cells = {}
    def cell(t, i):
        if i < 1 or i > n:
            return BND
        if t == 0:
            return 1 if i == 1 else 0
        if i > t + 1:
            return 0
        if (t, i) not in cells:
            vs = [new() for _ in W]
            exactly_one(vs)
            cells[(t, i)] = vs
        return cells[(t, i)]
    dom = lambda x: [(x, None)] if isinstance(x, int) else [(s, x[s]) for s in W]
    for t in range(0, tmx):
        A = alive[t + 1] if t + 1 <= tmx else False        # fires after t+1: row t+1 is a working row
        B = D.get(t + 1)                                   # fires at t+1
        if A is False and B is None:
            continue
        for i in range(1, n + 1):
            x, y, z = cell(t, i - 1), cell(t, i), cell(t, i + 1)
            nx = cell(t + 1, i) if A is not False else None
            for (al, va), (be, vb), (ga, vc) in itertools.product(dom(x), dom(y), dom(z)):
                lits = [-v for v in (va, vb, vc) if v is not None]
                Te = T[(al, be, ga)]
                if A is not False:
                    pre = lits + ([-A] if A is not True else [])
                    cl.append(pre + [-Te[F]])
                    if isinstance(nx, int):
                        cl.append(pre + [Te[nx]])
                    else:
                        for d in W:
                            cl.append(pre + [-Te[d], nx[d]])
                if B is not None:
                    cl.append(lits + [-B, Te[F]])
if a.mono:
    for n in lines:
        if n + 1 in tau:
            for t1, v1 in tau[n].items():
                for t2, v2 in tau[n + 1].items():
                    if t2 <= t1:
                        cl.append([-v1, -v2])
cnf = a.cnf or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cnf', 'ft_%d_%d_%d.cnf' % (k, a.N, os.getpid()))
os.makedirs(os.path.dirname(cnf), exist_ok=True)
with open(cnf, 'w') as f:
    f.write('p cnf %d %d\n' % (nv, len(cl)))
    f.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in cl))
print('k=%d lines %s: %d variables, %d clauses' % (k, '%d..%d' % (a.n0, a.N) + (',' + a.lines if a.lines else ''), nv, len(cl)), flush=True)
t0 = time.time()
cmd = [os.environ.get('KISSAT') or shutil.which('kissat') or 'kissat', '-q', '--time=%d' % a.time] + (['--seed=%d' % a.seed] if a.seed else []) + [cnf] if a.solver == 'kissat' else [os.environ.get('CADICAL') or shutil.which('cadical') or 'cadical', '-q', '-t', str(a.time), cnf]
r = subprocess.run(cmd, capture_output=True, text=True)
status = [l for l in r.stdout.split('\n') if l.startswith('s ')]
status = status[0][2:] if status else 'UNKNOWN'
print('%s %s (%.1f s)' % (a.solver, status, time.time() - t0), flush=True)
if not a.cnf:
    os.remove(cnf)
if status == 'SATISFIABLE':
    pos = set()
    for l in r.stdout.split('\n'):
        if l.startswith('v '):
            pos.update(int(x) for x in l[2:].split() if int(x) > 0)
    tab = {e: next(d for d in range(k) if vs[d] in pos) for e, vs in T.items()}
    def run(n, cap):
        row = [1] + [0] * (n - 1)
        for t in range(1, cap + 1):
            ext = [BND] + row + [BND]
            row = [tab[(ext[i - 1], ext[i], ext[i + 1])] for i in range(1, n + 1)]
            if F in row:
                return t if all(x == F for x in row) else -t
        return 0
    res = {n: run(n, a.cap * n + 20) for n in range(2, a.test + 1)}
    good = [n for n in res if res[n] > 0]
    print('firing times of the lines of the formula:', ' '.join('%d:%d' % (n, res[n]) for n in lines))
    print('synchronized lengths up to %d (%d): %s' % (a.test, len(good), ' '.join('%d:%d' % (n, res[n]) for n in good)))
    sym = lambda x: '*' if x == BND else NAMES[x]
    if a.out:
        with open(a.out, 'w') as f:
            f.write('# ftime.py %s\nk %d\n' % (' '.join(sys.argv[1:]), k))
            for (l, c, rr), d in tab.items():
                f.write('%s %s %s %s\n' % (sym(l), sym(c), sym(rr), NAMES[d]))
        print('rule written to', a.out)
