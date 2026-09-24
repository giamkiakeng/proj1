#!/usr/bin/env python3
"""
gencnf.py -- CNF encoding of the bounded minimal-time firing squad problem.

    MT(k, N):  there is a k-state rule delta (states L, G, aux..., F) with
               delta(L,L,L) = delta(L,L,*) = L such that for every length
               2 <= n <= N the line  G L ... L  fires exactly at time 2n-2.

Encoding.  Let C_inf be the space-time diagram of the half-line (general at
cell 1, no right border).  For a line of length n we have
C_n(t,i) = C_inf(t,i) whenever t+i <= 2n-2, because the right border is
first felt by cell n at time n-1 and this influence travels left at speed
at most one.  Hence only C_inf (for t+i <= 2N-2) and, for every n, the
triangle  R_n = {(t,i) : 1<=i<=n, 2n-1-i <= t <= 2n-3}  carry variables.

State codes: L=0, G=1, aux=2..k-2, F=k-1.  Working states W = {0..k-2}.
The border symbol is coded BND = -1.

Optional extras (all logically implied or symmetry breaking, see paper):
  --diff       C_n(2n-1-i,i) != C_inf(2n-1-i,i)            (implied)
  --symbreak   auxiliary states appear in C_inf in increasing order
               of first occurrence (time-major, left to right)
  --leftq      additionally require delta(*,L,L) = L
  --rev        redundant reverse clauses  y=d & nbhd -> T[nbhd]=d
"""
import argparse
import itertools
import sys

BND = -1


class Enc:
    def __init__(self, k, N, leftq=False):
        self.k = k
        self.N = N
        self.F = k - 1
        self.W = list(range(k - 1))
        self.nv = 0
        self.clauses = []
        # table variables T[(l,c,r)][d]
        self.T = {}
        side = [BND] + self.W
        for l in side:
            for c in self.W:
                for r in side:
                    if l == BND and r == BND:
                        continue
                    self.T[(l, c, r)] = [self.new() for _ in range(k)]
        for e, vs in self.T.items():
            self.exactly_one(vs)
        self.fix((0, 0, 0), 0)
        self.fix((0, 0, BND), 0)
        if leftq:
            self.fix((BND, 0, 0), 0)

    def new(self):
        self.nv += 1
        return self.nv

    def add(self, cl):
        self.clauses.append(cl)

    def exactly_one(self, vs):
        self.add(list(vs))
        for a, b in itertools.combinations(vs, 2):
            self.add([-a, -b])

    def fix(self, e, d):
        self.add([self.T[e][d]])

    # a "cell" is either an int (constant state or BND) or a list of
    # k-1 variables (one-hot over W)
    def newcell(self):
        vs = [self.new() for _ in self.W]
        self.exactly_one(vs)
        return vs

    @staticmethod
    def dom(x, W):
        if isinstance(x, int):
            return [(x, None)]
        return [(s, x[s]) for s in W]

    def transition(self, a, b, c, y, rev=False):
        """y = delta(a,b,c).  y is a cell (list), or 'FIRE' (must be F)."""
        W = self.W
        for (al, va), (be, vb), (ga, vc) in itertools.product(
                self.dom(a, W), self.dom(b, W), self.dom(c, W)):
            if al == BND and ga == BND:
                continue
            lits = [-v for v in (va, vb, vc) if v is not None]
            Te = self.T[(al, be, ga)]
            if y == 'FIRE':
                self.add(lits + [Te[self.F]])
            else:
                for d in W:
                    self.add(lits + [-Te[d], y[d]])
                    if rev:
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


