#!/usr/bin/env python3
"""
mcopy.py -- minimal-time firing squads with an exact recursive structure (the scheme of Mazoyer's solution).

Formula.  k states (L=0, G=1, auxiliaries 2..k-2, F=k-1), lengths nmin..N.  The rule must synchronize every
length nmin <= n <= N at time 2n-2 (the formula MT of the paper), and in addition every line must contain
verbatim copies of the diagrams of shorter lines:

  chain of cuts of the line n:  r_0 = n;  while m(r_j) >= mmin:  the sub-line  [r_j - m + 1, r_j]  of length
  m = m(r_j) is a "fresh" line of length m that fires at 2n-2, that is

        C_n(T + s, r_j - m + i) = C_m(s, i)      for all  s >= S0,  1 <= i <= m,     T = 2n - 2m;

  then r_{j+1} = r_j - m.   Cut function  m(r) = (r + a) // 3  (Mazoyer's solution: a = 2, S0 = 2, mmin = 3).

The copies are imposed by identifying variables, so the copied regions cost nothing; what is left of a
reflected triangle is the band that the echo of the right end crosses and the part next to the general.

usage: mcopy.py K N [--a A] [--s0 S0] [--mmin M] [--nmin 2] [--fix TABLE] [--cnf FILE] [--solve SOLVER]
                    [--time SEC] [--out TABLE] [--nocopy] [--half M]
"""
import argparse
import itertools
import os
import shutil
import subprocess
import sys
import tempfile
import time

BND = -1
NAMES = 'LGABCDEH'


class Enc:
    def __init__(self, k, rev=True):
        self.k, self.F, self.W = k, k - 1, list(range(k - 1))
        self.nv, self.cl, self.rev = 0, [], rev
        self.level, self.lev = 0, []
        self.T = {}
        side = [BND] + self.W
        for l in side:
            for c in self.W:
                for r in side:
                    if l == BND and r == BND:
                        continue
                    self.T[(l, c, r)] = [self.new() for _ in range(k)]
        for vs in self.T.values():
            self.exactly_one(vs)
        self.add([self.T[(0, 0, 0)][0]])
        self.add([self.T[(0, 0, BND)][0]])
        self.seen = set()
        self.ntrans = 0

    def new(self):
        self.nv += 1
        return self.nv

    def add(self, c):
        self.cl.append(c)
        self.lev.append(self.level)

    def exactly_one(self, vs):
        self.add(list(vs))
        for x, y in itertools.combinations(vs, 2):
            self.add([-x, -y])

    def newcell(self):
        vs = tuple(self.new() for _ in self.W)
        self.exactly_one(vs)
        return vs

    def dom(self, x):
        if isinstance(x, int):
            return [(x, None)]
        return [(s, x[s]) for s in self.W]

    def transition(self, a, b, c, y):
        """y = delta(a, b, c); y is a cell, a constant, or 'FIRE'.  Emitted once per (a, b, c, y)."""
        key = (a, b, c, y)
        if key in self.seen:
            return
        self.seen.add(key)
        self.ntrans += 1
        for (al, va), (be, vb), (ga, vc) in itertools.product(self.dom(a), self.dom(b), self.dom(c)):
            lits = [-v for v in (va, vb, vc) if v is not None]
            Te = self.T[(al, be, ga)]
            if y == 'FIRE':
                self.add(lits + [Te[self.F]])
            elif isinstance(y, int):
                self.add(lits + [Te[y]])
            else:
                for d in self.W:
                    self.add(lits + [-Te[d], y[d]])
                    if self.rev:
                        self.add(lits + [-y[d], Te[d]])
                self.add(lits + [-Te[self.F]])

    def differ(self, x, y):
        if isinstance(x, int) and isinstance(y, int):
            if x == y:
                self.add([])
            return
        if isinstance(x, int):
            x, y = y, x
        if isinstance(y, int):
            self.add([-x[y]])
        else:
            for s in self.W:
                self.add([-x[s], -y[s]])

    def equal(self, x, y):
        if x is y or x == y:
            return
        if isinstance(x, int) and isinstance(y, int):
            self.add([])
            return
        if isinstance(x, int):
            x, y = y, x
        if isinstance(y, int):
            self.add([x[y]])
        else:
            for s in self.W:
                self.add([-x[s], y[s]])
                self.add([x[s], -y[s]])


def chain(n, a, mmin, mfun=None):
    """the cuts (p, m, T) of the line of length n: sub-line [p, p+m-1], fresh time zero at T = 2n - 2m"""
    cuts, r = [], n
    while True:
        m = mfun(r) if mfun else (r + a) // 3
        if m < mmin or m >= r:
            break
        cuts.append((r - m + 1, m, 2 * n - 2 * m))
        r -= m
    return cuts


