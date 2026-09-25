#!/usr/bin/env python3
"""cnfcubes.py -- solve a DIMACS formula cube by cube (cube-and-conquer).

The formula is loaded once into an incremental CaDiCaL (PySAT); the cubes of
this worker's share (cube j with j % nparts == part) are solved under
assumptions, each with an optional conflict budget.  One line per cube:
"<j> SAT|UNSAT|UNKNOWN <seconds>"; on SAT the model is written to
<log>.model<j>.  The cubes produced by march_cu cover all assignments not
refuted during cubing, so the formula is unsatisfiable iff every cube is.

Cubes already decided (SAT/UNSAT) in any *.log file of the log directory are skipped.

A cube with any status in another worker's log is skipped as well (so that
forward and --reverse workers on the same share meet without overlap).

usage: cnfcubes.py formula.cnf cubes.icnf part nparts log [conflict_budget] [--reverse]
"""
import sys
import time

from pysat.formula import CNF
from pysat.solvers import Solver


def main():
    cnf, cubefile, part, nparts, log = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    budget = int(sys.argv[6]) if len(sys.argv) > 6 and not sys.argv[6].startswith('--') else 0
    F = CNF(from_file=cnf)
    cubes = []
    for ln in open(cubefile):
        if ln.startswith('a'):
            cubes.append([int(x) for x in ln.split()[1:] if x != '0'])
    import glob
    import os

    def decided():
        # cubes decided (SAT/UNSAT) or being handled by another worker: any log in the same directory
        out = set()
        for fn in glob.glob(os.path.join(os.path.dirname(os.path.abspath(log)), '*.log')):
            for ln in open(fn):
                t = ln.split()
                if len(t) >= 2 and t[1] in ('SAT', 'UNSAT', 'UNKNOWN') and fn != os.path.abspath(log):
                    out.add(int(t[0]))
                elif len(t) >= 2 and t[1] in ('SAT', 'UNSAT'):
                    out.add(int(t[0]))
        return out
    order = list(enumerate(cubes))
    if '--reverse' in sys.argv:
        order.reverse()
    s = Solver(name='cadical195', bootstrap_with=F.clauses)
    with open(log, 'a') as fh:
        for j, cube in order:
            if j % nparts != part or j in decided():
                continue
            t0 = time.time()
            if budget:
                s.conf_budget(budget)
                r = s.solve_limited(assumptions=cube)
            else:
                r = s.solve(assumptions=cube)
            res = {True: 'SAT', False: 'UNSAT', None: 'UNKNOWN'}[r]
            fh.write("%d %s %.2f\n" % (j, res, time.time() - t0))
            fh.flush()
            if r:
                with open('%s.model%d' % (log, j), 'w') as mf:
                    mf.write(' '.join(map(str, s.get_model())) + '\n')


if __name__ == '__main__':
    main()
