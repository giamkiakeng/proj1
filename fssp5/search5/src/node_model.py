#!/usr/bin/env python3
"""node_model.py K N OUTRULE CUBE [class options of gcert.py] [--tlim SEC] -- a rule at a node of the tree search.

Solves the formula of gcert.py with the given options (for example --strict: the lines 2..N and the class, nothing
else) together with the units of CUBE (transitions xyz=d separated by commas) with CaDiCaL, decodes the transition
table from the model, writes it to OUTRULE and checks it without the encoder: the table is simulated on the lines
2..60 from the initial state of --init (default G), and the conditions (B1) in the weak reading and (B2) without
borders are tested on the table if --b1 and --b2 I --b2nb are among the options.
"""
import sys, os, subprocess
argv = sys.argv[1:]
tlim = '3600'
if '--tlim' in argv:
    j = argv.index('--tlim'); tlim = argv[j + 1]; del argv[j:j + 2]
K, N, out, cube = argv[0], argv[1], argv[2], argv[3]
opts = argv[4:]
here = os.path.dirname(os.path.abspath(__file__))
src_name = 'gcert3.py' if os.path.exists(os.path.join(here, 'gcert3.py')) else 'gcert.py'
sys.argv = [src_name, K, N, '/dev/null'] + opts
src = open(os.path.join(here, src_name)).read().split("if __name__ == '__main__':")[0]
exec(compile(src, 'gcert-head', 'exec'))
units = [E.T[e][v] for e, v in parse(cube)]
cnf = os.path.join(TMP, 'nm_%d.cnf' % os.getpid())
with open(cnf, 'w') as f:
    f.write('p cnf %d %d\n' % (E.nv, NCL + len(units)))
    f.write(BASE)
    f.write(''.join('%d 0\n' % u for u in units))
r = subprocess.run([CAD, '-q', '-t', tlim, cnf], capture_output=True, text=True)
os.remove(cnf)
ans = [l for l in r.stdout.split('\n') if l.startswith('s ')]
ans = ans[0] if ans else 's UNKNOWN'
print(ans)
if ans != 's SATISFIABLE':
    sys.exit(1)
model = [int(x) for l in r.stdout.split('\n') if l.startswith('v ') for x in l[2:].split() if x != '0']
tab = M.table(model)
init = opts[opts.index('--init') + 1] if '--init' in opts else 'G'
with open(out, 'w') as f:
    f.write('# node_model.py %s\n# node: %s\n# initial state of the first cell: %s\nk %s\n' % (' '.join(sys.argv[1:3] + opts), cube, init, K))
    for (l, c, rr), d in sorted(tab.items()):
        f.write('%s %s %s %s\n' % (l, c, rr, d))
# ---- checks that do not use the encoder
W = ['L', 'G', 'A', 'B', 'C', 'D'][:int(K) - 1]
def sync(n):
    row = [init] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        new = []
        for i in range(n):
            e = (row[i - 1] if i > 0 else '*', row[i], row[i + 1] if i < n - 1 else '*')
            if e not in tab:
                return False
            new.append(tab[e])
        row = new
        if 'F' in row:
            return t == 2 * n - 2 and all(x == 'F' for x in row)
    return False
good = [n for n in range(2, 61) if sync(n)]
print('initial state %s; synchronized lengths among 2..60: %s' % (init, good))
used = set()
for n in range(2, int(N) + 1):
    row = [init] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        es = [(row[i - 1] if i > 0 else '*', row[i], row[i + 1] if i < n - 1 else '*') for i in range(n)]
        used.update(es); row = [tab[e] for e in es]
print('transitions used by the lines 2..%s: %d of %d' % (N, len(used), len(tab)))
if '--b1' in opts:
    bad = [(x, 'G', y) for x in W for y in W if (x, y) != ('G', 'G') and tab[(x, 'G', y)] != 'G']
    print('(B1) weak for G on the table:', 'holds' if not bad else 'VIOLATED at %s' % bad)
if '--b2' in opts and '--b2nb' in opts:
    I = opts[opts.index('--b2') + 1]
    inv = {x: x for x in W}
    if I != 'id':
        for a_, b_ in zip(I[0::2], I[1::2]):
            inv[a_], inv[b_] = b_, a_
    inv['F'] = 'F'
    bad = [(x, y, z) for x in W for y in W for z in W if tab[(inv[z], inv[y], inv[x])] != inv[tab[(x, y, z)]]]
    print('(B2) without borders for I = %s on the table:' % I, 'holds' if not bad else 'VIOLATED at %s' % bad[:5])
