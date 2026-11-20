#!/usr/bin/env python3
"""trisplit.py GERMFILE N [--spec SPEC ...] [--budget C] [--order up|down] [--cubes OUT] [--maxnodes M]

First-pass tree search for 'a rule with this germ synchronizes the lines 2..N' (the formula of gfix.py, full:2-N and the
optional further specs), with one incremental CaDiCaL solver.

A node is a set of free transitions with fixed values.  At a node the solver is called under these assumptions with a
conflict budget:  UNSAT -> closed (the cube is written to OUT as 'U cube');  SAT -> a model: the germ is completed to a
table that synchronizes the encoded lines (reported, search stops);  budget -> the node is split.
Splitting: the lines are simulated (order 'up': n = 2, 3, ..., N; 'down': n = N, N-1, ..., 2) with the germ, the half-line
and the fixed transitions; the first neighbourhood that is needed and not yet fixed is split on its values (L, G, A, B,
F).  If every line is fully determined by the fixed transitions, the node is closed by simulation.
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'paper', 'supplementary', 'research'))
import gfix
from pysat.solvers import Solver

ap = argparse.ArgumentParser()
ap.add_argument('germfile'); ap.add_argument('N', type=int)
ap.add_argument('--spec', action='append', default=[])
ap.add_argument('--budget', type=int, default=5000)
ap.add_argument('--order', default='up')
ap.add_argument('--cubes', default='')
ap.add_argument('--maxnodes', type=int, default=10 ** 9)
ap.add_argument('--knuth', type=int, default=0, help='R random descents: estimate the size of the tree and stop')
ap.add_argument('--seed', type=int, default=1)
a = ap.parse_args()

germ = gfix.parse_germ(a.germfile)
specs = ['full:2-%d' % a.N] + a.spec
E, ncells = gfix.build(germ, 5, specs)
print('# specs %s: %d cells, %d variables, %d clauses, %d free transitions' % (' '.join(specs), ncells, E.nv, len(E.cls), len(E.T)), flush=True)
S = Solver(name='cadical195', bootstrap_with=E.cls)
G = dict(E.germ)
HL = gfix.halfline(G, 2 * a.N)


def line_needs(n, fixed):
    """simulate the line n with the germ and the fixed transitions; return the first undefined neighbourhood,
    'ok' if it fires exactly at 2n-2, 'bad' otherwise"""
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        nbs = [((row[i - 1] if i > 0 else '*'), row[i], (row[i + 1] if i < n - 1 else '*')) for i in range(n)]
        new = []
        for nb in nbs:
            if nb in G:
                new.append(G[nb])
            elif nb in fixed:
                new.append(fixed[nb])
            else:
                return nb
        row = new
        if 'F' in row:
            return 'ok' if (t == 2 * n - 2 and all(x == 'F' for x in row)) else 'bad'
    return 'bad'


def split_var(fixed):
    order = range(2, a.N + 1) if a.order == 'up' else range(a.N, 1, -1)
    for n in order:
        r = line_needs(n, fixed)
        if r == 'bad':
            return 'bad'
        if r != 'ok':
            return r
    return 'ok'


if a.knuth:
    import random, statistics
    rng = random.Random(a.seed)
    ests, depths = [], []
    for r in range(a.knuth):
        fixed, w, tot, d = {}, 1, 1, 0
        S.conf_budget(a.budget)
        res = S.solve_limited(assumptions=[E.T[nb][v] for nb, v in fixed.items()])
        while res is None:
            nb = split_var(fixed)
            if nb in ('ok', 'bad'):
                break
            live = []
            for v in ['L', 'G', 'A', 'B', 'F']:
                f2 = dict(fixed); f2[nb] = v
                S.conf_budget(a.budget)
                r2 = S.solve_limited(assumptions=[E.T[x][y] for x, y in f2.items()])
                if r2 is True:
                    print('probe found a model', flush=True)
                if r2 is None:
                    live.append(f2)
            tot += 5 * w          # the 5 children of each undecided node of this level
            d += 1
            if not live:
                break
            w *= len(live)
            fixed = rng.choice(live)
        ests.append(tot); depths.append(d)
        print('probe %d: depth %d, estimate %d; running mean %.3g' % (r + 1, d, tot, statistics.mean(ests)), flush=True)
    print('KNUTH mean %.3g, median %.3g, max %.3g, mean depth %.1f' % (statistics.mean(ests), statistics.median(ests), max(ests), statistics.mean(depths)))
    sys.exit(0)
cubes = open(a.cubes, 'w') if a.cubes else None
stats = {'nodes': 0, 'unsat': 0, 'budget': 0, 'sim': 0}
t0 = time.time()
stack = [dict()]
found = None
while stack:
    fixed = stack.pop()
    stats['nodes'] += 1
    if stats['nodes'] > a.maxnodes:
        print('# node limit reached', flush=True); break
    assum = [E.T[nb][d] for nb, d in fixed.items()]
    S.conf_budget(a.budget)
    r = S.solve_limited(assumptions=assum)
    if r is False:
        stats['unsat'] += 1
        if cubes:
            cubes.write('U ' + ','.join('%s=%s' % (''.join(nb), d) for nb, d in sorted(fixed.items())) + '\n')
        continue
    if r is True:
        m = set(x for x in S.get_model() if x > 0)
        tab = {nb: d for nb, vs in E.T.items() for d, v in vs.items() if v in m}
        found = tab
        break
    stats['budget'] += 1
    nb = split_var(fixed)
    if nb in ('ok', 'bad'):
        # every encoded line is determined by the fixed transitions; the solver could not decide within the budget,
        # so solve without a budget
        r = S.solve(assumptions=assum)
        stats['sim'] += 1
        if r is True:
            m = set(x for x in S.get_model() if x > 0)
            found = {nb2: d for nb2, vs in E.T.items() for d, v in vs.items() if v in m}
            break
        if cubes:
            cubes.write('U ' + ','.join('%s=%s' % (''.join(x), d) for x, d in sorted(fixed.items())) + '\n')
        stats['unsat'] += 1
        continue
    for d in ['F', 'B', 'A', 'G', 'L']:
        f2 = dict(fixed); f2[nb] = d
        stack.append(f2)
    if stats['nodes'] % 200 == 0:
        print('# %.0f s: %s, open %d, depth %d' % (time.time() - t0, stats, len(stack), len(fixed)), flush=True)
print('# done in %.0f s: %s' % (time.time() - t0, stats), flush=True)
if found:
    tab = dict(found); tab.update(G)
    good = [n for n in range(2, 61) if line_needs(n, tab) == 'ok']
    print('MODEL: a completion synchronizes the lines %s' % good, flush=True)
    print('TABLE ' + ' '.join('%s>%s' % (''.join(nb), d) for nb, d in sorted(tab.items())), flush=True)
    print('RESULT SAT')
else:
    print('RESULT ' + ('UNSAT (every node closed)' if not stack else 'OPEN (stopped)'), flush=True)
