#!/usr/bin/env python3
"""reflsym.py -- restricted class: reflection-symmetric rules,
delta(l,c,r) = delta(r,c,l) for every neighbourhood (the border symbol is
mapped to itself).  usage: reflsym.py N [M] [pump] [timeout] [--sym]"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KISSAT = '/home/user/tools/kissat/build/kissat'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    N = int(args[0])
    M = int(args[1]) if len(args) > 1 else 78
    pump = int(args[2]) if len(args) > 2 else 40
    timeout = int(args[3]) if len(args) > 3 else 600
    E = gencnf.build(5, N, minf=M, pump=pump, symbreak='--sym' in sys.argv)
    for (l, c, r), vs in E.T.items():
        for d in range(E.k):
            E.add([-vs[d], E.T[(r, c, l)][d]])
    cnf = '/tmp/claude-0/reflsym_%d.cnf' % os.getpid()
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
        rule = '/tmp/claude-0/reflsym_N%d.txt' % N
        with open(rule, 'w') as fh:
            gencnf.decode(E, true, fh)
        r = subprocess.run([os.path.join(HERE, 'fsspcheck'), rule, '2', '200'], capture_output=True, text=True)
        extra = ' ' + r.stdout.strip()
    print("reflection-symmetric N=%d M=%d pump=%d: %s (%.1fs)%s" % (N, M, pump, res, time.time() - t0, extra))
    os.remove(cnf)


if __name__ == '__main__':
    main()
