#!/usr/bin/env python3
"""check_wwalls_enc.py N RULE... -- each rule (which must synchronize 2..N+2 and lie in the weak class) must satisfy
the formula Model(5, N, b1, b3w, noghw, front1) + weakwalls: its transitions are added as units and the formula is solved."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, NAMES, BND
from simlib import load, ok
from pysat.solvers import Solver
import weakwalls
N = int(sys.argv[1])
M = Model(5, N, copy=False, sym=False, b1=True, b3w=True, noghw=True, front1=True)
n0 = len(M.E.cl)
cnt = weakwalls.add_weak_walls(M, noghw=True)
E = M.E
print('formula: %d clauses, %d of them from weakwalls (%d calls)' % (len(E.cl), len(E.cl) - n0, cnt))
code = {NAMES[x]: x for x in range(4)}; code['*'] = BND; code['F'] = 4
res = {}
for path in sys.argv[2:]:
    k, tab = load(path)
    if not all(ok(tab, n) for n in range(2, N + 3)):
        res['skipped (does not synchronize 2..%d)' % (N + 2)] = res.get('skipped (does not synchronize 2..%d)' % (N + 2), 0) + 1
        continue
    # only the transitions that the lines 2..N+2 use are fixed (the others are free: B1 weak / B3 weak hold on the used ones)
    from simlib import sim
    used = {}
    for n in range(2, N + 3):
        rr = sim(tab, n)
        for t in range(2 * n - 2):
            row = '*' + ''.join(rr[t]) + '*'
            for i in range(1, n + 1):
                used[row[i - 1:i + 2]] = rr[t + 1][i - 1]
    S = Solver(name='cadical153', bootstrap_with=E.cl)
    units = [E.T[(code[e[0]], code[e[1]], code[e[2]])][code[d]] for e, d in used.items()]
    r = S.solve(assumptions=units)
    res['satisfied' if r else 'VIOLATED'] = res.get('satisfied' if r else 'VIOLATED', 0) + 1
    if not r:
        print('VIOLATED by', path)
    S.delete()
print(res)
