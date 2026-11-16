#!/usr/bin/env python3
"""lns.py RULE N [--dist D1,D2,...] [--core C] [--budget CONFLICTS] [--b3] [--b3w] [--b1] [--b1s] [--out FILE] [--k K]

Neighbourhood search around a rule with a SAT solver.

RULE is a transition table (lines 'l c r d' after 'k K', or one line 'xyz=d xyz=d ...').  Let U be the set of the
transitions that RULE uses on the lines 2..C (default: C = the largest n such that RULE synchronizes all lines 2..n).
The formula says: the table synchronizes every line 2..N in minimal time (the formula of mcopy.py with strict=True,
that is, the lines and the class conditions and nothing else), and

        #{ e in U : delta(e) != RULE(e) }  <=  D.

It is solved for D = D1, D2, ... with one incremental solver (a totalizer for the distance, the bound as an
assumption), each call with the conflict budget.  Answers:
    SAT      the table is decoded, simulated without the encoder on the lines 2..60, and written to FILE;
    UNSAT    no table within the distance D of RULE (on U) synchronizes the lines 2..N  [solver answer, no proof];
    BUDGET   not decided.
The transitions outside U are free in every case.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, NAMES, BND
from pysat.solvers import Solver
from pysat.card import ITotalizer

ap = argparse.ArgumentParser()
ap.add_argument('rule'); ap.add_argument('N', type=int)
ap.add_argument('--k', type=int, default=0)
ap.add_argument('--dist', default='0,1,2,3,4,6,8')
ap.add_argument('--core', type=int, default=0)
ap.add_argument('--budget', type=int, default=200000)
ap.add_argument('--out', default='')
ap.add_argument('--nmin', type=int, default=2)
ap.add_argument('--phase', action='store_true', help='prefer the values of RULE on U when the solver decides a table variable (forced phases)')
ap.add_argument('--phasecells', action='store_true', help='with --phase: also prefer the states of the diagrams of RULE for the cells of the lines and of the half-line')
for f in ('b1', 'b1s', 'b3', 'b3w', 'b4'):
    ap.add_argument('--' + f, action='store_true')
a = ap.parse_args()


def load(fn):
    k, tab = None, {}
    for l in open(fn):
        l = l.split('#')[0].strip()
        if not l:
            continue
        if l.startswith('RULE'):
            l = l.split(':', 1)[1].strip()
        p = l.split()
        if p[0] == 'k':
            k = int(p[1]); continue
        if '=' in p[0]:
            for it in p:
                e, d = it.split('=')
                tab[(e[0], e[1], e[2])] = d
        else:
            tab[(p[0], p[1], p[2])] = p[3]
    return k, tab


def run(tab, n, used=None):
    """True if the line of length n fires exactly at time 2n-2 (all cells, no F before)"""
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        es = [(row[i - 1] if i > 0 else '*', row[i], row[i + 1] if i < n - 1 else '*') for i in range(n)]
        if any(e not in tab for e in es):
            return False
        if used is not None:
            used.update(es)
        row = [tab[e] for e in es]
        if 'F' in row:
            return t == 2 * n - 2 and all(x == 'F' for x in row)
    return False


def top_of(tab, nmin=2):
    n = nmin
    while run(tab, n):
        n += 1
    return n - 1


k0, ref = load(a.rule)
k = a.k or k0 or 5
ref.setdefault(('L', 'L', 'L'), 'L'); ref.setdefault(('L', 'L', '*'), 'L')
top = top_of(ref, a.nmin)
core = a.core or top
U = set()
for n in range(a.nmin, core + 1):
    assert run(ref, n, U), 'the rule does not synchronize the line %d' % n
N = a.N
t0 = time.time()
M = Model(k, N, copy=False, sym=False, strict=True, nmin=a.nmin, b1=a.b1, b1s=a.b1s, b3=a.b3, b3w=a.b3w, b4=a.b4)
E = M.E
code = {NAMES[x]: x for x in range(k - 1)}; code['*'] = BND; code['F'] = k - 1
name = {v: s for s, v in code.items()}
S = Solver(name='cadical153', bootstrap_with=E.cl)
dl = sorted(-E.T[(code[e[0]], code[e[1]], code[e[2]])][code[ref[e]]] for e in U)      # literal: delta(e) != RULE(e)
dists = [int(x) for x in a.dist.split(',')]
tot = ITotalizer(lits=dl, ubound=max(dists) + 1, top_id=E.nv)
for c in tot.cnf.clauses:
    S.add_clause(c)
if a.phase:
    ph = []
    for e in U:
        vs = E.T[(code[e[0]], code[e[1]], code[e[2]])]
        ph += [vs[j] if j == code[ref[e]] else -vs[j] for j in range(k)]
    if a.phasecells:
        def diagram(n, tmax):
            rows = [['G'] + ['L'] * (n - 1)]
            for t in range(1, tmax + 1):
                r = ['*'] + rows[-1] + ['*']
                rows.append([ref.get((r[i - 1], r[i], r[i + 1]), '?') for i in range(1, n + 1)])
            return rows
        big = diagram(2 * N + 2, 2 * N)
        for (t, i), x in M.Hc.items():
            st = big[t][i - 1]
            if st in code and st != 'F':
                ph += [x[j] if j == code[st] else -x[j] for j in range(k - 1)]
        for (n, t, i), x in M.Rc.items():
            st = diagram(n, t)[t][i - 1] if n <= top else '?'
            if st in code and st != 'F':
                ph += [x[j] if j == code[st] else -x[j] for j in range(k - 1)]
    S.set_phases(ph)
print('# rule %s: synchronizes 2..%d; U = %d transitions (lines %d..%d); target: lines %d..%d; k = %d; %d variables, %d + %d clauses; built in %.0f s'
      % (a.rule, top, len(U), a.nmin, core, a.nmin, N, k, tot.top_id, len(E.cl), len(tot.cnf.clauses), time.time() - t0), flush=True)
found = None
for D in dists:
    if D >= len(dl):
        assum = []
    else:
        assum = [-tot.rhs[D]]
    t1 = time.time()
    S.conf_budget(a.budget)
    r = S.solve_limited(assumptions=assum)
    ans = 'SAT' if r is True else 'UNSAT' if r is False else 'BUDGET'
    print('D <= %d: %s  (%.0f s)' % (D, ans, time.time() - t1), flush=True)
    if r is True:
        model = set(x for x in S.get_model() if x > 0)
        tab = {}
        for e, vs in E.T.items():
            d = [j for j in range(k) if vs[j] in model]
            assert len(d) == 1
            tab[(name[e[0]], name[e[1]], name[e[2]])] = name[d[0]]
        good = [n for n in range(2, 61) if run(tab, n)]
        diff = sorted(''.join(e) + ':' + ref[e] + '>' + tab[e] for e in U if tab[e] != ref[e])
        ntop = top_of(tab, a.nmin)
        print('   simulated: synchronizes %s; distance %d on U: %s' % (good, len(diff), ' '.join(diff)), flush=True)
        assert ntop >= N, 'the decoded table fails on a line <= N'
        used = set()
        for n in range(a.nmin, ntop + 1):
            run(tab, n, used)
        if a.out:
            with open(a.out, 'w') as f:
                f.write('# lns.py %s\n# synchronizes the lines %d..%d (simulated); %d transitions used by these lines\nk %d\n'
                        % (' '.join(sys.argv[1:]), a.nmin, ntop, len(used), k))
                for e in sorted(used):
                    f.write('%s %s %s %s\n' % (e[0], e[1], e[2], tab[e]))
        found = ntop
        break
    if r is None:
        break
print('RESULT %s' % ('found %d' % found if found else 'none'), flush=True)
