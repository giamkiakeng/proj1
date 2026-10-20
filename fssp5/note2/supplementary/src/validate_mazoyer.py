#!/usr/bin/env python3
"""Soundness test of the encoding (note, Section 5).

Mazoyer's six-state rule (results/mazoyer6.txt, extracted from Duprat's Coq development by
mazoyer_from_coq.py) synchronizes the lengths n >= 3, so it must satisfy MT_6({3,...,N}; M, NP):
the formula of gencnf.build with the half-line to anti-diagonal M, the reflected triangles and
return chains of the lengths 3..N and PUMP(n,n') for 4 <= n < n' <= NP.  The rule table is fixed
by unit assumptions.  Tested without symmetry breaking (as every formula of the note) and, for
each renaming of the auxiliary states A, B, C, with the optional symmetry breaking (exactly one
renaming, the first-occurrence order, must be satisfiable).

usage: validate_mazoyer.py [N=12] [M=78] [NP=40]
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gencnf  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


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


tab = load(os.path.join(HERE, '..', 'results', 'mazoyer6.txt'))
N, M, NP = [int(x) for x in (sys.argv[1:] + ['12', '78', '40'][len(sys.argv) - 1:])][:3]
for sym in (False, True):
    ok_perms = []
    for p in itertools.permutations([2, 3, 4]):
        perm = dict(zip([2, 3, 4], p))
        E = gencnf.build(6, N, diff=True, symbreak=sym, fire_n=range(3, N + 1), minf=M, pump=NP)
        with Solver(name='cd19', bootstrap_with=E.clauses) as s:
            if s.solve(assumptions=units(E, tab, perm)):
                ok_perms.append(p)
        if not sym:
            break
    print("MT_6({3..%d}; %d, %d), symbreak=%s: satisfiable under renamings %s" % (N, M, NP, sym, ok_perms))
