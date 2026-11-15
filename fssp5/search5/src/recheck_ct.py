#!/usr/bin/env python3
"""recheck_ct.py N PARTSFILE... [--sample M] [--seed S] [--pump P] [--workers W] -- second check of certtree.py's output.

For the certified cubes of the files (all of them, or a random sample of M): the cube formula F + units is
rebuilt and its SHA-256 is compared with the recorded one; CaDiCaL is run again without time limit; the new
LRAT proof is checked by lrat-check and by cake_lpr (CAKELPR), and its SHA-256 is compared with the recorded one.
"""
import sys, os, random, hashlib, subprocess, time
args = sys.argv[1:]
def opt(name, default):
    if name in args:
        j = args.index(name); v = args[j + 1]; del args[j:j + 2]; return v
    return default
sample, seed, pump, workers = int(opt('--sample', 0)), int(opt('--seed', 1)), opt('--pump', '0'), int(opt('--workers', 1))
N_, files = args[0], args[1:]
sys.argv = ['certtree.py', N_, '/dev/null', '/dev/null', '--pump', pump]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certtree.py')).read().split("if __name__ == '__main__':")[0]
exec(compile(src, 'certtree-head', 'exec'))
CAKE = os.environ.get('CAKELPR', 'cake_lpr')
def one(rec):
    cube, cnfsha, prfsha = rec
    units = [E.T[e][v] for e, v in parse(cube)]
    tag = hashlib.sha1((cube + 'r').encode()).hexdigest()[:16]
    cnf, prf = os.path.join(TMP, 'rc_%s.cnf' % tag), os.path.join(TMP, 'rc_%s.lrat' % tag)
    try:
        with open(cnf, 'w') as f:
            f.write('p cnf %d %d\n' % (E.nv, NCL + len(units))); f.write(BASE); f.write(''.join('%d 0\n' % u for u in units))
        h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
        if h(cnf) != cnfsha:
            return cube, 'FORMULA-DIGEST', False
        r = subprocess.run([CAD, '-q', '--lrat', '--no-binary', cnf, prf], capture_output=True, text=True)
        if 's UNSATISFIABLE' not in r.stdout:
            return cube, 'NOT-UNSAT', False
        c1 = subprocess.run([LC, cnf, prf], capture_output=True, text=True)
        if 'c VERIFIED' not in c1.stdout:
            return cube, 'LRAT-CHECK', False
        c2 = subprocess.run([CAKE, cnf, prf], capture_output=True, text=True)
        if 's VERIFIED UNSAT' not in c2.stdout:
            return cube, 'CAKE', False
        return cube, 'OK', h(prf) == prfsha
    finally:
        for p in (cnf, prf):
            if os.path.exists(p):
                os.remove(p)
if __name__ == '__main__':
    from multiprocessing import Pool
    recs = []
    for fn in files:
        for l in open(fn):
            if l.startswith('#') or 'VERIFIED' not in l:
                continue
            p = [x.strip() for x in l.split(' | ')]
            recs.append((p[0], p[3], p[4]))
    total = len(recs)
    if sample and sample < total:
        recs = random.Random(seed).sample(recs, sample)
    t0 = time.time()
    with Pool(workers) as pool:
        res = pool.map(one, recs, chunksize=1)
    bad = [(c, st) for c, st, same in res if st != 'OK']
    same = sum(1 for c, st, s_ in res if st == 'OK' and s_)
    print('# recheck of %d of %d certified cubes (seed %d) in %.0f s: %d verified again by lrat-check and cake_lpr with the recorded formula digest; proof digest equal for %d; %d failures' % (
        len(recs), total, seed, time.time() - t0, len(recs) - len(bad), same, len(bad)))
    for c, st in bad[:20]:
        print('FAILED', st, c)
