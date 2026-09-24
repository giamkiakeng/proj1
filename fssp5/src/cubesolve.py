#!/usr/bin/env python3
"""
cubesolve.py -- solve MT(k,N) restricted to cubes (partial rule tables).

A cube line looks like   a *GL=L GL*=G ...   (entries l c r = value).
Each worker loads the formula once into an incremental solver and solves
the cubes of its share under assumptions, logging one line per cube.

usage: cubesolve.py k N cubefile part nparts logfile [--solver cd19|g4|...]
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def code(k, ch):
    if ch == '*':
        return gencnf.BND
    if ch == 'L':
        return 0
    if ch == 'G':
        return 1
    if ch == 'F':
        return k - 1
    return 'ABCDEHIJK'.index(ch) + 2


def cube_lits(E, k, line):
    lits = []
    for tok in line.split()[1:]:
        e, v = tok.split('=')
        l, c, r = (code(k, ch) for ch in e)
        lits.append(E.T[(l, c, r)][code(k, v)])
    return lits


def main():
    k, N = int(sys.argv[1]), int(sys.argv[2])
    cubefile, part, nparts, log = sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    name = 'cd19'
    if '--solver' in sys.argv:
        name = sys.argv[sys.argv.index('--solver') + 1]
    E = gencnf.build(k, N)
    cubes = [ln.strip() for ln in open(cubefile) if ln.startswith('a')]
    mine = [(j, c) for j, c in enumerate(cubes) if j % nparts == part]
    s = Solver(name=name, bootstrap_with=E.clauses)
    with open(log, 'a') as fh:
        for j, cube in mine:
            t0 = time.time()
            res = s.solve(assumptions=cube_lits(E, k, cube))
            dt = time.time() - t0
            fh.write("%d %s %.2f\n" % (j, 'SAT' if res else 'UNSAT', dt))
            fh.flush()
            if res:
                model = set(v for v in s.get_model() if v > 0)
                out = log + '.rule%d' % j
                with open(out, 'w') as rf:
                    gencnf.decode(E, model, rf)
                r = subprocess.run([os.path.join(HERE, 'fsspcheck'), out, '2', '400'],
                                   capture_output=True, text=True)
                fh.write("  rule %s: %s\n" % (out, r.stdout.strip()))
                fh.flush()


if __name__ == '__main__':
    main()
