#!/usr/bin/env python3
"""balzer_k.py -- k-state rules under Balzer's extra conditions (k >= 5).

Same conditions as balzer.py (Balzer, Inform. Control 10 (1967), p. 37; numbered as in
Mazoyer's account): B1 G stable, B2 image solution for an involution I, B3 GGG, *GG, GG* -> F,
B4 (G,V,G) -> G.  CONDS is a subset of 1234, with 's' for the strong reading (Balzer's
wording: B1 also for border neighbours, and no other neighbourhood produces F).
States: L=0, G=1, auxiliary 2..k-2, F=k-1.  I fixes the border, F and G (I(F)=F implies
I(G)=G by B1, B2 and B4; note, Section 5); since the conditions treat the auxiliary states symmetrically, it suffices to
take one involution of {L, aux} per type up to renaming of the auxiliary states:
  id         identity
  AB         (A B)
  LA         (L A)
  LA_BC      (L A)(B C)          (k >= 6)
balzer.py is the program behind the five-state results of the note (its formulas are the
ones whose digests are recorded in results/balzer.log); this script is used for six states and
writes the formula of the five-state weak-reading case I = id, N = 12 for Kissat (--cnf).

usage: balzer_k.py k N CONDS [I] [--lrat] [--timeout=SECONDS] [--cnf=PATH]
   --cnf=PATH writes the formula to PATH and exits without solving.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

# solver binaries: environment variables CADICAL and LRATCHECK, else the PATH, else the paths of the runs
CADICAL = os.environ.get('CADICAL') or shutil.which('cadical') or '/home/user/tools/cadical/build/cadical'
LRATCHECK = os.environ.get('LRATCHECK') or shutil.which('lrat-check') or '/home/user/tools/drat-trim/lrat-check'
BND, L, G = -1, 0, 1


def involution(k, name):
    A, B, C = 2, 3, 4
    table = {'id': {}, 'AB': {A: B, B: A}, 'LA': {L: A, A: L},
             'LA_BC': {L: A, A: L, B: C, C: B}}
    I = dict(table[name])
    if any(s > k - 2 for s in I):
        raise SystemExit('involution %s needs more states' % name)
    I[BND] = BND
    for s in range(k):
        I.setdefault(s, s)
    return I


def add_conditions(E, conds, inv):
    W, T, F = E.W, E.T, E.k - 1

    def setval(e, d):
        E.add([T[e][d]])

    strong = 's' in conds
    side = [BND] + W
    if '1' in conds:
        for x in (side if strong else W):
            for y in (side if strong else W):
                if x in (G, BND) and y in (G, BND):
                    continue
                setval((x, G, y), G)
    if '3' in conds:
        pre = [(G, G, G), (BND, G, G), (G, G, BND)]
        for e in pre:
            setval(e, F)
        if strong:
            for e, vs in T.items():
                if e not in pre:
                    E.add([-vs[F]])
    if '4' in conds:
        for v in W:
            if v != G:
                setval((G, v, G), G)
    if '2' in conds:
        I = involution(E.k, inv)
        for (x, y, z), vs in T.items():
            m = (I[z], I[y], I[x])
            for d in range(E.k):
                E.add([-vs[d], T[m][I[d]]])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    k, N, conds = int(args[0]), int(args[1]), args[2]
    inv = args[3] if len(args) > 3 else 'id'
    timeout = None
    for a in sys.argv[1:]:
        if a.startswith('--timeout='):
            timeout = int(a.split('=')[1])
    E = gencnf.build(k, N, symbreak=False)
    add_conditions(E, conds, inv)
    for a in sys.argv[1:]:
        if a.startswith('--cnf='):
            with open(a.split('=', 1)[1], 'w') as fh:
                gencnf.write_dimacs(E, fh)
            print('k=%d N=%d conds=%s I=%s vars=%d clauses=%d written to %s' % (
                k, N, conds, inv, E.nv, len(E.clauses), a.split('=', 1)[1]))
            return
    tmp = tempfile.mkdtemp(prefix='balzerk_', dir=os.environ.get('TMPDIR', '/tmp'))
    cnf = os.path.join(tmp, 'f.cnf')
    with open(cnf, 'w') as fh:
        gencnf.write_dimacs(E, fh)
    cmd = [CADICAL, '-q', cnf]
    lrat = None
    if '--lrat' in sys.argv:
        lrat = os.path.join(tmp, 'f.lrat')
        cmd = [CADICAL, '-q', '--lrat', '--binary=false', cnf, lrat]
    if timeout:
        cmd.insert(1, '-t')
        cmd.insert(2, str(timeout))
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
    res = st[0][2:] if st else 'UNKNOWN'
    out = 'k=%d N=%d conds=%s I=%s vars=%d clauses=%d %s %.1fs dir=%s' % (
        k, N, conds, inv if '2' in conds else '-', E.nv, len(E.clauses), res, dt, tmp)
    if lrat and res == 'UNSATISFIABLE':
        t1 = time.time()
        q = subprocess.run([LRATCHECK, cnf, lrat], capture_output=True, text=True)
        ok = 'VERIFIED' in q.stdout
        out += ' lrat=%s (%.1f MB, check %.1fs)' % ('VERIFIED' if ok else 'FAILED',
                                                   os.path.getsize(lrat) / 1e6,
                                                   time.time() - t1)
    if res == 'SATISFIABLE':
        true = set()
        for ln in p.stdout.splitlines():
            if ln.startswith('v '):
                true.update(int(x) for x in ln[2:].split() if int(x) > 0)
        with open(os.path.join(tmp, 'rule.txt'), 'w') as fh:
            gencnf.decode(E, true, fh)
    print(out, flush=True)


if __name__ == '__main__':
    main()