def add_pumping(E, vinf, Npump, nlo=4):
    """PUMP(n,n') for nlo <= n < n' <= Npump (see pumping.py): the input words
    of the reflected triangles of n and n' differ on the dependency cone of
    the right end of R_n at time 2n-2.  Only C_inf cells are involved."""
    import pumping
    npairs = 0
    for n in range(nlo, Npump):
        cn = pumping.cone(n)
        if cn is None:
            continue
        for n2 in range(n + 1, Npump + 1):
            lits = []
            satisfied = False
            for kk, d in sorted(cn):
                x = vinf(*pumping.input_cell(n, kk, d))
                y = vinf(*pumping.input_cell(n2, kk, d))
                if isinstance(x, int) and isinstance(y, int):
                    if x != y:
                        satisfied = True
                        break
                    continue
                if isinstance(x, int):
                    x, y = y, x
                if isinstance(y, int):
                    lits.append(-x[y])
                else:
                    dv = E.new()
                    for st in E.W:
                        E.add([-dv, -x[st], -y[st]])
                    lits.append(dv)
            if not satisfied:
                E.add(lits)
                npairs += 1
    return npairs


def add_links(E, vinf, Rall):
    """Determinacy links between reflected triangles of encoded lengths
    n < n': if the input words agree on positions 0..p, every relative cell
    whose dependency cone lies in 0..p has the same value in R_n and R_n'
    (and a firing cell of R_n forces a contradiction: pumping)."""
    import pumping
    ns = sorted(Rall)

    def eqvar(x, y):
        if isinstance(x, int) and isinstance(y, int):
            return True if x == y else False
        if isinstance(x, int):
            x, y = y, x
        e = E.new()
        if isinstance(y, int):
            E.add([-e, x[y]])
            E.add([e, -x[y]])
            return e
        for st in E.W:
            E.add([-x[st], -y[st], e])
            E.add([-e, -x[st], y[st]])
        return e

    for a, n in enumerate(ns):
        for n2 in ns[a + 1:]:
            # prefix-equality chain EQ(p) <-> EQ(p-1) & eq(lower p) & eq(upper p)
            EQ = []
            prev = True
            for p in range(0, n):
                parts = [prev]
                for d in (-2, -1):
                    parts.append(eqvar(vinf(*pumping.input_cell(n, p, d)),
                                       vinf(*pumping.input_cell(n2, p, d))))
                if any(q is False for q in parts):
                    cur = False
                else:
                    lits = [q for q in parts if q is not True]
                    if not lits:
                        cur = True
                    else:
                        cur = E.new()
                        for q in lits:
                            E.add([-cur, q])
                        E.add([cur] + [-q for q in lits])
                EQ.append(cur)
                prev = cur
            R1, R2 = Rall[n], Rall[n2]
            for tau in range(0, n):
                for kk in range(0, tau + 1):
                    p = pumping.cone_max(n, tau, kk)
                    if p is None:
                        continue
                    cond = EQ[p]
                    if cond is False:
                        continue
                    pre = [] if cond is True else [-cond]
                    t1, i1 = n - 1 + tau, n - kk
                    t2, i2 = n2 - 1 + tau, n2 - kk
                    if tau == n - 1:
                        # R_n fires here, R_n' must not (tau < n'-1)
                        E.add(pre)
                        continue
                    x, y = R1[(t1, i1)], R2[(t2, i2)]
                    for st in E.W:
                        E.add(pre + [-x[st], y[st]])
                        E.add(pre + [-y[st], x[st]])


