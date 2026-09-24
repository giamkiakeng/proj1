#!/usr/bin/env python3
"""coresize.py -- size of (minimized) UNSAT cores of germ transitions.

usage: coresize.py rulefile N2 [M]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}


def germ(tab, M):
    used = set()
    width = M + 2
    cur = ['G'] + ['L'] * (width - 1)
    for t in range(M):
        nxt = []
        for i in range(width):
            if t + (i + 1) >= M:
                nxt.append('?')
                continue
            l = cur[i - 1] if i > 0 else '*'
            r = cur[i + 1] if i + 1 < width else 'L'
            e = (l, cur[i], r)
            if '?' in e:
                nxt.append('?')
                continue
            used.add(e)
            nxt.append(tab[e])
        cur = nxt
    return used


def main():
    rule, N2 = sys.argv[1], int(sys.argv[2])
    M = int(sys.argv[3]) if len(sys.argv) > 3 else 78
    tab = {}
    for ln in open(rule):
        t = ln.split('#')[0].split()
        if len(t) == 4:
            tab[tuple(t[:3])] = t[3]
    g = germ(tab, M)
    E = gencnf.build(5, N2, minf=M, pump=min(40, M // 2), links=True)
    lits = {}
    for e in g:
        key = tuple(CODE[x] for x in e)
        if key in E.T:
            lits[E.T[key][CODE[tab[e]]]] = e
    s = Solver(name='cd19', bootstrap_with=E.clauses)
    t0 = time.time()
    res = s.solve(assumptions=list(lits))
    if res:
        print("germ completable for 2..%d" % N2)
        return
    core = s.get_core()
    t1 = time.time()
    # deletion-based minimization
    core = list(core)
    i = 0
    while i < len(core):
        trial = core[:i] + core[i + 1:]
        if not s.solve(assumptions=trial):
            c2 = set(s.get_core())
            core = [x for x in trial if x in c2]
        else:
            i += 1
    t2 = time.time()
    print("%s: germ %d transitions, raw core %d, minimal core %d (%.1fs / %.1fs)" % (
        os.path.basename(rule), len(lits), len(s.get_core() or []), len(core), t1 - t0, t2 - t1))
    print("   minimal core:", sorted("%s%s%s=%s" % (e[0], e[1], e[2], tab[e]) for e in (lits[x] for x in core)))


if __name__ == '__main__':
    main()
