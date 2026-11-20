#!/usr/bin/env python3
"""certgfix.py -- LRAT certificates for a closed tree of trisplit.py / trisplit2.py (a germ with its half-line fixed).

usage: certgfix.py GERMFILE N CUBEFILE OUTFILE [--enc paper|gfix] [--spec SPEC ...] [--tlim SEC] [--workers W]
                   [--tmp DIR] [--verdict-only]

The formula F (--enc):
  paper (default)  the formula of the paper's completion test (germinc.py / germcert.py of the supplement):
                   gencnf.build(5, N, minf=78, pump=39, symbreak=False), every length 2..N synchronizes in minimal
                   time, half-line to anti-diagonal 78, pumping pairs up to 39, plus one unit clause for every
                   transition of the germ;
  gfix             the formula of gfix.py for the germ and the specs full:2-N (plus the optional further specs),
                   which trisplit.py and trisplit2.py search.
The SHA-256 of the DIMACS text of F (without the units of a cube) is printed, so that every cube formula can be
rebuilt as F plus unit clauses.

1. Targets: the closed cubes of CUBEFILE (lines 'U cube') that are reached from the root by the split rule of
   trisplit.py (simulate the lines 2..N in this order with the germ and the fixed transitions; split on the first
   needed neighbourhood that is not fixed).
2. Every target not yet VERIFIED in OUTFILE is certified: CaDiCaL refutes F plus the units of the cube with an LRAT
   proof (time limit --tlim), lrat-check checks the proof against exactly that formula, and the line
       V cube | CaDiCaL seconds | proof bytes | proof SHA-256 | checkers | VERIFIED
   is appended to OUTFILE (the proof is deleted).  If the environment variable CAKELPR names the binary of the
   verified checker cake_lpr, every proof is checked by it as well (checkers: lrat-check+cake_lpr).  If CaDiCaL does not finish in time, the line 'X cube' is appended
   and the five children of the cube (by the split rule) are certified instead.
3. Verdict, from OUTFILE alone: starting at the root, a node is covered if its cube is VERIFIED, or if it has a
   proper superset among the VERIFIED cubes and its five children by the split rule are covered.  Each split is on a
   free transition, whose five values (L, G, A, B, F) are subject to an exactly-one constraint of F, so the children
   partition the node.  If the root is covered, F is unsatisfiable.
OUTFILE is appended to, so the program can be restarted.
"""
import argparse, hashlib, os, subprocess, sys, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
SUPP = os.path.join(HERE, '..', '..', 'paper', 'supplementary')
sys.path.insert(0, os.path.join(SUPP, 'research'))
sys.path.insert(0, os.path.join(SUPP, 'src'))
import gfix

ap = argparse.ArgumentParser()
ap.add_argument('germfile'); ap.add_argument('N', type=int); ap.add_argument('cubefile'); ap.add_argument('outfile')
ap.add_argument('--enc', default='paper', choices=['paper', 'gfix'])
ap.add_argument('--spec', action='append', default=[])
ap.add_argument('--tlim', type=int, default=600)
ap.add_argument('--workers', type=int, default=1)
ap.add_argument('--tmp', default='.')
ap.add_argument('--verdict-only', action='store_true')
a = ap.parse_args()
CAD = os.environ.get('CADICAL', 'cadical')
LC = os.environ.get('LRATCHECK', 'lrat-check')
CAKE = os.environ.get('CAKELPR', '')          # if set: every proof is also checked by the verified checker cake_lpr
VALUES = ['L', 'G', 'A', 'B', 'F']

germ = gfix.parse_germ(a.germfile)
G = dict(germ)
G.setdefault(('L', 'L', 'L'), 'L')
G.setdefault(('L', 'L', '*'), 'L')
if a.enc == 'gfix':
    specs = ['full:2-%d' % a.N] + a.spec
    E, ncells = gfix.build(germ, 5, specs)
    NV, CLS, T = E.nv, E.cls, E.T
    assert dict(E.germ) == G
    desc = 'gfix.py, specs %s' % ' '.join(specs)