class Model:
    def __init__(self, k, N, a=2, s0=2, mmin=3, nmin=2, copy=True, half=None, rev=True, sym=True, levels=99,
                 mfun=None, wake=0, margin=0, gstatic=None, period=0, ctheta=2, b3=False, b1=False, b4=False, b2=None, early=None, pump=0, b1s=False, b3w=False, nogh=False):
        self.wake, self.margin = wake, margin
        self.period, self.ctheta = period, ctheta
        self.E = E = Enc(k, rev)
        self.k, self.N, self.a, self.s0, self.mmin, self.nmin = k, N, a, s0, mmin, nmin
        self.early = early                            # (N2, T): the first T rows after the reflection of the lines up to N2
        NH = max(N, early[0]) if early else N
        self.M = half if half else 2 * NH - 1         # the half-line carries variables for t + i <= M
        self.Hc, self.Rc = {}, {}
        self.cuts = {n: (chain(n, a, mmin, mfun)[:levels] if copy else []) for n in range(nmin, N + 1)}
        if early:
            assert not copy, 'early rows are implemented without copies only'
            for n in range(N + 1, early[0] + 1):
                self.cuts[n] = []
        for n, cs in self.cuts.items():
            for p, m, T in cs:
                assert m >= nmin, (n, p, m)
                # the copied region lies in the reflected triangle
                assert T + s0 + p >= 2 * n - 1, ('copy region reaches the half-line zone', n, p, m, T)
        # half-line transitions
        for t in range(0, self.M):
            for i in range(1, min(t + 2, self.M - t - 1) + 1):          # cell (t+1, i), t+1+i <= M
                E.level = nmin if early else max(nmin, (t + 1 + i + 2) // 2)   # needed from the line of this length on
                E.transition(self.H(t, i - 1), self.H(t, i), self.H(t, i + 1), self.H(t + 1, i))
        # the front is never quiescent while some line n <= N still waits for it
        for t in range(1, NH - 1):
            E.level = nmin if early else max(nmin, t + 2)
            E.differ(self.H(t, t + 1), 0)
        # early rows of the lines up to N2: no F in the first T rows after the reflection, return chain != half-line
        if early:
            N2, Te = early
            E.level = nmin
            for n in range(nmin, N2 + 1):
                for t in range(n - 2, min(n - 1 + Te, 2 * n - 3)):
                    for i in range(max(1, 2 * n - 2 - t), n + 1):
                        E.transition(self.cell(n, t, i - 1), self.cell(n, t, i), self.cell(n, t, i + 1), self.cell(n, t + 1, i))
                for i in range(max(2, n - Te), n + 1):
                    t = 2 * n - 1 - i
                    if t + i <= self.M and t <= 2 * n - 3:
                        E.differ(self.cell(n, t, i), self.H(t, i))
        # lines
        for n in range(nmin, N + 1):
            E.level = n
            for t in range(n - 2, 2 * n - 2):
                for i in range(max(1, 2 * n - 2 - t), n + 1):           # cell (t+1, i) with t+1+i >= 2n-1
                    y = 'FIRE' if t + 1 == 2 * n - 2 else self.cell(n, t + 1, i)
                    E.transition(self.cell(n, t, i - 1), self.cell(n, t, i), self.cell(n, t, i + 1), y)
            # return chain differs from the half-line (Lemma 2.4 of the paper; redundant)
            for i in range(2, n + 1):
                t = 2 * n - 1 - i
                if t + i <= self.M and t <= 2 * n - 3:
                    E.differ(self.cell(n, t, i), self.H(t, i))
        if pump:      # PUMP(n, n') for 4 <= n < n' <= pump (Lemma 3.3 of the paper), on the half-line
            assert 2 * pump - 2 <= self.M, 'the half-line must reach the anti-diagonal 2*pump-2'
            E.level = nmin
            for q in (os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'paper', 'supplementary', 'src'),
                      ):
                if os.path.isdir(q) and q not in sys.path:
                    sys.path.insert(0, q)
            import gencnf
            self.npump = gencnf.add_pumping(E, self.H, pump)
        E.level = 0
        if b3:        # (B3), strong reading: exactly the neighbourhoods GGG, *GG and GG* give F
            for e, vs in E.T.items():
                E.add([vs[E.F]] if e in ((1, 1, 1), (BND, 1, 1), (1, 1, BND)) else [-vs[E.F]])
        if b1:        # (B1), weak reading: delta(x, G, y) = G for working states x, y, not both G
            for e, vs in E.T.items():
                if e[1] == 1 and e[0] != BND and e[2] != BND and (e[0], e[2]) != (1, 1):
                    E.add([vs[1]])
        if b2:        # (B2): delta(I(z), I(y), I(x)) = I(delta(x, y, z)) for an involution I of the states
            I = {x: x for x in list(range(k)) + [BND]}
            if b2 != 'id':
                u, v = NAMES.index(b2[0]), NAMES.index(b2[1])
                I[u], I[v] = v, u
            for (x, y, z), vs in E.T.items():
                ws = E.T[(I[z], I[y], I[x])]
                for d in range(k):
                    if vs[d] != ws[I[d]]:
                        E.add([-vs[d], ws[I[d]]])
        if b1s:       # (B1), strong reading: delta(x, G, y) = G unless x and y are both G or a border
            for e, vs in E.T.items():
                if e[1] == 1 and not (e[0] in (1, BND) and e[2] in (1, BND)):
                    E.add([vs[1]])
        if b3w:       # (B3), weak reading: GGG, *GG and GG* give F
            for e in ((1, 1, 1), (BND, 1, 1), (1, 1, BND)):
                E.add([E.T[e][E.F]])
        if nogh:      # consequence of (B1) strong and (B3) weak: the first cell is always G, and no other cell of the half-line is G
            for (t, i), x in sorted(self.Hc.items()):
                E.add([x[1]] if i == 1 else [-x[1]])
        if b4:        # (B4): delta(G, v, G) = G for v != G
            for e, vs in E.T.items():
                if e[0] == 1 and e[2] == 1 and e[1] != 1:
                    E.add([vs[1]])
        if gstatic is not None:
            for t in range(gstatic, self.M):
                E.level = max(nmin, (t + 1 + 2) // 2)
                E.equal(self.H(t, 1), 1)
        E.level = nmin
        if sym and k >= 5:
            self.symmetry()

    def H(self, t, i):
        if i < 1:
            return BND
        if i > t + 1:
            return 0
        if t == 0:
            return 1
        assert t + i <= self.M, (t, i)
        if self.period:
            # depth row j = t + 1 - i is periodic from time 2j + ctheta on: C(t, i) = C(t - P, i - P)
            j, P = t + 1 - i, self.period
            while t - P >= 2 * j + self.ctheta and t - P >= 1:
                t, i = t - P, i - P
        if (t, i) not in self.Hc:
            self.Hc[(t, i)] = self.E.newcell()
        return self.Hc[(t, i)]

    def cell(self, n, t, i):
        if i < 1 or i > n:
            return BND
        if t + i <= 2 * n - 2:
            return self.H(t, i)
        for p, m, T in self.cuts[n]:
            if p <= i <= p + m - 1:
                if t >= T + self.s0:
                    return self.cell(m, t - T, i - p + 1)
                # the echo leaves quiescent cells: more than `wake` cells behind the return chain, outside the seed
                if self.wake and t + i >= 2 * n - 1 + self.wake and i > p + self.s0 + self.margin:
                    return 0
        if (n, t, i) not in self.Rc:
            self.Rc[(n, t, i)] = self.E.newcell()
        return self.Rc[(n, t, i)]

    def symmetry(self):
        """auxiliary states first occur on the half-line in increasing order (time-major, left to right)"""
        E = self.E
        cells = [self.Hc[q] for q in sorted(self.Hc)]
        for s in range(2, self.k - 2):
            prev = None
            for c in cells:
                if prev is None:
                    E.add([-c[s + 1]])
                else:
                    E.add([-c[s + 1], prev])
                cur = E.new()
                E.add([-cur, c[s]] + ([prev] if prev is not None else []))
                prev = cur

    def fix_table(self, tab):
        code = {NAMES[s]: s for s in range(self.k - 1)}
        code['F'] = self.k - 1
        code['*'] = BND
        for (l, c, r), d in tab.items():
            e = (code[l], code[c], code[r])
            if e in self.E.T:
                self.E.add([self.E.T[e][code[d]]])

    def write(self, path, perm=None):
        E = self.E
        self.perm = perm
        with open(path, 'w') as f:
            f.write('p cnf %d %d\n' % (E.nv, len(E.cl)))
            if perm == 'rev':          # reverse the numbering: the table variables get the largest indices
                nv = E.nv
                f.write(''.join(' '.join(str((nv + 1 - v) if v > 0 else -(nv + 1 + v)) for v in c) + ' 0\n' for c in E.cl))
            else:
                f.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in E.cl))

    def table(self, model):
        E = self.E
        if getattr(self, 'perm', None) == 'rev':
            model = [(E.nv + 1 - v) if v > 0 else -(E.nv + 1 + v) for v in model]
        pos = set(v for v in model if v > 0)
        nm = lambda s: '*' if s == BND else ('F' if s == self.k - 1 else NAMES[s])
        return {(nm(l), nm(c), nm(r)): nm(next(d for d in range(self.k) if vs[d] in pos))
                for (l, c, r), vs in E.T.items()}


