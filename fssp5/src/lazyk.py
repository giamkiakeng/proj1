#!/usr/bin/env python3
"""
lazyk.py -- counterexample-guided loop with kissat (non-incremental).

Maintains a set of lengths; each iteration builds MT(5, lengths) with the
half-line to anti-diagonal M, pumping up to N' and determinacy links, solves
it with kissat, simulates the decoded rule and adds the first failing length.
Stops on UNSAT (a proof of non-existence for the accumulated lengths, to be
certified separately) or when a rule passes every length up to NMAX.

usage: lazyk.py n0 NMAX [--M 78] [--pump 40] [--timeout S] [--log f] [extra gencnf opts]
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KISSAT = '/home/user/tools/kissat/build/kissat'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('n0', type=int)
    ap.add_argument('NMAX', type=int)
    ap.add_argument('--M', type=int, default=78)
    ap.add_argument('--pump', type=int, default=40)
    ap.add_argument('--timeout', type=int, default=36000)
    ap.add_argument('--log', default='/tmp/claude-0/lazyk.log')
    ap.add_argument('--prefire', type=int, default=None)
    ap.add_argument('--fzper', default=None)
    a = ap.parse_args()
    lengths = list(range(2, a.n0 + 1))
    t0 = time.time()

    def say(msg):
        line = "[%8.1fs] %s" % (time.time() - t0, msg)
        print(line)
        sys.stdout.flush()
        with open(a.log, 'a') as fh:
            fh.write(line + "\n")

    it = 0
    while True:
        it += 1
        N = max(lengths)
        E = gencnf.build(5, N, minf=max(a.M, 2 * N - 2), pump=a.pump, links=True,
                         fire_n=sorted(lengths), prefire=a.prefire,
                         fzper=tuple(map(int, a.fzper.split(':'))) if a.fzper else None)
        cnf = a.log + '.cnf'
        with open(cnf, 'w') as fh:
            gencnf.write_dimacs(E, fh)
        t1 = time.time()
        p = subprocess.run([KISSAT, '-q', '--time=%d' % a.timeout, cnf],
                           capture_output=True, text=True)
        status, true = None, set()
        for ln in p.stdout.splitlines():
            if ln.startswith('s '):
                status = ln[2:].strip()
            elif ln.startswith('v '):
                true.update(int(x) for x in ln[2:].split() if int(x) > 0)
        dt = time.time() - t1
        if status != 'SATISFIABLE':
            say("iter %d: %s with lengths %s (%.1fs)" % (it, status, sorted(lengths), dt))
            return
        rule = a.log + '.rule%d.txt' % it
        with open(rule, 'w') as fh:
            gencnf.decode(E, true, fh)
        r = subprocess.run([os.path.join(HERE, 'fsspcheck'), rule, '2', str(a.NMAX)],
                           capture_output=True, text=True)
        out = r.stdout.strip()
        if out.startswith('OK'):
            say("iter %d: CANDIDATE %s passes 2..%d" % (it, rule, a.NMAX))
            return
        n = int(out.split('n=')[1].split(':')[0].split()[0])
        lengths.append(n)
        say("iter %d: SAT in %.1fs, model fails at n=%d (%s); now %d lengths, max %d" % (
            it, dt, n, out, len(lengths), max(lengths)))


if __name__ == '__main__':
    main()
