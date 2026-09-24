#!/usr/bin/env python3
"""
fixgerm.py -- can a given half-line "germ" be completed?

Takes a rule file, computes the half-line C_inf up to anti-diagonal M, fixes
every transition used there, and asks whether the remaining transitions can
be chosen so that all lengths 2..N synchronize in minimal time.

usage: fixgerm.py rulefile N [M] [--timeout S]
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402

KISSAT = '/home/user/tools/kissat/build/kissat'
CODE = {'*': gencnf.BND, 'L': 0, 'G': 1, 'A': 2, 'B': 3, 'C': 4}


def main():
    rule, N = sys.argv[1], int(sys.argv[2])
    M = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else 78
    timeout = int(sys.argv[sys.argv.index('--timeout') + 1]) if '--timeout' in sys.argv else 3600
    tab = {}
    k = 5
    for ln in open(rule):
        t = ln.split('#')[0].split()
        if len(t) == 2 and t[0] == 'k':
            k = int(t[1])
        elif len(t) == 4:
            tab[tuple(t[:3])] = t[3]
    CODE['F'] = k - 1
    # half-line up to anti-diagonal M
    used = set()
    width = M + 2
    cur = ['G'] + ['L'] * (width - 1)
    for t in range(M):
        nxt = []
        for i in range(width):
            if t + (i + 1) >= M:      # cell (t+1, i+1) has t+1+i+1 > M -> not needed
                nxt.append('?')
                continue
            l = cur[i - 1] if i > 0 else '*'
            r = cur[i + 1] if i + 1 < width else 'L'
            e = (l, cur[i], r)
            if '?' in e:
                nxt.append('?')
                continue
            used.add(e)
            nxt.append(tab[e])
        cur = nxt
    E = gencnf.build(k, N, minf=M, pump=min(40, M // 2))
    for (l, c, r) in used:
        if (CODE[l], CODE[c], CODE[r]) in E.T:
            E.add([E.T[(CODE[l], CODE[c], CODE[r])][CODE[tab[(l, c, r)]]]])
    cnf = '/tmp/claude-0/germ_%d_%d.cnf' % (os.getpid(), N)
    with open(cnf, 'w') as fh:
        gencnf.write_dimacs(E, fh)
    t0 = time.time()
    p = subprocess.run([KISSAT, '-q', '--time=%d' % timeout, cnf], capture_output=True, text=True)
    st = [ln for ln in p.stdout.splitlines() if ln.startswith('s ')]
    print("%s: %d half-line transitions fixed; lengths 2..%d: %s (%.1fs)" % (
        os.path.basename(rule), len(used), N, st[0][2:] if st else 'UNKNOWN', time.time() - t0))
    os.remove(cnf)


if __name__ == '__main__':
    main()
