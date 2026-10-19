#!/usr/bin/env python3
"""
gfix.py -- completion constraints for a fixed half-line (germ), with partial triangles.

The half-line C_inf of a rule is determined by its germ (the transitions it uses) as long as no
other neighbourhood occurs.  With C_inf fixed, every cell of a reflected triangle R_n is a function
of the cells below it, so any set of cells of R_n that is closed under predecessors gives
necessary conditions on the remaining transitions:

  full n     all cells of R_n (t + i >= 2n-1, t <= 2n-2): the line of length n fires exactly at 2n-2
  cone n:h   the cells on which the right h+1 cells at time 2n-2 depend (h = 0: the right end,
             Lemmas 3.1, 3.2 of the note)
  band n:h   the anti-diagonals t + i = 2n-1 .. 2n-2+h (chains 1..h), which decide cells 1..h
  early n:h  the cells of R_n at relative times tau = t-(n-1) <= h (h < n-1: no cell may fire)
  reset n:h:w  early n:h, and every cell with kappa <= tau - w (behind an echo of width w) is L,
             as in Mazoyer's solution (w = 4) until tau is about n/3

Cells at time 2n-2 must be F, all other encoded cells must not be F.  The return chain
(t + i = 2n-1) must differ from C_inf (Lemma 2.3).  Unknowns: the transitions not in the germ.

usage: gfix.py GERMFILE|FREE [k=5] spec... [--fix RULEFILE] [--cnf OUT] [--solve kissat|cadical] [--timeout S]
   spec: full:2-14  cone:15-30  cone:15:7  band:15-80:4   (lengths a-b or a,b,c;
         band takes :h = number of chains; cone takes an optional :h = the cones of the firing
         cells n-h .. n, i.e. the right h+1 cells of the firing row)
"""
import itertools
import os
import subprocess
import sys
import time

STATES = 'LGABCDE'
# lengths n for which the return-chain condition (Lemma 2.3, which needs line n+1 as well) is omitted
NORC = set(int(x) for x in os.environ.get('GFIX_NORC', '').split(',') if x)


def parse_germ(path):
    if path == 'FREE':
        return None
    for ln in open(path):
        w = ln.split()
        if w and w[0] == 'GERM':
            g = {}
            for tr in w[1:]:
                nb, d = tr.split('>')
                g[tuple(nb)] = d
            return g
    raise SystemExit('no GERM line in ' + path)


def load_rule(path):
    tab = {}
    for ln in open(path):
        w = ln.split('#')[0].split()
        if len(w) == 4:
            tab[tuple(w[:3])] = w[3]
    return tab


class Enc:
    def __init__(self, k, germ):
        self.k = k
        self.W = list(STATES[:k - 1])          # working states
        self.S = self.W + ['F']
        self.germ = dict(germ)
        self.germ.setdefault(('L', 'L', 'L'), 'L')
        self.germ.setdefault(('L', 'L', '*'), 'L')
        self.nv = 0
        self.cls = []
        self.rev = os.environ.get('GFIX_REV') == '1'   # redundant clauses: cell values determine T
        self.T = {}                             # free transitions: nbhd -> {d: var}
        side = ['*'] + self.W
        for a in side:
            for b in self.W:
                for c in side:
                    if a == '*' and c == '*':
                        continue
                    if (a, b, c) in self.germ:
                        continue
                    vs = {d: self.new() for d in self.S}
                    self.T[(a, b, c)] = vs
                    self.exactly_one(list(vs.values()))

    def new(self):
        self.nv += 1
        return self.nv

    def exactly_one(self, vs):
        self.cls.append(list(vs))
        for x, y in itertools.combinations(vs, 2):
            self.cls.append([-x, -y])

    def cell(self, values):
        vs = {d: self.new() for d in values}
        self.exactly_one(list(vs.values()))
        return vs

    def transition(self, p, q, r, out):
        """p, q, r: constants (str) or dicts value->var; out: dict value->var or the constant 'F'"""
        dom = lambda x: [(x, None)] if isinstance(x, str) else list(x.items())
        for (a, va), (b, vb), (c, vc) in itertools.product(dom(p), dom(q), dom(r)):
            pre = [-v for v in (va, vb, vc) if v is not None]
            nb = (a, b, c)
            if nb in self.germ:
                g = self.germ[nb]
                if isinstance(out, str):
                    if g != out:
                        self.cls.append(pre)
                elif g in out:
                    self.cls.append(pre + [out[g]])
                else:
                    self.cls.append(pre)
            else:
                Tv = self.T[nb]
                for d, td in Tv.items():
                    if isinstance(out, str):
                        if d != out:
                            self.cls.append(pre + [-td])
                    elif d in out:
                        self.cls.append(pre + [-td, out[d]])
                        if self.rev:
                            self.cls.append(pre + [-out[d], td])
                    else:
                        self.cls.append(pre + [-td])


