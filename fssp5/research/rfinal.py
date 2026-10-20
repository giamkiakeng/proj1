#!/usr/bin/env python3
"""rfinal.py ICNF P1OUT TAG : status of the cube tree of rcube.py.

A cube is closed if it is UNSAT (in P1OUT or TAG.rlog) or it was split and all its sub-cubes are closed.
Prints the number of top-level cubes, closed top-level cubes, UNSAT leaves of the tree, splits, and the open
frontier (untried or UNKNOWN cubes that are not split); 'ALL CLOSED' if every top-level cube is closed."""
import sys, os
icnf, p1, tag = sys.argv[1:4]
n = sum(1 for l in open(icnf) if l.startswith('a '))
st = {}
for f in ([] if p1 == '-' else p1.split(',')):
    for l in open(f):
        p = l.split()
        if len(p) >= 2 and p[1] in ('UNSAT', 'SAT', 'UNKNOWN') and st.get(p[0]) != 'UNSAT':
            st[p[0]] = p[1]
nsub = {}
if os.path.exists(tag + '.rlog'):
    for l in open(tag + '.rlog'):
        p = l.split()
        if p and p[0] == 'R' and st.get(p[1]) != 'UNSAT':
            st[p[1]] = p[2]
        elif p and p[0] == 'S':
            nsub[p[1]] = int(p[2])
sat = [k for k, v in st.items() if v == 'SAT']
leaves, frontier = [], []


def closed(path):
    if st.get(path) == 'UNSAT':
        leaves.append(path)
        return True
    if path in nsub:
        ok = True
        for k in range(nsub[path]):
            ok = closed('%s.%d' % (path, k)) and ok
        return ok
    frontier.append((path, st.get(path, 'untried')))
    return False


ntop = sum(1 for i in range(n) if closed(str(i)))
depth = max((p.count('.') for p in leaves), default=0)
print('%s: %d top-level cubes, %d closed; %d UNSAT leaves (max level %d), %d splits; open frontier %d '
      '(%d UNKNOWN, %d untried)%s%s'
      % (icnf, n, ntop, len(leaves), depth, len(nsub), len(frontier),
         sum(1 for _, s in frontier if s == 'UNKNOWN'), sum(1 for _, s in frontier if s == 'untried'),
         '; SAT: %s' % sat if sat else '', '; ALL CLOSED' if ntop == n and not sat else ''))
