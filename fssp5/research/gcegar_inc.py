#!/usr/bin/env python3
"""
gcegar_inc.py -- incremental version of gcegar.py: one CaDiCaL instance (PySAT) for the whole run.

Rounds only add constraints (cones of failing cells), so the clauses learned in earlier rounds
stay valid; this script keeps a single solver, adds the new cells and clauses of each round and
solves again.  Same semantics and output as gcegar.py.

usage: gcegar_inc.py GERMFILE|FREE NMAX OUT SPEC... [--budget S] [--P GGG,*GG,GG*] [--Pint GGG] [--k K] [--fine]
   --fine: on a failure add only the cone of the earliest wrong cell (one cell), not of all failing cells
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfix  # noqa: E402
from gcegar import simulate  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


class Inc:
    def __init__(self, germ, k, P, interior=False):
        self.free = germ is None
        self.E = gfix.Enc(k, {} if self.free else germ)
        if P is not None:
            gfix.apply_class(self.E, P, interior)
        self.lines = {}                 # n -> {cell: var dict or 'F'}
        self.H = {}                     # FREE: half-line cells (t, i) -> var dict
        self.hmax = 1                   # FREE: half-line encoded for t + i <= hmax
        self.germval = None if self.free else gfix.halfline(germ, 2)
        self.germ = germ
        self.gM = 2
        self.solver = Solver(name='cd19')
        self.sent = 0

    def val(self, t, i):
        if i == 0:
            return '*'
        if t == 0:
            return 'G' if i == 1 else 'L'
        if i > t + 1:
            return 'L'
        if self.free:
            return self.H[(t, i)]
        return self.germval(t, i)

    def ensure_halfline(self, M):
        if self.free:
            E = self.E
            for s in range(self.hmax + 1, M + 1):
                new = []
                for t in range(1, s):
                    i = s - t
                    if i > t + 1:
                        continue
                    self.H[(t, i)] = E.cell(E.W)
                    new.append((t, i))
                for (t, i) in new:
                    E.transition(self.val(t - 1, i - 1), self.val(t - 1, i), self.val(t - 1, i + 1), self.H[(t, i)])
            self.hmax = max(self.hmax, M)
        elif M > self.gM:
            self.germval = gfix.halfline(self.germ, M)
            self.gM = M

    def add(self, n, cells):
        E = self.E
        self.ensure_halfline(2 * n)
        var = self.lines.setdefault(n, {})
        new = [c for c in sorted(cells) if c not in var]
        for (t, i) in new:
            var[(t, i)] = 'F' if t == 2 * n - 2 else E.cell(E.W)

        def get(t, j):
            if j == 0 or j == n + 1:
                return '*'
            if (t, j) in var:
                return var[(t, j)]
            if t + j <= 2 * n - 2:
                return self.val(t, j)
            raise KeyError((n, t, j))
        for (t, i) in new:
            E.transition(get(t - 1, i - 1), get(t - 1, i), get(t - 1, i + 1), var[(t, i)])
            if t + i == 2 * n - 1 and t < 2 * n - 2:
                c = self.val(t, i)
                if isinstance(c, str):
                    if c in var[(t, i)]:
                        E.cls.append([-var[(t, i)][c]])
                else:
                    for d, x in var[(t, i)].items():
                        if d in c:
                            E.cls.append([-x, -c[d]])

    def solve(self):
        for c in self.E.cls[self.sent:]:
            self.solver.add_clause(c)
        self.sent = len(self.E.cls)
        r = self.solver.solve()
        model = set(x for x in self.solver.get_model() if x > 0) if r else set()
        return r, model

    def table(self, model):
        tab = dict(self.E.germ)
        for nb, vs in self.E.T.items():
            for d, v in vs.items():
                if v in model:
                    tab[nb] = d
        return tab


def first_wrong_cell(tab, n):
    """the earliest cell of R_n (absolute (t, i)) whose value is wrong: F before 2n-2, or not F at 2n-2"""
    c = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        r = ['*'] + c + ['*']
        c = [tab[(r[i - 1], r[i], r[i + 1])] for i in range(1, n + 1)]
        for i, x in enumerate(c, 1):
            if (x == 'F') != (t == 2 * n - 2):
                return (t, i)
    return (2 * n - 2, 1)


def main():
    a = sys.argv[1:]
    germ = gfix.parse_germ(a[0])
    nmax, out = int(a[1]), a[2]
    specs, k, budget, P, fine, interior = [], 5, None, None, False, False
    it = iter(a[3:])
    for x in it:
        if x == '--budget':
            budget = float(next(it))
        elif x == '--k':
            k = int(next(it))
        elif x in ('--P', '--Pint'):
            interior = x == '--Pint'
            P = {tuple(w) for w in next(it).split(',')}
        elif x == '--fine':
            fine = True
        else:
            specs.append(x)
    I = Inc(germ, k, P, interior)
    cone_h = {}
    for sp in specs:
        w = sp.split(':')
        kind, ns = w[0], gfix.parse_range(w[1])
        h = int(w[2]) if len(w) > 2 else None
        for n in ns:
            I.add(n, gfix.region(n, kind, h))
            if kind == 'cone':
                cone_h[n] = max(cone_h.get(n, 0), h or 0)
            elif kind == 'full':
                cone_h[n] = n - 1
    start = time.time()
    for rnd in range(1, 100000):
        if budget is not None and time.time() - start > budget:
            print('STOP: budget exhausted')
            return
        t0 = time.time()
        r, model = I.solve()
        ncells = sum(len(v) for v in I.lines.values())
        print('round %d: cells=%d vars=%d clauses=%d | %s (%.0f s)' % (
            rnd, ncells, I.E.nv, len(I.E.cls), 'SAT' if r else 'UNSAT', time.time() - t0), flush=True)
        if not r:
            print('STOP: UNSAT; constraints: %s' % ' '.join('cone:%d:%d' % (n, h) for n, h in sorted(cone_h.items())))
            return
        tab = I.table(model)
        fail = None
        for n in range(2, nmax + 1):
            f = simulate(tab, n)
            if f:
                fail = (n, f)
                break
        if fail is None:
            with open(out, 'w') as fh:
                fh.write('k %d\n' % k)
                for nb in sorted(tab):
                    fh.write('%s %s %s %s\n' % (nb + (tab[nb],)))
            print('FOUND: all lengths 2..%d synchronize; table written to %s' % (nmax, out))
            return
        n, (what, left) = fail
        if fine:
            cell = first_wrong_cell(tab, n)
            print('   length %d fails: %s -> cell cone of %s' % (n, what, cell), flush=True)
            I.add(n, gfix.region(n, 'cell', cell))
            cone_h.setdefault(n, 0)
            continue
        h = max(n - left, cone_h.get(n, 0))
        cone_h[n] = h
        print('   length %d fails: %s -> cone:%d:%d' % (n, what, n, h), flush=True)
        I.add(n, gfix.region(n, 'cone', h))


if __name__ == '__main__':
    main()
