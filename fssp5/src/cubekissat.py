#!/usr/bin/env python3
"""cubekissat.py -- decide single cubes with kissat (formula plus the cube as unit clauses).

For hard cubes this is much faster than solving under assumptions, because the
unit clauses are simplified away by kissat's preprocessing.  Cubes are taken
from CUBES; with --unknown LOGDIR only the cubes whose status in the logs of
LOGDIR is UNKNOWN (and never SAT/UNSAT) are processed; cubes already decided
in LOG are skipped.  One line per cube: "<j> SAT|UNSAT|UNKNOWN <seconds>".

Log files of kissat workers must be named k*.log; a cube listed in another
kissat worker's log is skipped.

usage: cubekissat.py formula.cnf cubes.icnf part nparts log timeout [--unknown LOGDIR] [--reverse]
"""
import glob
import os
import subprocess
import sys
import time

KISSAT = '/home/user/tools/kissat/build/kissat'


def statuses(logdir):
    st = {}
    for fn in glob.glob(os.path.join(logdir, '*.log')):
        for ln in open(fn):
            t = ln.split()
            if len(t) >= 2:
                j, s = int(t[0]), t[1]
                if s in ('SAT', 'UNSAT') or j not in st:
                    st[j] = s
    return st


def main():
    cnf, cubefile, part, nparts, log, timeout = (sys.argv[1], sys.argv[2], int(sys.argv[3]),
                                                 int(sys.argv[4]), sys.argv[5], int(sys.argv[6]))
    only = None
    if '--unknown' in sys.argv:
        st = statuses(sys.argv[sys.argv.index('--unknown') + 1])
        only = {j for j, s in st.items() if s == 'UNKNOWN'}
    logdir = os.path.dirname(os.path.abspath(log))

    def skip():
        # decided cubes, and cubes that another kissat worker (log name k*.log) has taken
        out = set()
        for fn in glob.glob(os.path.join(logdir, '*.log')):
            mine = os.path.abspath(fn) == os.path.abspath(log)
            other_k = os.path.basename(fn).startswith('k') and not mine
            for ln in open(fn):
                t = ln.split()
                if len(t) >= 2 and (t[1] in ('SAT', 'UNSAT') or other_k or (mine and t[1] == 'UNKNOWN')):
                    out.add(int(t[0]))
        return out
    cubes = [[int(x) for x in ln.split()[1:] if x != '0'] for ln in open(cubefile) if ln.startswith('a')]
    with open(cnf) as fh:
        head = fh.readline().split()
        body = fh.read()
    nv, nc = int(head[2]), int(head[3])
    with open(log, 'a') as fl:
        order = list(enumerate(cubes))
        if '--reverse' in sys.argv:
            order.reverse()
        for j, c in order:
            if j % nparts != part or j in skip() or (only is not None and j not in only):
                continue
            text = 'p cnf %d %d\n%s%s' % (nv, nc + len(c), body, ''.join('%d 0\n' % l for l in c))
            t0 = time.time()
            p = subprocess.run([KISSAT, '-q', '--time=%d' % timeout], input=text, capture_output=True, text=True)
            s = [x for x in p.stdout.splitlines() if x.startswith('s ')]
            res = {'s SATISFIABLE': 'SAT', 's UNSATISFIABLE': 'UNSAT'}.get(s[0] if s else '', 'UNKNOWN')
            fl.write('%d %s %.2f\n' % (j, res, time.time() - t0))
            fl.flush()
            if res == 'SAT':
                with open('%s.model%d' % (log, j), 'w') as fm:
                    fm.write(p.stdout)


if __name__ == '__main__':
    main()
