#!/usr/bin/env python3
"""germinc.py -- incremental completion test for a list of half-line germs.

Same question as germbatch.py (can the fixed half-line transitions be
completed so that every length 2..N synchronizes in minimal time, with the
half-line to anti-diagonal M and the pumping pairs up to M/2?), but the base
formula is loaded once into CaDiCaL (PySAT) and every germ is tested under
assumptions.  Learned clauses are consequences of the base formula alone, so
they remain valid from one germ to the next.  Germs whose status is UNKNOWN
(conflict budget exhausted) are reported as such and must be re-tested.

usage: germinc.py germfile N [M] [conflict_budget]
"""
import os
import sys
import time

from pysat.solvers import Solver

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}


def main():
    germfile, N = sys.argv[1], int(sys.argv[2])
    M = int(sys.argv[3]) if len(sys.argv) > 3 else 78
    budget = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    # symmetry is already broken by the germ enumeration (anti-diagonal order)
    E = gencnf.build(5, N, minf=M, pump=min(40, M // 2), symbreak=False)
    s = Solver(name='cadical195', bootstrap_with=E.clauses)
    stats = {}
    for j, ln in enumerate(open(germfile)):
        if not ln.startswith('GERM'):
            continue
        assum = []
        for tok in ln.split()[1:]:
            e, d = tok.split('>')
            assum.append(E.T[tuple(CODE[x] for x in e)][CODE[d]])
        t0 = time.time()
        if budget:
            s.conf_budget(budget)
            r = s.solve_limited(assumptions=assum)
        else:
            r = s.solve(assumptions=assum)
        res = {True: 'SATISFIABLE', False: 'UNSATISFIABLE', None: 'UNKNOWN'}[r]
        stats[res] = stats.get(res, 0) + 1
        print("%d %s %.2f %s" % (j, res, time.time() - t0, ln.strip()))
        sys.stdout.flush()
    print("SUMMARY", stats)


if __name__ == '__main__':
    main()
