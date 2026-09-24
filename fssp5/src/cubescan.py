#!/usr/bin/env python3
"""
cubescan.py -- quick scan of cubes with a conflict budget (incremental CaDiCaL).

usage: cubescan.py k N cubefile budget [gencnf options as key=value: minf=78 pump=40 ...]
Prints one line per cube: index, status (SAT/UNSAT/UNKNOWN), seconds.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402
from cubesolve import cube_lits  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


def main():
    k, N, cubefile, budget = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    opts = {}
    for a in sys.argv[5:]:
        key, v = a.split('=')
        opts[key] = int(v) if key != 'band' else tuple(map(int, v.split(':')))
    E = gencnf.build(k, N, **opts)
    cubes = [ln.strip() for ln in open(cubefile) if ln.startswith('a')]
    s = Solver(name='cd19', bootstrap_with=E.clauses)
    for j, cube in enumerate(cubes):
        t0 = time.time()
        s.conf_budget(budget)
        r = s.solve_limited(assumptions=cube_lits(E, k, cube))
        st = {True: 'SAT', False: 'UNSAT', None: 'UNKNOWN'}[r]
        print("%d %s %.1f %s" % (j, st, time.time() - t0, cube))
        sys.stdout.flush()


if __name__ == '__main__':
    main()
