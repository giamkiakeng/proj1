#!/usr/bin/env python3
"""enum_satnode.py OUTDIR [MAXMODELS] [TIMELIMIT] -- how many rules does the satisfiable node of the stable-general tree hold?

F_14 (the formula of certtree.py 14 ... --pump 14) with the 11 transitions of the node as units.  Models are
enumerated up to the transitions that the rule uses in the lines 2..14 and in the half-line up to the anti-diagonal
27 (the other entries of the table are free): after each model the conjunction of its used transitions is blocked.
The models are written to OUTDIR/model_J.txt, and F_14 with the units of the node and the blocking clauses of all
models to OUTDIR/f14_node_blocked.cnf; if the enumeration is complete, this formula is unsatisfiable, and a proof
of that (cadical --lrat, lrat-check, cake_lpr) certifies that there is no further model.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcopy import Model, NAMES, BND
from pysat.solvers import Solver
OUT = sys.argv[1]
MAXM = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
TL = float(sys.argv[3]) if len(sys.argv) > 3 else 600
N = 14
M = Model(5, N, copy=False, sym=False, b1s=True, b3=True, nogh=True, wimp=True, wgap=True, front1=True, pump=14)
E = M.E
code = {NAMES[x]: x for x in range(4)}; code['*'] = BND; code['F'] = 4
cube = 'GLL=A,GAL=B,ALL=B,GBB=A,BBL=L,BLL=A,ALA=B,LAL=L,BLB=L,LBL=B,LLB=L'
S = Solver(name='cadical153')
for c in E.cl:
    S.add_clause(c)
for tr in cube.split(','):
    l, d = tr.split('=')
    S.add_clause([E.T[(code[l[0]], code[l[1]], code[l[2]])][code[d]]])
nm = lambda s: '*' if s == BND else ('F' if s == 4 else NAMES[s])
def used_transitions(tab):
    """transitions used by the lines 2..14 (all rows before firing) and by the half-line up to the anti-diagonal 27"""
    used = set()
    for n in range(2, N + 1):
        row = ['G'] + ['L'] * (n - 1)
        for t in range(2 * n - 2):
            r = ['*'] + row + ['*']
            new = []
            for i in range(1, n + 1):
                e = (r[i - 1], r[i], r[i + 1]); used.add(e); new.append(tab[e])
            row = new
        assert set(row) == {'F'}, n
    # half-line: cells (t, i), t + i <= 27, computed on a long enough line (30 cells)
    L = 30; row = ['G'] + ['L'] * (L - 1); rows = [row]
    for t in range(1, 27):
        r = ['*'] + rows[-1] + ['L']
        new = []
        for i in range(1, L + 1):
            if t + i <= 27:
                e = (r[i - 1], r[i], r[i + 1]); used.add(e); new.append(tab[e])
            else:
                new.append('L' if i > t + 1 else '?')
        rows.append(new)
    return used
t0 = time.time(); models = []; sync = {}
while len(models) < MAXM and time.time() - t0 < TL:
    if not S.solve():
        print('# no further model: the enumeration is complete'); break
    pos = set(v for v in S.get_model() if v > 0)
    tab = {(nm(l), nm(c), nm(r)): nm(next(d for d in range(5) if vs[d] in pos)) for (l, c, r), vs in E.T.items()}
    U = used_transitions(tab)
    models.append((tab, U))
    S.add_clause([-E.T[(code[e[0]], code[e[1]], code[e[2]])][code[tab[e]]] for e in U])
    # which lengths does it synchronize (unused entries as the solver set them)?
    from simlib import ok
    good = tuple(n for n in range(2, 61) if ok(tab, n))
    sync[good] = sync.get(good, 0) + 1
    print('model %d: %d used transitions, synchronizes %s (%.0f s)' % (len(models), len(U), list(good), time.time() - t0), flush=True)
print('# %d models in %.0f s; by synchronized lengths: %s' % (len(models), time.time() - t0, {str(list(k)): v for k, v in sync.items()}))
# write the models, and the formula F_14 + cube + blocking clauses of all models
import hashlib
os.makedirs(OUT, exist_ok=True)
blocks = []
for j, (tab, U) in enumerate(models):
    with open(os.path.join(OUT, 'model_%d.txt' % (j + 1)), 'w') as f:
        f.write('k 5\n')
        for (l, c, r), d in sorted(tab.items()):
            f.write('%s %s %s %s%s\n' % (l, c, r, d, '' if (l, c, r) in U else '   # not used'))
    blocks.append([-E.T[(code[e[0]], code[e[1]], code[e[2]])][code[tab[e]]] for e in sorted(U)])
units = []
for tr in cube.split(','):
    l, d = tr.split('=')
    units.append([E.T[(code[l[0]], code[l[1]], code[l[2]])][code[d]]])
cls = list(E.cl) + units + blocks
with open(os.path.join(OUT, 'f14_node_blocked.cnf'), 'w') as f:
    f.write('p cnf %d %d\n' % (E.nv, len(cls)))
    f.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in cls))
print('# wrote f14_node_blocked.cnf: %d variables, %d clauses (%d of F_14, %d units, %d blocking clauses)' % (E.nv, len(cls), len(E.cl), len(units), len(blocks)))
for j, (tab, U) in enumerate(models):
    for i, (tab2, U2) in enumerate(models):
        if i < j:
            diff = sorted(e for e in U & U2 if tab[e] != tab2[e])
            print('# models %d and %d: used by both with different images: %s; used only by one: %d + %d' % (i + 1, j + 1, ' '.join('%s%s%s:%s/%s' % (e + (tab2[e], tab[e])) for e in diff), len(U2 - U), len(U - U2)))
if len(models) > 1:
    common = set.intersection(*[set((e, tab[e]) for e in U) for tab, U in models])
    print('# transitions used by all models with the same image: %d' % len(common))
