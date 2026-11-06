#!/usr/bin/env python3
"""
encoding_check.py -- differential test of the formula generators against a direct evaluation.

An LRAT proof certifies that a formula is unsatisfiable; it does not certify that the formula
expresses the intended conditions.  This program tests the generators gencnf.py, gfix.py and
balzer.py, the ones behind Theorem 6.1, Propositions 6.2, 6.4, 6.6 and Table 2, as follows.
For a rule table fixed by assumptions, a formula must be satisfiable exactly when the table
satisfies the conditions that the formula is meant to encode.  These conditions are evaluated
here directly, by simulating the lines and the half-line, in code written for this test from the
definitions of the paper (Section 2: lines and synchronization; Lemma 3.2 and the pumping lemma:
PUMP(n, n'); Definition 5.4: (G1)-(G5); Section 6.5: (B1)-(B4)); it shares no code with the
generators, which are used as black boxes.

Tables: the known rules (Mazoyer's, delta12, delta13, the five rules of Proposition 6.3,
balzer_sym11, balzer_noborder12), models of the satisfiable four-state formulas of Proposition 6.2 and Table 3, the
27 partial four-state rules for the lengths 2..8 completed at random, single and double
mutations of all of these, and uniformly random tables.  Every disagreement is printed, and the
program exits with status 1 if there is one.

Finally, the formulas of Theorem 6.1 and Propositions 6.4 and 6.6 are built once more in the
same way as for the test and compared with the published files formulas/*.cnf.xz.  They must be
identical, except that the published formula of Proposition 6.4 consists of the tested formula
followed by one selector per germ of results/germs/K14_refuted10.txt (Appendix A of the paper),
whose clauses are checked against that list.

usage: python3 encoding_check.py [--seed S] [--quick]
"""
import argparse
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'research'))
RESULTS = os.path.join(HERE, '..', 'results')

from pysat.solvers import Solver   # noqa: E402

import balzer   # noqa: E402  (generator under test)
import gencnf   # noqa: E402  (generator under test)
import gfix     # noqa: E402  (generator under test)

# ----------------------------------------------------------------------------------------------
# rule tables
# ----------------------------------------------------------------------------------------------


def working(k):
    return list('LGABC'[:k - 1])


def neighbourhoods(k):
    side = ['*'] + working(k)
    return [(x, y, z) for x in side for y in working(k) for z in side if not (x == '*' and z == '*')]


QUIESCENT = {('L', 'L', 'L'): 'L', ('L', 'L', '*'): 'L'}


def load_table(path):
    tab = {}
    for ln in open(path):
        w = ln.split('#')[0].split()
        if len(w) == 4 and w[0] != 'k':
            tab[tuple(w[:3])] = w[3]
    return tab


def complete(k, tab, rng):
    """a full table: the given entries, quiescence, and random values elsewhere"""
    out = {}
    states = working(k) + ['F']
    for nb in neighbourhoods(k):
        out[nb] = QUIESCENT.get(nb) or tab.get(nb) or rng.choice(states)
    return out


def mutate(k, tab, rng, m):
    """change m entries (never the two quiescence entries) to another value"""
    out = dict(tab)
    states = working(k) + ['F']
    free = [nb for nb in neighbourhoods(k) if nb not in QUIESCENT]
    for nb in rng.sample(free, m):
        out[nb] = rng.choice([s for s in states if s != out[nb]])
    return out


# ----------------------------------------------------------------------------------------------
# direct evaluation of the conditions (independent of the generators)
# ----------------------------------------------------------------------------------------------


