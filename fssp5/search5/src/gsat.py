#!/usr/bin/env python3
"""gsat.py -- depth-first search over the half-line of a k-state rule, with a SAT solver at every node.

The transitions that the half-line C_inf uses are fixed one at a time, in the order in which the anti-diagonals
t + i = 2, 3, ... need them (within an anti-diagonal by increasing time).  At every node the formula of
mcopy.py for the lines 2..N (with the clauses of the chosen class) is solved under the assumption of the
transitions fixed so far, with a conflict budget:
    UNSAT   -> no rule of the class has this beginning of the half-line: the subtree is closed;
    SAT     -> a rule for 2..N (re-simulated); with --all the search goes on below the node;
    budget  -> the next transition of the half-line is branched on.
A node whose half-line is complete up to the last anti-diagonal of the formula is solved with the leaf budget.
The branching is complete for the formula: a half-line cell is never F, the front is never L (clauses of the
formula; for the last front cell see README), auxiliary states are named in the order of their first
occurrence, and with --nogh (stable generals, Lemma 6.2) the first cell is G and no other cell is.
If no node is left open and no model was found, the formula is unsatisfiable.

usage: gsat.py K N [class options of mcopy.py] [--budget C] [--leaf C] [--all] [--prefix e=v,...]
               [--cubes FILE] [--out PREFIX]
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(10000)
from mcopy import Model, NAMES, BND
from simlib import ok
from pysat.solvers import Solver

ap = argparse.ArgumentParser()
ap.add_argument('k', type=int); ap.add_argument('N', type=int)
ap.add_argument('--budget', type=int, default=3000); ap.add_argument('--leaf', type=int, default=2000000)
ap.add_argument('--all', action='store_true'); ap.add_argument('--out'); ap.add_argument('--cubes')
for f in ('b1', 'b1s', 'b3', 'b3w', 'b4', 'nogh', 'noghw', 'wimp', 'wgap', 'strict'):
    ap.add_argument('--' + f, action='store_true')
ap.add_argument('--b2'); ap.add_argument('--extra', default=''); ap.add_argument('--early', type=int, nargs=2)
ap.add_argument('--pump', type=int, default=0); ap.add_argument('--solver', default='cadical153')
ap.add_argument('--prefix', default='', help='half-line transitions fixed at the root, in the order of the search, e.g. *GL=G,GLL=A')
ap.add_argument('--maxnodes', type=int, default=0)
ap.add_argument('--knuth', type=int, default=0, help='do not search: estimate the size of the tree by this many random descents (Knuth)')
ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--maxdepth', type=int, default=0, help='do not branch below this depth: the open nodes of this depth are written to --emit')
ap.add_argument('--emit', help='file for the open nodes at --maxdepth, as --prefix strings')
ap.add_argument('--front1', action='store_true')
ap.add_argument('--gstatic', type=int, default=None, help='the first cell is G at every time >= GSTATIC')
a = ap.parse_args()
k, N = a.k, a.N
M = Model(k, N, copy=False, sym=False, b1=a.b1, b1s=a.b1s, b3=a.b3, b3w=a.b3w, b4=a.b4, b2=a.b2, nogh=a.nogh, wimp=a.wimp,
          wgap=a.wgap, strict=a.strict, early=tuple(a.early) if a.early else None,
          extra=[int(x) for x in a.extra.split(',') if x], pump=a.pump, front1=a.front1, gstatic=a.gstatic, noghw=a.noghw)
E = M.E
S = Solver(name=a.solver)
for c in E.cl:
    S.add_clause(c)
MM = M.M                          # last anti-diagonal of the half-line in the formula
NFRONT = max([N] + M.extra) - 2   # the formula forbids L on the front cells (t, t+1) for t <= NFRONT (one less with --strict)
if a.strict:
    NFRONT -= 1
if a.front1 and not a.strict:
    NFRONT += 1
W = list(range(k - 1))
imin = 2 if a.nogh else 1
tab = {(0, 0, 0): 0}
val = {}
def cellv(t, i):
    if i < 1:
        return BND
    if i > t + 1:
        return 0
    if t == 0:
        return 1
    if i == 1 and a.nogh:
        return 1
    return val[(t, i)]
order = [(t, m - t) for m in range(2, MM + 1) for t in range(1, m) if imin <= m - t <= t + 1]
stats = {'nodes': 0, 'unsat': 0, 'sat': 0, 'budget': 0, 'leaf_unknown': 0}
by_depth, models, t0, last_report, cur = {}, [], time.time(), [time.time()], [[]]
code = {NAMES[x]: x for x in range(k - 1)}
code['*'] = BND
sym = lambda x: '*' if x == BND else NAMES[x]
name = lambda e, v: '%s%s%s>%s' % (sym(e[0]), sym(e[1]), sym(e[2]), NAMES[v])
cubef = open(a.cubes, 'w') if a.cubes else None
emitted = []
class Stop(Exception):
    pass
def solve(assum, budget):
    if a.maxnodes and stats['nodes'] > a.maxnodes:
        raise Stop()
    if time.time() - last_report[0] > 60:
        last_report[0] = time.time()
        print('.. %.0f s: %s; at depth %d: %s' % (time.time() - t0, stats, len(cur[0]), ' '.join(cur[0])), flush=True)
        print('.. by depth (unsat, sat, budget): ' + ' '.join('%d:%s' % (d, tuple(v)) for d, v in sorted(by_depth.items())), flush=True)
    S.conf_budget(budget)
    return S.solve_limited(assumptions=assum)
def found(names):
    tabm = M.table(S.get_model())
    key = tuple(sorted(tabm.items()))
    if key in models:
        return
    models.append(key)
    stats['sat'] += 1
    good = [x for x in range(2, 3 * N) if ok(tabm, x)]
    print('MODEL %d synchronizes %s depth=%d %s [%.0f s]' % (len(models), good, len(names), ' '.join(names), time.time() - t0), flush=True)
    if a.out:
        with open('%s_%d.txt' % (a.out, len(models)), 'w') as f:
            f.write('# gsat.py %s\nk %d\n' % (' '.join(sys.argv[1:]), k))
            for (l, c, rr), d in tabm.items():
                f.write('%s %s %s %s\n' % (l, c, rr, d))
def dfs(pos, assum, names, maxaux):
    start = pos
    def undo():
        for q in range(start, pos):
            val.pop(order[q], None)
    while pos < len(order):
        t, i = order[pos]
        e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
        if e not in tab:
            break
        val[(t, i)] = tab[e]
        pos += 1
        if i == t + 1 and tab[e] == 0 and t <= NFRONT:      # the front died: excluded by a clause of the formula
            undo()
            return
    if pos == len(order):
        stats['nodes'] += 1
        r = solve(assum, a.leaf)
        if r is True:
            found(names)
        elif r is False:
            stats['unsat'] += 1
            if cubef:
                cubef.write('LEAF ' + ' '.join(names) + '\n')
        else:
            stats['leaf_unknown'] += 1
            print('OPEN-LEAF depth=%d %s' % (len(names), ' '.join(names)), flush=True)
        undo()
        return
    t, i = order[pos]
    e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
    for v in W:
        if v == 0 and i == t + 1 and t <= NFRONT:
            continue
        if v == 1 and (a.nogh or (a.noghw and i >= 2)):
            continue
        if v >= 2 and v > maxaux + 1:
            continue
        stats['nodes'] += 1
        d = len(names) + 1
        by_depth.setdefault(d, [0, 0, 0])
        as2, nm2 = assum + [E.T[e][v]], names + [name(e, v)]
        cur[0] = nm2
        r = solve(as2, a.budget)
        if r is False:
            stats['unsat'] += 1; by_depth[d][0] += 1
            if cubef:
                cubef.write(' '.join(nm2) + '\n')
            continue
        if r is True:
            by_depth[d][1] += 1
            found(nm2)
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
def knuth_probe(rng):
    """one random descent: returns the estimate of the number of nodes, of solver calls with a model, and the depth"""
    tabk, valk = dict(tab), {}
    def cv(t, i):
        if i < 1:
            return BND
        if i > t + 1:
            return 0
        if t == 0:
            return 1
        if i == 1 and a.nogh:
            return 1
        return valk[(t, i)]
    assum, weight, est, sat, pos, maxaux, depth = list(root_assum), 1.0, 0.0, 0.0, 0, mx, 0
    while True:
        dead = False
        while pos < len(order):
            t, i = order[pos]
            e = (cv(t - 1, i - 1), cv(t - 1, i), cv(t - 1, i + 1))
            if e not in tabk:
                break
            valk[(t, i)] = tabk[e]
            pos += 1
            if i == t + 1 and tabk[e] == 0 and t <= NFRONT:
                dead = True
                break
        if dead or pos == len(order):
            return est, sat, depth, 'leaf' if not dead else 'dead'
        t, i = order[pos]
        e = (cv(t - 1, i - 1), cv(t - 1, i), cv(t - 1, i + 1))
        openc = []
        for v in W:
            if (v == 0 and i == t + 1 and t <= NFRONT) or (v == 1 and (a.nogh or (a.noghw and i >= 2))) or (v >= 2 and v > maxaux + 1):
                continue
            est += weight
            S.conf_budget(a.budget)
            r = S.solve_limited(assumptions=assum + [E.T[e][v]])
            if r is True:
                sat += weight
            elif r is None:
                openc.append(v)
        if not openc:
            return est, sat, depth, 'closed'
        v = rng.choice(openc)
        weight *= len(openc)
        tabk[e] = v; assum.append(E.T[e][v]); maxaux = max(maxaux, v); depth += 1

root_assum, root_names, mx = [], [], 1
for spec in [x for x in a.prefix.split(',') if x]:
    lcr, d = spec.split('=')
    e = (code[lcr[0]], code[lcr[1]], code[lcr[2]])
    root_assum.append(E.T[e][code[d]]); root_names.append(name(e, code[d]))
    tab[e] = code[d]; mx = max(mx, code[d])
print('# k=%d N=%d, %d variables, %d clauses, budget %d, leaf budget %d, %d half-line cells up to the anti-diagonal %d' % (
    k, N, E.nv, len(E.cl), a.budget, a.leaf, len(order), MM), flush=True)
if a.knuth:
    import random, statistics
    rng = random.Random(a.seed)
    ests, sats, depths = [], [], []
    for q in range(a.knuth):
        est, sat, depth, how = knuth_probe(rng)
        ests.append(est); sats.append(sat); depths.append(depth)
        if (q + 1) % 10 == 0 or q + 1 == a.knuth:
            se = statistics.stdev(ests) / len(ests) ** 0.5 if len(ests) > 1 else 0
            print('.. %d descents, %.0f s: estimated nodes %.3g (standard error %.2g), estimated nodes with a model %.3g, mean depth %.1f, max depth %d' % (
                q + 1, time.time() - t0, statistics.mean(ests), se, statistics.mean(sats), statistics.mean(depths), max(depths)), flush=True)
    sys.exit(0)
try:
    dfs(0, root_assum, root_names, mx)
    done = True
except Stop:
    done = False
if cubef:
    cubef.close()
if a.emit:
    with open(a.emit, 'w') as f:
        f.write(''.join(x + '\n' for x in emitted))
    print('# %d open nodes at depth %d written to %s' % (len(emitted), a.maxdepth, a.emit), flush=True)
print('# %s in %.0f s: %s' % ('done' if done else 'stopped at the node limit', time.time() - t0, stats), flush=True)
print('# by depth (unsat, sat, budget): ' + ' '.join('%d:%s' % (d, tuple(v)) for d, v in sorted(by_depth.items())), flush=True)
if done:
    if models:
        res = 'models found: %d' % len(models)
    elif emitted:
        res = '%d nodes deferred' % len(emitted)
    elif stats['leaf_unknown']:
        res = 'open leaves: %d' % stats['leaf_unknown']
    else:
        res = 'UNSAT (every node closed)'
    print('# RESULT: ' + res, flush=True)
