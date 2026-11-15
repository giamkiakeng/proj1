#!/usr/bin/env python3
"""gcover.py -- do the certified cubes of gcert.py form a complete case split of the half-lines?  No solver.

usage: gcover.py K N FILE... [--nogh] [--noghw] [--gstatic T] [--strict] [--front1] [--nh NH] [--root CUBE] [--init X] [--nointerior Y]

Reads the lines 'U cube | ...' of the FILEs.  Starting from the root (no transition fixed, or --root), a node is
covered if it is one of the cubes or if it has a next transition to branch on and all its children are covered.
The next transition is the neighbourhood of the first cell of the half-line, in the order of the anti-diagonals
t + i = 2, ..., M (within one by increasing time), whose value the transitions fixed so far do not determine;
M = 2 NH - 1 (2 NH - 2 with --strict), NH = N unless --nh is given (longest line of the formula).
Children: all working states except
  (a) L for a front cell (t, t+1), t <= NFRONT = NH - 2 (+1 with --front1, -1 with --strict);
  (b) G for a cell i >= 2 with --nogh or --noghw; with --nogh the first cell is G and is not branched on; with
      --gstatic T the first cell at times t >= T has the only child G; with --nointerior Y the state Y for a
      cell i >= 2;
  (c) an auxiliary state before all auxiliary states of smaller index have occurred (the initial state X of
      the first cell, --init X, counts as occurred).
This program is independent of gcert.py (it shares no code with it).
"""
import sys
sys.setrecursionlimit(100000)
args = sys.argv[1:]
def flag(name, has_val=False):
    if name in args:
        j = args.index(name)
        if has_val:
            v = args[j + 1]; del args[j:j + 2]; return v
        del args[j]; return True
    return None if has_val else False
nogh, noghw, strict, front1 = flag('--nogh'), flag('--noghw'), flag('--strict'), flag('--front1')
gstatic, nh, root, init = flag('--gstatic', True), flag('--nh', True), flag('--root', True), flag('--init', True)
noint = flag('--nointerior', True)
K, N = int(args[0]), int(args[1])
NH = int(nh) if nh else N
MM = 2 * NH - 2 if strict else 2 * NH - 1
NFRONT = NH - 2 - (1 if strict else 0) + (1 if front1 and not strict else 0)
NAMES = 'LGABCDE'[:K - 1]
STAR = 9
num = {c: j for j, c in enumerate(NAMES)}; num['*'] = STAR
ch = lambda x: '*' if x == STAR else NAMES[x]
imin = 2 if nogh else 1
INIT = num[init] if init else 1          # initial state of the first cell
order = [(t, m - t) for m in range(2, MM + 1) for t in range(1, m) if imin <= m - t <= t + 1]
cubes, anc = set(), set()
for fn in args[2:]:
    for line in open(fn):
        if not line.startswith('U '):
            continue
        trs = [x for x in line[2:].split(' | ')[0].strip().split(',') if x and x != '-']
        cubes.add(tuple(trs))
        for j in range(len(trs)):
            anc.add(tuple(trs[:j]))
used, uncovered, stats = set(), [], {'nodes': 0}
def walk(trs, tab, mx):
    stats['nodes'] += 1
    key = tuple(trs)
    if key in cubes:
        used.add(key)
        return
    if key not in anc:                       # no cube below this node
        uncovered.append(','.join(trs) or '-')
        return
    val = {}
    def cell(t, i):
        if i < 1:
            return STAR
        if i > t + 1:
            return 0
        if t == 0:
            return INIT
        if i == 1 and nogh:
            return 1
        return val[(t, i)]
    for (t, i) in order:
        e = (cell(t - 1, i - 1), cell(t - 1, i), cell(t - 1, i + 1))
        if e in tab:
            val[(t, i)] = tab[e]
            continue
        for v in range(K - 1):
            if v == 0 and i == t + 1 and t <= NFRONT:
                continue
            if v == 1 and (nogh or (noghw and i >= 2)):
                continue
            if noint and v == num[noint] and i >= 2:
                continue
            if v != 1 and i == 1 and gstatic is not None and t >= int(gstatic):
                continue
            if v >= 2 and v > mx + 1:
                continue
            tab[e] = v
            walk(trs + ['%s%s%s=%s' % (ch(e[0]), ch(e[1]), ch(e[2]), NAMES[v])], tab, max(mx, v))
            del tab[e]
        return
    uncovered.append(','.join(trs) or '-')   # complete half-line that is not a cube
tab0, trs0, mx0 = {(0, 0, 0): 0}, [], max(1, INIT)
if root:
    for tr in root.split(','):
        lcr, d = tr.split('=')
        tab0[(num[lcr[0]], num[lcr[1]], num[lcr[2]])] = num[d]; trs0.append(tr); mx0 = max(mx0, num[d])
walk(trs0, tab0, mx0)
print('cubes read: %d; used in the cover: %d; nodes walked: %d; uncovered: %d' % (len(cubes), len(used), stats['nodes'], len(uncovered)))
for u in uncovered[:30]:
    print('UNCOVERED', u)
print('RESULT: %s' % ('complete case split' if not uncovered else 'NOT complete'))
