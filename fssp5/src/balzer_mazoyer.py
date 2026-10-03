#!/usr/bin/env python3
"""balzer_mazoyer.py -- check Balzer's conditions (B1)-(B4), as formalized in Section 6.4 (and in
balzer.py), on the transitions that Mazoyer's six-state solution actually uses on the lines of
lengths 3..NMAX (the table extracted from Duprat's Coq file is total and emulates the borders, so
only used transitions are meaningful; it synchronizes the lengths n >= 3).  Mazoyer (1986, Sect. 7)
states that his solution satisfies only condition (B3).

usage: balzer_mazoyer.py [NMAX]   (run from fssp5/)"""
import itertools, sys
rule = {}
for ln in open('results/mazoyer6.txt'):
    p = ln.split()
    if len(p) == 4 and not ln.startswith('#'):
        rule[tuple(p[:3])] = p[3]
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150
used = {}
for n in range(3, NMAX + 1):
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        ext = ['*'] + row + ['*']
        new = []
        for i in range(1, n + 1):
            e = (ext[i - 1], ext[i], ext[i + 1])
            v = rule[e]
            used[e] = v
            new.append(v)
        row = new
        if 'F' in row:
            assert t == 2 * n - 2 and set(row) == {'F'}, (n, t, row)
    assert set(row) == {'F'}, n
print('lines 3..%d synchronize at 2n-2; used transitions: %d' % (NMAX, len(used)))
W = ['L', 'G', 'A', 'B', 'C']
GB = ('G', '*')
pre = {('G', 'G', 'G'), ('*', 'G', 'G'), ('G', 'G', '*')}
# B1 (strong: also border neighbours; weak: working neighbours only)
b1s = sorted(e for e, v in used.items() if e[1] == 'G' and not (e[0] in GB and e[2] in GB) and v != 'G')
b1w = [e for e in b1s if e[0] != '*' and e[2] != '*']
# B3 (weak: the three neighbourhoods give F; strong: and no other does)
b3w = [e for e in pre if used.get(e) != 'F']
b3s = sorted(e for e, v in used.items() if v == 'F' and e not in pre)
# B4
b4 = sorted(e for e, v in used.items() if e[0] == 'G' and e[2] == 'G' and e[1] != 'G' and v != 'G')
# B2: an involution I of the working states (F and the border fixed) consistent on used pairs
def involutions(xs):
    xs = list(xs)
    if not xs:
        yield {}
        return
    a, rest = xs[0], xs[1:]
    for I in involutions(rest):
        J = dict(I); J[a] = a; yield J
    for k, b in enumerate(rest):
        for I in involutions(rest[:k] + rest[k + 1:]):
            J = dict(I); J[a] = b; J[b] = a; yield J
ok_inv = []
for I in involutions(W):
    I = dict(I); I['*'] = '*'; I['F'] = 'F'
    bad = [(e, v) for e, v in used.items()
           if (I[e[2]], I[e[1]], I[e[0]]) in used and used[(I[e[2]], I[e[1]], I[e[0]])] != I[v]]
    if not bad:
        ok_inv.append({k: w for k, w in I.items() if k in W and k != w})
print('B1 violations: strong %d, weak %d; e.g. %s' % (len(b1s), len(b1w), b1w[:4]))
print('B2 consistent involutions:', ok_inv if ok_inv else 'none')
print('B3 weak missing: %s; strong: other neighbourhoods producing F: %s' % (b3w, b3s))
print('B4 violations: %d; e.g. %s' % (len(b4), b4[:4]))
