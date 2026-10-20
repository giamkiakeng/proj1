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
Paths: the top-level index, then '.k' for the k-th sub-cube of a split.

Work sharing (optional, environment variables; none of it affects what the output means):
  RC_CLAIM=DIR    an item is worked on (solved or split) only by the process that creates the file DIR/<path>
                  (O_EXCL), so several processes can share one TAG.  DIR must be emptied before processes are
                  restarted, since the claim of an unfinished item would keep it from being taken again.
  RC_STEAL=1      with RC_CLAIM: when its own items are exhausted, a process re-reads TAG.rlog and the splits
                  on record, takes the unclaimed open items of its range (the last ones first) and repeats;
                  it exits when no unclaimed open item is left (exit status 3 if it did no work at all).
  RC_REVERSE=1    the top-level cubes are taken in decreasing order."""
import sys, os, time, subprocess, tempfile
from pysat.formula import CNF
from pysat.solvers import Solver

MARCH = os.environ.get('MARCH') or '/home/user/tools/CnC/march_cu/march_cu'
RES = {True: 'SAT', False: 'UNSAT', None: 'UNKNOWN'}


def read_status(p1, tag, st, split):
    """results of P1OUT and TAG.rlog into st (UNSAT is never overwritten), splits on record into split"""
    if p1 != '-':
        for f in p1.split(','):
            for l in open(f):
                p = l.split()
                if len(p) >= 2 and p[1] in ('UNSAT', 'SAT', 'UNKNOWN') and st.get(p[0]) != 'UNSAT':
                    st[p[0]] = p[1]
    sdir = tag + '_split'
    if os.path.exists(tag + '.rlog'):
        for l in open(tag + '.rlog'):
            if not l.endswith('\n'):
                break                                   # a line still being written by another process
            p = l.split()
            if len(p) >= 3 and p[0] == 'R' and st.get(p[1]) != 'UNSAT':
                st[p[1]] = p[2]
            elif len(p) >= 3 and p[0] == 'S' and os.path.exists(os.path.join(sdir, p[1] + '.icnf')):
                split.add(p[1])


def main():
    cnf, icnf, p1, tag = sys.argv[1:5]
    budget = int(float(sys.argv[5])) if len(sys.argv) > 5 else 100000
    depth = int(sys.argv[6]) if len(sys.argv) > 6 else 6
    first = int(sys.argv[7]) if len(sys.argv) > 7 else 0
    last = int(sys.argv[8]) if len(sys.argv) > 8 else 10**9
    step = int(sys.argv[9]) if len(sys.argv) > 9 else 1
    cdir = os.environ.get('RC_CLAIM')
    steal = bool(cdir and os.environ.get('RC_STEAL'))
    cubes = [[int(x) for x in l.split()[1:-1]] for l in open(icnf) if l.startswith('a ')]
    st, split = {}, set()
    read_status(p1, tag, st, split)
    if any(v == 'SAT' for v in st.values()):
        print('a cube is SAT; nothing to do'); return
    sdir = tag + '_split'
    os.makedirs(sdir, exist_ok=True)
    if cdir:
        os.makedirs(cdir, exist_ok=True)
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

    def claim(path):
        if not cdir:
            return True
        try:
            fd = os.open(os.path.join(cdir, path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        os.write(fd, b'%d\n' % os.getpid())
        os.close(fd)
        return True

    top = [(str(i), cubes[i]) for i in range(first, min(last, len(cubes)), step)]
    if os.environ.get('RC_REVERSE'):
        top.reverse()

    def frontier():
        """the open items of the range (not UNSAT, not split), in tree order"""
        out, todo = [], list(reversed(top))
        while todo:
            path, c = todo.pop()
            if st.get(path) == 'UNSAT':
                continue
            if path in split:
                todo.extend(reversed(subs(path, c)))
            else:
                out.append((path, c))
        return out

    stack = [it for it in reversed(top) if st.get(it[0]) != 'UNSAT']
    print('%s: %d open top-level cubes (%d tried), budget %d, depth %d; %d splits on record%s'
          % (cnf, len(stack), sum(1 for p, _ in stack if p in st), budget, depth, len(split),
             '; claims in ' + cdir if cdir else ''), flush=True)
    nsolved = nsplit = 0
    t00 = time.time()
    with Solver(name='cd19', bootstrap_with=F.clauses) as s:
        while True:
            while stack:
                path, c = stack.pop()
                if st.get(path) == 'UNSAT':
                    continue
                if path in split:
                    stack.extend(reversed(subs(path, c)))
                    continue
                if not claim(path):
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
                # the split file is complete before the S line announces it to other processes
                sfn = os.path.join(sdir, path + '.icnf')
                with open(sfn + '.tmp', 'w') as fo:
                    fo.write(''.join(rel))
                os.replace(sfn + '.tmp', sfn)
                w(log, 'S %s %d %s (%.1f s)' % (path, len(rel), info, time.time() - t0))
                split.add(path)
                nsplit += 1
                stack.extend(reversed(subs(path, c)))
                print('%s split %s into %d; solved %d, splits %d, stack %d, %.0f s'
                      % (time.strftime('%H:%M:%S', time.gmtime()), path, len(rel), nsolved, nsplit, len(stack),
                         time.time() - t00), flush=True)
            if not steal:
                break
            read_status(p1, tag, st, split)
            if any(v == 'SAT' for v in st.values()):
                print('a cube is SAT (found by another process)', flush=True); return
            stack = [it for it in frontier() if not os.path.exists(os.path.join(cdir, it[0]))]
            if not stack:
                break
            print('%s steal: %d unclaimed open items' % (time.strftime('%H:%M:%S', time.gmtime()), len(stack)),
                  flush=True)
    print('done: solved %d, splits %d, %.0f s' % (nsolved, nsplit, time.time() - t00), flush=True)
    if steal and nsolved == 0 and nsplit == 0:
        sys.exit(3)


if __name__ == '__main__':
    main()
