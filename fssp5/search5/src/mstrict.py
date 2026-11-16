"""mstrict.py -- gap clauses of Lemma 6.3 for the strict formula of the lines 2..N (stable generals, (B1) strong).

mcopy.py --wgap assumes that a half-line cell i >= 2 is never G; with --strict this holds only for t + i <= 2N-4
(the wall lemma needs two lines), so the cells of the line N on the anti-diagonals 2N-3 and 2N-2 may be G.
add_strict_gaps(M, N) adds the same clauses with the variables of these cells: on the line n at a time
n-1 <= t <= 2n-4, two barriers (borders or cells in state G) at a distance d >= 2 need 2n-3-t <= M(d-1),
M(1) = 3, M(l) = 3^l + M(l-1) (five states).  Lemma 6.3 is a statement about one line, so nothing longer than N is used.
"""
MG = [0, 3, 12, 39, 120, 363]

def add_strict_gaps(M, N, nmin=2):
    E = M.E
    cnt = 0
    for n in range(nmin, N + 1):
        def g(t, i):
            if i == 0 or i == n + 1:
                return True
            if t + i <= 2 * n - 2:                      # agreement region: a half-line cell
                if i == 1:
                    return True                         # the first cell is G (unit clauses of --gstatic)
                if t + i <= 2 * N - 4:
                    return False                        # wall lemma for the lines up to N (unit clauses of --noghws)
            return M.cell(n, t, i)[1]
        for t in range(max(1, n - 1), 2 * n - 3):       # n-1 <= t <= 2n-4
            rho = 2 * n - 3 - t
            dmax = 1 + max(l for l in range(len(MG)) if MG[l] < rho)
            pos = [i for i in range(0, n + 2) if g(t, i) is not False]
            for x in pos:
                for d in range(2, dmax + 1):
                    y = x + d
                    if y > n + 1 or g(t, y) is False:
                        continue
                    c = [-v for v in (g(t, x), g(t, y)) if v is not True]
                    assert c, (n, t, x, y)
                    E.add(c); cnt += 1
    return cnt
