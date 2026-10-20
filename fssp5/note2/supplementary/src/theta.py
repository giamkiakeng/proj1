#!/usr/bin/env python3
"""
theta.py -- where the depth-rows behind the front become periodic (Theorem 3.4 of the note).

In the frame of the front, Phi_t(j) = C_inf(t, t+1-j) is the cell at depth j behind the front;
the depth-row t -> Phi_t(j) starts at time j and is eventually periodic.  For a rule file and a
finite horizon T this prints, for each depth j <= jmax, the least eventual period p <= pmax seen
on the tail of the row and theta_T(j) := the least t0 >= j with Phi_t(j) = Phi_{t+p}(j) for all
t0 <= t <= T-p.  On a finite horizon this is an observation, not a proof: if the row has period p
from theta(j) on, then theta_T(j) <= theta(j).

usage: theta.py RULEFILE [T=1400] [jmax=300] [jmin=10] [pmax=12]
   prints theta_T(j) - ceil(3j/2) and theta_T(j) - 2j for jmin <= j <= jmax (as sets) and the periods
"""
import sys


def load(rulefile):
    tab = {}
    for ln in open(rulefile):
        t = ln.split('#')[0].split()
        if len(t) == 4:
            tab[tuple(t[:3])] = t[3]
    return tab


def halfline(tab, T):
    """rows[t][i-1] = C_inf(t, i) for 1 <= i <= t+2 (cells beyond t+1 are quiescent)"""
    rows = [['G', 'L']]
    for t in range(T):
        prev = rows[-1] + ['L', 'L']
        rows.append([tab[(prev[i - 1] if i > 0 else '*', prev[i], prev[i + 1])] for i in range(len(prev) - 1)])
    return rows


def theta(rows, j, pmax, tail=200):
    T = len(rows) - 1
    r = [rows[t][t - j] for t in range(j, T + 1)]       # r[t-j] = Phi_t(j) = C_inf(t, t+1-j)
    for p in range(1, pmax + 1):
        if all(r[k] == r[k + p] for k in range(len(r) - tail, len(r) - p)):
            break
    else:
        return None, None
    k = len(r) - 1 - p
    while k >= 0 and r[k] == r[k + p]:
        k -= 1
    return j + k + 1, p


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    T, jmax, jmin, pmax = [int(x) for x in (a[1:] + ['1400', '300', '10', '12'][len(a) - 1:])][:4]
    rows = halfline(load(a[0]), T)
    res = {j: theta(rows, j, pmax) for j in range(jmin, jmax + 1)}
    if any(th is None for th, _ in res.values()):
        sys.exit('no period <= %d on the tail of some row; increase T or pmax' % pmax)
    print('%s, horizon T=%d, depths %d..%d:' % (a[0], T, jmin, jmax))
    print('  theta_T(j) - ceil(3j/2):', sorted({th - (3 * j + 1) // 2 for j, (th, _) in res.items()}))
    print('  theta_T(j) - 2j:        ', sorted({th - 2 * j for j, (th, _) in res.items()}))
    print('  periods:                ', sorted({p for _, p in res.values()}))


if __name__ == '__main__':
    main()
