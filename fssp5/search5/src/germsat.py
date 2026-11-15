#!/usr/bin/env python3
"""germsat.py -- stable generals (B1): depth-first search over the half-line, with a SAT solver at every node.

The half-line of the class is a diagram over {L, A, B} next to a constant G (Lemma 6.2 of README.md).  Its
transitions are fixed one at a time, in the order in which the anti-diagonals need them (as in germw.c).
At every node the formula "the lines 2..N are synchronized" with the clauses of the class is solved under the
assumption of the transitions fixed so far, with a conflict budget:
    UNSAT   -> no rule of the class with this beginning of the half-line: the subtree is closed;
    SAT     -> a rule for 2..N (re-simulated); with --all the search goes on below the node;
    budget  -> the next transition of the half-line is branched on.
A node whose half-line is complete up to the anti-diagonal 2N-1 is solved with the leaf budget.
The search is exhaustive: if no node is left open and no model was found, the formula is unsatisfiable.

usage: germsat.py N [--budget C] [--leaf C] [--all] [--extra n1,n2] [--early N2 T] [--pump P] [--out PREFIX]
                    [--maxdepth D] [--log FILE]
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(10000)
from mcopy import Model, NAMES, BND
from simlib import ok
from pysat.solvers import Solver

ap = argparse.ArgumentParser()
ap.add_argument('N', type=int)
ap.add_argument('--budget', type=int, default=3000); ap.add_argument('--leaf', type=int, default=2000000)
ap.add_argument('--all', action='store_true'); ap.add_argument('--out')
ap.add_argument('--extra', default=''); ap.add_argument('--early', type=int, nargs=2); ap.add_argument('--pump', type=int, default=0)
ap.add_argument('--solver', default='cadical153'); ap.add_argument('--nowgap', action='store_true')
ap.add_argument('--prefix', default='', help='transitions fixed at the root, e.g. ALL=A,GAL=B')
ap.add_argument('--grow', type=float, default=1.0, help='the budget is multiplied by GROW per level')
ap.add_argument('--cubes', help='write the closed nodes (one cube per line) to this file')
ap.add_argument('--maxdepth', type=int, default=0, help='do not branch below this depth: the open nodes of this depth are written to --emit')
ap.add_argument('--emit', help='file for the open nodes at --maxdepth, as --prefix strings')
a = ap.parse_args()
k, N = 5, a.N
M = Model(k, N, copy=False, sym=False, b1s=True, b3=True, nogh=True, wimp=True, wgap=not a.nowgap,
          early=tuple(a.early) if a.early else None, extra=[int(x) for x in a.extra.split(',') if x], pump=a.pump)
E = M.E
S = Solver(name=a.solver)
for c in E.cl:
    S.add_clause(c)
MM = 2 * N - 1                     # the half-line is branched on up to this anti-diagonal
L_, G_, A_, B_ = 0, 1, 2, 3
tab = {(0, 0, 0): 0}               # half-line transitions fixed so far: (a, b, c) -> value
val = {}                           # (t, i) -> state, i >= 2
def cellv(t, i):
    if i == 1:
        return G_
    if i > t + 1:
        return L_
    return val[(t, i)]
order = [(m - t, t) for m in range(3, MM + 1) for t in range(1, m) if 2 <= m - t <= t + 1]
order = [(t, i) for (i, t) in order]          # cells in the order of germw.c: anti-diagonal, then time
cubef = None
emitted = []
stats = {'nodes': 0, 'unsat': 0, 'sat': 0, 'budget': 0, 'leaf_unknown': 0, 'calls': 0}
by_depth = {}
models = []
t0 = time.time()
code = {NAMES[x]: x for x in range(k - 1)}
code['*'] = BND
def lit(e, v):
    return E.T[e][v]
def name(e, v):
    return '%s%s%s>%s' % (NAMES[e[0]], NAMES[e[1]], NAMES[e[2]], NAMES[v])
def report(tag, assum_names):
    print('%s depth=%d %s  [nodes %d, unsat %d, sat %d, open-leaf %d, %.0f s]' % (
        tag, len(assum_names), ' '.join(assum_names), stats['nodes'], stats['unsat'], stats['sat'], stats['leaf_unknown'], time.time() - t0), flush=True)
last_report = [time.time()]
cur_names = [[]]
def solve(assum, budget):
    stats['calls'] += 1
    if time.time() - last_report[0] > 60:
        last_report[0] = time.time()
        print('.. %.0f s: %s; at depth %d: %s' % (time.time() - t0, stats, len(cur_names[0]), ' '.join(cur_names[0])), flush=True)
        print('.. by depth (unsat, sat, budget): ' + ' '.join('%d:%s' % (d, tuple(v)) for d, v in sorted(by_depth.items())), flush=True)
    S.conf_budget(budget)
    return S.solve_limited(assumptions=assum)
def dfs(pos, assum, names, maxaux):
    """pos: index in `order` of the next cell to compute"""
    # advance the half-line as far as the fixed transitions allow
    start = pos
    while pos < len(order):
        t, i = order[pos]
        e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
        if e not in tab:
            break
        v = tab[e]
        if i == t + 1 and v == L_:
            for q in range(start, pos):
                val.pop(order[q], None)
            return
        val[(t, i)] = v
        pos += 1
    def undo():
        for q in range(start, pos):
            val.pop(order[q], None)
    if pos == len(order):
        stats['nodes'] += 1
        r = solve(assum, a.leaf)
        if r is True:
            found(assum, names)
        elif r is False:
            stats['unsat'] += 1
            if cubef:
                cubef.write('LEAF ' + ' '.join(names) + '\n')
        else:
            stats['leaf_unknown'] += 1
            report('OPEN-LEAF', names)
        undo()
        return
    t, i = order[pos]
    e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
    for v in (L_, A_, B_):
        if v == L_ and i == t + 1:
            continue
        if v >= 2 and v > maxaux + 1:
            continue
        stats['nodes'] += 1
        d = len(names) + 1
        by_depth.setdefault(d, [0, 0, 0])
        as2, nm2 = assum + [lit(e, v)], names + [name(e, v)]
        cur_names[0] = nm2
        r = solve(as2, int(a.budget * a.grow ** d))
        if r is False:
            stats['unsat'] += 1; by_depth[d][0] += 1
            if cubef:
                cubef.write(' '.join(nm2) + '\n')
            continue
        if r is True:
            by_depth[d][1] += 1
            found(as2, nm2)
            if not a.all:
                continue
        else:
            stats['budget'] += 1; by_depth[d][2] += 1
            if a.maxdepth and d >= a.maxdepth:
                emitted.append(','.join(x.replace('>', '=') for x in nm2))
                continue
        tab[e] = v
        dfs(pos, as2, nm2, max(maxaux, v))
        del tab[e]
    undo()
def found(assum, names):
    tabm = M.table(S.get_model())
    good = [x for x in range(2, 3 * N) if ok(tabm, x)]
    key = tuple(sorted(tabm.items()))
    if key in models:
        return
    models.append(key)
    stats['sat'] += 1
    report('MODEL %d synchronizes %s' % (len(models), good), names)
    if a.out:
        with open('%s_%d.txt' % (a.out, len(models)), 'w') as f:
            f.write('# germsat.py %s\nk %d\n' % (' '.join(sys.argv[1:]), k))
            for (l, c, rr), d in tabm.items():
                f.write('%s %s %s %s\n' % (l, c, rr, d))
root_assum, root_names, mx = [], [], 1
for spec in [x for x in a.prefix.split(',') if x]:
    lcr, d = spec.split('=')
    e = (code[lcr[0]], code[lcr[1]], code[lcr[2]])
    root_assum.append(lit(e, code[d])); root_names.append(name(e, code[d]) if BND not in e else spec)
    if BND not in e and e[1] != 1 and all(x in (0, 2, 3) or (x == 1 and j == 0) for j, x in enumerate(e)):
        tab[e] = code[d]; mx = max(mx, code[d])
print('# N=%d, %d variables, %d clauses, budget %d (x%.2f per level), leaf budget %d, half-line cells %d' % (
    N, E.nv, len(E.cl), a.budget, a.grow, a.leaf, len(order)), flush=True)
if a.cubes:
    cubef = open(a.cubes, 'w')
dfs(0, root_assum, root_names, mx)
if cubef:
    cubef.close()
if a.emit:
    with open(a.emit, 'w') as f:
        f.write(''.join(x + '\n' for x in emitted))
    print('# %d open nodes at depth %d written to %s' % (len(emitted), a.maxdepth, a.emit), flush=True)
print('# done in %.0f s: %s' % (time.time() - t0, stats), flush=True)
print('# by depth (unsat, sat, budget): ' + ' '.join('%d:%s' % (d, tuple(v)) for d, v in sorted(by_depth.items())), flush=True)
print('# RESULT: %s' % ('models found: %d' % len(models) if models else ('%d nodes deferred' % len(emitted) if emitted else ('UNSAT (every node closed)' if stats['leaf_unknown'] == 0 else 'open leaves: %d' % stats['leaf_unknown']))), flush=True)