class Half:
    """the half-line C_inf on the cells with t + i <= M; None = undefined (an F nearby)"""

    def __init__(self, tab, M):
        self.M = M
        self.C = {}
        for t in range(1, M):
            for i in range(1, min(t + 1, M - t) + 1):
                a, b, c = self.get(t - 1, i - 1), self.get(t - 1, i), self.get(t - 1, i + 1)
                self.C[(t, i)] = None if (None in (a, b, c) or 'F' in (a, b, c)) else tab[(a, b, c)]

    def get(self, t, i):
        if i == 0:
            return '*'
        if t == 0:
            return 'G' if i == 1 else 'L'
        if i > t + 1:
            return 'L'
        return self.C[(t, i)]

    def working(self):
        """no cell with t + i <= M is undefined or F"""
        return all(v is not None and v != 'F' for v in self.C.values())


def line(tab, n, tmax):
    """the line of length n up to time tmax or up to its first row with an F (included)"""
    rows = [['G'] + ['L'] * (n - 1)]
    while len(rows) <= tmax and 'F' not in rows[-1]:
        r = ['*'] + rows[-1] + ['*']
        rows.append([tab[(r[i - 1], r[i], r[i + 1])] for i in range(1, n + 1)])
    return rows


def synchronized(tab, n):
    rows = line(tab, n, 2 * n - 2)
    return len(rows) == 2 * n - 1 and all('F' not in r for r in rows[:-1]) and all(s == 'F' for s in rows[-1])


def early_ok(tab, n, T, half, rc=True):
    """(G2), and (G3) if rc: no F up to time n-1+T; the return chain differs from C_inf there"""
    tmax = n - 1 + T
    rows = line(tab, n, tmax)
    if len(rows) < tmax + 1 or any('F' in r for r in rows):
        return False
    if rc:
        for i in range(1, n + 1):
            t = 2 * n - 1 - i
            if t <= tmax and rows[t][i - 1] == half.get(t, i):
                return False
    return True


