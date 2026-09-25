#!/usr/bin/env python3
"""cuberefine.py -- split the undecided cubes of a cube-and-conquer run further.

For every cube whose status in the logs of LOGDIR is UNKNOWN (and never SAT or
UNSAT), the formula is extended by the cube's literals as unit clauses and
split again by march_cu (static depth D).  The combined cubes (old cube plus
new literals) are written to OUT (one "a ... 0" line each); OUT.map lists the
parent cube of every new cube.  A cube for which march_cu reports
unsatisfiability during cubing (no cube printed) needs no further work and is
recorded in OUT.refuted.  Since every cube is replaced by a set of cubes that
covers it (up to march_cu's satisfiability-preserving reductions), the
original formula is unsatisfiable iff all cubes of OUT (and all previously
decided cubes) are.

usage: cuberefine.py formula.cnf cubes.icnf LOGDIR D OUT
"""
import glob
import os
import subprocess
import sys

MARCH = '/home/user/tools/CnC/march_cu/march_cu'


def main():
    cnf, cubefile, logdir, D, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
    cubes = [[int(x) for x in ln.split()[1:] if x != '0'] for ln in open(cubefile) if ln.startswith('a')]
    status = {}
    for fn in glob.glob(os.path.join(logdir, '*.log')):
        for ln in open(fn):
            t = ln.split()
            if len(t) < 2:
                continue
            j, st = int(t[0]), t[1]
            if st in ('SAT', 'UNSAT') or j not in status:
                status[j] = st
    todo = sorted(j for j, st in status.items() if st == 'UNKNOWN')
    with open(cnf) as fh:
        header = fh.readline().split()
        body = fh.read()
    nv, nc = int(header[2]), int(header[3])
    tmp = '/tmp/claude-0/refine_%d.cnf' % os.getpid()
    tmpc = '/tmp/claude-0/refine_%d.icnf' % os.getpid()
    n_out = 0
    with open(out, 'w') as fo, open(out + '.map', 'w') as fm, open(out + '.refuted', 'w') as fr:
        for j in todo:
            c = cubes[j]
            with open(tmp, 'w') as fh:
                fh.write('p cnf %d %d\n' % (nv, nc + len(c)))
                fh.write(body)
                for lit in c:
                    fh.write('%d 0\n' % lit)
            if os.path.exists(tmpc):
                os.remove(tmpc)
            p = subprocess.run([MARCH, tmp, '-d', str(D), '-o', tmpc], capture_output=True, text=True)
            subs = []
            if os.path.exists(tmpc):
                subs = [[int(x) for x in ln.split()[1:] if x != '0'] for ln in open(tmpc) if ln.startswith('a')]
            if not subs:
                lines = p.stdout.splitlines()
                if any(l.startswith('s SATISFIABLE') for l in lines):
                    tag = 'SAT-by-march'
                elif any(l.startswith('s UNSATISFIABLE') for l in lines):
                    tag = 'UNSAT-by-march'
                else:
                    tag = 'NO-CUBES'
                fr.write('%d %s\n' % (j, tag))
                fr.flush()
                continue
            for s in subs:
                fo.write('a %s 0\n' % ' '.join(map(str, c + s)))
                fm.write('%d\n' % j)
                n_out += 1
            fo.flush()
            fm.flush()
    for f in (tmp, tmpc):
        if os.path.exists(f):
            os.remove(f)
    print('refined %d cubes into %d' % (len(todo), n_out))


if __name__ == '__main__':
    main()
