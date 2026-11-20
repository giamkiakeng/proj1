#!/usr/bin/env python3
"""trisplit2.py GERMFILE N --cubes FILE [--workers W] [--budget C] [--spec SPEC ...] [--order up|down]

Parallel, resumable version of trisplit.py: the same formula (gfix.py, full:2-N and the optional further specs), the
same tree (a node is a set of free transitions with fixed values; a node is split on the first neighbourhood that the
simulation of the lines 2..N needs and that is not fixed yet; the children are pushed in the order F, B, A, G, L).

FILE records 'U cube' (the solver proved the formula UNSAT under the cube) and 'S cube' (the node was split).  On a
restart the lines of FILE are reused:
  * a node whose cube is recorded U is closed without a solver call;
  * a node recorded S, or a proper subset of a cube recorded U, is split without a solver call (the tree is
    deterministic, so a proper subset of a closed cube that is a node of the tree is an ancestor of that cube);
  * every other node is solved.
A truncated last line of FILE (a crash while writing) is cut off before anything is appended.
Since UNSAT under a cube does not depend on the budget, and a stronger formula keeps every UNSAT cube UNSAT, a restart
may use another budget or further specs.

Every worker has its own incremental CaDiCaL solver and its own stack; the children of a split node go onto the stack
of the worker that split it, and an idle worker with an empty stack takes the shallowest node of the largest stack.
"""
import argparse
import multiprocessing as mp
import multiprocessing.connection
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'paper', 'supplementary', 'research'))
import gfix
from pysat.solvers import Solver

ap = argparse.ArgumentParser()
ap.add_argument('germfile'); ap.add_argument('N', type=int)
ap.add_argument('--spec', action='append', default=[])
ap.add_argument('--budget', type=int, default=5000)
ap.add_argument('--order', default='up')
ap.add_argument('--cubes', required=True)
ap.add_argument('--workers', type=int, default=2)
ap.add_argument('--report', type=int, default=120, help='seconds between progress lines')
a = ap.parse_args()

germ = gfix.parse_germ(a.germfile)
specs = ['full:2-%d' % a.N] + a.spec
E, ncells = gfix.build(germ, 5, specs)
G = dict(E.germ)
CHILDREN = ['F', 'B', 'A', 'G', 'L']
print('# specs %s: %d cells, %d variables, %d clauses, %d free transitions; budget %d, %d workers'
      % (' '.join(specs), ncells, E.nv, len(E.cls), len(E.T), a.budget, a.workers), flush=True)


def key_of(fixed):
    return ','.join('%s=%s' % (''.join(nb), d) for nb, d in sorted(fixed.items()))


def line_needs(n, fixed):
    """simulate the line n with the germ and the fixed transitions; the first undefined neighbourhood,
    'ok' if the line fires exactly at 2n-2, 'bad' otherwise"""
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        new = []
        for i in range(n):
            nb = ((row[i - 1] if i > 0 else '*'), row[i], (row[i + 1] if i < n - 1 else '*'))
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
    for n in (range(2, a.N + 1) if a.order == 'up' else range(a.N, 1, -1)):
        r = line_needs(n, fixed)
        if r == 'bad':
            return 'bad'
        if r != 'ok':
            return r
    return 'ok'


def worker(conn):
    S = Solver(name='cadical195', bootstrap_with=E.cls)
    while True:
        msg = conn.recv()
        if msg is None:
            break
        key, assum, nobudget = msg
        if nobudget:
            r = S.solve(assumptions=assum)
        else:
            S.conf_budget(a.budget)
            r = S.solve_limited(assumptions=assum)
        conn.send((key, r, S.get_model() if r is True else None))


# ---- the record of an earlier run
U, SPL = set(), set()
if os.path.exists(a.cubes):
    with open(a.cubes, 'rb') as f:
        data = f.read()
    cut = data.rfind(b'\n') + 1
    if cut < len(data):
        print('# cutting a truncated last line of %d bytes' % (len(data) - cut), flush=True)
        with open(a.cubes, 'r+b') as f:
            f.truncate(cut)
    for ln in data[:cut].decode().split('\n'):
        if not ln:
            continue
        tag, _, key = ln.partition(' ')
        if tag == 'U':
            U.add(key)
        elif tag == 'S':
            SPL.add(key)