def halfline(germ, M):
    """C_inf(t, i) for t + i <= M (dict), using the germ only; raises if it is not closed."""
    C = {}
    def val(t, i):
        if i == 0:
            return '*'
        if i > t + 1:
            return 'L'
        return C[(t, i)]
    C[(0, 1)] = 'G'
    for s in range(2, M + 1):          # anti-diagonal t + i = s
        for t in range(1, s):                 # increasing t: (t-1, i+1) is on the same anti-diagonal
            i = s - t
            if i > t + 1:
                continue
            nb = (val(t - 1, i - 1), val(t - 1, i), val(t - 1, i + 1))
            if nb == ('L', 'L', 'L'):
                C[(t, i)] = 'L'
            elif nb in germ:
                C[(t, i)] = germ[nb]
            else:
                raise SystemExit('germ not closed: neighbourhood %s at (t,i)=(%d,%d), anti-diagonal %d'
                                 % (''.join(nb), t, i, s))
    return val


def halfline_vars(E, M, shallow=None):
    """C_inf(t, i) for t + i <= M as variables (one-hot over W, so no half-line cell fires).
    shallow = (D, tmax): also the cells beyond anti-diagonal M at depth t+1-i <= D, for t <= tmax
    (the depth rows near the front; they are closed under predecessors and feed the early rows)"""
    C = {}
    def val(t, i):
        if i == 0:
            return '*'
        if t == 0:
            return 'G' if i == 1 else 'L'
        if i > t + 1:
            return 'L'
        return C[(t, i)]
    for s in range(2, M + 1):
        for t in range(1, s):
            i = s - t
            if i > t + 1:
                continue
            C[(t, i)] = E.cell(E.W)
    if shallow:
        D, tmax = shallow
        for t in range(1, tmax + 1):
            for j in range(0, D + 1):
                i = t + 1 - j
                if i >= 1 and t + i > M:
                    C[(t, i)] = E.cell(E.W)
    for (t, i) in sorted(C):
        E.transition(val(t - 1, i - 1), val(t - 1, i), val(t - 1, i + 1), C[(t, i)])
    return val


def region(n, kind, h=None):
    """cells (t, i) of R_n of the given kind"""
    R = {(t, i) for i in range(1, n + 1) for t in range(n - 1, 2 * n - 1) if t + i >= 2 * n - 1}
    if kind == 'full':
        return R
    if kind == 'band':
        return {(t, i) for (t, i) in R if t + i <= 2 * n - 2 + h}
    if kind == 'early':                                  # relative times tau = t - (n-1) <= h
        return {(t, i) for (t, i) in R if t <= n - 1 + h}
    if kind == 'cell':                                   # cone of the single cell (t, i) = h
        t0, i0 = h
        out, stack = set(), [(t0, i0)]
        while stack:
            t, i = stack.pop()
            if (t, i) in out:
                continue
            out.add((t, i))
            for j in (i - 1, i, i + 1):
                if (t - 1, j) in R:
                    stack.append((t - 1, j))
        return out
    if kind == 'cone':                                   # cones of the firing cells n-h .. n (h = 0: right end)
        out, stack = set(), [(2 * n - 2, i) for i in range(max(1, n - (h or 0)), n + 1)]
        while stack:
            t, i = stack.pop()
            if (t, i) in out:
                continue
            out.add((t, i))
            for j in (i - 1, i, i + 1):
                if (t - 1, j) in R:
                    stack.append((t - 1, j))
        return out
    raise ValueError(kind)


