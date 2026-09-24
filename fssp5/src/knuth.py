#!/usr/bin/env python3
"""
knuth.py -- Knuth's random-probe estimate of a look-ahead search tree.

Tree: transitions of the half-line are fixed in order of first use when the
half-line is evaluated anti-diagonal by anti-diagonal (as in fsspdfs.c);
a node is pruned when the full formula F (lengths 2..N, half-line to M,
pumping, links) with the node's partial table as assumptions is refuted by
the SAT solver within a conflict budget.  A probe walks from the root to a
leaf (pruned node or fully evaluated half-line), choosing a uniformly random
surviving child; the product of the numbers of surviving children is an
unbiased estimator of the number of leaves (and partial products estimate
the number of nodes per level).

usage: knuth.py N M probes budget [seed]
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

BND = gencnf.BND


def main():
    N, M, probes, budget = map(int, sys.argv[1:5])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    rnd = random.Random(seed)
    E = gencnf.build(5, N, minf=M, pump=min(40, M // 2), links=True)
    s = Solver(name='cd19', bootstrap_with=E.clauses)
    W = [0, 1, 2, 3]
    # evaluation order of half-line cells: anti-diagonals
    cells = []
    for m in range(2, M + 1):
        for t in range(1, m):
            i = m - t
            if 1 <= i <= t + 1:
                cells.append((t, i))
    est_levels = {}
    t0 = time.time()
    for p in range(probes):
        tab = {(0, 0, 0): 0}
        val = {}

        def v(t, i):
            if i == 0:
                return BND
            if t == 0:
                return 1 if i == 1 else 0
            if i > t + 1:
                return 0
            return val[(t, i)]
        weight = 1.0
        depth = 0
        assum = []
        leaf = 'complete'
        for (t, i) in cells:
            e = (v(t - 1, i - 1), v(t - 1, i), v(t - 1, i + 1))
            if e in tab:
                val[(t, i)] = tab[e]
                continue
            # branch: candidate values (front cells cannot be L)
            cands = [d for d in W if not (i == t + 1 and d == 0)]
            alive = []
            for d in cands:
                lit = E.T[e][d]
                s.conf_budget(budget)
                r = s.solve_limited(assumptions=assum + [lit])
                if r is not False:
                    alive.append(d)
            depth += 1
            est_levels.setdefault(depth, []).append(weight * len(alive))
            if not alive:
                leaf = 'pruned'
                break
            weight *= len(alive)
            d = rnd.choice(alive)
            tab[e] = d
            val[(t, i)] = d
            assum.append(E.T[e][d])
        print("probe %d: depth %d, %s, weight %.3g (%.0fs)" % (p, depth, leaf, weight, time.time() - t0))
        sys.stdout.flush()
    print("estimated nodes per level (mean over probes):")
    tot = 0.0
    for dpt in sorted(est_levels):
        vals = est_levels[dpt] + [0.0] * (probes - len(est_levels[dpt]))
        m = sum(vals) / probes
        tot += m
        print("  depth %2d: %.3g" % (dpt, m))
    print("estimated total nodes: %.3g" % tot)


if __name__ == '__main__':
    main()
