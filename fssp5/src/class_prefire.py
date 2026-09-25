#!/usr/bin/env python3
"""class_prefire.py germfile pattern N out.cnf -- restricted class of Section 6:
the germ is fixed, the lengths 2..N are required to synchronize in minimal time,
and for 4 <= n <= N the configuration one step before firing is prescribed:
pattern 'U:X' = uniform X^n, pattern 'LGB' = L G^(n-2) B (the class of delta14)."""
import sys
sys.path.insert(0, '/home/user/proj1/fssp5/src')
import gencnf
CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}
germfile, pattern, N, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
line = [l for l in open(germfile) if l.startswith('GERM')][0]
E = gencnf.build(5, N, fire_n=list(range(2, N + 1)), minf=78, pump=39, symbreak=False)
for tok in line.split()[1:]:
    e, d = tok.split('>')
    E.add([E.T[tuple(CODE[x] for x in e)][CODE[d]]])


def vinf(t, i):
    if i == 0:
        return gencnf.BND
    if t == 0:
        return 1 if i == 1 else 0
    if i > t + 1:
        return 0
    return E.inf[(t, i)]


for n in range(4, N + 1):
    R = {}

    def val(t, j, n=n, R=R):
        if j == 0 or j == n + 1:
            return gencnf.BND
        if t + j >= 2 * n - 1:
            return R[(t, j)]
        return vinf(t, j)
    for t in range(n - 1, 2 * n - 2):
        for i in range(1, n + 1):
            if t + i >= 2 * n - 1:
                R[(t, i)] = E.newcell()
    for t in range(n - 1, 2 * n - 2):
        for i in range(1, n + 1):
            if (t, i) in R:
                E.transition(val(t - 1, i - 1), val(t - 1, i), val(t - 1, i + 1), R[(t, i)])
    want = [pattern[2]] * n if pattern.startswith('U:') else ['L'] + ['G'] * (n - 2) + ['B']
    for i in range(1, n + 1):
        c = val(2 * n - 3, i)
        w = CODE[want[i - 1]]
        if isinstance(c, int):
            if c != w:
                E.add([])
        else:
            E.add([c[w]])
with open(out, 'w') as fh:
    gencnf.write_dimacs(E, fh)
print(E.nv, len(E.clauses))
