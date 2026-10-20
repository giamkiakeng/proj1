#!/usr/bin/env python3
"""icube.py CNF ICNF OUT [budget] [first] [last] [step]
Incremental cube solving: one CaDiCaL (PySAT cd19) instance; each cube is solved under assumptions with a
conflict budget; learned clauses carry over.  OUT gets one line per cube: index result seconds."""
import sys, time
from pysat.formula import CNF
from pysat.solvers import Solver
cnf, icnf, out = sys.argv[1:4]
budget = int(float(sys.argv[4])) if len(sys.argv) > 4 else 100000
first = int(sys.argv[5]) if len(sys.argv) > 5 else 0
last = int(sys.argv[6]) if len(sys.argv) > 6 else 10**9
step = int(sys.argv[7]) if len(sys.argv) > 7 else 1
cubes = [[int(x) for x in l.split()[1:-1]] for l in open(icnf) if l.startswith('a ')]
F = CNF(from_file=cnf)
done = set()
try:
    for l in open(out):
        p = l.split()
        if len(p) >= 2 and p[1] in ('UNSAT', 'SAT'):
            done.add(int(p[0]))
except FileNotFoundError:
    pass
with Solver(name='cd19', bootstrap_with=F.clauses) as s, open(out, 'a') as fo:
    for idx in range(first, min(last, len(cubes)), step):
        if idx in done:
            continue
        t0 = time.time()
        s.conf_budget(budget)
        r = s.solve_limited(assumptions=cubes[idx])
        res = {True: 'SAT', False: 'UNSAT', None: 'UNKNOWN'}[r]
        fo.write('%d %s %.1f\n' % (idx, res, time.time() - t0)); fo.flush()
        if r is True:
            fo.write('# model ' + ' '.join(str(x) for x in s.get_model() if x > 0) + '\n'); fo.flush()
