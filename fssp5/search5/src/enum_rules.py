#!/usr/bin/env python3
"""enum_rules.py K N [MAXMODELS] [mcopy class options, e.g. --b3 --b1s] -- all K-state rules for the lines 2..N.

Models of the strict formula of mcopy.py (the lines 2..N are synchronized, nothing else, plus the class options) are
enumerated up to the transitions that a rule uses in these lines: after each model the conjunction of its used
transitions is excluded.  Prints the number of rules and some statistics of their diagrams.
"""
import sys, os, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, NAMES, BND
from simlib import sim, ok
from pysat.solvers import Solver
K, N = int(sys.argv[1]), int(sys.argv[2])
rest = sys.argv[3:]
MAXM = int(rest.pop(0)) if rest and rest[0].isdigit() else 100000
kw = {o[2:]: True for o in rest}
M = Model(K, N, copy=False, sym=False, strict=True, **kw)
E = M.E
S = Solver(name='cadical153')
for c in E.cl:
    S.add_clause(c)
code = {NAMES[x]: x for x in range(K - 1)}; code['*'] = BND; code['F'] = K - 1
nm = lambda s: '*' if s == BND else ('F' if s == K - 1 else NAMES[s])
t0 = time.time(); n = 0
stat = collections.Counter(); longer = collections.Counter(); firing = collections.Counter(); first = collections.Counter(); nused = collections.Counter()
while n < MAXM and S.solve():
    pos = set(v for v in S.get_model() if v > 0)
    tab = {(nm(l), nm(c), nm(r)): nm(next(d for d in range(K) if vs[d] in pos)) for (l, c, r), vs in E.T.items()}
    used = set(); rows8 = None
    for m in range(2, N + 1):
        rows = sim(tab, m)
        assert len(rows) - 1 == 2 * m - 2 and set(rows[-1]) == {'F'}
        for t in range(len(rows) - 1):
            r = ['*'] + rows[t] + ['*']
            for i in range(1, m + 1):
                used.add((r[i - 1], r[i], r[i + 1]))
        if m == N:
            rows8 = rows
    S.add_clause([-E.T[(code[e[0]], code[e[1]], code[e[2]])][code[tab[e]]] for e in used])
    n += 1
    nused[len(used)] += 1
    firing[' '.join(sorted(''.join(e) for e in used if tab[e] == 'F'))] += 1
    first[''.join(r[0] for r in rows8[:-1])] += 1
    stat[''.join(rows8[-2])] += 1
    bad = sorted(''.join(e) for e in used if e[1] == 'G' and not (e[0] in 'G*' and e[2] in 'G*') and tab[e] != 'G')
    longer[len(bad)] += 1
print('k=%d, lines 2..%d%s: %d rules up to unused transitions%s (%.0f s)' % (K, N, ' ' + ' '.join(rest) if rest else '', n, '' if n < MAXM else ' (stopped)', time.time() - t0))
print('  used transitions: %s' % dict(sorted(nused.items())))
print('  firing neighbourhoods: %s' % dict(firing.most_common(8)))
print('  row before firing on the line %d: %s' % (N, dict(stat.most_common(8))))
print('  first cell on the line %d: %s' % (N, dict(first.most_common(6))))
print('  number of used entries (x,G,y) that are not G: %s' % dict(sorted(longer.items())))
