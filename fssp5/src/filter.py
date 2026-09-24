#!/usr/bin/env python3
"""
filter.py -- domain filtering of transition-table entries by SAT.

For every entry e = (l,c,r) and value d, decide whether MT(k, lengths) has a
model with delta(e) = d.  Values without a model are impossible in *every*
rule that synchronizes all the given lengths in minimal time (hence in every
minimal-time solution).  Uses the standard model-rotation trick: every model
found certifies all (e, value) pairs it contains.

usage: filter.py k N0 [--minf M] [--tinf T] [--fix file] [--out file]
The optional --fix file contains previously established facts
("l c r d1 d2 ..." = allowed values) that are added as clauses.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

SYM = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'C': 4}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('k', type=int)
    ap.add_argument('N0', type=int)
    ap.add_argument('--minf', type=int, default=None)
    ap.add_argument('--tinf', type=int, default=0)
    ap.add_argument('--fix', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--nosym', action='store_true')
    a = ap.parse_args()
    k = a.k
    SYM['F'] = k - 1
    E = gencnf.build(k, a.N0, minf=a.minf, tinf=a.tinf, symbreak=not a.nosym)
    if a.fix:
        for ln in open(a.fix):
            t = ln.split()
            if len(t) < 4 or ln.startswith('#'):
                continue
            e = tuple(SYM[x] for x in t[:3])
            E.add([E.T[e][SYM[x]] for x in t[3:]])
    s = Solver(name='cd19', bootstrap_with=E.clauses)
    possible = {e: set() for e in E.T}
    t0 = time.time()
    nsat = nunsat = 0

    def absorb():
        m = set(v for v in s.get_model() if v > 0)
        for e, vs in E.T.items():
            for d in range(k):
                if vs[d] in m:
                    possible[e].add(d)

    assert s.solve(), "base instance unsatisfiable"
    absorb()
    for e, vs in sorted(E.T.items()):
        for d in range(k):
            if d in possible[e]:
                continue
            if s.solve(assumptions=[vs[d]]):
                nsat += 1
                absorb()
            else:
                nunsat += 1
                s.add_clause([-vs[d]])
    names = {v: kk for kk, v in SYM.items()}
    lines = []
    for e in sorted(possible):
        if len(possible[e]) < k:
            lines.append("%s %s %s %s" % (names[e[0]], names[e[1]], names[e[2]],
                                          " ".join(names[d] for d in sorted(possible[e]))))
    hdr = "# filter k=%d N0=%d minf=%s tinf=%s: %d restricted entries (%.0fs)" % (
        k, a.N0, a.minf, a.tinf, len(lines), time.time() - t0)
    print(hdr)
    print("\n".join(lines))
    if a.out:
        with open(a.out, 'w') as fh:
            fh.write(hdr + "\n" + "\n".join(lines) + "\n")


if __name__ == '__main__':
    main()
