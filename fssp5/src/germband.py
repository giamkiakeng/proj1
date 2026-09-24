#!/usr/bin/env python3
"""germband.py -- band test for half-line germs on long lines.

For a germ that determines the half-line diagram far enough (see germext.c),
the first h chains of the reflected triangle R_n (anti-diagonals
t+i = 2n-1, ..., 2n-2+h) are determined by the rule and the two input
anti-diagonals alone (equation (4) of the paper): chain c at cell i is
delta(chain c-2 at i-1, chain c-1 at i, chain c at i+1).  A minimal-time
solution must fire the cells 1..h at time 2n-2 and nowhere earlier on these
chains, and the return chain must differ from the half-line (return-chain
lemma).  This script fixes the germ, encodes these band constraints for a set
of (long) lengths with the half-line values as constants, and asks kissat
whether some choice of the remaining transitions satisfies them all.
UNSATISFIABLE refutes the germ.

usage: germband.py germfile h lengths [timeout]    (lengths e.g. 20-200:20)
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

KISSAT = '/home/user/tools/kissat/build/kissat'
CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}


def parse(spec):
    out = []
    for part in spec.split(','):
        if ':' in part:
            rng, step = part.split(':')
            a, b = rng.split('-')
            out.extend(range(int(a), int(b) + 1, int(step)))
        elif '-' in part:
            a, b = part.split('-')
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def halfline(germ, T):
    """C_inf on the cells with t+i <= T as a dict of rows, or None if the
    germ does not determine it (a neighbourhood outside the germ occurs)."""
    rows = [[0] * (T + 3)]
    rows[0][1] = 1                    # rows[t][i], i = 1.. ; index 0 unused
    for t in range(1, T):
        prev = rows[-1]
        cur = [0] * (T + 3)
        for i in range(1, T - t + 1):
            if i > t + 1:
                break
            e = (prev[i - 1] if i > 1 else gencnf.BND, prev[i], prev[i + 1])
            d = germ.get(e)
            if d is None:
                return None
            cur[i] = d
        rows.append(cur)
    return rows


def main():
    germfile, h, spec = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 600
    lengths = parse(spec)
    T = 2 * max(lengths) - 1
    stats = {}
    for j, ln in enumerate(open(germfile)):
        if not ln.startswith('GERM'):
            continue
        germ = {(0, 0, 0): 0}
        for tok in ln.split()[1:]:
            e, d = tok.split('>')
            germ[tuple(CODE[x] for x in e)] = CODE[d]
        rows = halfline(germ, T)
        if rows is None:
            print("%d OPEN %s" % (j, ln.strip()))
            stats['OPEN'] = stats.get('OPEN', 0) + 1
            continue
        C = lambda t, i: rows[t][i]
        E = gencnf.Enc(5, max(lengths))
        for e, d in germ.items():
            if e in E.T:
                E.add([E.T[e][d]])
        for n in lengths:
            v = {}

            def val(c, i, n=n, v=v):
                if i == 0 or i == n + 1:
                    return gencnf.BND
                if c == -1:
                    return C(2 * n - 3 - i, i)
                if c == 0:
                    return C(2 * n - 2 - i, i)
                return v[(c, i)]
            for c in range(1, h + 1):
                for i in range(c + 1, n + 1):
                    v[(c, i)] = E.newcell()
            for c in range(1, h + 1):
                for i in range(c, n + 1):
                    a, b, r = val(c - 2, i - 1), val(c - 1, i), val(c, i + 1)
                    if i == c:
                        E.transition(a, b, r, 'FIRE')
                    else:
                        E.transition(a, b, r, v[(c, i)])
            for i in range(2, n + 1):        # return-chain lemma
                E.differ(v[(1, i)], C(2 * n - 1 - i, i))
        cnf = '/tmp/claude-0/germband_%d.cnf' % os.getpid()
        with open(cnf, 'w') as fh:
            gencnf.write_dimacs(E, fh)
        t0 = time.time()
        p = subprocess.run([KISSAT, '-q', '--time=%d' % timeout, cnf], capture_output=True, text=True)
        st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
        res = st[0][2:] if st else 'UNKNOWN'
        stats[res] = stats.get(res, 0) + 1
        print("%d %s %.1f %s" % (j, res, time.time() - t0, ln.strip()))
        sys.stdout.flush()
        os.remove(cnf)
    print("SUMMARY h=%d lengths=%s %s" % (h, spec, stats))


if __name__ == '__main__':
    main()