def add_line(E, val, n, cells):
    """encode the cells of R_n in CELLS; with GFIX_SHARE=1, cells that compute the same function of the
    table (same dependency tree down to the same input values and borders) share one variable, across
    all lengths encoded in E (structural hashing; a firing cell meeting a non-firing one is a conflict,
    which is how the pumping lemma shows up)"""
    share = os.environ.get('GFIX_SHARE') == '1'
    if share and not hasattr(E, 'share'):
        E.share, E.ids = {}, {}
    var, key = {}, {}

    def get(t, j):
        if j == 0 or j == n + 1:
            return '*'
        if (t, j) in var:
            return var[(t, j)]
        if t + j <= 2 * n - 2:
            return val(t, j)
        raise KeyError((n, t, j))

    def kget(t, j):
        if j == 0 or j == n + 1:
            return ('*',)
        if (t, j) in var:
            return key[(t, j)]
        c = val(t, j) if t + j <= 2 * n - 2 else None
        if c is None:
            raise KeyError((n, t, j))
        return ('c', c) if isinstance(c, str) else ('h', t, j)
    for (t, i) in sorted(cells):
        fire = t == 2 * n - 2
        if share:
            k = (kget(t - 1, i - 1), kget(t - 1, i), kget(t - 1, i + 1))
            kid = E.ids.setdefault(k, len(E.ids))
            key[(t, i)] = ('v', kid)
            if kid in E.share:
                v = E.share[kid]
                if (v == 'F') != fire:
                    E.cls.append([])                 # the same function must be F and not F
                var[(t, i)] = v
                new = False
            else:
                var[(t, i)] = E.share[kid] = 'F' if fire else E.cell(E.W)
                new = True
        else:
            var[(t, i)] = 'F' if fire else E.cell(E.W)
            new = True
        if new:
            E.transition(get(t - 1, i - 1), get(t - 1, i), get(t - 1, i + 1), var[(t, i)])
        if t + i == 2 * n - 1 and not fire and n not in NORC:   # return chain differs from C_inf
            c = val(t, i)
            v = var[(t, i)]
            if v == 'F':
                continue
            if isinstance(c, str):
                if c in v:
                    E.cls.append([-v[c]])
            else:
                for d, x in v.items():
                    if d in c:
                        E.cls.append([-x, -c[d]])
    return var


def parse_range(s):
    out = []
    for part in s.split(','):
        if '-' in part:
            a, b = part.split('-')
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def apply_class(E, P, interior=False):
    """firing class: the neighbourhoods mapped to F are exactly those of P; with interior=True
    only the neighbourhoods without a border are constrained (the border ones stay free)"""
    def scoped(nb):
        return not interior or (nb[0] != '*' and nb[2] != '*')
    for nb, vs in E.T.items():
        if scoped(nb):
            E.cls.append([vs['F']] if nb in P else [-vs['F']])
    for nb, d in E.germ.items():
        if scoped(nb) and (d == 'F') != (nb in P):
            E.cls.append([])                           # the germ contradicts the class


def equate(E, a, b):
    """the table entries of the neighbourhoods a and b are equal (constants from the germ allowed)"""
    va = E.germ.get(a, E.T.get(a))
    vb = E.germ.get(b, E.T.get(b))
    if va is None or vb is None:
        return
    if isinstance(va, str) and isinstance(vb, str):
        if va != vb:
            E.cls.append([])
    elif isinstance(va, str):
        E.cls.append([vb[va]] if va in vb else [])
    elif isinstance(vb, str):
        E.cls.append([va[vb]] if vb in va else [])
    else:
        for d in va:
            E.cls.append([-va[d], vb[d]])
            E.cls.append([va[d], -vb[d]])


