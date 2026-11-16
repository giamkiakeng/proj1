#!/usr/bin/env python3
"""near2.py -- is there a rule for the lengths 2..N that differs from a given rule in at most D of the transitions
that the given rule uses in the lines 2..NB?  (The other entries of the table are free.)  The formula is the strict
formula of mcopy.py for the lines 2..N (nothing that uses a longer line), without any class.
usage: near2.py BASE.txt NB N D [--time SEC] [--solver kissat] [--out FILE]"""
import argparse, os, sys, time, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, BND, NAMES, run_solver
from simlib import load, ok, sim
from pysat.card import CardEnc, EncType

ap = argparse.ArgumentParser()
ap.add_argument('base'); ap.add_argument('NB', type=int); ap.add_argument('N', type=int); ap.add_argument('D', type=int)
ap.add_argument('--time', type=int, default=600); ap.add_argument('--solver', default='kissat'); ap.add_argument('--out')
a = ap.parse_args()
k, base = load(a.base)
used = set()
for n in range(2, a.NB + 1):
    rows = sim(base, n)
    assert len(rows) - 1 == 2 * n - 2 and set(rows[-1]) == {'F'}, 'the base rule does not synchronize %d' % n
    for t in range(len(rows) - 1):
        r = ['*'] + rows[t] + ['*']
        for i in range(1, n + 1):
            used.add((r[i - 1], r[i], r[i + 1]))
M = Model(k, a.N, copy=False, sym=False, strict=True)
E = M.E
code = {NAMES[s]: s for s in range(k - 1)}; code['F'] = k - 1; code['*'] = BND
ch = [-E.T[(code[l], code[c], code[r])][code[base[(l, c, r)]]] for (l, c, r) in sorted(used) if (l, c, r) not in (('L', 'L', 'L'), ('L', 'L', '*'))]
enc = CardEnc.atmost(lits=ch, bound=a.D, top_id=E.nv, encoding=EncType.seqcounter)
for cl in enc.clauses:
    E.add(cl)
E.nv = max(E.nv, enc.nv)
cnf = os.path.join(tempfile.gettempdir() if not os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cnf')) else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cnf'), 'near2_%d_%d_%d.cnf' % (a.N, a.D, os.getpid()))
M.write(cnf)
t1 = time.time()
status, model = run_solver(a.solver, cnf, a.time)
os.remove(cnf)
msg = '%s: %d transitions used in 2..%d; N=%d D=%d: %s (%.1f s)' % (os.path.basename(a.base), len(used), a.NB, a.N, a.D, status, time.time() - t1)
if status == 'SATISFIABLE':
    tab = M.table(model)
    good = [n for n in range(2, 4 * a.N) if ok(tab, n)]
    diff = sum(1 for e in used if tab.get(e) != base[e])
    msg += '  %d used transitions changed, synchronizes %s' % (diff, good)
    if a.out:
        with open(a.out, 'w') as f:
            f.write('# near2.py %s\nk %d\n' % (' '.join(sys.argv[1:]), k))
            for (l, c, r), d in tab.items():
                f.write('%s %s %s %s\n' % (l, c, r, d))
print(msg, flush=True)
