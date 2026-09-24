#!/usr/bin/env python3
"""
lazy.py -- counterexample-guided (lazy) search for minimal-time rules.

Start from the lengths 2..n0.  Repeatedly: solve with an incremental SAT
solver; decode the full rule table of the model; simulate it with fsspcheck
on 2..NMAX; if some length fails, add the constraints of the first failing
length and continue (learned clauses are kept).  Terminates with UNSAT (for
the accumulated set of lengths -- which already proves that no rule works
for all lengths) or with a rule that passes every length up to NMAX.

usage: lazy.py k n0 NMAX [--solver cd19] [--log file]
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


class IncEnc(gencnf.Enc):
    """Incremental version: C_inf up to anti-diagonal M, lengths added on demand."""

    def __init__(self, k, M, symbreak=True):
        super().__init__(k, (M + 2) // 2)
        self.M = M
        self.inf = {}
        order = []
        for t in range(1, M):
            for i in range(1, t + 2):
                if t + i > M:
                    break
                self.inf[(t, i)] = self.newcell()
                order.append((t, i))
        for (t, i) in order:
            self.transition(self.vinf(t - 1, i - 1), self.vinf(t - 1, i),
                            self.vinf(t - 1, i + 1), self.inf[(t, i)])
        if symbreak and k >= 5:
            aux = list(range(2, k - 1))
            seen = {a: None for a in aux}
            for (t, i) in order:
                x = self.inf[(t, i)]
                for a in aux[1:]:
                    if seen[a - 1] is None:
                        self.add([-x[a]])
                    else:
                        self.add([-x[a], seen[a - 1]])
                for a in aux:
                    s = self.new()
                    prev = seen[a]
                    self.add([-x[a], s])
                    if prev is None:
                        self.add([-s, x[a]])
                    else:
                        self.add([-prev, s])
                        self.add([-s, prev, x[a]])
                    seen[a] = s
        self.lengths = []

    def vinf(self, t, i):
        if i == 0:
            return gencnf.BND
        if t == 0:
            return 1 if i == 1 else 0
        if i > t + 1:
            return 0
        return self.inf[(t, i)]

    def add_length(self, n, diff=True):
        assert 2 * n - 2 <= self.M
        R = {}

        def val(t, j):
            if j == 0 or j == n + 1:
                return gencnf.BND
            if t + j >= 2 * n - 1:
                return R[(t, j)]
            return self.vinf(t, j)

        for t in range(n - 1, 2 * n - 2):
            for i in range(1, n + 1):
                if t + i >= 2 * n - 1:
                    R[(t, i)] = self.newcell()
        for t in range(n - 1, 2 * n - 2):
            for i in range(1, n + 1):
                if (t, i) in R:
                    self.transition(val(t - 1, i - 1), val(t - 1, i), val(t - 1, i + 1), R[(t, i)])
        T = 2 * n - 3
        for i in range(1, n + 1):
            self.transition(val(T, i - 1), val(T, i), val(T, i + 1), 'FIRE')
        if diff and 2 * n - 1 <= self.M:
            for i in range(2, n + 1):
                t = 2 * n - 1 - i
                self.differ(R[(t, i)], self.vinf(t, i))
        self.lengths.append(n)


def first_failure(rulefile, nmax):
    r = subprocess.run([os.path.join(HERE, 'fsspcheck'), rulefile, '2', str(nmax)],
                       capture_output=True, text=True)
    out = r.stdout.strip()
    if out.startswith('OK'):
        return None, out
    n = int(out.split('n=')[1].split(':')[0].split()[0])
    return n, out


def main():
    k, n0, NMAX = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    name = sys.argv[sys.argv.index('--solver') + 1] if '--solver' in sys.argv else 'cd19'
    log = sys.argv[sys.argv.index('--log') + 1] if '--log' in sys.argv else None
    M = 2 * NMAX - 2
    E = IncEnc(k, M)
    for n in range(2, n0 + 1):
        E.add_length(n)
    s = Solver(name=name, bootstrap_with=E.clauses)
    done = len(E.clauses)
    it = 0
    t0 = time.time()
    rule = '/tmp/claude-0/lazy_rule_k%d.txt' % k

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t0, msg)
        print(line)
        sys.stdout.flush()
        if log:
            with open(log, 'a') as fh:
                fh.write(line + "\n")

    while True:
        it += 1
        res = s.solve()
        if not res:
            say("UNSAT with lengths %s" % sorted(E.lengths))
            return
        model = set(v for v in s.get_model() if v > 0)
        with open(rule, 'w') as fh:
            gencnf.decode(E, model, fh)
        n, out = first_failure(rule, NMAX)
        if n is None:
            say("CANDIDATE passes 2..%d: %s" % (NMAX, rule))
            os.rename(rule, rule + '.candidate%d' % it)
            return
        if n in E.lengths:
            raise RuntimeError("model violates an encoded length %d: %s" % (n, out))
        E.add_length(n)
        for cl in E.clauses[done:]:
            s.add_clause(cl)
        done = len(E.clauses)
        say("iter %d: model fails at n=%d (%s); lengths now %d" % (it, n, out, len(E.lengths)))


if __name__ == '__main__':
    main()
