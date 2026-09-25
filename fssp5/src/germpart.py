#!/usr/bin/env python3
"""germpart.py -- completion test of one germ with partial triangles of long lines.

The germ is fixed; the lengths 2..N must synchronize in minimal time; for the
lengths N < n <= NP the reflected triangle R_n is encoded up to time n-1+H and
no cell of it may fire there (a minimal-time solution never fires before
2n-2); half-line to anti-diagonal max(78, 2 NP - 2), pumping pairs up to 39.
UNSATISFIABLE refutes the germ.

usage: germpart.py germfile N NP H timeout [cnf_out]
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

KISSAT = '/home/user/tools/kissat/build/kissat'
CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}


def main():
    germfile, N, NP, H, timeout = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    out = sys.argv[6] if len(sys.argv) > 6 else '/tmp/claude-0/germpart_%d.cnf' % os.getpid()
    line = [l for l in open(germfile) if l.startswith('GERM')][0]
    E = gencnf.build(5, N, fire_n=list(range(2, N + 1)), minf=max(78, 2 * NP - 2), pump=39,
                     symbreak=False, npart=NP, hpart=H)
    for tok in line.split()[1:]:
        e, d = tok.split('>')
        E.add([E.T[tuple(CODE[x] for x in e)][CODE[d]]])
    with open(out, 'w') as fh:
        gencnf.write_dimacs(E, fh)
    t0 = time.time()
    p = subprocess.run([KISSAT, '-q', '--time=%d' % timeout, out], capture_output=True, text=True)
    st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
    res = st[0][2:] if st else 'UNKNOWN'
    print("%s N=%d NP=%d H=%d %.0fs vars=%d clauses=%d" % (res, N, NP, H, time.time() - t0, E.nv, len(E.clauses)))


if __name__ == '__main__':
    main()