else:
    if a.spec:
        sys.exit('--spec applies to --enc gfix only')
    import gencnf
    CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}
    E = gencnf.build(5, a.N, minf=78, pump=39, symbreak=False)
    T = {}
    for e, vs in E.T.items():
        nb = tuple('*' if x == gencnf.BND else VALUES[x] for x in e)
        if nb not in G:
            T[nb] = {VALUES[d]: vs[d] for d in range(5)}
    gunits = [[E.T[tuple(CODE[x] for x in nb)][CODE[d]]] for nb, d in sorted(germ.items())]
    NV, CLS = E.nv, E.clauses + gunits
    desc = 'gencnf.build(5, %d, minf=78, pump=39, symbreak=False) + %d germ units' % (a.N, len(gunits))
BASE = ''.join(' '.join(map(str, c)) + ' 0\n' for c in CLS)
SHA = hashlib.sha256(('p cnf %d %d\n' % (NV, len(CLS)) + BASE).encode()).hexdigest()
print('# F: germ %s, %s: %d variables, %d clauses, SHA-256 %s (DIMACS of F without cube units)'
      % (a.germfile, desc, NV, len(CLS), SHA), flush=True)


def parse(key):
    fixed = {}
    for tok in (key.split(',') if key else []):
        nb, d = tok.split('=')
        fixed[tuple(nb)] = d
    return fixed


def key_of(fixed):
    return ','.join('%s=%s' % (''.join(nb), d) for nb, d in sorted(fixed.items()))


def line_needs(n, fixed):
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        new = []
        for i in range(n):
            nb = ((row[i - 1] if i > 0 else '*'), row[i], (row[i + 1] if i < n - 1 else '*'))
            if nb in G:
                new.append(G[nb])
            elif nb in fixed:
                new.append(fixed[nb])
            else:
                return nb
        row = new
        if 'F' in row:
            return 'ok' if (t == 2 * n - 2 and all(x == 'F' for x in row)) else 'bad'
    return 'bad'


def split_var(fixed):
    for n in range(2, a.N + 1):
        r = line_needs(n, fixed)
        if r == 'bad':
            return 'bad'
        if r != 'ok':
            return r
    return 'ok'


def children(fixed):
    nb = split_var(fixed)
    if nb in ('ok', 'bad'):
        return None
    assert nb in T and nb not in fixed and set(T[nb]) == set(VALUES)
    out = []
    for d in VALUES:
        f2 = dict(fixed); f2[nb] = d
        out.append(f2)
    return out


class Index:
    """proper-superset queries on a set of cubes"""
    def __init__(self, keys):
        self.keys = set(keys)
        self.lst = sorted(self.keys)
        self.inv = {}
        for j, k in enumerate(self.lst):
            for tok in (k.split(',') if k else []):
                self.inv.setdefault(tok, set()).add(j)

    def below(self, key):
        """some cube of the set is a proper superset of key (called only for a key not in the set)"""
        if not self.lst:
            return False
        if key == '':
            return True
        sets = []
        for tok in key.split(','):
            s = self.inv.get(tok)
            if not s:
                return False
            sets.append(s)
        sets.sort(key=len)
        cur = set(sets[0])
        for s in sets[1:]:
            cur &= s
            if not cur:
                return False
        return True


def leaves(keys):
    """the cubes of keys reached from the root by the split rule, and the nodes on the way that are not covered"""
    idx = Index(keys)
    found, holes, stack = [], [], [{}]
    while stack:
        f = stack.pop()
        k = key_of(f)
        if k in idx.keys:
            found.append(k)
        elif idx.below(k):
            ch = children(f)
            if ch is None:
                holes.append(k)
            else:
                stack.extend(ch)
        else:
            holes.append(k)
    return found, holes


