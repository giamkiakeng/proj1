#!/usr/bin/env python3
"""
pumping.py -- the right-end pumping lemma.

Relative coordinates for the reflected triangle R_n of a line of length n:
tau = t-(n-1) (time since the right end was reached), kk = n-i (distance to
the right end).  R_n = {0 <= kk <= tau <= n-1}; its input cells are the
C_inf cells with tau-kk in {-1,-2} (anti-diagonals 2n-2 and 2n-3), i.e.
    J_n(kk) = ( C_inf(n-3+kk, n-kk), C_inf(n-2+kk, n-kk) ).
The right border is kk=-1, the left border kk=n.  The relative computation
does not depend on n except through the left border.

cone(n) = set of input positions kk on which the right end at relative time
n-1 (absolute time 2n-2) depends; computed by breadth-first search over the
dependency relation.  If the cone avoids the left border and J_n = J_n' on
cone(n) for some n' > n, the right end of line n' is in state F at time
n'+n-2 < 2n'-2.  Hence every minimal-time solution satisfies
    PUMP(n,n'):  J_n and J_n' differ somewhere on cone(n).
"""
import functools
import sys


@functools.lru_cache(maxsize=None)
def cone(n):
    """Input positions kk (and which of the two anti-diagonals) that the
    right end at relative time n-1 depends on; None if the left border of
    R_n is reached."""
    need = set()
    seen = set()
    stack = [(n - 1, 0)]
    while stack:
        tau, kk = stack.pop()
        if (tau, kk) in seen:
            continue
        seen.add((tau, kk))
        for dk in (1, 0, -1):
            k2, t2 = kk + dk, tau - 1
            if k2 == -1:
                continue            # right border
            if k2 >= n:
                return None         # left border reached
            d = t2 - k2
            if d >= 0:
                stack.append((t2, k2))
            elif d in (-1, -2):
                need.add((k2, d))   # input cell; d=-1: anti-diag 2n-2, d=-2: 2n-3
            else:
                raise AssertionError("dependency below the input anti-diagonals")
    return frozenset(need)


@functools.lru_cache(maxsize=None)
def cone_max(n, tau, kk):
    """largest input position kk' in the dependency cone of the relative cell
    (tau,kk) of R_n, or None if the left border kk=n is reached"""
    best = -1
    seen = set()
    stack = [(tau, kk)]
    while stack:
        t1, k1 = stack.pop()
        if (t1, k1) in seen:
            continue
        seen.add((t1, k1))
        for dk in (1, 0, -1):
            k2, t2 = k1 + dk, t1 - 1
            if k2 == -1:
                continue
            if k2 >= n:
                return None
            d = t2 - k2
            if d >= 0:
                stack.append((t2, k2))
            else:
                best = max(best, k2)
    return best


def input_cell(n, kk, d):
    """absolute (t,i) of the input cell at relative position kk on
    anti-diagonal 2n-2 (d=-1) or 2n-3 (d=-2)"""
    i = n - kk
    t = (2 * n - 2 - i) if d == -1 else (2 * n - 3 - i)
    return t, i


def check_rule(rulefile, nmax):
    """verify PUMP(n,n') on an actual rule (simulating C_inf)"""
    tab = {}
    k = None
    for ln in open(rulefile):
        t = ln.split('#')[0].split()
        if len(t) == 2 and t[0] == 'k':
            k = int(t[1])
        elif len(t) == 4:
            tab[tuple(t[:3])] = t[3]
    T = 2 * nmax
    rows = [['G'] + ['L'] * (T + 2)]
    for t in range(T):
        prev = rows[-1]
        new = []
        for i in range(len(prev)):
            l = prev[i - 1] if i > 0 else '*'
            r = prev[i + 1] if i + 1 < len(prev) else 'L'
            new.append(tab[(l, prev[i], r)])
        rows.append(new)

    def C(t, i):
        return rows[t][i - 1]

    bad = 0
    for n in range(4, nmax):
        cn = cone(n)
        if cn is None:
            continue
        for n2 in range(n + 1, nmax + 1):
            if all(C(*input_cell(n, kk, d)) == C(*input_cell(n2, kk, d)) for kk, d in cn):
                bad += 1
                print("PUMP violated for n=%d n'=%d" % (n, n2))
    print("checked PUMP(n,n') for 4 <= n < n' <= %d: %d violations" % (nmax, bad))


if __name__ == '__main__':
    for n in (4, 5, 6, 10, 20):
        c = cone(n)
        print(n, None if c is None else sorted(c))
    if len(sys.argv) > 2:
        check_rule(sys.argv[1], int(sys.argv[2]))
