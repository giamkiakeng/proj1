#!/usr/bin/env python3
"""gcert.py -- certified tree search over the half-line, for any class of mcopy.py.

The same tree as gsat.py: the transitions that the half-line uses are fixed one at a time (anti-diagonals
t + i = 2, 3, ..., within an anti-diagonal by increasing time).  A node is a cube (the transitions fixed so
far).  For a node, CaDiCaL is run on F plus the units of the cube with a time limit and an LRAT proof:
    UNSATISFIABLE and lrat-check accepts the proof (answer and empty last lemma are required)  -> leaf 'U';
    no answer in the time limit -> the node is split on the next transition that the half-line needs  'S';
    SATISFIABLE -> the class has a rule for the lines of the formula: reported, the search stops.
Children of a node: every working state except
    (a) L for a front cell (t, t+1) with t <= NFRONT          (unit clause of F),
    (b) G for a cell i >= 2 with --nogh / --noghw, anything but G for the first cell with --nogh, and for the
        first cell at times t >= GSTATIC with --gstatic      (unit clauses of F),
    (c) an auxiliary state before the auxiliary states of smaller index have occurred (naming; this is sound
        for classes that are invariant under renaming the auxiliary states).
gcover.py replays these rules without a solver and checks that the 'U' cubes are a complete case split.
OUTFILE gets one line per node:  U cube | seconds | proof bytes | formula SHA-256 | proof SHA-256 | VERIFIED
or  S cube.  A run that was interrupted is continued by the same command (nodes on OUTFILE are not redone).
Proofs are deleted after the check; a cube formula is F (its SHA-256 is printed) plus the units of the cube.

usage: gcert.py K N OUTFILE [class options of gsat.py] [--tlim SEC] [--workers W] [--mindepth D] [--prefixfile FILE]
"""
import argparse, hashlib, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
from mcopy import Model, NAMES, BND

ap = argparse.ArgumentParser()
ap.add_argument('k', type=int); ap.add_argument('N', type=int); ap.add_argument('outfile')
for f in ('b1', 'b1s', 'b3', 'b3w', 'b4', 'nogh', 'noghw', 'wimp', 'wgap', 'strict', 'b2nb', 'front1'):
    ap.add_argument('--' + f, action='store_true')
