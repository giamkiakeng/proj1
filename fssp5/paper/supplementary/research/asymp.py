#!/usr/bin/env python3
"""
asymp.py -- the early rows of all reflected triangles R_n, n >= NMIN, for a fixed half-line.

For a germ that determines C_inf, the cells of R_n at relative times tau <= T depend only on the
input cells at kappa <= T+1 and on C_inf on the return chain at kappa <= T, i.e. on the depth rows
j <= D := 2T+4 near the front.  The depth column V_t = (Phi_t(0), ..., Phi_t(D)) evolves by a fixed
map for t > D, so a repetition V_t0 = V_t0+p certifies that the rows 0..D are periodic from t0 with
period p.  Then the early rows of R_n depend only on n mod p for n >= t0+3, and the constraint
"no cell of R_n fires at tau <= T, for every n >= NMIN" reduces to finitely many lengths: one per
distinct signature among max(NMIN, T+3) <= n < max(NMIN, t0+3) + p, plus each NMIN <= n < T+3.

usage: asymp.py GERMFILE T NMIN [TMAX]
   prints the certificate (t0, p) and the specs early:n:T of the representative lengths
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfix  # noqa: E402


def depth_rows(germ, D, tmax):
    """Phi_t(j) for 0 <= j <= D, 0 <= t <= tmax (L for j < 0 and before row j starts)"""
    val = gfix.halfline(germ, 2 * D + 4)        # cells (t, t+1-j), t <= D+1, j <= D, lie on anti-diagonals <= 2D+3
    phi = []
    for t in range(tmax + 1):
        row = []
        for j in range(D + 1):
            if j > t:
                row.append(None)                # row j starts at time j
            elif t <= D + 1:
                row.append(val(t, t + 1 - j))
            else:
                p = phi[t - 1]
                g = lambda x: 'L' if x < 0 else p[x]
                nb = (g(j), g(j - 1), g(j - 2))
                if nb == ('L', 'L', 'L'):
                    row.append('L')
                elif nb in germ:
                    row.append(germ[nb])
                else:
                    raise SystemExit('germ not closed: neighbourhood %s at depth %d, time %d' % (''.join(nb), j, t))
        phi.append(row)
    return phi


def main():
    germ = gfix.parse_germ(sys.argv[1])
    germ.setdefault(('L', 'L', 'L'), 'L')
    T, nmin = int(sys.argv[2]), int(sys.argv[3])
    tmax = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
    D = 2 * T + 4
    phi = depth_rows(germ, D, tmax)
    seen = {}
    t0 = p = None
    for t in range(D + 2, tmax + 1):
        key = tuple(phi[t])
        if key in seen:
            t0, p = seen[key], t - seen[key]
            break
        seen[key] = t
    if t0 is None:
        raise SystemExit('no repetition of the depth column (D = %d) up to time %d' % (D, tmax))
    assert all(phi[t0 + s] == phi[t0 + p + s] for s in range(min(p, tmax - t0 - p) + 1))

    def Phi(t, j):
        if j < 0:
            return 'L'
        if t > tmax:                            # periodic continuation (certified above)
            t = t0 + (t - t0) % p
        return phi[t][j]

    def sig(n):
        return tuple((Phi(n - 3 + k, 2 * k - 2) if n - 3 + k >= 0 else 'L', Phi(n - 2 + k, 2 * k - 1), Phi(n - 1 + k, 2 * k))
                     for k in range(T + 3))
    # lengths below T+3 are kept individually (Lemma A needs n >= T+3); above, one length per signature
    small = list(range(nmin, min(T + 3, max(nmin, t0 + 3) + p)))
    reps = {}
    for n in range(max(nmin, T + 3), max(nmin, t0 + 3) + p):
        reps.setdefault(sig(n), n)
    lengths = sorted(set(small) | set(reps.values()))
    print('# depth rows 0..%d periodic from t0 = %d with period p = %d; %d lengths below T+3 = %d, '
          '%d signatures among n >= %d' % (D, t0, p, len(small), T + 3, len(reps), max(nmin, T + 3)))
    print(' '.join('early:%d:%d' % (n, T) for n in lengths))


if __name__ == '__main__':
    main()
