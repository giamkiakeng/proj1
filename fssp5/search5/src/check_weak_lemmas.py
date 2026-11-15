#!/usr/bin/env python3
"""check_weak_lemmas.py RULE... -- the statements (a)-(e) of weakwalls.py, checked on the diagrams of rules that
satisfy the weak reading of (B1) and delta(GGG) = delta(*GG) = delta(GG*) = F on the transitions they use."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simlib import load, sim, ok
MG = [0, 3, 12, 39, 120, 363, 1092]
MB = [0, 3, 15, 51, 159, 483, 1455]
for path in sys.argv[1:]:
    k, tab = load(path)
    if k != 5:
        continue
    good = [n for n in range(2, 60) if ok(tab, n)]
    used = {}
    for n in good:
        rr = sim(tab, n)
        for t in range(2 * n - 2):
            row = '*' + ''.join(rr[t]) + '*'
            for i in range(1, n + 1):
                used[row[i - 1:i + 2]] = rr[t + 1][i - 1]
    b1w = all(d == 'G' for e, d in used.items() if e[1] == 'G' and '*' not in e and (e[0], e[2]) != ('G', 'G'))
    b3w = all(used.get(e, 'F') == 'F' for e in ('GGG', '*GG', 'GG*'))
    name = os.path.basename(path)
    if not (b1w and b3w):
        print('%-28s sync %s: not in the class (B1 weak %s, B3 weak %s on used transitions)' % (name, good[:3] + ['..'] + good[-1:], b1w, b3w))
        continue
    bad = []
    wallfree, walled = [], []
    for n in good:
        if n < 3:
            continue
        rr = [''.join(r) for r in sim(tab, n)]
        T = 2 * n - 3
        g = lambda t, i: i < 1 or i > n or rr[t][i - 1] == 'G'
        (walled if any(g(t, i) for t in range(T + 1) for i in range(2, n)) else wallfree).append(n)
        for t in range(0, T):
            rho = T - t
            for i in range(1, n + 1):
                if g(t, i - 1) and g(t, i) and g(t, i + 1):
                    bad.append(('a', n, t, i))
            inter = [i for i in range(2, n) if g(t, i)]
            for i in inter:
                if not g(t + 1, i):
                    bad.append(('b', n, t, i))
            for x in inter:
                for y in inter:
                    d = y - x
                    if d >= 2 and d - 1 < len(MG) and MG[d - 1] < rho:
                        bad.append(('d', n, t, x, y))
                if x - 1 < len(MB) and MB[x - 1] < rho:
                    bad.append(('e-left', n, t, x))
                if n - x < len(MB) and MB[n - x] < rho:
                    bad.append(('e-right', n, t, x))
        if any(g(T, i) for i in range(2, n)) and rr[T] != 'G' * n:
            bad.append(('c', n, rr[T]))
        # half-line: no G beyond the first cell on the part that the longer synchronized lines determine
        for t in range(T + 1):
            for i in range(2, n + 1):
                if t + i <= 2 * n - 2 and rr[t][i - 1] == 'G' and (n + 1 in good):
                    bad.append(('wall-lemma', n, t, i))
    print('%-28s sync %s: in the class; lines with interior walls %s, without %s; violations: %s' % (
        name, [good[0], '..', good[-1]] if good == list(range(good[0], good[-1] + 1)) else good, walled[:2] + ['..'] + walled[-1:] if walled else [], wallfree, bad[:5] if bad else 'none'))
