#!/usr/bin/env python3
"""
models_check.py -- the two models named in Section 7 of the paper.

usage: python3 models_check.py        (in the directory research/)

Both models (research/models/*.txt) are completions of the germ of delta14d (results/delta14d.txt).
The program checks:
  germ14d_T10, T = 10: (G1)-(G3) of Definition 5.4 for every n >= 12;
  d14d_T7c,    T = 7:  (G1)-(G3) for every n >= 9, and (G5) for 9 <= n <= 20; moreover, the lines of
                       lengths 9, 11..17 and 19 have cells 1 and n, but not all cells, in state F at
                       time 2n-2, and no cell in state F before.
Method:
  - the germ of delta14d below anti-diagonal 3000 is computed from results/delta14d.txt; each model
    must contain it, so its half-line is that of delta14d, which has no cell in state F there;
  - (G1): the lines 2..T+1 are simulated;
  - (G2), (G3) for all n >= T+2: asymp.py certifies that the depth rows 0..2T+4 of the half-line
    are periodic and lists representative lengths; its signature of n contains the input cells at
    kappa <= T+2 and the half-line cells that the return chain is compared with, so by Lemma 5.1 and
    Corollary 5.3 of the paper the early rows tau <= T of R_n, and the comparisons of (G3), are those
    of a representative; each representative line is simulated up to time n-1+T;
  - (G5): the lines are simulated as partial maps (a cell is defined iff its three predecessors are
    defined and none of them is F), as in Section 2 of the paper.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
M = 3000


def load(path):
    tab = {}
    for ln in open(path):
        w = ln.split('#')[0].split()
        if len(w) == 4:
            tab[tuple(w[:3])] = w[3]
    return tab


def halfline(tab, M):
    """rows[t][i-1] = C_inf(t, i) for t + i <= M, and the germ below M (neighbourhoods of cells t >= 1)"""
    rows = [['G'] + ['L'] * (M + 1)]
    germ = {}
    for t in range(1, M):
        prev = rows[-1]
        r = ['*'] + prev + ['L']
        cur = list(prev)
        for i in range(1, M - t + 1):
            nb = (r[i - 1], r[i], r[i + 1])
            d = tab[nb]
            if d == 'F':
                sys.exit('the half-line fires at (%d, %d)' % (t, i))
            cur[i - 1] = d
            if nb != ('L', 'L', 'L'):
                germ[nb] = d
        rows.append(cur)
    return rows, germ


def line(tab, n, tmax, partial=False):
    """configurations of the line of length n at t = 0..tmax; partial=True: None marks undefined cells.
    Without partial, the simulation stops after the first configuration that contains F."""
    rows = [['G'] + ['L'] * (n - 1)]
    for t in range(1, tmax + 1):
        p = ['*'] + rows[-1] + ['*']
        if not partial and 'F' in rows[-1]:
            break
        cur = []
        for i in range(1, n + 1):
            nb = (p[i - 1], p[i], p[i + 1])
            cur.append(None if None in nb or 'F' in nb else tab[nb])
        rows.append(cur)
    return rows


def synchronized(tab, n):
    rows = line(tab, n, 2 * n - 2)
    return len(rows) == 2 * n - 1 and all('F' not in r for r in rows[:-1]) and all(c == 'F' for c in rows[-1])


def representatives(germ, T):
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as fh:
        fh.write('GERM ' + ' '.join('%s>%s' % (''.join(nb), d) for nb, d in sorted(germ.items())) + '\n')
        path = fh.name
    out = subprocess.run([sys.executable, os.path.join(HERE, 'asymp.py'), path, str(T), str(T + 2), '8000'],
                         capture_output=True, text=True)
    os.unlink(path)
    lines = out.stdout.splitlines()
    if len(lines) < 2:
        sys.exit(out.stderr)
    return lines[0], [int(s.split(':')[1]) for s in lines[1].split()]


def check_early(tab, C, germ, T):
    """(G1), and (G2), (G3) for all n >= T+2"""
    ok = True
    g1 = [n for n in range(2, T + 2) if not synchronized(tab, n)]
    print('  (G1) lines 2..%d synchronized at 2n-2: %s' % (T + 1, 'yes' if not g1 else 'NO %s' % g1))
    ok &= not g1
    cert, reps = representatives(germ, T)
    print('  ' + cert.lstrip('# '))
    bad = []
    for n in reps:
        rows = line(tab, n, n - 1 + T)
        if len(rows) < n + T or any('F' in r for r in rows):
            bad.append((n, 'F before or at relative time %d' % T))
            continue
        for i in range(n - T, n + 1):            # return chain: t = 2n-1-i <= n-1+T
            t = 2 * n - 1 - i
            if rows[t][i - 1] == C[t][i - 1]:
                bad.append((n, 'return chain equals C_inf at cell %d' % i))
    print('  (G2), (G3) for all n >= %d via %d representative lengths (%d..%d): %s'
          % (T + 2, len(reps), min(reps), max(reps), 'yes' if not bad else 'NO %s' % bad[:5]))
    return ok and not bad


def check_cones(tab, C, lengths):
    """(G5) for the given lengths, with partial lines"""
    bad = []
    for n in lengths:
        rows = line(tab, n, 2 * n - 2, partial=True)

        def R(tau, kappa):
            return rows[n - 1 + tau][n - kappa - 1]
        for tau in range(n):
            for kappa in range(0, min(tau, n - 1 - tau) + 1):
                v = R(tau, kappa)
                if tau < n - 1 and (v is None or v == 'F'):
                    bad.append((n, tau, kappa, v))
        if R(n - 1, 0) != 'F':
            bad.append((n, 'right end not F'))
        for kappa in range(0, (n - 1) // 2 + 1):
            if R(kappa, kappa) == C[n - 1 + kappa][n - kappa - 1]:
                bad.append((n, 'return chain', kappa))
    return bad


def both_ends(tab, n):
    rows = line(tab, n, 2 * n - 2)
    if len(rows) < 2 * n - 1 or any('F' in r for r in rows[:-1]):
        return False
    last = rows[-1]
    return last[0] == 'F' and last[-1] == 'F' and any(c != 'F' for c in last)


def main():
    d14d = load(os.path.join(RES, 'delta14d.txt'))
    C, germ = halfline(d14d, M)
    print('germ of delta14d below anti-diagonal %d: %d neighbourhoods besides (L,L,L); no F' % (M, len(germ)))
    allok = True
    for name, T in (('germ14d_T10', 10), ('d14d_T7c', 7)):
        tab = load(os.path.join(HERE, 'models', name + '.txt'))
        contains = all(tab.get(nb) == d for nb, d in germ.items())
        print('%s (T = %d): contains the germ of delta14d: %s' % (name, T, contains))
        ok = contains and check_early(tab, C, germ, T)
        if name == 'd14d_T7c':
            bad = check_cones(tab, C, range(9, 21))
            print('  (G5) for 9 <= n <= 20 (partial lines): %s' % ('yes' if not bad else 'NO %s' % bad[:5]))
            ends = [n for n in range(9, 25) if both_ends(tab, n)]
            print('  lengths 9..24 whose line has cells 1 and n, not all cells, F at 2n-2 and no F before: %s'
                  % ends)
            ok &= not bad and ends == [9, 11, 12, 13, 14, 15, 16, 17, 19]
        allok &= ok
    print('ALL CHECKS PASSED' if allok else 'SOME CHECK FAILED')


if __name__ == '__main__':
    main()
