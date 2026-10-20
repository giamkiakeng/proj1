#!/usr/bin/env python3
"""germ_k14_check.py -- independent check of the half-line part of Proposition 5.4 of the note.

For each of the 14 germs of complexity <= 14 that survive the completion test (the germs of
results/germs/germs_K14.txt not in K14_refuted10.txt), simulate the half-line from the germ alone
(no neighbourhood outside the germ may occur below anti-diagonal 330) and find a length n <= 163
and a period L <= 5 for which Lemma 4.1 applies with s = 1 and k = 5, i.e. both input
anti-diagonals of the line of length n are L-periodic on [1, Y] (resp. [1, Y-1]) with
Y <= n - 1, Y >= 1 + L and Y - 1 > 16 L.  Written independently of germext.c.

usage: python3 germ_k14_check.py"""
import os

GERMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'germs')


def load(p):
    out = []
    for ln in open(p):
        if ln.startswith('GERM'):
            out.append(tuple(sorted(ln.split()[1:])))
    return out
allg = load(os.path.join(GERMS, 'germs_K14.txt'))
ref = set(load(os.path.join(GERMS, 'K14_refuted10.txt')))
surv = [g for g in allg if g not in ref]
print('survivors:', len(surv))
MMAX = 330
for g in surv:
    rule = {}
    for tok in g:
        nb, v = tok.split('>')
        rule[tuple(nb)] = v
    rule[('L', 'L', 'L')] = 'L'
    # C[t] = configuration at time t, cells 1..t+1 (cells beyond are L)
    C = [['G']]
    ok = True
    for t in range(1, MMAX):
        prev = C[-1] + ['L', 'L']
        row = []
        for i in range(1, t + 2):
            l = '*' if i == 1 else prev[i - 2]
            e = (l, prev[i - 1], prev[i])
            if e not in rule:
                ok = False
                break
            row.append(rule[e])
        if not ok:
            break
        C.append(row)
    assert ok, 'new neighbourhood before t=%d' % MMAX
    def cell(t, i):
        return C[t][i - 1] if i <= t + 1 else 'L'
    found = None
    for n in range(4, 164):
        if 2 * n - 2 >= MMAX:
            break
        for L in range(1, 6):
            # largest Y <= n-1 such that both words are L-periodic from y = 1
            Y = 1
            while Y + 1 <= n - 1:
                Yn = Y + 1
                okp = all(cell(2*n-2-y, y) == cell(2*n-2-y-L, y+L) for y in range(1, Yn - L + 1)) and \
                      all(cell(2*n-3-y, y) == cell(2*n-3-y-L, y+L) for y in range(1, Yn - 1 - L + 1))
                if not okp:
                    break
                Y = Yn
            if Y - 1 > 16 * L and Y >= 1 + L:
                found = (n, L, Y)
                break
        if found:
            break
    print(len(g), 'neighbourhoods; Lemma 4.1 applies at (n, L, Y) =', found)