def build(germ, k, specs, P=None, interior=False, upf=None):
    """P: optional set of neighbourhoods (tuples) that are exactly the ones mapped to F
    (with interior=True: exactly the interior ones mapped to F); upf: a state X, adds the
    redundant clauses of the class 'pre-firing configuration X^n for n >= 3' (see add_upf)"""
    free = germ is None
    # GFIX_UNFIX=*GL,GLL: these germ transitions still define the half-line but are free in the table
    # (used for the common relaxation of the two labellings of the complexity-15 half-line)
    unfix = {tuple(w) for w in os.environ.get('GFIX_UNFIX', '').split(',') if w}
    E = Enc(k, {} if free else {nb: d for nb, d in germ.items() if nb not in unfix})
    if P is not None:
        apply_class(E, P, interior)
    be = os.environ.get('GFIX_BE')                # e.g. L,G: the left border acts as L, the right as G
    if be:
        xl, xr = be.split(',')
        for y in E.W:
            for z in E.W:
                if xl != '-':
                    equate(E, ('*', y, z), (xl, y, z))
                if xr != '-':
                    equate(E, (z, y, '*'), (z, y, xr))
    lines = []
    for sp in specs:
        w = sp.split(':')
        kind, ns = w[0], parse_range(w[1])
        h = int(w[2]) if len(w) > 2 else None
        if kind == 'reset':                     # reset:n:T:w = early:n:T, quiescent behind an echo of width w
            lines += [(n, ('reset', int(w[3])), h) for n in ns]
        else:
            lines += [(n, kind, h) for n in ns]
    # half-line encoded to anti-diagonal 2N-2+MARGIN; for FREE, a margin > 0 also forbids F on the
    # anti-diagonals beyond 2N-2, i.e. requires line N+1 not to fire early at its left cells
    margin = int(os.environ.get('GFIX_MARGIN', '2'))
    shallow = None
    if free and os.environ.get('GFIX_SHALLOW') == '1':
        # FREE mode: encode the whole half-line only as far as the non-early regions need it, and for
        # the early/reset regions only the depth rows near the front (depth <= 2T+2) that they read
        full = [2 * n - 2 for n, kind, _ in lines if kind not in ('early',) and not isinstance(kind, tuple)]
        early = [(n, h) for n, kind, h in lines if kind == 'early' or isinstance(kind, tuple)]
        M = (max(full) if full else 2) + margin
        if early:
            shallow = (2 * max(h for _, h in early) + 2, max(n - 1 + h + 1 for n, h in early))
    else:
        M = max(2 * n - 2 for n, _, _ in lines) + margin
    val = halfline_vars(E, M, shallow) if free else halfline(germ, M)
    ncells = 0
    for n, kind, h in lines:
        cells = region(n, 'early' if isinstance(kind, tuple) else kind, h)
        ncells += len(cells)
        var = add_line(E, val, n, cells)
        if isinstance(kind, tuple):             # reset: R_n(tau, kappa) = L for kappa <= tau - w
            wid = kind[1]
            for (t, i), v in var.items():
                if t + i >= 2 * n - 1 + wid:
                    E.cls.append([v['L']] if isinstance(v, dict) else [])
        if upf is not None and n >= 3:
            add_upf(E, val, n, var, upf)
    return E, ncells


def add_upf(E, val, n, var, X):
    """redundant clauses for the class 'pre-firing configuration X^n' (n >= 3): the encoded cells
    of line n at time 2n-3 are X, and so is the half-line cell (2n-3, 1)"""
    for (t, i), v in var.items():
        if t == 2 * n - 3:
            E.cls.append([v[X]] if X in v else [])
    c = val(2 * n - 3, 1)
    if isinstance(c, str):
        if c != X:
            E.cls.append([])
    else:
        E.cls.append([c[X]] if X in c else [])


def write_cnf(E, path, extra=()):
    with open(path, 'w') as fh:
        fh.write('p cnf %d %d\n' % (E.nv, len(E.cls) + len(extra)))
        for c in list(E.cls) + list(extra):
            fh.write(' '.join(map(str, c)) + ' 0\n')


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    germ = parse_germ(a[0])
    k, specs, fix, out, solver, timeout = 5, [], None, None, None, 3600
    it = iter(a[1:])
    for x in it:
        if x == '--fix':
            fix = next(it)
        elif x == '--cnf':
            out = next(it)
        elif x == '--solve':
            solver = next(it)
        elif x == '--timeout':
            timeout = int(next(it))
        elif x.isdigit():
            k = int(x)
        else:
            specs.append(x)
    t0 = time.time()
    E, ncells = build(germ, k, specs)
    units = []
    if fix:
        tab = load_rule(fix)
        for nb, vs in E.T.items():
            if nb in tab:
                units.append([vs[tab[nb]]])
    print('k=%d specs=%s cells=%d vars=%d clauses=%d free transitions=%d (%.1f s)'
          % (k, ' '.join(specs), ncells, E.nv, len(E.cls), len(E.T), time.time() - t0), flush=True)
    if out:
        write_cnf(E, out, units)
    if solver:
        from pysat.solvers import Solver
        if solver == 'cadical':
            with Solver(name='cd19', bootstrap_with=E.cls + units) as s:
                t1 = time.time()
                r = s.solve()
                print('cadical:', 'SAT' if r else 'UNSAT', '%.1f s' % (time.time() - t1))
                if r:
                    m = set(x for x in s.get_model() if x > 0)
                    print('TABLE', ' '.join('%s>%s' % (''.join(nb), d)
                                            for nb, vs in sorted(E.T.items()) for d, v in vs.items() if v in m))
        else:
            path = out or '/tmp/claude-0/gfix_%d.cnf' % os.getpid()
            if not out:
                write_cnf(E, path, units)
            t1 = time.time()
            p = subprocess.run(['/home/user/tools/kissat/build/kissat', '-q', '--time=%d' % timeout, path],
                               capture_output=True, text=True)
            st = [l for l in p.stdout.splitlines() if l.startswith('s ')]
            print('kissat:', st[0] if st else 'UNKNOWN', '%.1f s' % (time.time() - t1))


if __name__ == '__main__':
    main()
