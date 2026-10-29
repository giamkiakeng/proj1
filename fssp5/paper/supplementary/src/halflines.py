#!/usr/bin/env python3
"""
halflines.py -- two observations on half-lines used in Section 5 of the note.

  values RULE T      for every cell i, the set of states of C_inf(t, i), 3 <= t < T (cells 1, 2,
                     and all cells i >= 3 together), and, if the cells i >= 3 use exactly two
                     states x < y, the elementary cellular automaton number of the rule
                     restricted to {x, y}^3 (Wolfram's numbering with x = 0, y = 1)
  compare M RULE...  whether the half-lines of the rules agree on the cells t >= 1, t + i <= M up to
                     a renaming of the states other than L (states renamed by first occurrence in
                     the order of anti-diagonals, then time)

usage: halflines.py values results/delta14.txt 1500
       halflines.py compare 300 results/delta14.txt results/delta14b.txt ...
"""
import itertools
import sys

from theta import halfline, load


def values(rule, T):
    rows = halfline(load(rule), T)
    tab = load(rule)
    seen = {1: set(), 2: set(), 3: set()}
    for t in range(3, T):
        for i, x in enumerate(rows[t][:t + 1], 1):     # cells 1..t+1 (beyond the front: L)
            seen[min(i, 3)].add(x)
    print('%s, 3 <= t < %d: cell 1 %s, cell 2 %s, cells i >= 3 %s' % (
        rule, T, sorted(seen[1]), sorted(seen[2]), sorted(seen[3])))
    if len(seen[3]) == 2:
        x, y = sorted(seen[3], key=lambda s: (s != 'L', s))
        bit = {x: 0, y: 1}
        code = 0
        for nb in itertools.product((x, y), repeat=3):
            d = tab[nb]
            if d not in bit:
                print('  the rule leaves {%s,%s}: delta%s = %s' % (x, y, nb, d))
                return
            code |= bit[d] << (4 * bit[nb[0]] + 2 * bit[nb[1]] + bit[nb[2]])
        print('  rule restricted to {%s,%s}^3 (%s = 0, %s = 1): elementary CA %d' % (x, y, x, y, code))


def canon(rows, M):
    ren, fresh, out = {'L': 'L'}, iter('abcdefgh'), []
    for s in range(2, M + 1):
        for t in range(1, s):
            if s - t <= t + 1:
                x = rows[t][s - t - 1]
                if x not in ren:
                    ren[x] = next(fresh)
                out.append(ren[x])
    return ''.join(out)


def compare(M, rules):
    H = {r: canon(halfline(load(r), M), M) for r in rules}
    for a, b in itertools.combinations(rules, 2):
        print('%s  %s  %s' % (a, b, 'equal up to renaming' if H[a] == H[b] else 'differ'))
    classes = len(set(H.values()))
    print('%d rules, %d distinct half-lines up to renaming (t + i <= %d)' % (len(rules), classes, M))


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == 'values':
        values(a[1], int(a[2]))
    elif len(a) >= 3 and a[0] == 'compare':
        compare(int(a[1]), a[2:])
    else:
        sys.exit(__doc__)
