#!/usr/bin/env python3
"""mcopy_inc.py -- the formula of mcopy.py solved incrementally: the lines are added one at a time (increasing
length) to one CaDiCaL instance, so that the clauses learnt for the shorter lines are kept.
usage: mcopy_inc.py K N [mcopy options: --a --s0 --mmin --nmin --wake --margin --gstatic --period --ctheta --nocopy]
                    [--from N1] [--time SEC per step]"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model
from simlib import ok
from pysat.solvers import Solver
import threading

ap = argparse.ArgumentParser()
ap.add_argument('k', type=int); ap.add_argument('N', type=int)
ap.add_argument('--a', type=int, default=2); ap.add_argument('--s0', type=int, default=2)
ap.add_argument('--mmin', type=int, default=3); ap.add_argument('--nmin', type=int, default=2)
ap.add_argument('--wake', type=int, default=0); ap.add_argument('--margin', type=int, default=0)
ap.add_argument('--gstatic', type=int); ap.add_argument('--period', type=int, default=0)
ap.add_argument('--ctheta', type=int, default=2); ap.add_argument('--nocopy', action='store_true')
ap.add_argument('--start', type=int, default=0); ap.add_argument('--time', type=int, default=0)
ap.add_argument('--solver', default='cadical153'); ap.add_argument('--out')
a = ap.parse_args()
M = Model(a.k, a.N, a.a, a.s0, a.mmin, a.nmin, not a.nocopy, None, True, True, 99, None, a.wake, a.margin,
          a.gstatic, a.period, a.ctheta)
E = M.E
by = {}
for c, l in zip(E.cl, E.lev):
    by.setdefault(l, []).append(c)
print('%d variables, %d clauses, levels %d..%d' % (E.nv, len(E.cl), min(by), max(by)), flush=True)
S = Solver(name=a.solver)
t0 = time.time()
for l in sorted(by):
    if l < a.nmin:
        for c in by[l]:
            S.add_clause(c)
for n in range(a.nmin, a.N + 1):
    for c in by.get(n, []):
        S.add_clause(c)
    if n < a.start:
        continue
    t1 = time.time()
    res = S.solve()
    print('N=%d: %s  (%.1f s, total %.1f s)' % (n, {True: 'SAT', False: 'UNSAT', None: 'UNKNOWN'}[res], time.time() - t1, time.time() - t0), flush=True)
    if res is False:
        break
    if res is True and (n == a.N or True):
        tab = M.table(S.get_model())
        good = [x for x in range(2, 3 * a.N) if ok(tab, x)]
        print('   model synchronizes', good, flush=True)
        if a.out:
            with open(a.out, 'w') as f:
                f.write('# mcopy_inc.py %s (model at N=%d)\nk %d\n' % (' '.join(sys.argv[1:]), n, a.k))
                for (l, c, r), d in tab.items():
                    f.write('%s %s %s %s\n' % (l, c, r, d))
