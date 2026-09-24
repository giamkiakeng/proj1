#!/usr/bin/env python3
"""equiv.py -- restricted class: rules equivariant under a state permutation.

For a permutation sigma of the working states {L,G,A,B} (F and the border
fixed), require delta(sigma a, sigma b, sigma c) = sigma delta(a,b,c) for every
neighbourhood.  Scans all non-identity permutations on
MT_5(2..N; M, N') (no symmetry breaking: the class is not invariant under
renaming A <-> B) and reports kissat's verdict for each.

usage: equiv.py N [M] [pump] [timeout] [perm ...]
"""
import itertools
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KISSAT = '/home/user/tools/kissat/build/kissat'
NAMES = 'LGAB'


def add_equiv(E, sig):
    s = dict(enumerate(sig))
    s[gencnf.BND] = gencnf.BND
    s[E.F] = E.F
    for e, vs in E.T.items():
        e2 = tuple(s[x] for x in e)
        for d in range(E.k):
            E.add([-vs[d], E.T[e2][s[d]]])


def main():
    N = int(sys.argv[1])
    M = int(sys.argv[2]) if len(sys.argv) > 2 else 78
    pump = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 120
    perms = sys.argv[5:] or [''.join(NAMES[x] for x in p) for p in itertools.permutations(range(4))][1:]
    for ps in perms:
        sig = [NAMES.index(ch) for ch in ps]
        E = gencnf.build(5, N, minf=M, pump=pump, symbreak=False)
        add_equiv(E, sig)
        cnf = '/tmp/claude-0/equiv_%d.cnf' % os.getpid()
        with open(cnf, 'w') as fh:
            gencnf.write_dimacs(E, fh)
        t0 = time.time()
        p = subprocess.run([KISSAT, '-q', '--time=%d' % timeout, cnf], capture_output=True, text=True)
        st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
        res = st[0][2:] if st else 'UNKNOWN'
        extra = ''
        if res == 'SATISFIABLE':
            true = set()
            for ln in p.stdout.splitlines():
                if ln.startswith('v '):
                    true.update(int(x) for x in ln[2:].split() if int(x) > 0)
            rule = '/tmp/claude-0/equiv_%s_N%d.txt' % (ps, N)
            with open(rule, 'w') as fh:
                gencnf.decode(E, true, fh)
            r = subprocess.run([os.path.join(HERE, 'fsspcheck'), rule, '2', '200'],
                               capture_output=True, text=True)
            extra = ' ' + r.stdout.strip()
        print("sigma LGAB->%s N=%d: %s (%.1fs)%s" % (ps, N, res, time.time() - t0, extra))
        sys.stdout.flush()
        os.remove(cnf)


if __name__ == '__main__':
    main()
