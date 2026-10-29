#!/usr/bin/env python3
"""failall.py RULEFILE T [NMIN] -- does the rule fire early, at relative time <= T, on every line n >= NMIN?
Uses asymp.py's certificate: the depth rows 0..2T+4 are periodic from t0 with period p, so the early rows
of R_n (tau <= T) are determined by the signature of n, and it suffices to simulate one length per
signature among NMIN <= n < max(NMIN, t0+3) + p."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfix
rule, T = sys.argv[1], int(sys.argv[2])
nmin = int(sys.argv[3]) if len(sys.argv) > 3 else 15
tab = gfix.load_rule(rule)
# germ of the half-line up to anti-diagonal M (large enough for asymp.py's depth rows 0..2T+4 to repeat)
M = 3000
germ = {}
cur = ['G'] + ['L'] * (M + 2)
for t in range(M):
    r = ['*'] + cur + ['L']
    nxt = list(cur)
    for i in range(1, min(t + 3, len(cur)) + 1):
        nb = (r[i - 1], r[i], r[i + 1])
        germ[nb] = tab[nb]
        nxt[i - 1] = tab[nb]
    cur = nxt
germ.pop(('L', 'L', 'L'), None)
assert all(v != 'F' for v in germ.values()), 'the half-line fires'
gpath = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'germ_%s_%d.txt' % (os.path.basename(rule).split('.')[0], os.getpid()))
open(gpath, 'w').write('GERM ' + ' '.join('%s>%s' % (''.join(nb), d) for nb, d in sorted(germ.items())) + '\n')
out = subprocess.run(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asymp.py'), gpath, str(T), str(nmin), '8000'],
                     capture_output=True, text=True)
lines = out.stdout.splitlines()
if not lines:
    sys.exit(out.stderr)
print(lines[0])
reps = [int(s.split(':')[1]) for s in lines[1].split()]

def first_fire(n):
    """relative time of the first F on the line of length n, and whether the line synchronizes"""
    c = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        r = ['*'] + c + ['*']
        c = [tab[(r[i - 1], r[i], r[i + 1])] for i in range(1, n + 1)]
        f = [i + 1 for i, x in enumerate(c) if x == 'F']
        if f:
            return t - (n - 1), (t == 2 * n - 2 and len(f) == n)
    return None, False
res = {n: first_fire(n) for n in reps}
taus = {n: r[0] for n, r in res.items()}
# every representative must fail; from T+3 on (where Lemma A transfers the failure) within tau <= T
bad = [n for n, (tau, ok) in res.items() if ok or tau is None or (n >= T + 3 and tau > T)]
print('%d representative lengths in [%d, %d]; first firing tau: min %d, max %s' %
      (len(reps), min(reps), max(reps), min(t for t in taus.values() if t is not None), max(t for t in taus.values() if t is not None)))
print('VERIFIED: no line n >= %d synchronizes; from n = %d on the first F is at tau <= %d' % (nmin, max(nmin, T + 3), T) if not bad else 'NOT VERIFIED for T = %d: %s' % (T, bad[:10]))