def cone_ok(tab, n, half, rc=True):
    """(G5): the backward dependency cone {tau + kappa <= n-1} of the right end at the firing
    time, computed by the local rule from the half-line: working before tau = n-1, F at
    (n-1, 0), and R_n(kappa, kappa) != C_inf(n-1+kappa, n-kappa) for 2 kappa <= n-1"""
    val = {}

    def pred(t, j):
        if j == 0 or j == n + 1:
            return '*'
        if t + j <= 2 * n - 2:
            return half.get(t, j)
        return val[(t, j)]                     # KeyError: the cone is not closed (cannot happen)
    for tau in range(n):
        for kap in range(min(tau, n - 1 - tau) + 1):
            t, i = n - 1 + tau, n - kap
            a, b, c = pred(t - 1, i - 1), pred(t - 1, i), pred(t - 1, i + 1)
            val[(t, i)] = None if (None in (a, b, c) or 'F' in (a, b, c)) else tab[(a, b, c)]
    for (t, i), v in val.items():
        if t < 2 * n - 2 and (v is None or v == 'F'):
            return False
    if val[(2 * n - 2, n)] != 'F':
        return False
    if rc:
        for kap in range((n - 1) // 2 + 1):
            if val[(n - 1 + kap, n - kap)] == half.get(n - 1 + kap, n - kap):
                return False
    return True


def cone_positions(n):
    """Lemma 3.2: the input cells of cone_n(n-1, 0) as (kappa, 'lo'|'up')"""
    pos = [(0, 'up')]
    for kap in range(1, n // 2 + 1):
        pos += [(kap, 'lo'), (kap, 'up')]
    if n % 2 == 1:
        pos.append(((n + 1) // 2, 'lo'))
    return pos


def input_cell(n, kap, which):
    return (n - 3 + kap, n - kap) if which == 'lo' else (n - 2 + kap, n - kap)


def pump_ok(half, Np, nlo=4):
    """PUMP(n, n') for nlo <= n < n' <= Np: the input words differ on the cone of the right end"""
    for n in range(nlo, Np):
        pos = cone_positions(n)
        for n2 in range(n + 1, Np + 1):
            if all(half.get(*input_cell(n, kap, w)) == half.get(*input_cell(n2, kap, w)) for kap, w in pos):
                return False
    return True


def direct_G(tab, specs, norc=()):
    """the conditions encoded by gfix.py FREE k SPECS (Definition 5.4 for the specs of the paper)"""
    lines = []
    for sp in specs:
        w = sp.split(':')
        ns = [n for part in w[1].split(',') for n in
              (range(int(part.split('-')[0]), int(part.split('-')[-1]) + 1))]
        lines += [(n, w[0], int(w[2]) if len(w) > 2 else None) for n in ns]
    M = max(2 * n - 2 for n, _, _ in lines) + 2
    half = Half(tab, M)
    if not half.working():
        return False
    for n, kind, h in lines:
        rc = n not in norc
        if kind == 'full' and not synchronized(tab, n):
            return False
        if kind == 'early' and not early_ok(tab, n, h, half, rc):
            return False
        if kind == 'cone' and not cone_ok(tab, n, half, rc):
            return False
    return True


def direct_MT(tab, lengths, M, Np=None):
    """the conditions encoded by gencnf.build: the lines of the given lengths synchronized, the
    half-line working on t + i <= M, and PUMP(n, n') for 4 <= n < n' <= Np"""
    half = Half(tab, M)
    if not half.working():
        return False
    if not all(synchronized(tab, n) for n in lengths):
        return False
    return Np is None or pump_ok(half, Np)


INV = {'id': {}, 'AB': {'A': 'B', 'B': 'A'}, 'LA': {'L': 'A', 'A': 'L'}, 'LB': {'L': 'B', 'B': 'L'}}


def direct_B(tab, conds, inv):
    """(B1)-(B4) of Section 6.5 for five states; 's' in conds selects the strong reading of (B1)
    and (B3), 'b' restricts (B2) to the neighbourhoods without a border"""
    strong = 's' in conds
    W = working(5)
    side = ['*'] + W
    if '1' in conds:
        for x in (side if strong else W):
            for y in (side if strong else W):
                if x in ('G', '*') and y in ('G', '*'):
                    continue
                if tab[(x, 'G', y)] != 'G':
                    return False
    if '3' in conds:
        pre = [('G', 'G', 'G'), ('*', 'G', 'G'), ('G', 'G', '*')]
        if any(tab[e] != 'F' for e in pre):
            return False
        if strong and any(tab[e] == 'F' for e in neighbourhoods(5) if e not in pre):
            return False
    if '4' in conds:
        if any(tab[('G', v, 'G')] != 'G' for v in W if v != 'G'):
            return False
    if '2' in conds:
        def I(s):
            return INV[inv].get(s, s)
        for (x, y, z) in neighbourhoods(5):
            if 'b' in conds and '*' in (x, z):
                continue                          # 'b': (B2) only for neighbourhoods without a border
            if tab[(I(z), I(y), I(x))] != I(tab[(x, y, z)]):
                return False
    return True


# ----------------------------------------------------------------------------------------------
# the generators, as black boxes: build once, then solve with the table as assumptions
# ----------------------------------------------------------------------------------------------


class Formula:
    def __init__(self, name, k, clauses, unit_of, direct):
        self.name, self.k, self.direct = name, k, direct
        self.unit_of = unit_of                  # (nb, value) -> literal, or None if fixed by the formula
        self.solver = Solver(name='cadical195', bootstrap_with=clauses)
        self.stats = {'sat': 0, 'unsat': 0, 'disagree': 0}

    def test(self, tab):
        units = []
        for nb, d in tab.items():
            lit = self.unit_of(nb, d)
            if lit is not None:
                units.append(lit)
        got = self.solver.solve(assumptions=units)
        want = self.direct(tab)
        self.stats['sat' if want else 'unsat'] += 1
        if got != want:
            self.stats['disagree'] += 1
            print('DISAGREE %s: formula %s, direct %s, table %s' % (
                self.name, got, want, ' '.join('%s>%s' % (''.join(nb), d) for nb, d in sorted(tab.items()))))
        return got


def gfix_formula(k, specs, share=True, norc=()):
    os.environ['GFIX_SHARE'] = '1' if share else '0'
    gfix.NORC = set(norc)
    E, _ = gfix.build(None, k, specs)

    def unit_of(nb, d):
        vs = E.T.get(nb)
        return None if vs is None else vs[d]
    name = 'gfix %d %s%s%s' % (k, ' '.join(specs), ' share' if share else '',
                                ' norc=' + ','.join(map(str, sorted(norc))) if norc else '')
    return Formula(name, k, E.cls, unit_of, lambda tab: direct_G(tab, specs, norc)), E


def gencnf_formula(k, lengths, M, Np=None, extra=None):
    E = gencnf.build(k, max(lengths), symbreak=False, fire_n=list(lengths), minf=M, pump=Np)
    if extra:
        extra(E)
    code = {'*': gencnf.BND, 'L': 0, 'G': 1, 'F': k - 1}
    for j, s in enumerate('ABC'[:k - 3]):
        code[s] = 2 + j

    def unit_of(nb, d):
        return E.T[tuple(code[x] for x in nb)][code[d]]
    Mfull = max(M or 0, 2 * max(lengths) - 2)
    return Formula('gencnf %d lengths %d..%d M=%d pump=%s' % (k, min(lengths), max(lengths), Mfull, Np),
                   k, E.clauses, unit_of, lambda tab: direct_MT(tab, lengths, Mfull, Np)), E


def models(F, E, count, k):
    """up to COUNT tables that are models of the gfix formula F (blocking each table)"""
    out = []
    s = Solver(name='cadical195', bootstrap_with=F_clauses(E))
    while len(out) < count and s.solve():
        m = set(x for x in s.get_model() if x > 0)
        tab = dict(QUIESCENT)
        block = []
        for nb, vs in E.T.items():
            for d, v in vs.items():
                if v in m:
                    tab[nb] = d
                    block.append(-v)
        out.append(tab)
        s.add_clause(block)
    s.delete()
    return out


def F_clauses(E):
    return E.cls


def partial_rules_4():
    """the 27 partial four-state rules for the lengths 2..8 (fsspdfs, Proposition 6.2 (a))"""
    exe = os.path.join(HERE, 'fsspdfs')
    if not os.path.exists(exe):
        subprocess.run(['gcc', '-O3', '-o', exe, os.path.join(HERE, 'fsspdfs.c')], check=True)
    p = subprocess.run([exe, '4', '8', '-s'], capture_output=True, text=True, cwd=HERE)
    rules = []
    for ln in p.stdout.splitlines():
        if ln.startswith('SOL'):
            tab = {}
            for tok in ln.split()[1:]:
                if '>' in tok:
                    nb, d = tok.split('>')
                    tab[tuple(nb)] = d
            rules.append(tab)
    return rules


# ----------------------------------------------------------------------------------------------


def run(seed, quick):
    rng = random.Random(seed)
    nmut, nrand = (4, 20) if quick else (25, 150)
    formulas = []
    t0 = time.time()

    # ---- four states: Theorem 6.1 (i)-(iii), Proposition 6.2, Table 3
    print('four states: building the formulas', flush=True)
    G4 = [(['full:2-7', 'early:8-10:6'], ()),                       # Theorem 6.1 (ii)
          (['full:2-5', 'early:6-10:4', 'cone:6-10'], ()),          # Theorem 6.1 (iii)
          (['full:2-6', 'early:7-30:5'], ()),                       # Proposition 6.2 (b)
          (['full:2-7', 'early:8-9:6'], ()),
          (['full:2-5', 'early:6-30:4', 'cone:6-9'], ()),
          (['full:2-4', 'early:5-30:3', 'cone:5-12'], ()),
          (['full:2-5', 'cone:6-12'], ()),
          (['full:2-7', 'early:8-10:6'], (8, 9, 10))]               # ... without (G3)
    base4 = []
    for specs, norc in G4:
        F, E = gfix_formula(4, specs, True, norc)
        formulas.append(F)
        if (specs, norc) not in G4[:2]:
            base4 += models(F, E, 2 if quick else 6, 4)
        F2, _ = gfix_formula(4, specs, False, norc)               # the same without structural sharing
        formulas.append(F2)
    formulas.append(gencnf_formula(4, range(2, 10), None)[0])        # Theorem 6.1 (i): MT_4({2..9}; 16)
    formulas.append(gencnf_formula(4, range(2, 9), None)[0])         # lines 2..8: satisfiable
    four = formulas[:]
    partial = partial_rules_4()
    print('  %d models of the satisfiable formulas, %d partial rules for 2..8 (%.0f s)'
          % (len(base4), len(partial), time.time() - t0), flush=True)
    tables4 = list(base4)
    for p in partial:
        tables4 += [complete(4, p, rng) for _ in range(2)]
    tables4 += [mutate(4, t, rng, rng.choice((1, 2))) for t in list(tables4) for _ in range(nmut)]
    tables4 += [complete(4, {}, rng) for _ in range(nrand)]
    for tab in tables4:
        for F in four:
            F.test(tab)

    # ---- five states: Proposition 6.3 (Table 2), Proposition 6.4 (germ formula), Proposition 6.6
    print('five states (%.0f s)' % (time.time() - t0), flush=True)
    known5 = [load_table(os.path.join(RESULTS, f)) for f in
              ('uniformA_2-12.txt', 'delta13.txt', 'delta14.txt', 'delta14b.txt', 'delta14c.txt',
               'delta14d.txt', 'delta14e.txt', 'balzer_sym11.txt', 'balzer_noborder12.txt')]
    five = [gfix_formula(5, ['full:2-14'])[0],                        # Table 2
            gfix_formula(5, ['full:2-15'])[0],
            gfix_formula(5, ['full:2-14', 'early:15-30:6'])[0],
            gfix_formula(5, ['full:2-14', 'early:15-30:8'])[0],
            gfix_formula(5, ['full:2-12', 'early:13-20:4', 'cone:13-14'])[0],
            gencnf_formula(5, range(2, 11), 78, 39)[0],               # Proposition 6.4: MT_5({2..10}; 78, 39)
            gencnf_formula(5, range(2, 13), None, 12)[0]]
    for N, conds, inv in ((11, '1234s', 'id'), (12, '1234', 'id'), (10, '1234', 'AB'),     # Prop. 6.6
                          (9, '1234', 'LA'), (9, '1234', 'LB'), (11, '1234', 'id'),
                          (12, '1234b', 'id'), (9, '1234b', 'LA'), (10, '1234b', 'LA')):   # (B2) without borders
        def extra(E, conds=conds, inv=inv):
            balzer.add_conditions(E, conds, inv)

        F, _ = gencnf_formula(5, range(2, N + 1), None, None, extra)
        F.name += ' + (B) %s %s' % (conds, inv)
        F.direct = (lambda tab, N=N, conds=conds, inv=inv:
                    direct_MT(tab, range(2, N + 1), 2 * N - 2) and direct_B(tab, conds, inv))
        five.append(F)
    tables5 = [complete(5, t, rng) for t in known5 for _ in range(2)]
    tables5 += [mutate(5, t, rng, rng.choice((1, 2))) for t in list(tables5) for _ in range(2 * nmut)]
    tables5 += [complete(5, {}, rng) for _ in range(nrand)]
    for tab in tables5:
        for F in five:
            F.test(tab)

    # ---- the Balzer clauses alone, on tables built to satisfy or nearly satisfy them
    print('the clauses of (B1)-(B4) alone (%.0f s)' % (time.time() - t0), flush=True)
    Bstats = {'agree': 0, 'disagree': 0, 'holds': 0}
    for conds in ('1234', '1234s', '1234b', '13', '2', '2b', '134s'):
        for inv in INV:
            E = gencnf.build(5, 2, symbreak=False)
            n0 = len(E.clauses)
            balzer.add_conditions(E, conds, inv)
            added = E.clauses[n0:]
            code = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}
            for tab in tables5[:200] + [balzer_like(rng, conds, inv) for _ in range(60)]:
                true = {E.T[tuple(code[x] for x in nb)][code[d]] for nb, d in tab.items()}
                allv = {v for vs in E.T.values() for v in vs}
                val = (lambda lit: (abs(lit) in true) == (lit > 0) if abs(lit) in allv else None)
                got = all(any(val(l) for l in c) for c in added)
                want = direct_B(tab, conds, inv)
                Bstats['holds'] += want
                if got == want:
                    Bstats['agree'] += 1
                else:
                    Bstats['disagree'] += 1
                    print('DISAGREE (B) %s %s' % (conds, inv))

    # ---- six states: Mazoyer's solution (Table 2) and its mutations
    print('six states (%.0f s)' % (time.time() - t0), flush=True)
    maz = complete(6, load_table(os.path.join(RESULTS, 'mazoyer6.txt')), rng)
    six = [gencnf_formula(6, range(3, 13), 78, 40)[0],
           gfix_formula(6, ['full:3-12', 'early:13-20:8'])[0],
           gfix_formula(6, ['full:3-10', 'early:11-14:5', 'cone:11-14'])[0]]
    tables6 = [maz] + [mutate(6, maz, rng, rng.choice((1, 2))) for _ in range(3 * nmut)]
    tables6 += [complete(6, {}, rng) for _ in range(nrand // 3)]
    for tab in tables6:
        for F in six:
            F.test(tab)

    # ---- Lemma 3.2: the cone of the right end, by search, against the closed form used above
    lemma = all(cone_by_search(n) == set(cone_positions(n)) for n in range(2, 200))

    # ---- the tested formulas against the published files
    print('the published formulas (%.0f s)' % (time.time() - t0), flush=True)
    published = published_check()

    print('\nformula                                                        tables   sat  unsat  disagree')
    bad = 0
    for F in four + five + six:
        s = F.stats
        bad += s['disagree']
        print('%-62s %6d %5d %6d %9d' % (F.name[:62], s['sat'] + s['unsat'], s['sat'], s['unsat'], s['disagree']))
    print('(B1)-(B4) clauses alone: %d tables, %d satisfying, %d disagreements'
          % (Bstats['agree'] + Bstats['disagree'], Bstats['holds'], Bstats['disagree']))
    print('Lemma 3.2 (cone of the right end) by search for 2 <= n < 200: %s' % lemma)
    print('tested formulas identical to formulas/*.cnf.xz (k14_n10: with the selectors of its 230 germs): %s'
          % ', '.join('%s %s' % (name, same) for name, same in published))
    bad += Bstats['disagree'] + (not lemma) + sum(not same for _, same in published)
    total = sum(F.stats['sat'] + F.stats['unsat'] for F in four + five + six)
    print('%d formula/table pairs, %d disagreements (%.0f s)' % (total, bad, time.time() - t0))
    return bad


def balzer_like(rng, conds, inv):
    """a random five-state table that satisfies (B1)-(B4) for (conds, inv), up to one mutation"""
    W = working(5)
    tab = complete(5, {}, rng)
    for _ in range(4):                        # a few passes to settle the involution constraints
        for nb in neighbourhoods(5):
            x, y, z = nb
            if '1' in conds and y == 'G' and (x in W or 's' in conds) and (z in W or 's' in conds) \
                    and not (x in ('G', '*') and z in ('G', '*')):
                tab[nb] = 'G'
            if '4' in conds and x == 'G' and z == 'G' and y != 'G':
                tab[nb] = 'G'
            if '3' in conds and nb in (('G', 'G', 'G'), ('*', 'G', 'G'), ('G', 'G', '*')):
                tab[nb] = 'F'
            elif '3' in conds and 's' in conds and tab[nb] == 'F':
                tab[nb] = 'L'
        if '2' in conds:
            def I(s):
                return INV[inv].get(s, s)
            for nb in neighbourhoods(5):
                x, y, z = nb
                if 'b' in conds and '*' in (x, z):
                    continue
                tab[(I(z), I(y), I(x))] = I(tab[nb])
    for nb, d in QUIESCENT.items():
        tab[nb] = d
    return mutate(5, tab, rng, 1) if rng.random() < 0.5 else tab


def published_check():
    """the formulas of Theorem 6.1 and Propositions 6.4 and 6.6, built as in run(), against the
    published files formulas/*.cnf.xz; returns a list of (name, identical)"""
    import lzma
    form = os.path.join(HERE, '..', 'formulas')

    def dimacs(nv, cls):
        return ('p cnf %d %d\n' % (nv, len(cls))
                + ''.join(' '.join(map(str, c)) + ' 0\n' for c in cls)).encode()

    def same(name, nv, cls):
        return (name, dimacs(nv, cls) == lzma.open(os.path.join(form, name + '.cnf.xz')).read())

    out = []
    F, E = gencnf_formula(4, range(2, 10), None)                      # Theorem 6.1 (i)
    F.solver.delete()
    out.append(same('mt4_9', E.nv, E.clauses))
    for name, specs in (('k4_G6', ['full:2-7', 'early:8-10:6']),      # Theorem 6.1 (ii), (iii)
                        ('k4_G4c', ['full:2-5', 'early:6-10:4', 'cone:6-10'])):
        F, E = gfix_formula(4, specs, True)
        F.solver.delete()
        out.append(same(name, E.nv, E.cls))
    for name, N, conds, inv in (('balzer_AB_10', 10, '1234', 'AB'), ('balzer_LA_9', 9, '1234', 'LA'),
                                ('balzer_LB_9', 9, '1234', 'LB'), ('balzer_id_12', 12, '1234', 'id')):
        F, E = gencnf_formula(5, range(2, N + 1), None, None,           # Proposition 6.6
                              lambda E, c=conds, i=inv: balzer.add_conditions(E, c, i))
        F.solver.delete()
        out.append(same(name, E.nv, E.clauses))
    F, E = gencnf_formula(5, range(2, 11), 78, 39)                    # Proposition 6.4
    F.solver.delete()
    code = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}
    sel, extra = [], []
    for ln in open(os.path.join(RESULTS, 'germs', 'K14_refuted10.txt')):
        if ln.startswith('GERM'):
            s = E.nv + len(sel) + 1                                   # one new variable per germ
            sel.append(s)
            for tok in ln.split()[1:]:
                nb, d = tok.split('>')
                extra.append([-s, E.T[tuple(code[x] for x in nb)][code[d]]])
    out.append(same('k14_n10', E.nv + len(sel), [list(c) for c in E.clauses] + extra + [sel]))
    return out


def cone_by_search(n):
    """the input cells reached from the relative cell (n-1, 0) of R_n through predecessors"""
    seen, stack, inputs = set(), [(n - 1, 0)], set()
    while stack:
        tau, kap = stack.pop()
        if (tau, kap) in seen:
            continue
        seen.add((tau, kap))
        for k2 in (kap - 1, kap, kap + 1):
            t2 = tau - 1
            if k2 == -1:
                continue                                  # right border
            assert k2 < n, 'left border reached'
            if t2 >= k2:
                stack.append((t2, k2))
            elif t2 == k2 - 1:
                inputs.add((k2, 'up'))
            elif t2 == k2 - 2 and t2 >= -1 and not (k2 == 0):
                inputs.add((k2, 'lo'))
    return inputs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--quick', action='store_true')
    a = ap.parse_args()
    sys.exit(1 if run(a.seed, a.quick) else 0)


if __name__ == '__main__':
    main()
