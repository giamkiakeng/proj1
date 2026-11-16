#!/usr/bin/env python3
"""lns2.py RULE N --core C --maxd D [--budget CONFLICTS] [--b3] [--out FILE] [--order near|far]

The neighbourhood of lns.py, searched by an explicit case split.

U = the transitions that RULE uses on the lines 2..C.  The question is the same as in lns.py: is there a table that
synchronizes the lines 2..N and differs from RULE in at most D transitions of U (the other transitions are free)?
Here the changes are enumerated: the lines 2, 3, ..., C are simulated in this order with the table defined so far;
the first undefined transition e of U is given the value of RULE (cost 0) or another value (cost 1, while the cost
stays <= D).  A line that needs a transition outside U is left to the solver; a line that fails ends the branch.
Every leaf is a partial assignment of U with d <= D changes; it is given to one incremental solver as assumptions,
together with the bound D on the total number of changes (totalizer), with the conflict budget.  The leaves are a
complete case split of the neighbourhood: every table of the neighbourhood agrees with exactly one leaf or is cut
off by a line among 2..C that it does not synchronize.

Output: one line per leaf (changes, answer, time); models are simulated without the encoder and the best is kept.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, NAMES, BND
from pysat.solvers import Solver
from pysat.card import ITotalizer

ap = argparse.ArgumentParser()
ap.add_argument('rule'); ap.add_argument('N', type=int)
ap.add_argument('--k', type=int, default=0)
ap.add_argument('--core', type=int, default=0); ap.add_argument('--maxd', type=int, default=2)
ap.add_argument('--budget', type=int, default=50000)
ap.add_argument('--out', default=''); ap.add_argument('--stop', action='store_true', help='stop at the first model')
ap.add_argument('--order', default='near', help='near: leaves with few changes first; far: many changes first; dfs: as found')
ap.add_argument('--maxleaves', type=int, default=10 ** 9)
ap.add_argument('--all', type=int, default=0, help='up to this many further models per satisfiable leaf (two models differ in a transition that the lines 2..N use)')
ap.add_argument('--outprefix', default='', help='write every model to PREFIX_<number>_top<top>.txt')
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
    """'ok' if the line n fires exactly at 2n-2; 'fail' if it certainly does not; else the first undefined transition"""
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        es = [(row[i - 1] if i > 0 else '*', row[i], row[i + 1] if i < n - 1 else '*') for i in range(n)]
        for e in es:
            if e not in tab:
                return e
        if used is not None:
            used.update(es)
        row = [tab[e] for e in es]
        if 'F' in row:
            return 'ok' if (t == 2 * n - 2 and all(x == 'F' for x in row)) else 'fail'
    return 'fail'


def top_of(tab, nmax=150):
    n = 2
    while n <= nmax and run(tab, n) == 'ok':
        n += 1
    return n - 1


k0, ref = load(a.rule)
k = a.k or k0 or 5
ref.setdefault(('L', 'L', 'L'), 'L'); ref.setdefault(('L', 'L', '*'), 'L')
top = top_of(ref)
core = a.core or top
U = set()
for n in range(2, core + 1):
    assert run(ref, n, U) == 'ok'
STATES = list(NAMES[:k - 1])
FIRE = {('G', 'G', 'G'), ('*', 'G', 'G'), ('G', 'G', '*')}
FIXED = {('L', 'L', 'L'), ('L', 'L', '*')}


def values(e):
    if e in FIXED:
        return ['L']
    if a.b3:
        return ['F'] if e in FIRE else STATES
    if a.b3w and e in FIRE:
        return ['F']
    return STATES + ['F']


leaves = []


def explore(tab, d, n0):
    if len(leaves) >= a.maxleaves:
        return
    for n in range(n0, core + 1):
        r = run(tab, n)
        if r == 'fail':
            return
        if r == 'ok':
            continue
        if r in U:
            vs = values(r)
            for v in [ref[r]] + [x for x in vs if x != ref[r]]:
                c = 0 if v == ref[r] else 1
                if d + c <= a.maxd and v in vs:
                    tab[r] = v
                    explore(tab, d + c, n)
                    del tab[r]
            return
        # the line needs a transition outside U: left to the solver
    leaves.append((d, dict(tab)))


t0 = time.time()
explore({e: ref[e] for e in FIXED}, 0, 2)
if a.order == 'near':
    leaves.sort(key=lambda x: x[0])
elif a.order == 'far':
    leaves.sort(key=lambda x: -x[0])
print('# rule %s: synchronizes 2..%d; U = %d transitions (lines 2..%d); at most %d changes: %d leaves (by number of changes: %s) in %.0f s'
      % (a.rule, top, len(U), core, a.maxd, len(leaves), {d: sum(1 for x in leaves if x[0] == d) for d in range(a.maxd + 1)}, time.time() - t0), flush=True)
if a.N == 0:
    sys.exit(0)
N = a.N
t0 = time.time()
M = Model(k, N, copy=False, sym=False, strict=True, b1=a.b1, b1s=a.b1s, b3=a.b3, b3w=a.b3w, b4=a.b4)
E = M.E
code = {NAMES[x]: x for x in range(k - 1)}; code['*'] = BND; code['F'] = k - 1
name = {v: s for s, v in code.items()}
lit = lambda e, v: E.T[(code[e[0]], code[e[1]], code[e[2]])][code[v]]
S = Solver(name='cadical153', bootstrap_with=E.cl)
dl = sorted(-lit(e, ref[e]) for e in U)
tot = ITotalizer(lits=dl, ubound=a.maxd + 1, top_id=E.nv)
for c in tot.cnf.clauses:
    S.add_clause(c)
bound = [-tot.rhs[a.maxd]] if a.maxd < len(dl) else []
print('# target: lines 2..%d; %d variables, %d clauses; built in %.0f s; conflict budget %d per leaf' % (N, tot.top_id, len(E.cl) + len(tot.cnf.clauses), time.time() - t0, a.budget), flush=True)
best, stats = None, {'UNSAT': 0, 'SAT': 0, 'BUDGET': 0}
nmodels = 0
tstart = time.time()
for j, (d, tab) in enumerate(leaves):
    assum = [lit(e, v) for e, v in sorted(tab.items()) if e in U] + bound
    ch = ' '.join(sorted(''.join(e) + ':' + ref[e] + '>' + v for e, v in tab.items() if e in U and v != ref[e]))
    t1 = time.time()
    S.conf_budget(a.budget)
    r = S.solve_limited(assumptions=assum)
    ans = 'SAT' if r is True else 'UNSAT' if r is False else 'BUDGET'
    stats[ans] += 1
    if ans != 'UNSAT' or (j + 1) % 50 == 0:
        print('leaf %d/%d  [%d changes: %s]  %d transitions fixed: %s  (%.1f s; total %.0f s; %s)' % (j + 1, len(leaves), d, ch, len(assum) - len(bound), ans, time.time() - t1, time.time() - tstart, stats), flush=True)
    nm = 0
    while r is True:
        model = set(x for x in S.get_model() if x > 0)
        full = {}
        for e, vs in E.T.items():
            dd = [q for q in range(k) if vs[q] in model]
            full[(name[e[0]], name[e[1]], name[e[2]])] = name[dd[0]]
        ntop = top_of(full)
        diff = sorted(''.join(e) + ':' + ref[e] + '>' + full[e] for e in U if full[e] != ref[e])
        print('   model: synchronizes 2..%d and %s; distance %d on U: %s' % (ntop, [n for n in range(ntop + 1, 61) if run(full, n) == 'ok'], len(diff), ' '.join(diff)), flush=True)
        assert ntop >= N
        used = set()
        for n in range(2, ntop + 1):
            run(full, n, used)
        nmodels += 1; nm += 1

        def write(fn):
            with open(fn, 'w') as f:
                f.write('# lns2.py %s\n# synchronizes the lines 2..%d (simulated); %d transitions used by these lines\nk %d\n' % (' '.join(sys.argv[1:]), ntop, len(used), k))
                for e in sorted(used):
                    f.write('%s %s %s %s\n' % (e[0], e[1], e[2], full[e]))
        if a.outprefix:
            write('%s_%d_top%d.txt' % (a.outprefix, nmodels, ntop))
        if best is None or ntop > best[0]:
            best = (ntop, full)
            if a.out:
                write(a.out)
        if nm > a.all:
            break
        usedN = set()
        for n in range(2, N + 1):
            run(full, n, usedN)
        S.add_clause([-lit(e, full[e]) for e in usedN])
        S.conf_budget(a.budget)
        r = S.solve_limited(assumptions=assum)
    if best and a.stop:
        break
print('RESULT %s; leaves: %s; %.0f s' % ('found %d' % best[0] if best else 'none', stats, time.time() - tstart), flush=True)
