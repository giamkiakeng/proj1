#!/usr/bin/env python3
"""class_prefire14.py N -- CNF: germ of delta14 fixed, lengths 2..N, and the pre-firing
configuration L G^(n-2) B required for 4 <= n <= N (restricted class of the paper, Section 6)."""
import sys
sys.path.insert(0, '/home/user/proj1/fssp5/src')
import gencnf
CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}
N = int(sys.argv[1])
line = open('/home/user/proj1/fssp5/results/germs/germ_delta14.txt').read()
E = gencnf.build(5, N, fire_n=list(range(2, N + 1)), minf=78, pump=39, symbreak=False)
for tok in line.split()[1:]:
    e, d = tok.split('>')
    E.add([E.T[tuple(CODE[x] for x in e)][CODE[d]]])
# restricted class: pre-firing configuration L G^(n-2) B for 4 <= n <= N.
# Re-create the reflected-triangle variables: gencnf.build keeps them only
# implicitly, so impose the class through the transition table instead:
# the cells at time 2n-3 are determined by cells at time 2n-4; we add the
# constraint by encoding the lines again with explicit target cells.
Rall = {}
def vinf(t, i):
    if i == 0: return gencnf.BND
    if t == 0: return 1 if i == 1 else 0
    if i > t + 1: return 0
    return E.inf[(t, i)]
for n in range(4, N + 1):
    R = {}
    def val(t, j, n=n, R=R):
        if j == 0 or j == n + 1: return gencnf.BND
        if t + j >= 2 * n - 1: return R[(t, j)]
        return vinf(t, j)
    for t in range(n - 1, 2 * n - 2):
        for i in range(1, n + 1):
            if t + i >= 2 * n - 1:
                R[(t, i)] = E.newcell()
    for t in range(n - 1, 2 * n - 2):
        for i in range(1, n + 1):
            if (t, i) in R:
                E.transition(val(t - 1, i - 1), val(t - 1, i), val(t - 1, i + 1), R[(t, i)])
    T = 2 * n - 3
    want = ['L'] + ['G'] * (n - 2) + ['B']
    for i in range(1, n + 1):
        c = val(T, i)
        w = CODE[want[i - 1]]
        if isinstance(c, int):
            if c != w: E.add([])
        else:
            E.add([c[w]])
with open('/home/user/proj1/fssp5/cnf/class15_%d.cnf' % N, 'w') as fh:
    gencnf.write_dimacs(E, fh)
print(E.nv, len(E.clauses))
