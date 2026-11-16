#!/usr/bin/env python3
"""ladder.py K N R [--nob3] [--time SEC] [--solver cadical|kissat] [--out FILE] -- rules that are almost stable-general rules.

Class C_R: (B3) in the strong reading (exactly GGG, *GG, GG* give F; left out with --nob3), and at most R of the
entries delta(x, G, y), where x and y are not both in {G, *}, differ from G.  C_0 is the class of the stable
generals (README, Section 6); for R equal to the number of these entries only (B3) is left.
The formula is the strict formula of the lines 2..N.  Prints the answer and, for a model, the violated entries.
"""
import argparse, os, sys, time, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, BND, NAMES, run_solver
from simlib import ok
from pysat.card import CardEnc, EncType
ap = argparse.ArgumentParser()
ap.add_argument('k', type=int); ap.add_argument('N', type=int); ap.add_argument('R', type=int)
ap.add_argument('--nob3', action='store_true'); ap.add_argument('--time', type=int, default=600)
ap.add_argument('--solver', default='cadical'); ap.add_argument('--out')
ap.add_argument('--free', default='', help='instead of R: these entries delta(x,G,y) are free and all others are G; patterns xGy with ? as a wildcard, comma-separated, e.g. LG?,AGL (R is ignored)')
a = ap.parse_args()
M = Model(a.k, a.N, copy=False, sym=False, strict=True, b3=not a.nob3)
E = M.E
ents = [e for e in E.T if e[1] == 1 and not (e[0] in (1, BND) and e[2] in (1, BND))]
viol = [-E.T[e][1] for e in ents]                       # literal: delta(e) != G
if a.free:
    nm0 = lambda s: '*' if s == BND else NAMES[s]
    pats = a.free.split(',')
    match = lambda e: any(len(q) == 3 and q[1] == 'G' and q[0] in ('?', nm0(e[0])) and q[2] in ('?', nm0(e[2])) for q in pats)
    nfree = 0
    for e in ents:
        if match(e):
            nfree += 1
        else:
            E.add([E.T[e][1]])
    a.R = nfree
elif a.R < len(viol):
    enc = CardEnc.atmost(lits=viol, bound=a.R, top_id=E.nv, encoding=EncType.seqcounter)
    for cl in enc.clauses:
        E.add(cl)
    E.nv = max(E.nv, enc.nv)
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cnf')
cnf = os.path.join(d if os.path.isdir(d) else tempfile.gettempdir(), 'ladder_%d_%d_%d_%d.cnf' % (a.k, a.N, a.R, os.getpid()))
M.write(cnf)
t1 = time.time()
status, model = run_solver(a.solver, cnf, a.time)
os.remove(cnf)
msg = 'k=%d N=%d %s%s: %s (%.1f s)' % (a.k, a.N, ('free %s (%d of %d entries)' % (a.free, a.R, len(ents))) if a.free else ('R=%d of %d' % (a.R, len(ents))), ' without (B3)' if a.nob3 else '', status, time.time() - t1)
if status == 'SATISFIABLE':
    tab = M.table(model)
    nm = lambda s: '*' if s == BND else NAMES[s]
    bad = [nm(e[0]) + 'G' + nm(e[2]) + '>' + tab[(nm(e[0]), 'G', nm(e[2]))] for e in ents if tab[(nm(e[0]), 'G', nm(e[2]))] != 'G']
    good = [n for n in range(2, 4 * a.N) if ok(tab, n)]
    msg += '  violated: %s; synchronizes %s' % (' '.join(bad) if bad else 'none', good)
    if a.out:
        with open(a.out, 'w') as f:
            f.write('# ladder.py %s\nk %d\n' % (' '.join(sys.argv[1:]), a.k))
            for (l, c, r), v in tab.items():
                f.write('%s %s %s %s\n' % (l, c, r, v))
print(msg, flush=True)