def build(k, N, diff=True, symbreak=True, leftq=False, rev=False, fire_n=None,
          minf=None, tinf=0, npart=None, hpart=None, pump=None, band=None, links=False):
    """minf: anti-diagonal bound of C_inf (default 2N-2); tinf: C_inf also
    contains every cell with t <= tinf.  npart: lengths N < n <= npart for
    which the reflected triangle is added (non-firing only) up to time
    n-1+hpart (limited by the available part of C_inf)."""
    E = Enc(k, N, leftq)
    M = 2 * N - 2
    M1 = max(M, minf or 0)
    inf = {}  # (t,i) -> cell

    def vinf(t, i):
        if i == 0:
            return BND
        if t == 0:
            return 1 if i == 1 else 0
        if i > t + 1:
            return 0
        return inf[(t, i)]

    order = []
    for t in range(1, max(M1, tinf + 1)):
        for i in range(1, t + 2):
            if t + i > M1 and t > tinf:
                break
            inf[(t, i)] = E.newcell()
            order.append((t, i))
    for (t, i) in order:
        E.transition(vinf(t - 1, i - 1), vinf(t - 1, i), vinf(t - 1, i + 1),
                     inf[(t, i)], rev)

    ns = range(2, N + 1) if fire_n is None else fire_n
    Rall = {}
    for n in ns:
        R = {}
        Rall[n] = R

        def val(t, j, n=n, R=R):
            if j == 0 or j == n + 1:
                return BND
            if t + j >= 2 * n - 1:
                return R[(t, j)]
            return vinf(t, j)

        for t in range(n - 1, 2 * n - 2):
            for i in range(1, n + 1):
                if t + i >= 2 * n - 1:
                    R[(t, i)] = E.newcell()
        for t in range(n - 1, 2 * n - 2):
            for i in range(1, n + 1):
                if (t, i) in R:
                    E.transition(val(t - 1, i - 1), val(t - 1, i),
                                 val(t - 1, i + 1), R[(t, i)], rev)
        T = 2 * n - 3
        for i in range(1, n + 1):
            E.transition(val(T, i - 1), val(T, i), val(T, i + 1), 'FIRE')
        if diff and 2 * n - 1 <= M:
            for i in range(2, n + 1):
                t = 2 * n - 1 - i
                E.differ(R[(t, i)], vinf(t, i))

    if npart:
        for n in range(N + 1, npart + 1):
            R = {}
            tmax = min(2 * n - 3, n - 1 + (hpart if hpart is not None else n))

            def val(t, j, n=n, R=R):
                if j == 0 or j == n + 1:
                    return BND
                if t + j >= 2 * n - 1:
                    return R[(t, j)]
                return vinf(t, j)
            # the C_inf cells we need are (t-1, j) with t-1 <= tmax-1
            if not all((tt, j) in inf or j > tt + 1 for tt in range(max(1, n - 2), tmax)
                       for j in range(1, n + 1) if tt + j <= 2 * n - 2):
                break
            for t in range(n - 1, tmax + 1):
                for i in range(1, n + 1):
                    if t + i >= 2 * n - 1:
                        R[(t, i)] = E.newcell()
            for t in range(n - 1, tmax + 1):
                for i in range(1, n + 1):
                    if (t, i) in R:
                        E.transition(val(t - 1, i - 1), val(t - 1, i),
                                     val(t - 1, i + 1), R[(t, i)], rev)

    if pump:
        assert 2 * pump - 2 <= M1, "C_inf too small for the pumping constraints"
        add_pumping(E, vinf, pump)

    if links:
        add_links(E, vinf, Rall)

    if band:
        # band = (h, Nb): for lengths N < n <= Nb, the first h anti-diagonal
        # chains of R_n (cells with 2n-1 <= t+i <= 2n-2+h, t <= 2n-3) and the
        # firing of cells 1..h at time 2n-2
        h, Nb = band
        assert 2 * Nb - 2 <= M1, "C_inf too small for the band constraints"
        done_n = set(ns)
        for n in range(min(ns), Nb + 1):
            if n in done_n:
                continue
            Rb = {}

            def val(t, j, n=n, Rb=Rb):
                if j == 0 or j == n + 1:
                    return BND
                if t + j >= 2 * n - 1:
                    return Rb[(t, j)]
                return vinf(t, j)
            cells = [(t, i) for t in range(n - 1, 2 * n - 2) for i in range(1, n + 1)
                     if 2 * n - 1 <= t + i <= 2 * n - 2 + h]
            for c in cells:
                Rb[c] = E.newcell()
            for (t, i) in cells:
                E.transition(val(t - 1, i - 1), val(t - 1, i), val(t - 1, i + 1), Rb[(t, i)], rev)
            T = 2 * n - 3
            for i in range(1, min(h, n) + 1):
                E.transition(val(T, i - 1), val(T, i), val(T, i + 1), 'FIRE')
            if diff and 2 * n - 1 <= M1:
                for i in range(2, n + 1):
                    t = 2 * n - 1 - i
                    E.differ(Rb[(t, i)], vinf(t, i))

    if symbreak and k >= 5:
        aux = list(range(2, k - 1))
        seen = {a: None for a in aux}  # prefix-OR variable of "a seen"
        for (t, i) in order:
            x = inf[(t, i)]
            for a in aux[1:]:
                # x == a  ->  a-1 seen strictly before
                if seen[a - 1] is None:
                    E.add([-x[a]])
                else:
                    E.add([-x[a], seen[a - 1]])
            for a in aux:
                s = E.new()
                prev = seen[a]
                # s <-> prev or x[a]
                E.add([-x[a], s])
                if prev is None:
                    E.add([-s, x[a]])
                else:
                    E.add([-prev, s])
                    E.add([-s, prev, x[a]])
                seen[a] = s
    return E


