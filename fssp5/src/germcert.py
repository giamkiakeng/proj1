#!/usr/bin/env python3
"""germcert.py -- one LRAT certificate for a whole list of refuted germs.

Builds the base formula of germinc.py for the lengths 2..N and adds, for
every germ g of the list, a selector s_g with the clauses (-s_g | l) for
each fixed transition literal l of g, and the clause OR_g s_g.  The formula
is unsatisfiable iff every germ of the list is refuted; CaDiCaL then emits an
LRAT proof that is checked with lrat-check.

usage: germcert.py germfile N out_prefix [M]
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4}
CADICAL = '/home/user/tools/cadical/build/cadical'
LRATCHECK = '/home/user/tools/drat-trim/lrat-check'


def main():
    germfile, N, pre = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    M = int(sys.argv[4]) if len(sys.argv) > 4 else 78
    E = gencnf.build(5, N, minf=M, pump=min(40, M // 2), symbreak=False)
    sel = []
    ngerm = 0
    for ln in open(germfile):
        if not ln.startswith('GERM'):
            continue
        ngerm += 1
        s = E.new()
        sel.append(s)
        for tok in ln.split()[1:]:
            e, d = tok.split('>')
            E.add([-s, E.T[tuple(CODE[x] for x in e)][CODE[d]]])
    E.add(sel)
    cnf = pre + '.cnf'
    with open(cnf, 'w') as fh:
        gencnf.write_dimacs(E, fh)
    t0 = time.time()
    p = subprocess.run([CADICAL, '-q', '--lrat', '--binary=false', cnf, pre + '.lrat'],
                       capture_output=True, text=True)
    st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
    t1 = time.time()
    print("%d germs, lengths 2..%d: %s (%.1fs)" % (ngerm, N, st[0] if st else '?', t1 - t0))
    if st and st[0] == 's UNSATISFIABLE':
        q = subprocess.run([LRATCHECK, cnf, pre + '.lrat'], capture_output=True, text=True)
        ok = any(x.strip() in ('c VERIFIED', 's VERIFIED') for x in q.stdout.splitlines())
        print("lrat-check: %s (%.1fs)" % ('VERIFIED' if ok else 'NOT VERIFIED', time.time() - t1))
    sys.stdout.flush()


if __name__ == '__main__':
    main()
