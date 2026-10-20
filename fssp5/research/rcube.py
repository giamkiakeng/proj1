#!/usr/bin/env python3
"""rcube.py CNF ICNF P1OUT TAG [budget] [depth] [first] [last] [step]

Recursive cube-and-conquer.  The work items are the cubes of ICNF (indices first..last-1, step) that P1OUT
(icube.py output; several files may be joined by commas, or '-' for none) does not mark UNSAT.  An item that
has not been tried is solved under assumptions by one incremental CaDiCaL (PySAT cd19) at the conflict
budget; an item that stays UNKNOWN is split by march_cu -d depth on CNF + its unit clauses, and its sub-cubes
(the item's literals followed by a relative cube of march_cu) become new items, processed depth-first.

Output, for certification and for restarting (a restart with the same arguments continues where it stopped):
  TAG.rlog   'R path result secs'   a solved item (UNSAT, SAT or UNKNOWN)
             'S path nsub info'     a split of item 'path' into nsub sub-cubes
             'M path info'          march_cu returned no cubes for item 'path' (it is then solved as usual)
  TAG.cubes  'path lit ... 0'       the literals of every item, when it is first handled
  TAG_split/<path>.icnf             the relative cubes of each split (for the coverage check)
Paths: the top-level index, then '.k' for the k-th sub-cube of a split."""
import sys, os, time, subprocess, tempfile
from pysat.formula import CNF
from pysat.solvers import Solver

MARCH = os.environ.get('MARCH') or '/home/user/tools/CnC/march_cu/march_cu'
RES = {True: 'SAT', False: 'UNSAT', None: 'UNKNOWN'}


def main():
    cnf, icnf, p1, tag = sys.argv[1:5]
    budget = int(float(sys.argv[5])) if len(sys.argv) > 5 else 100000
    depth = int(sys.argv[6]) if len(sys.argv) > 6 else 6
    first = int(sys.argv[7]) if len(sys.argv) > 7 else 0
    last = int(sys.argv[8]) if len(sys.argv) > 8 else 10**9
    step = int(sys.argv[9]) if len(sys.argv) > 9 else 1
    cubes = [[int(x) for x in l.split()[1:-1]] for l in open(icnf) if l.startswith('a ')]
    st = {}
    if p1 != '-':
        for f in p1.split(','):
            for l in open(f):
                p = l.split()
                if len(p) >= 2 and p[1] in ('UNSAT', 'SAT', 'UNKNOWN') and st.get(p[0]) != 'UNSAT':
                    st[p[0]] = p[1]
    split = set()
    sdir = tag + '_split'
    if os.path.exists(tag + '.rlog'):
        for l in open(tag + '.rlog'):
            p = l.split()
            if p and p[0] == 'R' and st.get(p[1]) != 'UNSAT':
                st[p[1]] = p[2]
            elif p and p[0] == 'S' and os.path.exists(os.path.join(sdir, p[1] + '.icnf')):
                split.add(p[1])
    if any(v == 'SAT' for v in st.values()):
        print('a cube is SAT; nothing to do'); return
    os.makedirs(sdir, exist_ok=True)
    F = CNF(from_file=cnf)
    body = ''.join(' '.join(map(str, c)) + ' 0\n' for c in F.clauses)
    tmp = tempfile.mkdtemp(prefix='rc.', dir=os.path.dirname(os.path.abspath(tag)))
    log = open(tag + '.rlog', 'a')
    cub = open(tag + '.cubes', 'a')

    def w(f, s):
        f.write(s + '\n'); f.flush()

    def subs(path, c):
        rel = [[int(x) for x in l.split()[1:-1]] for l in open(os.path.join(sdir, path + '.icnf'))
               if l.startswith('a ')]
        return [('%s.%d' % (path, k), c + q) for k, q in enumerate(rel)]

    top = [(str(i), cubes[i]) for i in range(first, min(last, len(cubes)), step)]
    stack = [it for it in reversed(top) if st.get(it[0]) != 'UNSAT']
    print('%s: %d open top-level cubes (%d tried), budget %d, depth %d; %d splits on record'
          % (cnf, len(stack), sum(1 for p, _ in stack if p in st), budget, depth, len(split)), flush=True)
    nsolved = nsplit = 0
    t00 = time.time()
    with Solver(name='cd19', bootstrap_with=F.clauses) as s:
        while stack:
            path, c = stack.pop()
            if st.get(path) == 'UNSAT':
                continue
            if path in split:
                stack.extend(reversed(subs(path, c)))
                continue
            if path not in st:
                w(cub, path + ' ' + ' '.join(map(str, c)) + ' 0')
                s.conf_budget(budget)
                t1 = time.time()
                res = s.solve_limited(assumptions=c)
                st[path] = RES[res]
                nsolved += 1
                w(log, 'R %s %s %.1f' % (path, RES[res], time.time() - t1))
                if res is True:
                    w(log, '# model ' + ' '.join(str(x) for x in s.get_model() if x > 0))
                    print('SAT at', path, flush=True); return
                if res is False:
                    continue
            # UNKNOWN: split
            fn = os.path.join(tmp, 'f.cnf')
            with open(fn, 'w') as fo:
                fo.write('p cnf %d %d\n' % (F.nv, len(F.clauses) + len(c)))
                fo.write(body)
                fo.write(''.join('%d 0\n' % l for l in c))
            on = os.path.join(tmp, 's.icnf')
            if os.path.exists(on):
                os.remove(on)
            t0 = time.time()
            r = subprocess.run([MARCH, fn, '-d', str(depth), '-o', on], capture_output=True, text=True)
            info = ' '.join(l.strip() for l in r.stdout.splitlines()
                            if 'number of cubes' in l or 'UNSAT' in l or l.startswith('s '))
            rel = []
            if os.path.exists(on):
                rel = [l for l in open(on) if l.startswith('a ')]
            if not rel:
                # march_cu gave no cubes (it refuted CNF + c by itself, or failed): solve at 20 x the budget
                w(log, 'M %s rc=%d %s' % (path, r.returncode, info))
                t1 = time.time()
                s.conf_budget(20 * budget)
                res = s.solve_limited(assumptions=c)
                st[path] = RES[res]
                w(log, 'R %s %s %.1f' % (path, RES[res], time.time() - t1))
                if res is True:
                    w(log, '# model ' + ' '.join(str(x) for x in s.get_model() if x > 0))
                    print('SAT at', path, flush=True); return
                if res is None:
                    print('STUCK at', path, flush=True)
                continue
            with open(os.path.join(sdir, path + '.icnf'), 'w') as fo:
                fo.write(''.join(rel))
            w(log, 'S %s %d %s (%.1f s)' % (path, len(rel), info, time.time() - t0))
            split.add(path)
            nsplit += 1
            stack.extend(reversed(subs(path, c)))
            print('%s split %s into %d; solved %d, splits %d, stack %d, %.0f s'
                  % (time.strftime('%H:%M:%S', time.gmtime()), path, len(rel), nsolved, nsplit, len(stack),
                     time.time() - t00), flush=True)
    print('done: solved %d, splits %d, %.0f s' % (nsolved, nsplit, time.time() - t00), flush=True)


if __name__ == '__main__':
    main()
