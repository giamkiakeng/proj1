#!/usr/bin/env python3
"""leftbar.py RULE [MAXM] [SMAX] [LMAX] -- the left-border lemma (Lemma 4.1 of the paper) for the half-line of a rule.

The half-line C_inf is simulated with the transitions of RULE on all cells with t + i <= MAXM (default 2600); the
program stops if a neighbourhood occurs that RULE does not list, and reports the set of neighbourhoods used (the
germ).  Then, for s = 1..SMAX and l = 1..LMAX it looks for the least n with 2n - 2 <= MAXM such that, for some
Y <= n - s with Y - s > (k-1)^(2s) l  (k = 5), the word y -> C_inf(2n-2-y, y) is l-periodic on [s, Y] and the word
y -> C_inf(2n-3-y, y) is l-periodic on [s, Y-1].  By Lemma 4.1, no rule with this germ synchronizes the line n.
"""
import sys
fn = sys.argv[1]; MAXM = int(sys.argv[2]) if len(sys.argv) > 2 else 2600
SMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 3; LMAX = int(sys.argv[4]) if len(sys.argv) > 4 else 12
K = 5
tab = {}
for l in open(fn):
    w = l.split('#')[0].split()
    if len(w) == 4:
        tab[tuple(w[:3])] = w[3]
    elif len(w) == 2 and w[0] == 'k':
        K = int(w[1])
tab[('L', 'L', 'L')] = 'L'
code = {'L': 0, 'G': 1, 'A': 2, 'B': 3, 'C': 4, '*': 9}
T = {}
for (a, b, c), d in tab.items():
    if d != 'F' and c != '*':
        T[(code[a], code[b], code[c])] = code[d]
# rows[t][i-1] = C_inf(t, i) for t + i <= MAXM
rows = [bytearray([1] + [0] * (MAXM - 1))]
germ = set()
for t in range(0, MAXM - 1):
    prev = rows[-1]; n = MAXM - (t + 1)
    new = bytearray(n)
    left = 9
    for i in range(n):
        e = (left, prev[i], prev[i + 1] if i + 1 < len(prev) else 0)
        if e not in T:
            sys.exit('undefined neighbourhood %s at the cell (%d, %d)' % (e, t + 1, i + 1))
        if e != (0, 0, 0):
            germ.add(e)
        new[i] = T[e]; left = prev[i]
    rows.append(new)
name = {v: s for s, v in code.items()}
print('half-line determined on t + i <= %d; germ: %d neighbourhoods besides LLL: %s' % (MAXM, len(germ), ' '.join(sorted(''.join(name[x] for x in e) + '>' + name[T[e]] for e in germ))))
best = None
for s in range(1, SMAX + 1):
    for l in range(1, LMAX + 1):
        bound = (K - 1) ** (2 * s) * l
        for n in range(s + bound + 2, MAXM // 2 + 2):
            if 2 * n - 2 > MAXM:
                break
            up = lambda y: rows[2 * n - 2 - y][y - 1]
            lo = lambda y: rows[2 * n - 3 - y][y - 1]
            # the largest Y <= n - s with both words periodic
            Y = s
            while Y + 1 <= n - s and (Y + 1 - l < s or up(Y + 1) == up(Y + 1 - l)) and (Y - l < s or lo(Y) == lo(Y - l)):
                Y += 1
            if Y - s > bound:
                print('s = %d, l = %d: n = %d, Y = %d, Y - s = %d > %d = (k-1)^(2s) l   upper word starts %s, lower word starts %s'
                      % (s, l, n, Y, Y - s, bound, ''.join(name[up(y)] for y in range(s, s + 3 * l)), ''.join(name[lo(y)] for y in range(s, s + 3 * l))))
                if best is None or n < best[0]:
                    best = (n, s, l, Y)
                break
if best:
    print('RESULT: no rule with this germ synchronizes the line of length %d (Lemma 4.1 with k = %d, s = %d, l = %d, Y = %d)' % (best[0], K, best[1], best[2], best[3]))
else:
    print('RESULT: the lemma does not apply for 2n - 2 <= %d, s <= %d, l <= %d' % (MAXM, SMAX, LMAX))
