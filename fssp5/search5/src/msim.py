#!/usr/bin/env python3
"""
msim.py -- is there a k-state rule whose diagrams decode, cell by cell, to the diagrams of a given solution
(Mazoyer's six-state rule) through a local decoding map?

  decoder R:  M(t,i) = phi(c(t,i), c(t,i+1))        L:  phi(c(t,i-1), c(t,i))
          T:  phi(c(t-1,i), c(t,i))                  3:  phi(c(t,i-1), c(t,i), c(t,i+1))
for all lines n0 <= n <= N and all cells before the firing time; the k-state rule must fire every line at 2n-2
(lengths nmin..N).  usage: msim.py K N DEC [--target mazoyer6.txt] [--n0 3] [--nmin 2] [--time SEC]
"""
import argparse, itertools, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, BND, NAMES, run_solver
from simlib import load, sim, ok

ap = argparse.ArgumentParser()
ap.add_argument('k', type=int); ap.add_argument('N', type=int); ap.add_argument('dec')
ap.add_argument('--target', default='mazoyer6.txt'); ap.add_argument('--n0', type=int, default=3)
ap.add_argument('--nmin', type=int, default=2); ap.add_argument('--time', type=int, default=600)
ap.add_argument('--solver', default='kissat'); ap.add_argument('--out')
ap.add_argument('--keepL', action='store_true'); ap.add_argument('--keepG', action='store_true')
ap.add_argument('--keepL1', action='store_true', help='target blank => cell blank')
ap.add_argument('--nodec', action='store_true', help='no decoding constraints (only the preservation constraints)')
ap.add_argument('--keepL2', action='store_true', help='cell blank => target blank')
a = ap.parse_args()
kt, ttab = load(a.target)
tcode = {NAMES[s]: s for s in range(kt - 1)}
M = Model(a.k, a.N, copy=False, nmin=a.nmin, sym=False)
E = M.E
W = E.W
dom = [BND] + W
arity = 3 if a.dec == '3' else 2
phi = {}
def PHI(key):
    if key not in phi:
        phi[key] = [E.new() for _ in range(kt - 1)]
        E.exactly_one(phi[key])
    return phi[key]
def lits(x):
    return [(x, None)] if isinstance(x, int) else [(s, x[s]) for s in W]
ncon = 0
for n in range(a.n0, a.N + 1):
    rows = sim(ttab, n)
    assert len(rows) - 1 == 2 * n - 2 and set(rows[-1]) == {'F'}, n
    for t in range(0, 2 * n - 2):
        for i in range(1, n + 1):
            tgt = tcode[rows[t][i - 1]]
            x = M.cell(n, t, i)
            if not isinstance(x, int):
                if a.keepL or (a.keepL1 and tgt == 0) or (a.keepL2 and tgt != 0):
                    E.add([x[0]] if tgt == 0 else [-x[0]])
                if a.keepG:
                    E.add([x[1]] if tgt == 1 else [-x[1]])
            if a.dec == 'R':
                cs = [M.cell(n, t, i), M.cell(n, t, i + 1)]
            elif a.dec == 'L':
                cs = [M.cell(n, t, i - 1), M.cell(n, t, i)]
            elif a.dec == 'T':
                if t == 0:
                    continue
                cs = [M.cell(n, t - 1, i), M.cell(n, t, i)]
            elif a.dec == '5':
                cs = [M.cell(n, t, i + q) if 1 <= i + q <= n else BND for q in (-2, -1, 0, 1, 2)]
            else:
                cs = [M.cell(n, t, i - 1), M.cell(n, t, i), M.cell(n, t, i + 1)]
            if a.nodec:
                continue
            for combo in itertools.product(*[lits(c) for c in cs]):
                E.add([-v for _, v in combo if v is not None] + [PHI(tuple(s for s, _ in combo))[tgt]])
            ncon += 1
print('k=%d N=%d decoder %s%s%s: %d vars, %d clauses, %d decode constraints, %d phi entries' % (a.k, a.N, a.dec, ' keepL' if a.keepL else (' keepL1' if a.keepL1 else (' keepL2' if a.keepL2 else '')), ' keepG' if a.keepG else '', E.nv, len(E.cl), ncon, len(phi)), flush=True)
import tempfile
cnf = os.path.join(tempfile.gettempdir(), 'sim_%d_%d_%s_%d.cnf' % (a.k, a.N, a.dec, os.getpid()))
M.write(cnf)
t1 = time.time()
status, model = run_solver(a.solver, cnf, a.time)
print('%s %s (%.1f s)' % (a.solver, status, time.time() - t1), flush=True)
if status == 'SATISFIABLE':
    tab = M.table(model)
    out = a.out or cnf[:-4] + '.rule.txt'
    with open(out, 'w') as f:
        f.write('# msim.py %s\nk %d\n' % (' '.join(sys.argv[1:]), a.k))
        for (l, c, r), d in tab.items():
            f.write('%s %s %s %s\n' % (l, c, r, d))
    pos = set(v for v in model if v > 0)
    nm = lambda s: '*' if s == BND else NAMES[s]
    print('phi:', ' '.join('%s>%s' % (''.join(nm(s) for s in key), NAMES[next(d for d in range(kt - 1) if vs[d] in pos)]) for key, vs in sorted(phi.items())))
    print('rule written to', out, '; synchronized lengths up to %d:' % (4 * a.N), [n for n in range(2, 4 * a.N) if ok(tab, n)])
os.remove(cnf)
