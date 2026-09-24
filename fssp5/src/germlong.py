#!/usr/bin/env python3
"""germlong.py -- completion test of half-line germs against long lines.

For each germ (GERM line), fix its transitions and ask kissat whether the
remaining transitions can be chosen so that every length of the given set
synchronizes in minimal time.  The half-line is encoded up to anti-diagonal
2*max-2 (at least 78) and the pumping pairs up to 39; for germs that
determine the half-line that far (see germext.c) the half-line part of the
formula is fixed by unit propagation and only the reflected triangles remain.

usage: germlong.py germfile lengths [timeout]      (lengths e.g. 2-10,24,32)
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
    germfile, spec = sys.argv[1], sys.argv[2]
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    lengths = gencnf.parse_lengths(spec)
    N = max(lengths)
    E = gencnf.build(5, N, fire_n=lengths, minf=max(78, 2 * N - 2), pump=39, symbreak=False)
    base = '/tmp/claude-0/germlong_base_%d.cnf' % os.getpid()
    with open(base, 'w') as fh:
        gencnf.write_dimacs(E, fh)
    with open(base) as fh:
        fh.readline()
        body = fh.read()
    os.remove(base)
    stats = {}
    for j, ln in enumerate(open(germfile)):
        if not ln.startswith('GERM'):
            continue
        units = []
        for tok in ln.split()[1:]:
            e, d = tok.split('>')
            units.append(E.T[tuple(CODE[x] for x in e)][CODE[d]])
        cnf = '/tmp/claude-0/germlong_%d.cnf' % os.getpid()
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
        os.remove(cnf)
    print("SUMMARY", spec, stats)


if __name__ == '__main__':
    main()
