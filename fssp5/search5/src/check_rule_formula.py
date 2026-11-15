#!/usr/bin/env python3
"""check_rule_formula.py RULE K N [class options of gcert.py] -- does the rule satisfy the formula F of gcert.py?

The whole table of the rule is added to F as unit clauses and the formula is solved.  A rule of the class that
synchronizes the lines 2..N+2 must satisfy F (N+1 without --front1 and --nogh/--noghw); this is a test of the
encoder.  With --used only the transitions that the lines 2..N+2 use are fixed (for rules whose unused
transitions do not satisfy the class conditions)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
rule = sys.argv[1]
used_only = '--used' in sys.argv
argv = [x for x in sys.argv[2:] if x != '--used']
sys.argv = ['gcert.py', argv[0], argv[1], '/dev/null'] + argv[2:]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gcert.py')).read().split("if __name__ == '__main__':")[0]
exec(compile(src, 'gcert-head', 'exec'))
from simlib import load, sim, ok
from pysat.solvers import Solver
kk, tab = load(rule)
good = [n for n in range(2, 3 * N) if ok(tab, n)]
c2 = dict(code); c2['F'] = k - 1
if used_only:
    ent = {}
    for n in range(2, N + 3):
        rr = sim(tab, n)
        for t in range(min(2 * n - 2, len(rr) - 1)):
            row = '*' + ''.join(rr[t]) + '*'
            for i in range(1, n + 1):
                ent[(row[i - 1], row[i], row[i + 1])] = rr[t + 1][i - 1]
else:
    ent = tab
units = [E.T[(c2[l], c2[c], c2[r])][c2[d]] for (l, c, r), d in ent.items() if (c2[l], c2[c], c2[r]) in E.T]
S_ = Solver(name='cadical153', bootstrap_with=E.cl)
r = S_.solve(assumptions=units)
print('%s: synchronizes %s; %d transitions fixed; formula (k=%d, N=%d, %d clauses): %s' % (
    os.path.basename(rule), good, len(units), k, N, len(E.cl), 'SATISFIED' if r else 'NOT satisfied'))
if not r:
    core = S_.get_core() or []
    inv = {E.T[e][d]: (e, d) for e in E.T for d in range(k)}
    print('  core:', ' '.join('%s%s%s>%s' % (sym(inv[u][0][0]), sym(inv[u][0][1]), sym(inv[u][0][2]), (NAMES + 'F')[inv[u][1]] if inv[u][1] < len(NAMES) else 'F') for u in core[:12]))