def parse_lengths(spec):
    out = []
    for part in spec.split(','):
        if '-' in part:
            a, b = part.split('-')
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def write_dimacs(E, fh):
    fh.write("p cnf %d %d\n" % (E.nv, len(E.clauses)))
    for cl in E.clauses:
        fh.write(" ".join(map(str, cl)) + " 0\n")


SYMS = None


def symname(k, s):
    if s == BND:
        return '*'
    if s == 0:
        return 'L'
    if s == 1:
        return 'G'
    if s == k - 1:
        return 'F'
    return 'ABCDEHIJK'[s - 2]


def decode(E, model_true, fh):
    k = E.k
    fh.write("k %d\n" % k)
    for e, vs in sorted(E.T.items()):
        vals = [d for d in range(k) if vs[d] in model_true]
        assert len(vals) == 1, (e, vals)
        l, c, r = e
        fh.write("%s %s %s %s\n" % (symname(k, l), symname(k, c), symname(k, r),
                                    symname(k, vals[0])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('k', type=int)
    ap.add_argument('N', type=int)
    ap.add_argument('out')
    ap.add_argument('--nodiff', action='store_true')
    ap.add_argument('--nosym', action='store_true')
    ap.add_argument('--leftq', action='store_true')
    ap.add_argument('--rev', action='store_true')
    ap.add_argument('--nmin', type=int, default=2)
    ap.add_argument('--lengths', default=None, help='e.g. 2-9,16,20 (overrides N/nmin)')
    ap.add_argument('--minf', type=int, default=None)
    ap.add_argument('--tinf', type=int, default=0)
    ap.add_argument('--npart', type=int, default=None)
    ap.add_argument('--hpart', type=int, default=None)
    ap.add_argument('--pump', type=int, default=None)
    ap.add_argument('--band', default=None, help='h:Nb')
    ap.add_argument('--links', action='store_true')
    a = ap.parse_args()
    E = build(a.k, a.N, diff=not a.nodiff, symbreak=not a.nosym,
              leftq=a.leftq, rev=a.rev, fire_n=parse_lengths(a.lengths) if a.lengths else range(a.nmin, a.N + 1),
              minf=a.minf, tinf=a.tinf, npart=a.npart, hpart=a.hpart, pump=a.pump,
              band=tuple(map(int, a.band.split(':'))) if a.band else None,
              links=a.links)
    with open(a.out, 'w') as fh:
        write_dimacs(E, fh)
    sys.stderr.write("k=%d N=%d vars=%d clauses=%d\n" % (a.k, a.N, E.nv,
                                                         len(E.clauses)))


if __name__ == '__main__':
    main()