def run_solver(solver, cnf, tlim, extra=()):
    binp = os.environ.get(solver.upper()) or shutil.which(solver)        # KISSAT / CADICAL, or the PATH
    if not binp:
        sys.exit('%s not found: set the environment variable %s' % (solver, solver.upper()))
    cmd = [binp, '-q'] + list(extra) + [cnf]
    if tlim:
        cmd = ['timeout', str(tlim)] + cmd
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    status, model = 'UNKNOWN', []
    for ln in r.stdout.split('\n'):
        if ln.startswith('s '):
            status = ln[2:].strip()
        elif ln.startswith('v '):
            model += [int(x) for x in ln[2:].split()]
    return status, model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('k', type=int)
    ap.add_argument('N', type=int)
    ap.add_argument('--a', type=int, default=2)
    ap.add_argument('--s0', type=int, default=2)
    ap.add_argument('--mmin', type=int, default=3)
    ap.add_argument('--nmin', type=int, default=2)
    ap.add_argument('--levels', type=int, default=99)
    ap.add_argument('--half', type=int)
    ap.add_argument('--fix')
    ap.add_argument('--cnf')
    ap.add_argument('--solve')
    ap.add_argument('--time', type=int, default=0)
    ap.add_argument('--out')
    ap.add_argument('--nocopy', action='store_true')
    ap.add_argument('--norev', action='store_true')
    ap.add_argument('--nosym', action='store_true')
    ap.add_argument('--opt', action='append', default=[])
    ap.add_argument('--wake', type=int, default=0)
    ap.add_argument('--margin', type=int, default=0)
    ap.add_argument('--gstatic', type=int)
    ap.add_argument('--period', type=int, default=0)
    ap.add_argument('--perm')
    ap.add_argument('--b3', action='store_true')
    ap.add_argument('--b1', action='store_true')
    ap.add_argument('--b4', action='store_true')
    ap.add_argument('--b2')
    ap.add_argument('--early', type=int, nargs=2, metavar=('N2', 'T'))
    ap.add_argument('--pump', type=int, default=0)
    ap.add_argument('--b1s', action='store_true')
    ap.add_argument('--b3w', action='store_true')
    ap.add_argument('--nogh', action='store_true')
    ap.add_argument('--ctheta', type=int, default=2)
    a = ap.parse_args()
    t0 = time.time()
    M = Model(a.k, a.N, a.a, a.s0, a.mmin, a.nmin, not a.nocopy, a.half, not a.norev, not a.nosym, a.levels,
              None, a.wake, a.margin, a.gstatic, a.period, a.ctheta, a.b3, a.b1, a.b4, a.b2, tuple(a.early) if a.early else None, a.pump, a.b1s, a.b3w, a.nogh)
    if a.fix:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from simlib import load
        M.fix_table(load(a.fix)[1])
    E = M.E
    print('k=%d N=%d a=%d s0=%d mmin=%d wake=%d: %d vars, %d clauses, %d transitions, %d half-line cells, %d triangle cells (%.1f s)'
          % (a.k, a.N, a.a, a.s0, a.mmin, a.wake, E.nv, len(E.cl), E.ntrans, len(M.Hc), len(M.Rc), time.time() - t0), flush=True)
    cnf = a.cnf or os.path.join(tempfile.gettempdir(), 'mc_k%d_N%d_a%d_s%d_m%d_%d.cnf' % (
        a.k, a.N, a.a, a.s0, a.mmin, os.getpid()))
    M.write(cnf, a.perm)
    if not a.solve:
        return
    t1 = time.time()
    status, model = run_solver(a.solve, cnf, a.time, a.opt)
    print('%s %s (%.1f s)' % (a.solve, status, time.time() - t1), flush=True)
    if status == 'SATISFIABLE':
        tab = M.table(model)
        out = a.out or cnf[:-4] + '.rule.txt'
        with open(out, 'w') as f:
            f.write('# mcopy.py %s\nk %d\n' % (' '.join(sys.argv[1:]), a.k))
            for (l, c, r), d in tab.items():
                f.write('%s %s %s %s\n' % (l, c, r, d))
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from simlib import ok
        good = [n for n in range(2, 4 * a.N) if ok(tab, n)]
        if any(n not in good for n in range(a.nmin, a.N + 1)):
            print('MODEL CHECK FAILED: the decoded rule does not synchronize every length %d..%d' % (a.nmin, a.N))
        print('rule written to', out)
        print('synchronized lengths up to %d: %s' % (4 * a.N - 1, good))
    if not a.cnf:
        os.remove(cnf)


if __name__ == '__main__':
    main()
