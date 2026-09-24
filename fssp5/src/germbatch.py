#!/usr/bin/env python3
"""germbatch.py -- completion test for a list of half-line germs (output of germdfs).

For each germ (fixed half-line transitions), decide with kissat whether some
completion synchronizes all lengths 2..N in minimal time (with the half-line to
anti-diagonal M and pumping up to M/2).  Prints one line per germ.

usage: germbatch.py germfile N [M] [timeout]
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
    germfile, N = sys.argv[1], int(sys.argv[2])
    M = int(sys.argv[3]) if len(sys.argv) > 3 else 78
    timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 600
    # symmetry already broken by the germ enumeration (anti-diagonal order); the
    # time-major symmetry breaking of the CNF must NOT be added on top of it
    E = gencnf.build(5, N, minf=M, pump=min(40, M // 2), symbreak=False)
    base = '/tmp/claude-0/germbatch_base_%d.cnf' % os.getpid()
    with open(base, 'w') as fh:
        gencnf.write_dimacs(E, fh)
    hdr_len = len(open(base).readline())
    body = open(base).read()[hdr_len:]
    stats = {}
    for j, ln in enumerate(open(germfile)):
        if not ln.startswith('GERM'):
            continue
        units = []
        for tok in ln.split()[1:]:
            e, d = tok.split('>')
            key = tuple(CODE[x] for x in e)
            units.append(E.T[key][CODE[d]])
        cnf = '/tmp/claude-0/germbatch_%d.cnf' % os.getpid()
        with open(cnf, 'w') as fh:
            fh.write("p cnf %d %d\n" % (E.nv, len(E.clauses) + len(units)))
            fh.write(body)
            for u in units:
                fh.write("%d 0\n" % u)
        t0 = time.time()
        p = subprocess.run([KISSAT, '-q', '--time=%d' % timeout, cnf], capture_output=True, text=True)
        st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
        res = st[0][2:] if st else 'UNKNOWN'
        stats[res] = stats.get(res, 0) + 1
        print("%d %s %.1f %s" % (j, res, time.time() - t0, ln.strip()))
        sys.stdout.flush()
    print("SUMMARY", stats)
    for f in (base, '/tmp/claude-0/germbatch_%d.cnf' % os.getpid()):
        if os.path.exists(f):
            os.remove(f)


if __name__ == '__main__':
    main()
