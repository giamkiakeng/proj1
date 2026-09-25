#!/usr/bin/env python3
"""check_rightborder.py -- periodic stretches of the diagonals t-i = n-3, n-4 read from
the right end (Remark 3.8 of the paper) for a rule synchronizing lines in minimal time.
usage: check_rightborder.py rulefile k NMAX"""
import sys
rule, k, NMAX = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
tab = {}
for ln in open(rule):
    t = ln.split('#')[0].split()
    if len(t) == 4: tab[tuple(t[:3])] = t[3]
worst = {}
for n in range(6, NMAX + 1, 7):
    rows = [['G'] + ['L'] * (n - 1)]
    for t in range(1, 2 * n - 2):
        cur = rows[-1]
        rows.append([tab[(cur[i-1] if i > 0 else '*', cur[i], cur[i+1] if i + 1 < n else '*')] for i in range(n)])
    C = lambda t, i: rows[t][i - 1]          # 1-based cells
    U = lambda y: C(2*n - 2 - y, n + 1 - y)  # diagonal t-i = n-3
    Lw = lambda y: C(2*n - 3 - y, n + 1 - y) # diagonal t-i = n-4
    for s in (1, 2):
        for L in range(1, 7):
            Y = s + L - 1
            while Y + 1 <= n - s:
                y = Y + 1
                if y - L >= s and U(y) != U(y - L): break
                x = y - 1
                if x - L >= s and Lw(x) != Lw(x - L): break
                Y = y
            if Y >= s + L:
                key = (s, L)
                if Y - s > worst.get(key, (-1, 0))[0]: worst[key] = (Y - s, n)
                if Y - s > (k - 1) ** (2 * s) * L: print('VIOLATION', n, s, L, Y)
for key in sorted(worst): print('s=%d L=%d: max stretch %d (n=%d), bound %d' % (key + worst[key] + ((k-1)**(2*key[0])*key[1],)))
