#!/usr/bin/env python3
"""certtree.py -- certificates for the tree search of germsat.py (stable generals, lines 2..N).

For every cube of PREFIXFILE (half-line transitions xyz=d, comma-separated) the formula F with the cube as unit
clauses is refuted by CaDiCaL with an LRAT proof, and the proof is checked by lrat-check.  If CaDiCaL does not
finish within the time limit, the cube is split on the next transition that the half-line needs (the same
branching as germsat.py) and the parts are certified instead.  One line per certified cube is appended to
OUTFILE: cube | CaDiCaL seconds | proof bytes | formula SHA-256 | proof SHA-256 | VERIFIED.  Proofs are deleted
after the check.  F is the formula of mcopy.py without its symmetry clauses:
    Model(5, N, copy=False, sym=False, b1s, b3, nogh, wimp, wgap, front1)
and its SHA-256 (without units) is printed, so that a cube formula can be rebuilt as F plus units.

usage: certtree.py N PREFIXFILE OUTFILE [--tlim SEC] [--workers W] [--first I] [--last J]
"""
import argparse, hashlib, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
from mcopy import Model, NAMES, BND

ap = argparse.ArgumentParser()
ap.add_argument('N', type=int); ap.add_argument('prefixfile'); ap.add_argument('outfile')
ap.add_argument('--tlim', type=int, default=100); ap.add_argument('--workers', type=int, default=2)
ap.add_argument('--first', type=int, default=1); ap.add_argument('--last', type=int, default=10 ** 9)
a = ap.parse_args()
CAD = os.environ.get('CADICAL', 'cadical'); LC = os.environ.get('LRATCHECK', 'lrat-check')
TMP = os.environ.get('CERTTMP', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cert'))
N = a.N
M = Model(5, N, copy=False, sym=False, b1s=True, b3=True, nogh=True, wimp=True, wgap=True, front1=True)
E = M.E
BASE = ''.join(' '.join(map(str, c)) + ' 0\n' for c in E.cl)
NCL = len(E.cl)
MM = 2 * N - 1
code = {NAMES[x]: x for x in range(4)}; code['*'] = BND
order = [(t, m - t) for m in range(3, MM + 1) for t in range(1, m) if 2 <= m - t <= t + 1]

def parse(cube):
    out = []
    for tr in cube.replace('>', '=').split(','):
        lcr, d = tr.split('=')
        out.append(((code[lcr[0]], code[lcr[1]], code[lcr[2]]), code[d]))
    return out

def next_branch(cube):
    """the next transition that the half-line needs after the cube, with the values that germsat.py tries"""
    tab = {(0, 0, 0): 0}
    for e, v in parse(cube):
        tab[e] = v
    val = {}
    def cellv(t, i):
        return 1 if i == 1 else (0 if i > t + 1 else val[(t, i)])
    for (t, i) in order:
        e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
        if e not in tab:
            return e, [v for v in (0, 2, 3) if not (v == 0 and i == t + 1)]
        if i == t + 1 and tab[e] == 0:
            return None, 'dead'
        val[(t, i)] = tab[e]
    return None, 'complete'

def refute(cube, tlim):
    """CaDiCaL + lrat-check on F and the units of the cube; returns (status, line)"""
    units = [E.T[e][v] for e, v in parse(cube)]
    tag = hashlib.sha1(cube.encode()).hexdigest()[:16]
    cnf, prf = os.path.join(TMP, 'ct_%s.cnf' % tag), os.path.join(TMP, 'ct_%s.lrat' % tag)
    with open(cnf, 'w') as f:
        f.write('p cnf %d %d\n' % (E.nv, NCL + len(units)))
        f.write(BASE)
        f.write(''.join('%d 0\n' % u for u in units))
    t0 = time.time()
    try:
        r = subprocess.run([CAD, '-q', '--lrat', '--no-binary', '-t', str(tlim), cnf, prf], capture_output=True, text=True)
        ans = [l for l in r.stdout.split('\n') if l.startswith('s ')]
        ans = ans[0] if ans else 's UNKNOWN'
        dt = time.time() - t0
        if ans != 's UNSATISFIABLE':
            return ('SAT' if ans == 's SATISFIABLE' else 'UNKNOWN'), None
        last = None
        with open(prf, 'rb') as f:               # the last lemma must be the empty clause
            f.seek(max(0, os.path.getsize(prf) - 65536))
            for l in f.read().decode('ascii', 'replace').split('\n'):
                p = l.split()
                if len(p) >= 2 and p[1] != 'd':
                    last = p
        if last is None or last[1] != '0':
            return 'NOEMPTY', None
        c = subprocess.run([LC, cnf, prf], capture_output=True, text=True)
        if 'c VERIFIED' not in c.stdout:
            return 'CHECKFAIL', None
        h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
        return 'OK', '%s | %.0f s | %d | %s | %s | VERIFIED' % (cube, dt, os.path.getsize(prf), h(cnf), h(prf))
    finally:
        for p in (cnf, prf):
            if os.path.exists(p):
                os.remove(p)

def work(job):
    idx, cube = job
    lines, stack, bad = [], [cube], []
    while stack:
        c = stack.pop()
        st, line = refute(c, a.tlim)
        if st == 'OK':
            lines.append(line)
            continue
        if st != 'UNKNOWN':
            bad.append('%s: %s' % (st, c)); continue
        e, vals = next_branch(c)
        if e is None:
            bad.append('OPEN (%s, time limit): %s' % (vals, c)); continue
        sym = lambda x: '*' if x == BND else NAMES[x]
        for v in reversed(vals):
            stack.append('%s,%s%s%s=%s' % (c, sym(e[0]), sym(e[1]), sym(e[2]), NAMES[v]))
    return idx, cube, lines, bad

if __name__ == '__main__':
    print('# F: %d variables, %d clauses, sha256 of the clause lines %s' % (E.nv, NCL, hashlib.sha256(BASE.encode()).hexdigest()), flush=True)
    cubes = [l.strip() for l in open(a.prefixfile) if l.strip()]
    jobs = [(i, c.replace(' ', ',').replace('>', '=')) for i, c in enumerate(cubes, 1) if a.first <= i <= a.last]
    t0, ncert, nbad = time.time(), 0, 0
    with Pool(a.workers) as pool, open(a.outfile, 'a') as out:
        for idx, cube, lines, bad in pool.imap_unordered(work, jobs):
            out.write('# cube %d: %s -> %d certified parts%s\n' % (idx, cube, len(lines), '' if not bad else '; NOT CERTIFIED: ' + ' ;; '.join(bad)))
            out.write(''.join(l + '\n' for l in lines)); out.flush()
            ncert += len(lines); nbad += len(bad)
            print('cube %d: %d parts, %d not certified  [%d certified so far, %.0f s]' % (idx, len(lines), len(bad), ncert, time.time() - t0), flush=True)
    print('# done: %d certified cubes, %d not certified, %.0f s' % (ncert, nbad, time.time() - t0), flush=True)
