#!/usr/bin/env python3
"""
gcegar.py -- counterexample-guided completion of a fixed half-line with partial triangles.

Start from the constraints SPEC (gfix.py syntax), solve with kissat, read the table off the model,
simulate the lines of lengths 2..NMAX, and for the first length n that fails add the cones of the
firing cells n-h..n, where n-h is the leftmost cell involved in the failure (a cell firing early,
or a cell of the firing row that is not F).  Repeat until all lengths 2..NMAX synchronize (the
table is written to OUT) or the constraints become unsatisfiable (the half-line has no completion
for the lengths involved).

usage: gcegar.py GERMFILE NMAX OUT SPEC... [--timeout S] [--budget S] [--k K] [--P GGG,*GG,GG*] [--Pint GGG] [--upf G]
   --P: restrict to rules whose F-producing neighbourhoods are exactly the listed ones
   --Pint: the same for the neighbourhoods without a border only (border entries stay free)
   --upf X: add the redundant clauses 'cells at time 2n-3 are X' (use with --Pint XXX)
   --timeout: limit per SAT call; --budget: total time, after which the loop stops
   GCEGAR_START1=AB: simulate the lines from the configuration AB L...L at time 1 and only for the
      lengths n > 2 (for the common relaxation of two germs that agree from time 1 on)
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfix  # noqa: E402

KISSAT = os.environ.get('KISSAT') or '/home/user/tools/kissat/build/kissat'


KOPTS = os.environ.get('KISSAT_OPTS', '').split()


def solve(E, path, timeout):
    gfix.write_cnf(E, path)
    t0 = time.time()
    p = subprocess.run([KISSAT] + KOPTS + ['--time=%d' % timeout, path], capture_output=True, text=True)
    st = next((l for l in p.stdout.splitlines() if l.startswith('s ')), 's UNKNOWN')
    model = set()
    for l in p.stdout.splitlines():
        if l.startswith('v '):
            model.update(int(x) for x in l[2:].split() if int(x) > 0)
    return st, model, time.time() - t0


def table_from_model(E, model):
    tab = dict(E.germ)
    for nb, vs in E.T.items():
        for d, v in vs.items():
            if v in model:
                tab[nb] = d
    return tab


START1 = os.environ.get('GCEGAR_START1', '')   # e.g. AB: simulate from this configuration at time 1


def simulate(tab, n):
    """first failure of the line of length n: None, or (kind, leftmost cell involved)"""
    c = ['G'] + ['L'] * (n - 1)
    t1 = 1
    if START1 and n > len(START1):
        c, t1 = list(START1) + ['L'] * (n - len(START1)), 2
    for t in range(t1, 2 * n - 1):
        r = ['*'] + c + ['*']
        c = [tab[(r[i - 1], r[i], r[i + 1])] for i in range(1, n + 1)]
        fired = [i + 1 for i, x in enumerate(c) if x == 'F']
        if fired:
            if t < 2 * n - 2:
                return ('early t=%d cells %s' % (t, fired), min(fired))
            if len(fired) < n:
                missing = [i for i in range(1, n + 1) if i not in fired]
                return ('incomplete firing, missing %s' % missing, min(missing))
            return None
    return ('no firing at 2n-2', 1)


def main():
    a = sys.argv[1:]
    germ = gfix.parse_germ(a[0])
    nmax, out = int(a[1]), a[2]
    specs, timeout, k, budget, P, interior, upf = [], 3600, 5, None, None, False, None
    it = iter(a[3:])
    for x in it:
        if x == '--timeout':
            timeout = int(next(it))
        elif x == '--budget':
            budget = float(next(it))
        elif x in ('--P', '--Pint'):
            interior = x == '--Pint'
            P = {tuple(w) for w in next(it).split(',')}
        elif x == '--upf':
            upf = next(it)
        elif x == '--k':
            k = int(next(it))
        else:
            specs.append(x)
    work = out + '.cnf'
    start = time.time()
    for rnd in range(1, 200):
        if budget is not None and time.time() - start > budget:
            print('STOP: budget exhausted')
            return
        E, ncells = gfix.build(germ, k, specs, P, interior, upf)
        left = timeout if budget is None else max(10, min(timeout, int(budget - (time.time() - start))))
        st, model, dt = solve(E, work, left)
        print('round %d: %s | cells=%d clauses=%d | %s (%.0f s)' % (rnd, ' '.join(specs), ncells, len(E.cls), st, dt),
              flush=True)
        if st != 's SATISFIABLE':
            print('STOP:', st)
            return
        tab = table_from_model(E, model)
        with open('%s.round%d' % (out, rnd), 'w') as fh:          # keep every model for later analysis
            fh.write('k %d\n' % k)
            for nb in sorted(tab):
                fh.write('%s %s %s %s\n' % (nb + (tab[nb],)))
        fail = None
        for n in range(len(START1) + 1 if START1 else 2, nmax + 1):
            f = simulate(tab, n)
            if f:
                fail = (n, f)
                break
        if fail is None:
            with open(out, 'w') as fh:
                fh.write('k %d\n' % k)
                for nb in sorted(tab):
                    fh.write('%s %s %s %s\n' % (nb + (tab[nb],)))
            print('FOUND: all lengths 2..%d synchronize; table written to %s' % (nmax, out))
            return
        n, (what, left) = fail
        h = n - left
        old = [s for s in specs if s == 'cone:%d' % n or s.startswith('cone:%d:' % n)]
        h = max([h] + [int(s.split(':')[2]) if s.count(':') == 2 else 0 for s in old])
        print('   length %d fails: %s -> cone:%d:%d' % (n, what, n, h), flush=True)
        specs = [s for s in specs if s not in old] + ['cone:%d:%d' % (n, h)]
    print('STOP: too many rounds')


if __name__ == '__main__':
    main()
