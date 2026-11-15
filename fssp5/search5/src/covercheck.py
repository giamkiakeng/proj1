#!/usr/bin/env python3
"""covercheck.py N FILE... -- is a set of cubes a complete case split of the half-lines of the stable-general class?

Every FILE lists cubes (half-line transitions, xyz=d or xyz>d, separated by commas or blanks; an optional
'LEAF' and anything after ' | ' are ignored; lines starting with '#' or 'RULE' are skipped).  Starting from the
root delta(G,L,L) = A, the tree of germsat.py / enumtree.py is replayed: a node is covered if it is one of the
cubes, or if the front cell is L on the part of the half-line that its transitions determine, or if it has a
next transition to branch on and its children (values L, A, B; not L at the front) are all covered.  Prints the
numbers of cubes used and unused and every uncovered node (at most 20).  No solver and no enumeration.
"""
import sys
sys.setrecursionlimit(100000)
NAMES = 'LGAB'
N = int(sys.argv[1]); MM = 2 * N - 1
code = {c: i for i, c in enumerate(NAMES)}
order = [(t, m - t) for m in range(3, MM + 1) for t in range(1, m) if 2 <= m - t <= t + 1]
cubes = set()
anc = set()          # the nodes above the cubes
for fn in sys.argv[2:]:
    for line in open(fn):
        line = line.split(' | ')[0].strip()
        if not line or line.startswith('#') or line.startswith('RULE'):
            continue
        trs = line.replace('LEAF', '').replace(',', ' ').replace('>', '=').split()
        cubes.add(frozenset(trs))
        for j in range(1, len(trs)):
            anc.add(frozenset(trs[:j]))
used, uncovered, stats = set(), [], {'nodes': 0, 'dead': 0}
maxlen = max(len(c) for c in cubes)
def walk(trs, tab, val, pos):
    """trs: list of transitions fixed (strings), tab: dict, val: half-line cells computed, pos: index in order"""
    stats['nodes'] += 1
    key = frozenset(trs)
    if key in cubes:
        used.add(key)
        return
    cellv = lambda t, i: 1 if i == 1 else (0 if i > t + 1 else val[(t, i)])
    added = []
    hopeless = key not in anc            # no cube lies below this node: it is covered only if the front is L
    try:
        while pos < len(order):
            t, i = order[pos]
            e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
            if e not in tab:
                break
            if i == t + 1 and tab[e] == 0:
                stats['dead'] += 1
                return
            val[(t, i)] = tab[e]; added.append((t, i)); pos += 1
        if pos == len(order) or len(trs) >= maxlen or hopeless:
            if len(uncovered) < 1000:
                uncovered.append(' '.join(trs))          # no cube can lie below this node
            stats['unc'] = stats.get('unc', 0) + 1
            return
        t, i = order[pos]
        e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
        for v in (0, 2, 3):
            if v == 0 and i == t + 1:
                continue
            tab[e] = v
            walk(trs + ['%s%s%s=%s' % (NAMES[e[0]], NAMES[e[1]], NAMES[e[2]], NAMES[v])], tab, val, pos)
            del tab[e]
    finally:
        for c in added:
            del val[c]
# a node that is neither a cube nor splittable further below a cube is reported; nodes below unused cubes are not visited
root = ['GLL=A']
def walk_root():
    walk(root, {(0, 0, 0): 0, (1, 0, 0): 2}, {}, 0)
walk_root()
# the walk stops at nodes that are not cubes and have children: those are fine only if all children are covered,
# which the recursion checks; a node without cube and without closed descendants ends at a complete half-line
print('cubes read: %d; used in the cover: %d; nodes walked: %d; closed by the front condition: %d; uncovered: %d' % (
    len(cubes), len(used), stats['nodes'], stats['dead'], stats.get('unc', 0)))
for u in uncovered[:1000]:
    print('UNCOVERED', u)
print('RESULT: %s' % ('complete case split' if not uncovered else 'NOT complete'))
