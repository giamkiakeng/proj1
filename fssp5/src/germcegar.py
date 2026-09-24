#!/usr/bin/env python3
"""germcegar.py -- counterexample-guided completion of fixed half-line germs.

For each germ (GERM line), start with the lengths 2..N0 and repeat: solve the
completion problem with kissat (germ fixed, half-line to anti-diagonal
max(78, 2N-2), pumping pairs up to 39, no symmetry breaking), decode the
rule, simulate it for all lengths 2..NMAX; if some length fails, add the
first failing length and repeat.  Stops on UNSAT (the germ is refuted for
the accumulated lengths), on a timeout, or when a rule passes 2..NMAX.
Prints one line per iteration; rules are saved next to the log.

usage: germcegar.py germfile N0 NMAX timeout logprefix
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KISSAT = '/home/user/tools/kissat/build/kissat'
CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}


def main():
    germfile, N0, NMAX, timeout, pre = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    for j, ln in enumerate(open(germfile)):
        if not ln.startswith('GERM'):
            continue
        germ = []
        for tok in ln.split()[1:]:
            e, d = tok.split('>')
            germ.append((tuple(CODE[x] for x in e), CODE[d]))
        lengths = list(range(2, N0 + 1))
        best = None
        it = 0
        while True:
            it += 1
            N = max(lengths)
            E = gencnf.build(5, N, fire_n=sorted(lengths), minf=max(78, 2 * N - 2), pump=39, symbreak=False)
            for e, d in germ:
                E.add([E.T[e][d]])
            cnf = '%s_%d.cnf' % (pre, os.getpid())
            with open(cnf, 'w') as fh:
                gencnf.write_dimacs(E, fh)
            t0 = time.time()
            p = subprocess.run([KISSAT, '-q', '--time=%d' % timeout, cnf], capture_output=True, text=True)
            os.remove(cnf)
            st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
            res = st[0][2:] if st else 'UNKNOWN'
            if res != 'SATISFIABLE':
                print("germ %d iter %d: %s with lengths %s (%.0fs); best %s" % (
                    j, it, res, compress(lengths), time.time() - t0, best))
                break
            true = set()
            for x in p.stdout.splitlines():
                if x.startswith('v '):
                    true.update(int(y) for y in x[2:].split() if int(y) > 0)
            rule = '%s_g%d_it%d.txt' % (pre, j, it)
            with open(rule, 'w') as fh:
                gencnf.decode(E, true, fh)
            r = subprocess.run([os.path.join(HERE, 'fsspcheck'), rule, '2', str(NMAX)], capture_output=True, text=True)
            out = r.stdout.strip()
            if out.startswith('OK'):
                print("germ %d iter %d: CANDIDATE %s passes 2..%d" % (j, it, rule, NMAX))
                break
            n = int(out.split('n=')[1].split(':')[0].split()[0])
            if best is None or n - 1 > best[0]:
                best = (n - 1, rule)
            print("germ %d iter %d: SAT in %.0fs, synchronizes 2..%d, fails n=%d" % (j, it, time.time() - t0, n - 1, n))
            sys.stdout.flush()
            lengths.append(n)
        sys.stdout.flush()


def compress(ls):
    ls = sorted(ls)
    out, a = [], ls[0]
    prev = a
    for x in ls[1:] + [None]:
        if x is not None and x == prev + 1:
            prev = x
            continue
        out.append('%d-%d' % (a, prev) if prev > a else str(a))
        if x is not None:
            a = prev = x
    return ','.join(out)


if __name__ == '__main__':
    main()
