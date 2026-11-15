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
ap.add_argument('--b3', action='store_true'); ap.add_argument('--b1', action='store_true'); ap.add_argument('--b4', action='store_true')
ap.add_argument('--b2', help='image solutions: id, AB, LA or LB')
ap.add_argument('--early', type=int, nargs=2, metavar=('N2', 'T'))
ap.add_argument('--pump', type=int, default=0)
ap.add_argument('--b1s', action='store_true'); ap.add_argument('--b3w', action='store_true'); ap.add_argument('--nogh', action='store_true')
ap.add_argument('--chains', type=int, nargs=2, metavar=('N3', 'C'))
ap.add_argument('--rfire', type=int, default=0)
ap.add_argument('--rbg', action='store_true')
ap.add_argument('--wimp', action='store_true')
ap.add_argument('--wgap', action='store_true')
ap.add_argument('--strict', action='store_true')
ap.add_argument('--extra', default='')
ap.add_argument('--set', action='append', default=[], metavar='LCR=D', help='fix a transition, e.g. ALL=B or AL*=G')
ap.add_argument('--walls', help='target rule: its static G cells (G at t and t+1) must be G')
ap.add_argument('--blanks', help='target rule: its quiescent cells must be quiescent')
ap.add_argument('--skel0', type=int, default=3, help='first line with skeleton constraints')
a = ap.parse_args()
M = Model(a.k, a.N, a.a, a.s0, a.mmin, a.nmin, not a.nocopy, None, True, True, 99, None, a.wake, a.margin,
          a.gstatic, a.period, a.ctheta, a.b3, a.b1, a.b4, a.b2, tuple(a.early) if a.early else None, a.pump, a.b1s, a.b3w, a.nogh, tuple(a.chains) if a.chains else None, a.rfire, a.rbg, a.wimp, a.wgap, a.strict, [int(x) for x in a.extra.split(',') if x])
E = M.E
from mcopy import NAMES, BND
for spec in a.set:
    code = {NAMES[x]: x for x in range(a.k - 1)}
    code['F'] = a.k - 1
    code['*'] = BND
    lcr, d = spec.split('=')
    E.level = 0
    E.add([E.T[(code[lcr[0]], code[lcr[1]], code[lcr[2]])][code[d]]])
by = {}
for c, l in zip(E.cl, E.lev):
    by.setdefault(l, []).append(c)
if a.walls or a.blanks:
    from simlib import load, sim
    tt = load(a.walls or a.blanks)[1]
    nsk = 0
    for n in range(max(a.skel0, a.nmin), a.N + 1):
        rows = sim(tt, n)
        assert len(rows) - 1 == 2 * n - 2
        for t in range(1, 2 * n - 2):
            for i in range(1, n + 1):
                x = M.cell(n, t, i)
                if isinstance(x, int):
                    continue
                if a.walls and rows[t][i - 1] == 'G' and t + 1 <= 2 * n - 3 and rows[t + 1][i - 1] == 'G':
                    by.setdefault(n, []).append([x[1]]); nsk += 1
                if a.blanks and rows[t][i - 1] == 'L':
                    by.setdefault(n, []).append([x[0]]); nsk += 1
    print('%d skeleton clauses' % nsk, flush=True)
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
