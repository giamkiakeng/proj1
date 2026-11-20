#!/usr/bin/env python3
"""verify_ext.py GERMFILE EXTFILE -- independent check of the refutations reported by germext.

GERMFILE: lines 'GERM xyz>d ...' (the germs, in order); EXTFILE: the output of germext for these germs, one line per germ:
    j CLOSED reach=M REFUTED n=.. s=.. L=.. Y=..      (Lemma 4.1 of the paper)
    j CLOSED reach=M PUMPFAIL n=.. n2=..               (Lemma 3.3: J_n and J_n2 agree on cone_n(n-1,0))
For every such line the half-line C_inf of germ j is simulated here with numpy (written independently of germext.c) on
the cells with t + i <= 2*max(n, n2) - 2, using only the transitions of the germ and LLL -> L (the run stops if another
neighbourhood occurs), and the claim is checked:
  REFUTED: s <= Y <= n - s, Y - s > (k-1)^(2s) L with k = 5, the word y -> C(2n-2-y, y) is L-periodic on [s, Y] and the
           word y -> C(2n-3-y, y) is L-periodic on [s, Y-1];
  PUMPFAIL: J_n(kappa) = (C(n-3+kappa, n-kappa), C(n-2+kappa, n-kappa)) and J_n2 agree on the positions of cone_n(n-1,0):
           the upper input cell at kappa = 0, both cells at 1 <= kappa <= floor(n/2) and, for odd n, the lower cell at
           kappa = (n+1)/2.  (No cell of these words is F: the germ has no F.)
Prints one line per checked claim and a summary."""
import sys
import numpy as np

CODE = {'L': 0, 'G': 1, 'A': 2, 'B': 3, '*': 4}
K = 5


def load_germs(fn):
    out = []
    for l in open(fn):
        if l.startswith('GERM'):
            tab = {}
            for tok in l.split()[1:]:
                nb, v = tok.split('>')
                tab[nb] = v
            out.append(tab)
    return out


def halfline(tab, M):
    """rows[t] = numpy array of C(t, i), i = 1..t+1, for 0 <= t <= M - 1 (cells with t + i <= M are all computed)"""
    T = np.full(5 * 5 * 5, -1, dtype=np.int16)
    for nb, v in tab.items():
        T[CODE[nb[0]] * 25 + CODE[nb[1]] * 5 + CODE[nb[2]]] = CODE[v]
    T[0] = 0                                    # LLL -> L
    rows = [np.array([1], dtype=np.int16)]
    for t in range(1, M):
        prev = rows[-1]
        n = len(prev) + 1                       # cells 1..t+1
        left = np.empty(n, dtype=np.int16); left[0] = 4; left[1:] = prev
        mid = np.zeros(n, dtype=np.int16); mid[:n - 1] = prev
        right = np.zeros(n, dtype=np.int16); right[:n - 2] = prev[1:]
        idx = left * 25 + mid * 5 + right
        new = T[idx]
        if (new < 0).any():
            i = int(np.nonzero(new < 0)[0][0])
            raise ValueError('neighbourhood outside the germ at the cell (%d, %d)' % (t, i + 1))
        rows.append(new)
    return rows


def C(rows, t, i):
    if i > t + 1:
        return 0
    return int(rows[t][i - 1])


germs = load_germs(sys.argv[1])
ok = bad = 0
for l in open(sys.argv[2]):
    w = l.split()
    if len(w) < 4 or w[3] not in ('REFUTED', 'PUMPFAIL'):
        continue
    j = int(w[0]) - 1
    kv = dict(x.split('=') for x in w[4:])
    tab = germs[j]
    if w[3] == 'REFUTED':
        n, s, L, Y = int(kv['n']), int(kv['s']), int(kv['L']), int(kv['Y'])
        rows = halfline(tab, 2 * n - 1)
        up = [C(rows, 2 * n - 2 - y, y) for y in range(s, Y + 1)]
        lo = [C(rows, 2 * n - 3 - y, y) for y in range(s, Y)]
        good = (s <= Y <= n - s and Y - s > (K - 1) ** (2 * s) * L
                and all(up[a] == up[a + L] for a in range(len(up) - L))
                and all(lo[a] == lo[a + L] for a in range(len(lo) - L)))
        print('%d REFUTED n=%d s=%d L=%d Y=%d: %s' % (j + 1, n, s, L, Y, 'confirmed' if good else 'NOT CONFIRMED'), flush=True)
    else:
        n, n2 = int(kv['n']), int(kv['n2'])
        rows = halfline(tab, 2 * n2 - 1)
        J = lambda m, kap: (C(rows, m - 3 + kap, m - kap), C(rows, m - 2 + kap, m - kap))
        pos = [(0, 'up')] + [(kap, 'both') for kap in range(1, n // 2 + 1)] + ([((n + 1) // 2, 'lo')] if n % 2 else [])
        agree = True
        for kap, which in pos:
            a, b = J(n, kap), J(n2, kap)
            if which == 'up' and a[1] != b[1]:
                agree = False
            if which == 'lo' and a[0] != b[0]:
                agree = False
            if which == 'both' and a != b:
                agree = False
        good = agree
        print('%d PUMPFAIL n=%d n2=%d: %s' % (j + 1, n, n2, 'confirmed' if good else 'NOT CONFIRMED'), flush=True)
    ok += good; bad += (not good)
print('SUMMARY confirmed %d, not confirmed %d' % (ok, bad))
