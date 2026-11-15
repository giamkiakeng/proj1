#!/usr/bin/env python3
"""enumtree.py -- stable generals (B1): exhaustive enumeration, with the half-line as a case split.  No SAT solver.

A cube is a list of transitions of the half-line (xyz=d).  For every cube of PREFIXFILE the enumerator mdfs
(depth-first enumeration of all partial rules, transitions fixed lazily, as fsspdfs.c of the paper) is run on
the class "(B1), exactly GGG, *GG, GG* give F, no G on the half-line beyond the first cell" for the lines
2..N, with the transitions of the cube fixed.  If mdfs finishes within the node limit, it reports the number
of rules of the class that synchronize 2..N (in the sense of the formula Phi_N of README.md) and have these
transitions.  If the limit is reached, the cube is split on the next transition that the half-line needs
(values L, A, B; the front is never L), and the parts are enumerated instead.

Output, one line per cube of PREFIXFILE: number of parts, total nodes, rules found.  The parts are written to
PARTSFILE (cube | nodes), so that the case split can be checked for completeness (covercheck.py) and re-run.

usage: enumtree.py N PREFIXFILE PARTSFILE [--limit NODES] [--workers W] [--first I] [--last J] [--mdfs PATH]
"""
import argparse, os, re, subprocess, sys, tempfile, time
from multiprocessing import Pool
NAMES = 'LGAB'
ap = argparse.ArgumentParser()
ap.add_argument('N', type=int); ap.add_argument('prefixfile'); ap.add_argument('partsfile')
ap.add_argument('--limit', type=int, default=100000000); ap.add_argument('--workers', type=int, default=2)
ap.add_argument('--first', type=int, default=1); ap.add_argument('--last', type=int, default=10 ** 9)
ap.add_argument('--mdfs', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mdfs'))
ap.add_argument('--enum', default='wenum', choices=['wenum', 'mdfs'], help='which enumerator')
ap.add_argument('--wenum', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wenum'))
ap.add_argument('--nosplit', action='store_true', help='report a cube that reaches the node limit as open instead of splitting it')
a = ap.parse_args()
N = a.N
MM = 2 * N - 1
code = {c: i for i, c in enumerate(NAMES)}
order = [(t, m - t) for m in range(3, MM + 1) for t in range(1, m) if 2 <= m - t <= t + 1]

def parse(cube):
    return [((code[tr[0]], code[tr[1]], code[tr[2]]), code[tr[4]]) for tr in cube.replace('>', '=').split(',')]

def next_branch(cube):
    tab = {(0, 0, 0): 0}
    for e, v in parse(cube):
        tab[e] = v
    val = {}
    cellv = lambda t, i: 1 if i == 1 else (0 if i > t + 1 else val[(t, i)])
    for (t, i) in order:
        e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
        if e not in tab:
            return e, [v for v in (0, 2, 3) if not (v == 0 and i == t + 1)]
        if i == t + 1 and tab[e] == 0:
            return None, 'dead'
        val[(t, i)] = tab[e]
    return None, 'complete'

def enumerate_cube(cube, limit):
    if a.enum == 'wenum':
        txt = 'k 5\n' + ''.join('%s %s %s %s\n' % (tr[0], tr[1], tr[2], tr[4]) for tr in cube.replace('>', '=').split(','))
        out = subprocess.run([a.wenum, str(N), str(limit)], input=txt, capture_output=True, text=True).stdout
        m = re.search(r'rules (\d+), nodes (\d+)(.*)', out)
        return int(m.group(2)), int(m.group(1)), 'limit' in m.group(3), ['(%d rules, see mdfs -s)' % int(m.group(1))] if int(m.group(1)) else []
    return enumerate_cube_mdfs(cube, limit)

def enumerate_cube_mdfs(cube, limit):
    with tempfile.NamedTemporaryFile('w', suffix='.txt', dir=os.environ.get('TMPDIR'), delete=False) as f:
        f.write('k 5\n' + ''.join('%s %s %s %s\n' % (tr[0], tr[1], tr[2], tr[4]) for tr in cube.replace('>', '=').split(',')))
        name = f.name
    try:
        out = subprocess.run([a.mdfs, '5', str(N), '2', '2', '3', '0', '0', '2', '-c', '-b3', '-b1s', '-nogh', '-s', '-f', name, '-n', str(limit)],
                             capture_output=True, text=True).stdout
    finally:
        os.remove(name)
    m = re.search(r'nodes (\d+)\s+solutions (\d+)(.*)', out)
    sols = [l for l in out.split('\n') if l.startswith('SOL')]
    return int(m.group(1)), int(m.group(2)), 'limit' in m.group(3), sols

def work(job):
    idx, cube = job
    parts, stack, nodes, found, bad = [], [cube], 0, [], []
    while stack:
        c = stack.pop()
        e, vals = next_branch(c)
        if e is None and vals == 'dead':
            parts.append((c, 0)); continue           # the front is L: excluded without enumeration
        n, s, lim, sols = enumerate_cube(c, a.limit)
        nodes += n
        if s:
            found.extend(sols)
        if not lim:
            parts.append((c, n)); continue
        if e is None or a.nosplit:
            bad.append(c); continue                   # node limit: left open
        for v in reversed(vals):
            stack.append('%s,%s%s%s=%s' % (c, NAMES[e[0]], NAMES[e[1]], NAMES[e[2]], NAMES[v]))
    return idx, cube, parts, nodes, found, bad

if __name__ == '__main__':
    cubes = [l.strip() for l in open(a.prefixfile) if l.strip()]
    jobs = [(i, c.replace('LEAF ', '').replace(' ', ',').replace('>', '=')) for i, c in enumerate(cubes, 1) if a.first <= i <= a.last]
    t0, tp, tn, tf, tb = time.time(), 0, 0, 0, 0
    with Pool(a.workers) as pool, open(a.partsfile, 'a') as out:
        for idx, cube, parts, nodes, found, bad in pool.imap_unordered(work, jobs):
            out.write('# cube %d: %s -> %d parts, %d nodes, %d rules%s\n' % (idx, cube, len(parts), nodes, len(found), '' if not bad else '; OPEN: ' + ' ;; '.join(bad)))
            out.write(''.join('%s | %d\n' % p for p in parts)); out.write(''.join('RULE %s\n' % s for s in found)); out.flush()
            tp += len(parts); tn += nodes; tf += len(found); tb += len(bad)
            print('cube %d: %d parts, %d nodes, %d rules, %d open  [total: %d parts, %.3g nodes, %d rules, %d open, %.0f s]' % (
                idx, len(parts), nodes, len(found), len(bad), tp, tn, tf, tb, time.time() - t0), flush=True)
    print('# done: %d cubes, %d parts, %d nodes, %d rules, %d open, %.0f s' % (len(jobs), tp, tn, tf, tb, time.time() - t0), flush=True)
