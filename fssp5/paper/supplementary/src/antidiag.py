#!/usr/bin/env python3
"""
antidiag.py -- neighbourhoods and anti-diagonals of the half-line of a rule (Corollary 6.4).

usage: python3 antidiag.py RULE M [D LO HI ...]

Simulates the half-line of the rule table RULE on the cells (t, i) with t + i <= M and prints
  - the neighbourhoods (l, c, r) of the cells (t, i) with t >= 1 and t + i <= M, other than (L, L, L),
    with their values (the germ below M), in the one-line format 'GERM lcr>d ...';
  - for each triple D LO HI, the states of the cells LO..HI on the anti-diagonal t + i = D, as runs
    'state x count'.
Rule tables as in firstfire.py.  Written independently of the other programs.
"""
import sys


def load(path):
    tab = {}
    for ln in open(path):
        w = ln.split()
        if not w or w[0].startswith('#') or w[0] == 'k':
            continue
        tab[tuple(w[:3])] = w[3]
    return tab


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    tab = load(sys.argv[1])
    M = int(sys.argv[2])
    rows = [['G'] + ['L'] * (M + 1)]                 # rows[t][i-1] = C_inf(t, i), cells 1..M+2
    germ = {}
    for t in range(1, M):
        prev = rows[-1]
        r = ['*'] + prev + ['L']
        cur = list(prev)
        for i in range(1, M - t + 1):                # cells with t + i <= M
            nb = (r[i - 1], r[i], r[i + 1])
            d = tab[nb]
            if d == 'F':
                sys.exit('the half-line fires at (%d, %d)' % (t, i))
            cur[i - 1] = d
            if nb != ('L', 'L', 'L'):
                germ[nb] = d
        rows.append(cur)
    print('%s: %d neighbourhoods besides (L,L,L) on the cells with t >= 1, t + i <= %d'
          % (sys.argv[1], len(germ), M))
    print('GERM ' + ' '.join('%s>%s' % (''.join(nb), d) for nb, d in sorted(germ.items())))
    args = sys.argv[3:]
    for j in range(0, len(args) - 2, 3):
        D, lo, hi = int(args[j]), int(args[j + 1]), int(args[j + 2])
        word = [rows[D - i][i - 1] for i in range(lo, hi + 1)]
        runs = []
        for s in word:
            if runs and runs[-1][0] == s:
                runs[-1][1] += 1
            else:
                runs.append([s, 1])
        print('anti-diagonal t+i=%d, cells %d..%d: %s' % (D, lo, hi, ' '.join('%sx%d' % (s, c) for s, c in runs)))


if __name__ == '__main__':
    main()
