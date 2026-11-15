#!/usr/bin/env python3
"""germscan.py -- for each half-line germ of a list: up to which length can a k-state rule with this germ
synchronize all lines 2..n in minimal time?

One incremental solver serves all germs.  The clauses that the line n needs are guarded by an activation
literal act[n] (n > n0); a germ is passed as assumptions on the table variables, so the clauses learnt for
one germ remain valid for the others.

usage: germscan.py GERMFILE N [--n0 8] [--budget CONFLICTS] [--solver cadical153] [--first I] [--last J]
                   [--out PREFIX] [--k 5]
GERMFILE: one germ per line, 'GERM xyz>d xyz>d ...' (output of germdfs).
Output: one line per germ: index, complexity, largest n found satisfiable, and how the scan of the germ ended
(UNSAT at n / budget at n / SAT at N); rules that reach N are written to PREFIX_<index>.txt.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, NAMES, BND
from simlib import ok
from pysat.solvers import Solver

ap = argparse.ArgumentParser()
ap.add_argument('germfile'); ap.add_argument('N', type=int)
ap.add_argument('--k', type=int, default=5); ap.add_argument('--n0', type=int, default=8)
ap.add_argument('--budget', type=int, default=20000); ap.add_argument('--solver', default='cadical153')
ap.add_argument('--first', type=int, default=0); ap.add_argument('--last', type=int, default=10 ** 9)
ap.add_argument('--out', default=None); ap.add_argument('--quiet', action='store_true')
ap.add_argument('--show', type=int, default=99, help='with --quiet: still print the germs that reach this length')
for f in ('b1s', 'b3', 'nogh', 'wimp', 'wgap'):
    ap.add_argument('--' + f, action='store_true')
ap.add_argument('--early', type=int, nargs=2, metavar=('N2', 'T'))
ap.add_argument('--extra', default=''); ap.add_argument('--pump', type=int, default=0)
ap.add_argument('--stop', type=int, default=0, help='stop a germ at the first satisfiable length >= STOP (cube mode)')
a = ap.parse_args()
k = a.k
M = Model(k, a.N, copy=False, sym=False, b1s=a.b1s, b3=a.b3, nogh=a.nogh, wimp=a.wimp, wgap=a.wgap,
          early=tuple(a.early) if a.early else None, extra=[int(x) for x in a.extra.split(',') if x], pump=a.pump)
E = M.E
code = {NAMES[x]: x for x in range(k - 1)}
code['F'] = k - 1
code['*'] = BND
act = {}
S = Solver(name=a.solver)
nv = E.nv
for c, l in zip(E.cl, E.lev):
    if l <= a.n0:
        S.add_clause(c)
    else:
        if l not in act:
            nv += 1
            act[l] = nv
        S.add_clause(c + [-act[l]])
germs = [l.split()[1:] for l in open(a.germfile) if l.startswith('GERM')]
print('# %d germs, k=%d, lines 2..%d (unguarded up to %d), budget %d conflicts per call, %d variables, %d clauses' % (
    len(germs), k, a.N, a.n0, a.budget, nv, len(E.cl)), flush=True)
t0 = time.time()
stat = {}
for gi, g in enumerate(germs):
    if gi < a.first or gi > a.last:
        continue
    lits = []
    for tr in g:
        lcr, d = tr.split('>')
        lits.append(E.T[(code[lcr[0]], code[lcr[1]], code[lcr[2]])][code[d]])
    best, end = 0, None
    t1 = time.time()
    for n in range(a.n0, a.N + 1):
        S.conf_budget(a.budget)
        r = S.solve_limited(assumptions=lits + [act[m] for m in range(a.n0 + 1, n + 1)])
        if r is True:
            best = n
            if a.out and n >= a.show and n < a.N:
                tabm = M.table(S.get_model())
                with open('%s_%d_n%d.txt' % (a.out, gi, n), 'w') as f:
                    f.write('# germscan.py %s (germ %d, lines 2..%d)\nk %d\n' % (' '.join(sys.argv[1:]), gi, n, k))
                    for (l, c, rr), d in tabm.items():
                        f.write('%s %s %s %s\n' % (l, c, rr, d))
            if n == a.N:
                end = 'SAT at %d' % n
                tab = M.table(S.get_model())
                good = [x for x in range(2, 3 * a.N) if ok(tab, x)]
                end += ' synchronizes %s' % good
                if a.out:
                    with open('%s_%d.txt' % (a.out, gi), 'w') as f:
                        f.write('# germscan.py %s (germ %d)\nk %d\n' % (' '.join(sys.argv[1:]), gi, k))
                        for (l, c, rr), d in tab.items():
                            f.write('%s %s %s %s\n' % (l, c, rr, d))
        elif r is False:
            end = 'UNSAT at %d' % n
            break
        else:
            end = 'budget at %d' % n
            break
    key = end.split(' synchronizes')[0]
    stat[key] = stat.get(key, 0) + 1
    if not a.quiet or not end.startswith('UNSAT') or best >= a.show:
        print('%d c=%d best=%d %s (%.1f s)' % (gi, len(g), best, end, time.time() - t1), flush=True)
print('# done in %.0f s: %s' % (time.time() - t0, ', '.join('%s: %d' % kv for kv in sorted(stat.items()))), flush=True)
