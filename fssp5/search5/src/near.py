#!/usr/bin/env python3
"""near.py -- rules for the lengths 2..N within Hamming distance D of a given rule table (large-neighbourhood search).
usage: near.py BASE.txt N D [--time SEC] [--half M] [--solver kissat] [--out FILE]"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, BND, NAMES, run_solver
from simlib import load, ok
from pysat.card import CardEnc, EncType

ap = argparse.ArgumentParser()
ap.add_argument('base'); ap.add_argument('N', type=int); ap.add_argument('D', type=int)
ap.add_argument('--time', type=int, default=600); ap.add_argument('--half', type=int)
ap.add_argument('--solver', default='kissat'); ap.add_argument('--out'); ap.add_argument('--nmin', type=int, default=2)
a = ap.parse_args()
k, base = load(a.base)
M = Model(k, a.N, copy=False, nmin=a.nmin, sym=False, half=a.half)
E = M.E
code = {NAMES[s]: s for s in range(k - 1)}; code['F'] = k - 1; code['*'] = BND
used = set()
for n in range(2, 15):
    pass
ch = []
for (l, c, r), d in base.items():
    e = (code[l], code[c], code[r])
    if e in E.T and e not in ((0, 0, 0), (0, 0, BND)):
        ch.append(-E.T[e][code[d]])          # literal "entry changed"
enc = CardEnc.atmost(lits=ch, bound=a.D, top_id=E.nv, encoding=EncType.seqcounter)
for cl in enc.clauses:
    E.add(cl)
E.nv = max(E.nv, enc.nv)
import tempfile
cnf = os.path.join(tempfile.gettempdir(), 'near_%d_%d_%d.cnf' % (a.N, a.D, os.getpid()))
M.write(cnf)
t1 = time.time()
status, model = run_solver(a.solver, cnf, a.time)
os.remove(cnf)
msg = '%s N=%d D=%d: %s (%.1f s)' % (os.path.basename(a.base), a.N, a.D, status, time.time() - t1)
if status == 'SATISFIABLE':
    tab = M.table(model)
    good = [n for n in range(2, 4 * a.N) if ok(tab, n)]
    diff = sum(1 for e, d in base.items() if tab.get(e) != d)
    msg += '  distance %d, synchronizes %s' % (diff, good)
    if a.out:
        with open(a.out, 'w') as f:
            f.write('# near.py %s\nk %d\n' % (' '.join(sys.argv[1:]), k))
            for (l, c, r), d in tab.items():
                f.write('%s %s %s %s\n' % (l, c, r, d))
print(msg, flush=True)
