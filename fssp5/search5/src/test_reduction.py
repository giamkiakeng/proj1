#!/usr/bin/env python3
"""test_reduction.py N0 COUNT -- empirical test of the reduction used for the length 15 (README, Section 6).

Claim, for any N0: a rule with (B1) (normal form: F only from GGG, *GG, GG*; delta(G,L,L) = A) that synchronizes the
lines 2..N0+1 satisfies the formula F_N0 (lines 2..N0 with the consequences of the lines N0+1 and N0+2), or its
half-line has a G on the anti-diagonal 2*N0-1 at a cell 3 <= i <= N0-1.
Test: COUNT models of the strict formula of the lines 2..N0+1 with (B1) are enumerated (blocking the used transitions);
for each one, F_N0 with the whole table fixed is solved, and the anti-diagonal 2*N0-1 of the line N0+1 is inspected.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, NAMES, BND
from simlib import sim, ok
from pysat.solvers import Solver
N0 = int(sys.argv[1]); COUNT = int(sys.argv[2])
code = {NAMES[x]: x for x in range(4)}; code['*'] = BND; code['F'] = 4
nm = lambda s: '*' if s == BND else ('F' if s == 4 else NAMES[s])
MS = Model(5, N0 + 1, copy=False, sym=False, strict=True, b1s=True, b3=True)
ES = MS.E
S = Solver(name='cadical153')
for c in ES.cl:
    S.add_clause(c)
S.add_clause([ES.T[(1, 0, 0)][2]])                      # naming: delta(G,L,L) = A
MF = Model(5, N0, copy=False, sym=False, b1s=True, b3=True, nogh=True, wimp=True, wgap=True, front1=True, pump=N0)
EF = MF.E
SF = Solver(name='cadical153')
for c in EF.cl:
    SF.add_clause(c)
stats = {'models': 0, 'F_N0 holds': 0, 'wall on the anti-diagonal': 0, 'both': 0, 'neither': 0}
t0 = time.time()
while stats['models'] < COUNT:
    if not S.solve():
        print('# no further model of the strict formula'); break
    pos = set(v for v in S.get_model() if v > 0)
    tab = {(nm(l), nm(c), nm(r)): nm(next(d for d in range(5) if vs[d] in pos)) for (l, c, r), vs in ES.T.items()}
    assert all(ok(tab, n) for n in range(2, N0 + 2))
    used = set()
    for n in range(2, N0 + 2):
        rows = sim(tab, n)
        for t in range(len(rows) - 1):
            r = ['*'] + rows[t] + ['*']
            for i in range(1, n + 1):
                used.add((r[i - 1], r[i], r[i + 1]))
    S.add_clause([-ES.T[(code[e[0]], code[e[1]], code[e[2]])][code[tab[e]]] for e in used])
    stats['models'] += 1
    # (1) does the rule satisfy F_N0?  all transitions fixed as assumptions
    assum = [EF.T[(code[l], code[c], code[r])][code[d]] for (l, c, r), d in tab.items() if (code[l], code[c], code[r]) in EF.T]
    holds = SF.solve(assumptions=assum)
    # (2) a G on the anti-diagonal 2*N0-1 of the half-line (= the line N0+1 there), cells 3..N0-1?
    rows = sim(tab, N0 + 1)
    m = 2 * N0 - 1
    wall = [i for i in range(3, N0) if rows[m - i][i - 1] == 'G']
    other = [i for i in (2, N0) if m - i >= 0 and rows[m - i][i - 1] in ('G',)] + (['front L'] if rows[N0 - 1][N0 - 1] == 'L' else [])
    key = 'both' if holds and wall else ('F_N0 holds' if holds else ('wall on the anti-diagonal' if wall else 'neither'))
    stats[key] += 1
    if key == 'neither' or other:
        print('COUNTEREXAMPLE or unexpected:', key, other, 'synchronizes', [n for n in range(2, 40) if ok(tab, n)])
print('N0=%d: %s (%.0f s)' % (N0, stats, time.time() - t0))
