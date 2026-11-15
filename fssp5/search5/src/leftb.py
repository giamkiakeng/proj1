#!/usr/bin/env python3
"""leftb.py -- how long can the input anti-diagonals be periodic at the left border?  (Lemma 4.1 of the paper)

Is there a k-state rule that synchronizes the line of length n at time 2n-2 such that the words
    y -> C(2n-2-y, y)  (s <= y <= Y)      and      y -> C(2n-3-y, y)  (s <= y <= Y-1)
are l-periodic?  Lemma 4.1 says no if Y - s > (k-1)^(2s) l.  Only the line n is required to be synchronized
(the hypothesis of the lemma); with --also n1,n2,... further lines must be synchronized as well.

usage: leftb.py K n s l Y [--also LIST] [--time SEC] [--solver kissat|cadical] [--out FILE]
"""
import argparse, itertools, os, subprocess, sys, time
ap = argparse.ArgumentParser()
ap.add_argument('k', type=int); ap.add_argument('n', type=int); ap.add_argument('s', type=int)
ap.add_argument('l', type=int); ap.add_argument('Y', type=int)
ap.add_argument('--also', default=''); ap.add_argument('--time', type=int, default=600)
ap.add_argument('--solver', default='kissat'); ap.add_argument('--out'); ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args()
k, n, s, l, Y = a.k, a.n, a.s, a.l, a.Y
assert s >= 1 and l >= 1 and s <= Y <= n - s
W = list(range(k - 1)); F = k - 1; BND = -1
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
for L_ in side:
    for c in W:
        for r in side:
            if L_ == BND and r == BND:
                continue
            T[(L_, c, r)] = [new() for _ in range(k)]
            exactly_one(T[(L_, c, r)])
cl.append([T[(0, 0, 0)][0]]); cl.append([T[(0, 0, BND)][0]])
dom = lambda x: [(x, None)] if isinstance(x, int) else [(st, x[st]) for st in W]
def line(m):
    cells = {}
    def cell(t, i):
        if i < 1 or i > m:
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
    for t in range(0, 2 * m - 2):
        for i in range(1, m + 1):
            x, y, z = cell(t, i - 1), cell(t, i), cell(t, i + 1)
            fire = (t + 1 == 2 * m - 2)
            nx = None if fire else cell(t + 1, i)
            for (al, va), (be, vb), (ga, vc) in itertools.product(dom(x), dom(y), dom(z)):
                lits = [-v for v in (va, vb, vc) if v is not None]
                Te = T[(al, be, ga)]
                if fire:
                    cl.append(lits + [Te[F]])
                elif isinstance(nx, int):
                    cl.append(lits + [Te[nx]])
                else:
                    cl.append(lits + [-Te[F]])
                    for d in W:
                        cl.append(lits + [-Te[d], nx[d]])
    return cell
cell = line(n)
def equal(p, q):
    if isinstance(p, int) and isinstance(q, int):
        if p != q:
            cl.append([])
        return
    if isinstance(p, int):
        p, q = q, p
    if isinstance(q, int):
        cl.append([p[q]]); return
    for d in W:
        cl.append([-p[d], q[d]]); cl.append([p[d], -q[d]])
neq = 0
for y in range(s, Y + 1):
    if y + l <= Y:
        equal(cell(2 * n - 2 - y, y), cell(2 * n - 2 - y - l, y + l)); neq += 1
    if y + l <= Y - 1:
        equal(cell(2 * n - 3 - y, y), cell(2 * n - 3 - y - l, y + l)); neq += 1
for m in [int(x) for x in a.also.split(',') if x]:
    line(m)                      # separate cell variables; the same rule
import tempfile
cnf = os.path.join(tempfile.gettempdir(), 'lb_%d_%d_%d_%d_%d_%d.cnf' % (k, n, s, l, Y, os.getpid()))
with open(cnf, 'w') as f:
    f.write('p cnf %d %d\n' % (nv, len(cl)))
    f.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in cl))
t0 = time.time()
cmd = [os.environ.get('KISSAT') or shutil.which('kissat') or 'kissat', '-q', '--time=%d' % a.time] + (['--seed=%d' % a.seed] if a.seed else []) + [cnf] if a.solver == 'kissat' else [os.environ.get('CADICAL') or shutil.which('cadical') or 'cadical', '-q', '-t', str(a.time), cnf]
r = subprocess.run(cmd, capture_output=True, text=True)
os.remove(cnf)
status = [x for x in r.stdout.split('\n') if x.startswith('s ')]
status = status[0][2:] if status else 'UNKNOWN'
bound = (k - 1) ** (2 * s) * l
print('k=%d n=%d s=%d l=%d Y=%d (Y-s=%d, bound of the lemma %d; %d equalities): %d variables, %d clauses: %s (%.1f s)' % (
    k, n, s, l, Y, Y - s, bound, neq, nv, len(cl), status, time.time() - t0), flush=True)
if status == 'SATISFIABLE':
    pos = set()
    for x in r.stdout.split('\n'):
        if x.startswith('v '):
            pos.update(int(z) for z in x[2:].split() if int(z) > 0)
    tab = {e: next(d for d in range(k) if vs[d] in pos) for e, vs in T.items()}
    def run(m):
        rows = [[1] + [0] * (m - 1)]
        for t in range(1, 2 * m - 1):
            ext = [BND] + rows[-1] + [BND]
            row = [tab[(ext[i - 1], ext[i], ext[i + 1])] for i in range(1, m + 1)]
            rows.append(row)
            if F in row:
                break
        return rows
    rows = run(n)
    ok = len(rows) == 2 * n - 1 and all(x == F for x in rows[-1])
    w0 = ''.join(NAMES[rows[2 * n - 2 - y][y - 1]] for y in range(s, Y + 1))
    w1 = ''.join(NAMES[rows[2 * n - 3 - y][y - 1]] for y in range(s, Y))
    per = all(w0[j] == w0[j + l] for j in range(len(w0) - l)) and all(w1[j] == w1[j + l] for j in range(len(w1) - l))
    good = []
    for m in range(2, 3 * n):
        rr = run(m)
        if len(rr) == 2 * m - 1 and all(x == F for x in rr[-1]):
            good.append(m)
    print('   re-simulated: line %d synchronized: %s; input words %s / %s, %d-periodic: %s; lengths synchronized below %d: %s' % (n, ok, w0, w1, l, per, 3 * n, good))
    if a.out:
        sym = lambda x: '*' if x == BND else NAMES[x]
        with open(a.out, 'w') as f:
            f.write('# leftb.py %s\nk %d\n' % (' '.join(sys.argv[1:]), k))
            for (L_, c, rr), d in tab.items():
                f.write('%s %s %s %s\n' % (sym(L_), sym(c), sym(rr), NAMES[d]))
