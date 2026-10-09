#!/usr/bin/env python3
"""balzer.py -- five-state rules under Balzer's extra conditions.

Balzer (Inform. Control 10 (1967), p. 37) reported that no five-state minimal-time solution
satisfies four extra conditions.  Numbered as in Mazoyer's account (Publ. Dept. Math. Lyon 1986,
section 7; Balzer lists C2 first and C1 second):

  C1  stability of G:  delta(x,G,y) = G for all working x,y, (x,y) != (G,G)
  C2  image solution:  there is an involution I of the states with
                       delta(I(z),I(y),I(x)) = I(delta(x,y,z))
  C3  pre-firing by G: delta(G,G,G) = delta(*,G,G) = delta(G,G,*) = F
  C4  G dominant:      delta(G,V,G) = G for every working V != G

Without 's', C1 and C3 are used in the weaker form of Yunes (thesis, Paris 7, 1993, section
2.7): C1 only for working neighbours, C3 without "only these neighbourhoods produce F".  With
's' they are used in Balzer's own wording (the strong reading).  For C2 we take I(*) = *,
I(F) = F; then I(G) = G by C1, C2 and C4 (note, Section 5), so I is one of the four
involutions of {L, A, B}.  States:
L=0, G=1, A=2, B=3, F=4.  (balzer_k.py generalizes this to k states and produces identical
formulas for k = 5.)

usage: balzer.py N CONDS [I] [--lrat]
   CONDS: a subset of 1234, e.g. 1234 or 134, optionally with 's' for the
   strong readings of C1 (also for border neighbours: G changes only when
   both neighbours are G or the border) and C3 (no other neighbourhood
   produces F);  I: id, AB, LA, LB (for C2)
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
BND, L, G, A, B, F = -1, 0, 1, 2, 3, 4
INVOLUTIONS = {'id': {}, 'AB': {A: B, B: A}, 'LA': {L: A, A: L}, 'LB': {L: B, B: L}}


def add_conditions(E, conds, inv):
    W = E.W
    T = E.T

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
        I = dict(INVOLUTIONS[inv])
        I.setdefault(BND, BND)
        for s in range(E.k):
            I.setdefault(s, s)
        for (x, y, z), vs in T.items():
            m = (I[z], I[y], I[x])
            for d in range(E.k):
                E.add([-vs[d], T[m][I[d]]])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    N, conds = int(args[0]), args[1]
    inv = args[2] if len(args) > 2 else 'id'
    E = gencnf.build(5, N, symbreak=False)
    add_conditions(E, conds, inv)
    tmp = tempfile.mkdtemp(prefix='balzer_', dir=os.environ.get('TMPDIR', '/tmp'))
    cnf = os.path.join(tmp, 'f.cnf')
    with open(cnf, 'w') as fh:
        gencnf.write_dimacs(E, fh)
    cmd = [CADICAL, '-q', cnf]
    lrat = None
    if '--lrat' in sys.argv:
        lrat = os.path.join(tmp, 'f.lrat')
        cmd = [CADICAL, '-q', '--lrat', '--binary=false', cnf, lrat]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
    res = st[0][2:] if st else 'UNKNOWN'
    out = 'N=%d conds=%s I=%s vars=%d clauses=%d %s %.1fs' % (
        N, conds, inv if '2' in conds else '-', E.nv, len(E.clauses), res, dt)
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
        rule = os.path.join(tmp, 'rule.txt')
        with open(rule, 'w') as fh:
            gencnf.decode(E, true, fh)
        out += ' rule=' + rule
    print(out, flush=True)


if __name__ == '__main__':
    main()
