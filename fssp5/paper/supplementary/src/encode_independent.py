#!/usr/bin/env python3
"""
encode_independent.py -- a second, independent encoder of the unsatisfiable formulas of the paper.

It is written from the definitions of the paper (Section 2: lines and synchronization; Lemma 3.2 and
the pumping lemma; Definition 5.4; Section 6.5: Balzer's conditions in the weak reading) and from the
clause schemas (E1)-(E5) of Appendix A, and shares no code with the generators gencnf.py, gfix.py,
germcert.py, balzer.py and balzer_k.py.  It encodes the conditions literally: no structural sharing,
no symmetry breaking, the cones of the right ends found by a search over predecessors, and the
formulas G_k(T, N1, C) exactly as in Definition 5.4 (without the return chains of the complete
lines, which Appendix A shows to be implied).

  python3 encode_independent.py test [--quick]   differential test against the direct evaluation of
                                                 encoding_check.py, on the tables that it uses
  python3 encode_independent.py write DIR        write the eight formulas to DIR/*.cnf
  python3 encode_independent.py solve DIR        write them and solve the seven smaller ones with
                                                 PySAT's CaDiCaL (balzer_id_12 is left to Kissat)
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results')


class Encoder:
    """Boolean variables for a k-state rule table and for cells; clauses per Appendix A."""

    def __init__(self, k):
        self.k = k
        self.S = ['L', 'G'] + ['A', 'B', 'C', 'D', 'E'][:k - 3] + ['F']
        self.W = self.S[:-1]                       # working states
        self.nv, self.cls = 0, []
        self.x = {}                                # (E1): neighbourhood -> {state: variable}
        for a in self.W + ['*']:
            for b in self.W:
                for c in self.W + ['*']:
                    if (a, c) != ('*', '*'):
                        self.x[(a, b, c)] = {s: self.var() for s in self.S}
                        self.exactly_one(list(self.x[(a, b, c)].values()))
        self.cls.append([self.x[('L', 'L', 'L')]['L']])
        self.cls.append([self.x[('L', 'L', '*')]['L']])
        self.half, self.R, self.M = {}, {}, None

    def var(self):
        self.nv += 1
        return self.nv

    def exactly_one(self, vs):
        self.cls.append(list(vs))
        self.cls.extend([-vs[i], -vs[j]] for i in range(len(vs)) for j in range(i + 1, len(vs)))

    def cell(self):
        """(E2): a cell in a working state"""
        c = {s: self.var() for s in self.W}
        self.exactly_one(list(c.values()))
        return c

    @staticmethod
    def options(c):
        return [(c, None)] if isinstance(c, str) else list(c.items())

    def rule(self, u, p1, p2, p3):
        """(E3): u = delta(p1, p2, p3) for a working cell u, or u == 'F' for a cell of a firing row"""
        for a, la in self.options(p1):
            for b, lb in self.options(p2):
                for d, ld in self.options(p3):
                    P = [-l for l in (la, lb, ld) if l is not None]
                    xe = self.x[(a, b, d)]
                    if u == 'F':
                        self.cls.append(P + [xe['F']])
                    else:
                        self.cls.extend(P + [-xe[s], u[s]] for s in self.W)
                        self.cls.append(P + [-xe['F']])

    def differ(self, u, v):
        """(E4): two cells in different working states"""
        self.cls.extend([-u[s], -v[s]] for s in self.W)

    # ---- the half-line, up to the anti-diagonal t + i = M
    def build_half(self, M):
        self.M = M
        for t in range(1, M):
            for i in range(1, t + 2):
                if t + i <= M:
                    self.half[(t, i)] = self.cell()
        for (t, i), u in sorted(self.half.items()):
            self.rule(u, self.h(t - 1, i - 1), self.h(t - 1, i), self.h(t - 1, i + 1))

    def h(self, t, i):
        if i == 0:
            return '*'
        if t <= 0:
            return 'G' if (t == 0 and i == 1) else 'L'   # t = -1: the convention for J_2(0)
        if t < i - 1:
            return 'L'                                   # Lemma 2.1
        assert t + i <= self.M, (t, i)
        return self.half[(t, i)]

    # ---- the line of length n: the half-line where t + i <= 2n - 2 (Lemma 2.2), else R_n
    def line(self, n, t, i):
        if i == 0 or i == n + 1:
            return '*'
        if t + i <= 2 * n - 2:
            return self.h(t, i)
        assert t <= 2 * n - 3, 'cells of the firing row are constrained by fire()'
        key = (n, t, i)
        if key not in self.R:
            u = self.R[key] = self.cell()
            self.rule(u, self.line(n, t - 1, i - 1), self.line(n, t - 1, i), self.line(n, t - 1, i + 1))
        return self.R[key]

    def fire(self, n, i):
        """the cell (2n-2, i) is F"""
        t = 2 * n - 3
        self.rule('F', self.line(n, t, i - 1), self.line(n, t, i), self.line(n, t, i + 1))

    def complete(self, n):
        """the line of length n is synchronized at time 2n-2 (all its cells before are working cells)"""
        for i in range(1, n + 1):
            self.fire(n, i)

    def return_chain(self, n, imin=2):
        """(E4) and (G3): the cells (2n-1-i, i) of the line differ from the half-line"""
        for i in range(imin, n + 1):
            self.differ(self.line(n, 2 * n - 1 - i, i), self.h(2 * n - 1 - i, i))

    def early(self, n, T, rc=True):
        """(G2), and (G3) if rc: the cells of R_n at the relative times tau <= T"""
        for t in range(n - 1, n + T):
            for i in range(1, n + 1):
                if t + i >= 2 * n - 1:
                    self.line(n, t, i)
        if rc:
            self.return_chain(n, imin=n - T)

    def cone(self, n):
        """(G5): the cone of the right end at the firing time"""
        for tau in range(0, n - 1):
            for kap in range(0, min(tau, n - 1 - tau) + 1):
                self.line(n, n - 1 + tau, n - kap)
        self.fire(n, n)
        for kap in range(0, (n - 1) // 2 + 1):
            self.differ(self.line(n, n - 1 + kap, n - kap), self.h(n - 1 + kap, n - kap))

    # ---- PUMP(n, n') (E5), with the cone of Lemma 3.2 found by a search over predecessors
    @staticmethod
    def cone_inputs(n):
        seen, stack, out = set(), [(n - 1, 0)], set()
        while stack:
            tau, kap = stack.pop()
            if (tau, kap) in seen:
                continue
            seen.add((tau, kap))
            for k2 in (kap + 1, kap, kap - 1):
                t2 = tau - 1
                if k2 < 0 or k2 >= n:
                    continue                     # a border
                if t2 >= k2:
                    stack.append((t2, k2))       # a cell of R_n
                elif t2 == k2 - 1:
                    out.add((k2, 'up'))          # on t + i = 2n - 2
                else:
                    out.add((k2, 'lo'))          # on t + i = 2n - 3
        return sorted(out)

    def inp(self, n, kap, which):
        return self.h(n - 3 + kap if which == 'lo' else n - 2 + kap, n - kap)

    def pump(self, n, n2):
        lits = []
        for kap, which in self.cone_inputs(n):
            v, w = self.inp(n, kap, which), self.inp(n2, kap, which)
            if isinstance(v, str) and isinstance(w, str):
                if v != w:
                    return                       # the two input words differ at a constant cell
                continue
            z = self.var()
            if isinstance(v, str):
                v, w = w, v
            if isinstance(w, str):
                self.cls.append([-z, -v[w]])
            else:
                self.cls.extend([-z, -v[s], -w[s]] for s in self.W)
            lits.append(z)
        self.cls.append(lits)

    # ---- Proposition 6.4: one selector per germ
    def germs(self, path):
        sel = []
        for ln in open(path):
            if ln.startswith('GERM'):
                s = self.var()
                sel.append(s)
                for tok in ln.split()[1:]:
                    e, d = tok.split('>')
                    self.cls.append([-s, self.x[tuple(e)][d]])
        self.cls.append(sel)
        return len(sel)

    # ---- Proposition 6.6: (B1)-(B4) in the weak reading, for an involution of {L, A, B}
    def balzer_weak(self, swap, border=True):
        """border=False: (B2) only for the neighbourhoods without a border"""
        I = {s: s for s in self.S + ['*']}
        for a, b in swap:
            I[a], I[b] = b, a
        for a in self.W:                                         # (B1), working neighbours only
            for c in self.W:
                if (a, c) != ('G', 'G'):
                    self.cls.append([self.x[(a, 'G', c)]['G']])
        for (a, b, c), vs in self.x.items():                     # (B2)
            if not border and '*' in (a, c):
                continue
            for s, v in vs.items():
                self.cls.append([-v, self.x[(I[c], I[b], I[a])][I[s]]])
        for e in (('G', 'G', 'G'), ('*', 'G', 'G'), ('G', 'G', '*')):    # (B3) without "only"
            self.cls.append([self.x[e]['F']])
        for v in self.W:                                         # (B4)
            if v != 'G':
                self.cls.append([self.x[('G', v, 'G')]['G']])

    def dimacs(self):
        return 'p cnf %d %d\n' % (self.nv, len(self.cls)) + ''.join(
            ' '.join(map(str, c)) + ' 0\n' for c in self.cls)


# ---- the formulas
def MT(k, lengths, M=None, Np=None):
    """MT_k(lengths; M, Np): lengths an interval 2..N (or 3..N)"""
    N = max(lengths)
    E = Encoder(k)
    E.build_half(max(M or 0, 2 * N - 2))
    for n in lengths:
        E.complete(n)
    for n in lengths:
        if n + 1 in lengths:
            E.return_chain(n)
    if Np:
        for n in range(4, Np):
            for n2 in range(n + 1, Np + 1):
                E.pump(n, n2)
    return E


def G(k, T, N1, C=None, norc=()):
    """G_k(T, N1, C) of Definition 5.4; norc: lengths whose early rows get no condition (G3)"""
    C = C or T + 1
    E = Encoder(k)
    E.build_half(2 * N1)                                  # (G4)
    for n in range(2, T + 2):                             # (G1)
        E.complete(n)
    for n in range(T + 2, N1 + 1):                        # (G2), (G3)
        E.early(n, T, rc=n not in norc)
    for n in range(T + 2, C + 1):                         # (G5)
        E.cone(n)
    return E


INV = {'id': (), 'AB': (('A', 'B'),), 'LA': (('L', 'A'),), 'LB': (('L', 'B'),)}


def balzer(N, inv, border=True):
    E = MT(5, range(2, N + 1))
    E.balzer_weak(INV[inv], border)
    return E


def claims():
    """the eight unsatisfiable formulas of Theorem 6.1 and Propositions 6.4 and 6.6"""
    def k14():
        E = MT(5, range(2, 11), 78, 39)
        E.germs(os.path.join(RESULTS, 'germs', 'K14_refuted10.txt'))
        return E
    return [('mt4_9', 'Theorem 6.1 (i)', lambda: MT(4, range(2, 10))),
            ('k4_G6', 'Theorem 6.1 (ii)', lambda: G(4, 6, 10)),
            ('k4_G4c', 'Theorem 6.1 (iii)', lambda: G(4, 4, 10, 10)),
            ('k14_n10', 'Proposition 6.4', k14),
            ('balzer_AB_10', 'Proposition 6.6, I = (A B)', lambda: balzer(10, 'AB')),
            ('balzer_LA_9', 'Proposition 6.6, I = (L A)', lambda: balzer(9, 'LA')),
            ('balzer_LB_9', 'Proposition 6.6, I = (L B)', lambda: balzer(9, 'LB')),
            ('balzer_id_12', 'Proposition 6.6, I = id', lambda: balzer(12, 'id'))]


# ---- differential test against the direct evaluation of encoding_check.py
def test(quick):
    import random
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.join(HERE, '..', 'research'))
    import encoding_check as ec
    from pysat.solvers import Solver
    rng = random.Random(1)
    nmut, nrand = (4, 20) if quick else (25, 150)
    t0 = time.time()

    def table_units(E, tab):
        return [E.x[nb][d] for nb, d in tab.items() if nb in E.x]

    # tables as in encoding_check.py: models of satisfiable formulas, partial rules, mutations, random
    base4 = []
    for specs, norc in ((['full:2-6', 'early:7-30:5'], ()), (['full:2-7', 'early:8-9:6'], ()),
                        (['full:2-5', 'early:6-30:4', 'cone:6-9'], ()),
                        (['full:2-4', 'early:5-30:3', 'cone:5-12'], ()), (['full:2-5', 'cone:6-12'], ()),
                        (['full:2-7', 'early:8-10:6'], (8, 9, 10))):
        F, E0 = ec.gfix_formula(4, specs, True, norc)
        F.solver.delete()
        base4 += ec.models(F, E0, 2 if quick else 6, 4)
    tables4 = list(base4)
    for p in ec.partial_rules_4():
        tables4 += [ec.complete(4, p, rng) for _ in range(2)]
    tables4 += [ec.mutate(4, t, rng, rng.choice((1, 2))) for t in list(tables4) for _ in range(nmut)]
    tables4 += [ec.complete(4, {}, rng) for _ in range(nrand)]
    known5 = [ec.load_table(os.path.join(RESULTS, f)) for f in
              ('uniformA_2-12.txt', 'delta13.txt', 'delta14.txt', 'delta14b.txt', 'delta14c.txt',
               'delta14d.txt', 'delta14e.txt', 'balzer_sym11.txt', 'balzer_noborder12.txt')]
    tables5 = [ec.complete(5, t, rng) for t in known5 for _ in range(2)]
    tables5 += [ec.mutate(5, t, rng, rng.choice((1, 2))) for t in list(tables5) for _ in range(2 * nmut)]
    tables5 += [ec.complete(5, {}, rng) for _ in range(nrand)]
    germs = [dict((tuple(tok.split('>')[0]), tok.split('>')[1]) for tok in ln.split()[1:])
             for ln in open(os.path.join(RESULTS, 'germs', 'K14_refuted10.txt')) if ln.startswith('GERM')]

    cases4 = [('MT_4({2..9};16)  [Thm 6.1 (i)]', MT(4, range(2, 10)),
               lambda tab: ec.direct_MT(tab, range(2, 10), 16)),
              ('MT_4({2..8};14)', MT(4, range(2, 9)), lambda tab: ec.direct_MT(tab, range(2, 9), 14))]
    for specs, args, norc, name in (
            (['full:2-7', 'early:8-10:6'], (6, 10), (), 'G_4(6,10)  [Thm 6.1 (ii)]'),
            (['full:2-5', 'early:6-10:4', 'cone:6-10'], (4, 10, 10), (), 'G_4(4,10,10)  [Thm 6.1 (iii)]'),
            (['full:2-6', 'early:7-30:5'], (5, 30), (), 'G_4(5,30)'),
            (['full:2-7', 'early:8-9:6'], (6, 9), (), 'G_4(6,9)'),
            (['full:2-5', 'early:6-30:4', 'cone:6-9'], (4, 30, 9), (), 'G_4(4,30,9)'),
            (['full:2-4', 'early:5-30:3', 'cone:5-12'], (3, 30, 12), (), 'G_4(3,30,12)'),
            (['full:2-7', 'early:8-10:6'], (6, 10), (8, 9, 10), 'G_4(6,10) without (G3)')):
        cases4.append((name, G(4, *args, norc=norc),
                       lambda tab, specs=specs, norc=norc: ec.direct_G(tab, specs, norc)))
    # (G1) for T = 4 and (G5) for 6 <= n <= 12: the lines 6..12 get only their cones
    E = Encoder(4)
    E.build_half(24)
    for n in range(2, 6):
        E.complete(n)
    for n in range(6, 13):
        E.cone(n)
    cases4.append(('(G1) for T = 4, (G5) for 6..12', E,
                   lambda tab: ec.direct_G(tab, ['full:2-5', 'cone:6-12'], ())))

    base10 = MT(5, range(2, 11), 78, 39)
    cases5 = [('MT_5({2..10};78,39)  [Prop 6.4, base]', base10,
               lambda tab: ec.direct_MT(tab, range(2, 11), 78, 39)),
              ('MT_5({2..12};22,12)', MT(5, range(2, 13), None, 12),
               lambda tab: ec.direct_MT(tab, range(2, 13), 22, 12))]
    for N, inv, border in ((12, 'id', True), (10, 'AB', True), (9, 'LA', True), (9, 'LB', True),
                           (11, 'id', True), (12, 'id', False), (9, 'LA', False), (10, 'LA', False)):
        conds = '1234' if border else '1234b'
        claim = border and N != 11
        cases5.append(('MT_5({2..%d}) + (B) %s, I = %s%s' % (N, conds, inv, '  [Prop 6.6]' if claim else ''),
                       balzer(N, inv, border),
                       lambda tab, N=N, inv=inv, conds=conds: ec.direct_MT(tab, range(2, N + 1), 2 * N - 2)
                       and ec.direct_B(tab, conds, inv)))
    E = MT(5, range(2, 11), 78, 39)
    E.germs(os.path.join(RESULTS, 'germs', 'K14_refuted10.txt'))
    cases5.append(('the formula of Prop 6.4 (with the selectors)', E,
                   lambda tab: ec.direct_MT(tab, range(2, 11), 78, 39)
                   and any(all(tab.get(e) == d for e, d in g.items()) for g in germs)))

    print('%-48s %7s %5s %6s %9s' % ('formula (independent encoder)', 'tables', 'sat', 'unsat', 'disagree'))
    total = bad = 0
    for cases, tables in ((cases4, tables4), (cases5, tables5)):
        for name, E, direct in cases:
            s = Solver(name='cadical195', bootstrap_with=E.cls)
            st = {'sat': 0, 'unsat': 0, 'bad': 0}
            for tab in tables:
                got = s.solve(assumptions=table_units(E, tab))
                want = bool(direct(tab))
                st['sat' if want else 'unsat'] += 1
                if got != want:
                    st['bad'] += 1
                    print('DISAGREE %s: formula %s, direct %s' % (name, got, want))
            s.delete()
            total += st['sat'] + st['unsat']
            bad += st['bad']
            print('%-48s %7d %5d %6d %9d' % (name[:48], st['sat'] + st['unsat'], st['sat'], st['unsat'], st['bad']))
    print('%d formula/table pairs, %d disagreements (%.0f s)' % (total, bad, time.time() - t0))
    return bad


def write(outdir, solve=False):
    os.makedirs(outdir, exist_ok=True)
    if solve:
        from pysat.solvers import Solver
    for name, claim, make in claims():
        t0 = time.time()
        E = make()
        path = os.path.join(outdir, name + '.cnf')
        with open(path, 'w') as f:
            f.write(E.dimacs())
        line = '%-13s %-27s vars=%-6d clauses=%-7d written to %s' % (name, claim, E.nv, len(E.cls), path)
        if solve and name != 'balzer_id_12':
            with Solver(name='cadical195', bootstrap_with=E.cls) as s:
                r = s.solve()
            line += ': %s (%.0f s)' % ('SATISFIABLE' if r else 'UNSATISFIABLE', time.time() - t0)
        print(line, flush=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in ('test', 'write', 'solve'):
        sys.exit(__doc__)
    if a[0] == 'test':
        sys.exit(1 if test('--quick' in a) else 0)
    write(a[1], solve=a[0] == 'solve')
