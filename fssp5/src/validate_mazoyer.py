#!/usr/bin/env python3
"""Soundness test: Mazoyer's rule (lengths 3..N) must satisfy MT(6,N) restricted
to n >= 3, both without symmetry breaking and, after renaming the auxiliary
states into canonical first-occurrence order, with symmetry breaking."""
import itertools, sys
sys.path.insert(0, '.')
import gencnf
from pysat.solvers import Solver

def load(fn):
    tab = {}
    for ln in open(fn):
        ln = ln.split('#')[0].split()
        if len(ln) == 4:
            tab[tuple(ln[:3])] = ln[3]
    return tab

def code(ch):
    return {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'C': 4, 'F': 5}[ch]

def units(E, tab, perm):
    lits = []
    for (l, c, r), d in tab.items():
        e = tuple(perm.get(code(x), code(x)) for x in (l, c, r))
        lits.append(E.T[e][perm.get(code(d), code(d))])
    return lits

tab = load('../results/mazoyer6.txt')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
for sym in (False, True):
    ok_perms = []
    for p in itertools.permutations([2, 3, 4]):
        perm = dict(zip([2, 3, 4], p))
        E = gencnf.build(6, N, diff=True, symbreak=sym, fire_n=range(3, N + 1))
        with Solver(name='cd19', bootstrap_with=E.clauses) as s:
            if s.solve(assumptions=units(E, tab, perm)):
                ok_perms.append(p)
        if not sym:
            break
    print("symbreak=%s N=%d: satisfiable under renamings %s" % (sym, N, ok_perms))