ULIST = sorted(U)
INDEX = {}
for j, k in enumerate(ULIST):
    for tok in (k.split(',') if k else []):
        INDEX.setdefault(tok, set()).add(j)
print('# resumed: %d closed cubes, %d split cubes' % (len(U), len(SPL)), flush=True)


def ancestor_of_closed(key):
    """some recorded U cube is a proper superset of this cube (which is not itself recorded U)"""
    if not ULIST:
        return False
    if key == '':
        return True
    sets = []
    for tok in key.split(','):
        s = INDEX.get(tok)
        if not s:
            return False
        sets.append(s)
    sets.sort(key=len)
    cur = set(sets[0])
    for s in sets[1:]:
        cur &= s
        if not cur:
            return False
    return True


out = open(a.cubes, 'a')
W = a.workers
ctx = mp.get_context('fork')
conns, procs = [], []
for w in range(W):
    p_conn, c_conn = ctx.Pipe()
    p = ctx.Process(target=worker, args=(c_conn,), daemon=True)
    p.start()
    conns.append(p_conn); procs.append(p)
stacks = [[] for _ in range(W)]
stacks[0].append({})
stats = dict(solved=0, unsat=0, split=0, sim=0, closed_old=0, split_old=0)
maxdepth = 0


def push_children(w, fixed, nb):
    for d in CHILDREN:
        f2 = dict(fixed); f2[nb] = d
        stacks[w].append(f2)


def next_node(w):
    """the next node that needs the solver, for worker w (None if every stack is empty)"""
    while True:
        if stacks[w]:
            fixed = stacks[w].pop()
        else:
            v = max(range(W), key=lambda x: len(stacks[x]))
            if not stacks[v]:
                return None
            fixed = stacks[v].pop(0)
        key = key_of(fixed)
        if key in U:
            stats['closed_old'] += 1
            continue
        if key in SPL or ancestor_of_closed(key):
            nb = split_var(fixed)
            if nb not in ('ok', 'bad'):
                stats['split_old'] += 1
                push_children(w, fixed, nb)
                continue
        return fixed, key


t0 = tlast = time.time()
busy = {}
found = None
while True:
    for w in range(W):
        if w not in busy:
            nd = next_node(w)
            if nd is not None:
                fixed, key = nd
                busy[w] = (fixed, key)
                maxdepth = max(maxdepth, len(fixed))
                conns[w].send((key, [E.T[nb][d] for nb, d in fixed.items()], False))
    if not busy:
        break
    for c in mp.connection.wait([conns[w] for w in busy]):
        w = conns.index(c)
        key, r, model = c.recv()
        fixed, key0 = busy.pop(w)
        assert key == key0
        stats['solved'] += 1
        if r is False:
            stats['unsat'] += 1
            out.write('U %s\n' % key); out.flush()
        elif r is True:
            found = model
        else:
            nb = split_var(fixed)
            if nb in ('ok', 'bad'):
                # every encoded line is determined by the fixed transitions: decide the node without a budget
                stats['sim'] += 1
                busy[w] = (fixed, key)
                conns[w].send((key, [E.T[x][d] for x, d in fixed.items()], True))
            else:
                stats['split'] += 1
                out.write('S %s\n' % key); out.flush()
                push_children(w, fixed, nb)
    if found is not None:
        break
    if time.time() - tlast > a.report:
        tlast = time.time()
        print('# %.0f s: %s, stacks %s, max depth %d' % (tlast - t0, stats, [len(s) for s in stacks], maxdepth), flush=True)
for c in conns:
    try:
        c.send(None)
    except Exception:
        pass
print('# done in %.0f s: %s' % (time.time() - t0, stats), flush=True)
if found is not None:
    m = set(x for x in found if x > 0)
    tab = {nb: d for nb, vs in E.T.items() for d, v in vs.items() if v in m}
    tab.update(G)
    good = [n for n in range(2, 61) if line_needs(n, tab) == 'ok']
    print('MODEL: a completion synchronizes the lines %s' % good, flush=True)
    print('TABLE ' + ' '.join('%s>%s' % (''.join(nb), d) for nb, d in sorted(tab.items())), flush=True)
    print('RESULT SAT', flush=True)
else:
    print('RESULT UNSAT (every node closed)', flush=True)
for p in procs:
    p.join(timeout=5)