def certify(key):
    tag = hashlib.sha1(key.encode()).hexdigest()[:16]
    cnf = os.path.join(a.tmp, 'c_%s.cnf' % tag)
    prf = os.path.join(a.tmp, 'c_%s.lrat' % tag)
    units = [T[nb][d] for nb, d in parse(key).items()]
    with open(cnf, 'w') as fh:
        fh.write('p cnf %d %d\n' % (NV, len(CLS) + len(units)))
        fh.write(BASE)
        for u in units:
            fh.write('%d 0\n' % u)
    t0 = time.time()
    p = subprocess.run([CAD, '-q', '-t', str(a.tlim), '--lrat', '--binary=false', cnf, prf], capture_output=True, text=True)
    sec = time.time() - t0
    st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
    if st and st[0] == 's UNSATISFIABLE':
        q = subprocess.run([LC, cnf, prf], capture_output=True, text=True)
        ok = any(x.strip() in ('c VERIFIED', 's VERIFIED') for x in q.stdout.splitlines())
        checkers = 'lrat-check'
        if ok and CAKE:
            q = subprocess.run([CAKE, cnf, prf], capture_output=True, text=True)
            ok = 's VERIFIED UNSAT' in q.stdout
            checkers = 'lrat-check+cake_lpr'
        size = os.path.getsize(prf)
        h = hashlib.sha256(open(prf, 'rb').read()).hexdigest()
        res = 'V %s | %.2f | %d | %s | %s | %s' % (key, sec, size, h, checkers, 'VERIFIED' if ok else 'NOT VERIFIED')
    elif st and st[0] == 's SATISFIABLE':
        res = 'SAT %s' % key
    else:
        res = 'X %s' % key
    for fn in (cnf, prf):
        if os.path.exists(fn):
            os.remove(fn)
    return res


def read_out():
    ver, spl = set(), set()
    if os.path.exists(a.outfile):
        for ln in open(a.outfile):
            if not ln.endswith('\n'):
                continue
            w = ln.split(' ', 1)
            if w[0] == 'V' and ln.rstrip().endswith('| VERIFIED'):
                ver.add(w[1].split(' | ')[0])
            elif w[0] == 'X':
                spl.add(w[1].rstrip('\n'))
    return ver, spl


if not a.verdict_only:
    U = set()
    for ln in open(a.cubefile):
        if ln.startswith('U ') and ln.endswith('\n'):
            U.add(ln[2:].rstrip('\n'))
    targets, holes = leaves(U)
    print('# %d closed cubes in %s, %d reached from the root; %d nodes not covered by them'
          % (len(U), a.cubefile, len(targets), len(holes)), flush=True)
    for h in holes[:10]:
        print('#   not covered: %s' % h, flush=True)
    t0 = time.time()
    while True:
        ver, spl = read_out()
        todo = []
        for k in targets:
            stack = [k]
            while stack:
                x = stack.pop()
                if x in ver:
                    continue
                ch = children(parse(x)) if x in spl else None
                if ch is not None:
                    stack.extend(key_of(c) for c in ch)
                else:
                    todo.append(x)
        if not todo:
            break
        print('# %.0f s: %d cubes to certify' % (time.time() - t0, len(todo)), flush=True)
        with Pool(a.workers) as pool, open(a.outfile, 'a') as out:
            for j, res in enumerate(pool.imap_unordered(certify, todo, chunksize=1)):
                out.write(res + '\n'); out.flush()
                if res.startswith('SAT') or res.endswith('NOT VERIFIED'):
                    print('# PROBLEM: %s' % res, flush=True)
                if (j + 1) % 1000 == 0:
                    print('# %.0f s: %d of %d done' % (time.time() - t0, j + 1, len(todo)), flush=True)
        if any(x.startswith('SAT') for x in open(a.outfile)):
            break

ver, spl = read_out()
found, holes = leaves(ver)
nv = sum(1 for ln in open(a.outfile) if ln.startswith('V ')) if os.path.exists(a.outfile) else 0
print('# verdict: %d VERIFIED cubes (%d V lines), %d reached from the root, %d nodes not covered'
      % (len(ver), nv, len(found), len(holes)), flush=True)
for h in holes[:10]:
    print('#   not covered: %s' % h, flush=True)
print('RESULT ' + ('CERTIFIED: F is unsatisfiable (every leaf refuted, LRAT VERIFIED)' if not holes else 'NOT CERTIFIED'),
      flush=True)
