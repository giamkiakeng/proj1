#!/usr/bin/env python3
"""
solve.py -- build MT(k,N), run kissat, decode and re-check any model.

usage: solve.py k N [--timeout S] [--check M] [--out rulefile] [gencnf options]
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402
from gencnf import parse_lengths  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KISSAT = os.environ.get('KISSAT', '/home/user/tools/kissat/build/kissat')
CHECK = os.path.join(HERE, 'fsspcheck')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('k', type=int)
    ap.add_argument('N', type=int)
    ap.add_argument('--timeout', type=int, default=3600)
    ap.add_argument('--check', type=int, default=0)
    ap.add_argument('--out', default=None)
    ap.add_argument('--cnf', default=None)
    ap.add_argument('--nodiff', action='store_true')
    ap.add_argument('--nosym', action='store_true')
    ap.add_argument('--leftq', action='store_true')
    ap.add_argument('--rev', action='store_true')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--nmin', type=int, default=2)
    ap.add_argument('--lengths', default=None, help='e.g. 2-9,16,20 (overrides N/nmin)')
    ap.add_argument('--minf', type=int, default=None)
    ap.add_argument('--tinf', type=int, default=0)
    ap.add_argument('--npart', type=int, default=None)
    ap.add_argument('--hpart', type=int, default=None)
    ap.add_argument('--pump', type=int, default=None)
    ap.add_argument('--band', default=None, help='h:Nb')
    ap.add_argument('--links', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    E = gencnf.build(a.k, a.N, diff=not a.nodiff, symbreak=not a.nosym,
                     leftq=a.leftq, rev=a.rev, fire_n=parse_lengths(a.lengths) if a.lengths else range(a.nmin, a.N + 1),
                     minf=a.minf, tinf=a.tinf, npart=a.npart, hpart=a.hpart, pump=a.pump,
                     band=tuple(map(int, a.band.split(':'))) if a.band else None,
                     links=a.links)
    cnf = a.cnf or '/tmp/claude-0/mt_k%d_N%d.cnf' % (a.k, a.N)
    os.makedirs(os.path.dirname(cnf), exist_ok=True)
    with open(cnf, 'w') as fh:
        gencnf.write_dimacs(E, fh)
    t1 = time.time()
    print("k=%d N=%d vars=%d clauses=%d (gen %.1fs)" % (a.k, a.N, E.nv,
                                                        len(E.clauses), t1 - t0))
    sys.stdout.flush()
    p = subprocess.run([KISSAT, '-q', '--time=%d' % a.timeout,
                        '--seed=%d' % a.seed, cnf],
                       capture_output=True, text=True)
    t2 = time.time()
    status = None
    true = set()
    for line in p.stdout.splitlines():
        if line.startswith('s '):
            status = line[2:].strip()
        elif line.startswith('v '):
            for x in line[2:].split():
                v = int(x)
                if v > 0:
                    true.add(v)
    print("result: %s  (solve %.1fs)" % (status, t2 - t1))
    if status == 'SATISFIABLE':
        out = a.out or '/tmp/claude-0/rule_k%d_N%d.txt' % (a.k, a.N)
        with open(out, 'w') as fh:
            gencnf.decode(E, true, fh)
        print("rule written to", out)
        M = a.check or a.N
        r = subprocess.run([CHECK, out, str(a.nmin), str(M)], capture_output=True, text=True)
        print("check %d..%d:" % (a.nmin, M), r.stdout.strip())
    if not a.cnf:
        os.remove(cnf)


if __name__ == '__main__':
    main()