ap.add_argument('--b2'); ap.add_argument('--extra', default=''); ap.add_argument('--early', type=int, nargs=2)
ap.add_argument('--pump', type=int, default=0); ap.add_argument('--gstatic', type=int, default=None)
ap.add_argument('--tlim', type=int, default=4); ap.add_argument('--workers', type=int, default=4)
ap.add_argument('--mindepth', type=int, default=0, help='nodes with fewer transitions are split without calling the solver')
ap.add_argument('--prefixfile', help='start from these cubes instead of the root (the cover is then relative to them)')
ap.add_argument('--first', type=int, default=1); ap.add_argument('--last', type=int, default=10 ** 9)
ap.add_argument('--maxtlim', type=int, default=4000, help='time limit for a node that cannot be split (complete half-line)')
ap.add_argument('--wwalls', action='store_true', help='redundant clauses for the weak reading of (B1) with GGG, *GG, GG* -> F (weakwalls.py)')
ap.add_argument('--nocake', action='store_true', help='do not run the second checker cake_lpr')
ap.add_argument('--recheck', action='store_true', help='re-verify the certified cubes of OUTFILE: rebuild each formula, compare its SHA-256, rerun CaDiCaL and both checkers')
ap.add_argument('--sample', type=int, default=0, help='with --recheck: only this many cubes, chosen at random (seed 1)')
ap.add_argument('--init', default='G', help='initial state of the first cell (default G); the class conditions speak about G')
ap.add_argument('--nointerior', default='', help='class: this state never occurs in an interior cell (cells 2..n-1 of the lines, cells i >= 2 of the half-line)')
ap.add_argument('--noghws', action='store_true', help='with --strict: no G in a half-line cell i >= 2 with t + i <= 2N-4 (the wall lemma for the lines 2..N only)')
ap.add_argument('--set', default='', help='class condition: transitions xyz=d, comma-separated (unit clauses of F)')
ap.add_argument('--neq', default='', help='class condition: delta(x,y,z) != d for xyz=d, comma-separated (unit clauses of F)')
a = ap.parse_args()
CAD = os.environ.get('CADICAL', 'cadical'); LC = os.environ.get('LRATCHECK', 'lrat-check')
TMP = os.environ.get('CERTTMP', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cert'))
CAKE = os.environ.get('CAKELPR', '')          # binary of cake_lpr; without it only lrat-check is run
USECAKE = (not a.nocake) and os.path.exists(CAKE)
k, N = a.k, a.N
import minit
INIT = NAMES.index(a.init)
M = minit.model_class(INIT)(k, N, copy=False, sym=False, b1=a.b1, b1s=a.b1s, b3=a.b3, b3w=a.b3w, b4=a.b4, b2=a.b2, nogh=a.nogh, wimp=a.wimp,
          wgap=a.wgap, strict=a.strict, early=tuple(a.early) if a.early else None,
          extra=[int(x) for x in a.extra.split(',') if x], pump=a.pump, front1=a.front1, gstatic=a.gstatic, noghw=a.noghw, b2nb=a.b2nb)
if a.wwalls:
    import weakwalls
    weakwalls.add_weak_walls(M, noghw=a.noghw)
E = M.E
_c = {NAMES[x]: x for x in range(k - 1)}; _c['*'] = BND; _c['F'] = k - 1
if a.noghws:
    for (_t, _i), _x in sorted(M.Hc.items()):
        if _i >= 2 and _t + _i <= 2 * N - 4:
            E.add([-_x[1]])
XI = _c[a.nointerior] if a.nointerior else None
if XI is not None:
    for (_t, _i), _x in sorted(M.Hc.items()):
        if _i >= 2:
            E.add([-_x[XI]])
    for (_n, _t, _i), _x in sorted(M.Rc.items()):
        if 2 <= _i <= _n - 1:
            E.add([-_x[XI]])
for _spec, _sign in ((a.set, 1), (a.neq, -1)):
    for _tr in [x for x in _spec.split(',') if x]:
        _l, _d = _tr.split('=')
        E.add([_sign * E.T[(_c[_l[0]], _c[_l[1]], _c[_l[2]])][_c[_d]]])
BASE = ''.join(' '.join(map(str, c)) + ' 0\n' for c in E.cl)
NCL = len(E.cl)
MM = M.M
NFRONT = max([N] + M.extra) - 2
if a.strict:
    NFRONT -= 1
if a.front1 and not a.strict:
    NFRONT += 1
W = list(range(k - 1))
imin = 2 if a.nogh else 1
code = {NAMES[x]: x for x in range(k - 1)}; code['*'] = BND
sym = lambda x: '*' if x == BND else NAMES[x]
order = [(t, m - t) for m in range(2, MM + 1) for t in range(1, m) if imin <= m - t <= t + 1]

def parse(cube):
    out = []
    for tr in [x for x in cube.split(',') if x and x != '-']:
        lcr, d = tr.split('=')
        out.append(((code[lcr[0]], code[lcr[1]], code[lcr[2]]), code[d]))
    return out

def next_branch(cube):
    """(e, values) for the next transition that the half-line needs after the cube; (None, why) if there is none"""
    tab = {(0, 0, 0): 0}
    mx = max(1, INIT)
    for e, v in parse(cube):
        tab[e] = v; mx = max(mx, v)
    val = {}
    def cellv(t, i):
        if i < 1:
            return BND
        if i > t + 1:
            return 0
        if t == 0:
            return INIT
        if i == 1 and a.nogh:
            return 1
        return val[(t, i)]
    for (t, i) in order:
        e = (cellv(t - 1, i - 1), cellv(t - 1, i), cellv(t - 1, i + 1))
        if e not in tab:
            vals = []
            for v in W:
                if v == 0 and i == t + 1 and t <= NFRONT:
                    continue
                if v == 1 and (a.nogh or (a.noghw and i >= 2) or (a.noghws and i >= 2 and t + i <= 2 * N - 4)):
                    continue
                if XI is not None and v == XI and i >= 2:
                    continue
                if v != 1 and i == 1 and a.gstatic is not None and t >= a.gstatic:
                    continue
                if v >= 2 and v > mx + 1:
                    continue
                vals.append(v)
            return e, vals
        if i == t + 1 and tab[e] == 0 and t <= NFRONT:
            return None, 'dead'
        val[(t, i)] = tab[e]
    return None, 'complete'

def refute(cube, tlim):
    """CaDiCaL + lrat-check on F and the units of the cube; returns (cube, status, line)"""
    units = [E.T[e][v] for e, v in parse(cube)]
    tag = hashlib.sha1((cube + str(os.getpid())).encode()).hexdigest()[:16]
    cnf, prf = os.path.join(TMP, 'gc_%s.cnf' % tag), os.path.join(TMP, 'gc_%s.lrat' % tag)
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
        if ans == 's SATISFIABLE':
            return cube, 'SAT', None
        if ans != 's UNSATISFIABLE':
            return cube, 'UNKNOWN', None
        last = None
        with open(prf, 'rb') as f:               # the last lemma must be the empty clause
            f.seek(max(0, os.path.getsize(prf) - 65536))
            for l in f.read().decode('ascii', 'replace').split('\n'):
                p = l.split()
                if len(p) >= 2 and p[1] != 'd':
                    last = p
        if last is None or last[1] != '0':
            return cube, 'NOEMPTY', None
        c = subprocess.run([LC, cnf, prf], capture_output=True, text=True)
        if 'c VERIFIED' not in c.stdout:
            return cube, 'CHECKFAIL', None
        tail = 'VERIFIED'
        if USECAKE:
            c2 = subprocess.run([CAKE, cnf, prf], capture_output=True, text=True)
            if 's VERIFIED UNSAT' not in c2.stdout:
                return cube, 'CAKEFAIL', None
            tail = 'VERIFIED | cake_lpr VERIFIED UNSAT'
        h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
        return cube, 'OK', '%s | %.1f s | %d | %s | %s | %s' % (cube, dt, os.path.getsize(prf), h(cnf), h(prf), tail)
    finally:
        for p in (cnf, prf):
            if os.path.exists(p):
                os.remove(p)

def children(cube):
    e, vals = next_branch(cube)
    if e is None:
        return None, vals
    pre = '' if cube == '-' else cube + ','
    return ['%s%s%s%s=%s' % (pre, sym(e[0]), sym(e[1]), sym(e[2]), NAMES[v]) for v in vals], None

if __name__ == '__main__':
    fsha = hashlib.sha256(BASE.encode()).hexdigest()
    print('# F: k=%d N=%d, %d variables, %d clauses, sha256 of the clause lines %s; half-line to the anti-diagonal %d, NFRONT %d' % (
        k, N, E.nv, NCL, fsha, MM, NFRONT), flush=True)
    if a.recheck:
        rec = [l[2:].strip().split(' | ') for l in open(a.outfile) if l.startswith('U ')]
        if a.sample and a.sample < len(rec):
            import random
            rec = random.Random(1).sample(rec, a.sample)
        t0, okc, same, bad = time.time(), 0, 0, []
        with Pool(a.workers) as pool:
            res = pool.starmap(refute, [(r[0], a.maxtlim) for r in rec], chunksize=1)
        for r, (cube, st, line) in zip(rec, res):
            if st != 'OK':
                bad.append('%s: %s' % (st, cube)); continue
            p = line.split(' | ')
            if p[3] != r[3]:
                bad.append('formula SHA-256 differs: %s' % cube); continue
            okc += 1; same += (p[4] == r[4])
        print('# recheck of %d cubes in %.0f s: %d verified again by lrat-check%s, formula SHA-256 equal for all of them, proof SHA-256 equal for %d; %d failures' % (
            len(rec), time.time() - t0, okc, ' and cake_lpr' if USECAKE else '', same, len(bad)), flush=True)
        for b_ in bad[:50]:
            print('RECHECK FAILED', b_)
        sys.exit(1 if bad else 0)
    doneU, doneS = set(), set()
    if os.path.exists(a.outfile):
        for l in open(a.outfile):
            if l.startswith('U '):
                doneU.add(l[2:].split(' | ')[0].strip())
            elif l.startswith('S '):
                doneS.add(l[2:].strip())
    if a.prefixfile:
        cubes = [l.strip().replace(' ', ',').replace('>', '=') for l in open(a.prefixfile) if l.strip() and not l.startswith('#')]
        stack = [c for i, c in enumerate(cubes, 1) if a.first <= i <= a.last][::-1]
    else:
        stack = ['-']
    t0, ncert, nsplit, bad, sat = time.time(), 0, 0, [], []
    last_report = time.time()
    depth = lambda c: 0 if c == '-' else c.count(',') + 1
    with Pool(a.workers) as pool, open(a.outfile, 'a') as out:
        if os.path.getsize(a.outfile) == 0:
            out.write('# gcert.py %s\n# F: %d variables, %d clauses, sha256 %s\n' % (' '.join(sys.argv[1:]), E.nv, NCL, fsha))
        inflight = {}
        def split(c, record):
            global nsplit
            ch, why = children(c)
            if ch is None:
                return why
            if record:
                out.write('S %s\n' % c); out.flush()
            nsplit += 1
            stack.extend(ch[::-1])
            return None
        while (stack or inflight) and not sat:
            while stack and len(inflight) < a.workers:
                c = stack.pop()
                if c in doneU:
                    continue
                if c in doneS:
                    split(c, False); continue
                if depth(c) < a.mindepth and split(c, True) is None:
                    continue
                ch, why = children(c)
                tl = a.tlim if ch is not None and why != 'complete' else (a.tlim if why == 'dead' else a.maxtlim)
                inflight[c] = pool.apply_async(refute, (c, tl))
            ready = [c for c, r in inflight.items() if r.ready()]
            if not ready:
                time.sleep(0.02)
            for c in ready:
                cube, st, line = inflight.pop(c).get()
                if st == 'OK':
                    out.write('U ' + line + '\n'); out.flush(); ncert += 1
                elif st == 'UNKNOWN':
                    why = split(cube, True)
                    if why is not None:
                        bad.append('OPEN (%s, time limit): %s' % (why, cube))
                elif st == 'SAT':
                    sat.append(cube); out.write('# SAT %s\n' % cube); out.flush()
                else:
                    bad.append('%s: %s' % (st, cube))
            if time.time() - last_report > 300:
                last_report = time.time()
                print('.. %.0f s: %d certified, %d split, %d on the stack, %d not certified' % (time.time() - t0, ncert, nsplit, len(stack), len(bad)), flush=True)
        for b in bad:
            out.write('# NOT CERTIFIED %s\n' % b)
        pool.terminate()
    print('# done in %.0f s: %d certified leaves in this run (%d on file before), %d splits, %d not certified, %d satisfiable' % (
        time.time() - t0, ncert, len(doneU), nsplit, len(bad), len(sat)), flush=True)
    for b in bad[:50]:
        print('NOT CERTIFIED', b)
    for c in sat:
        print('SATISFIABLE', c)
