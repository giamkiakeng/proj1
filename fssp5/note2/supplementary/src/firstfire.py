#!/usr/bin/env python3
"""
firstfire.py -- first firing times of the lines of a rule.

usage: python3 firstfire.py RULE NMIN NMAX [TAU]

Simulates every line of length NMIN <= n <= NMAX of the rule table RULE in full (cell 1 starts as G,
the other cells as L, borders * on both sides) and reports:
  - the lengths whose line is synchronized at time 2n-2 (all cells F at 2n-2, none before);
  - for every other line, the relative time tau = t - (n-1) of the first time t at which some cell
    is F, or 'none' if no cell is F up to time 2n-2;
  - whether every such line has a cell in state F at a relative time tau <= n-2 (before time 2n-2);
  - with TAU: the smallest length whose line has a cell in state F at a relative time tau <= TAU.

Rule tables: a line 'k <states>', then one line 'l c r d' per transition; lines starting with '#'
are comments.  Written independently of the other programs.
"""
import sys


def load(path):
    tab = {}
    for ln in open(path):
        w = ln.split()
        if not w or w[0].startswith('#') or w[0] == 'k':
            continue
        tab[tuple(w[:3])] = w[3]
    return tab


def first_fire(tab, n):
    """(tau, synchronized): tau of the first F (None if none up to time 2n-2)"""
    c = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        r = ['*'] + c + ['*']
        c = [tab[(r[i - 1], r[i], r[i + 1])] for i in range(1, n + 1)]
        if 'F' in c:
            return t - (n - 1), (t == 2 * n - 2 and c.count('F') == n)
    return None, False


def ranges(ns):
    out, start, prev = [], None, None
    for n in ns:
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            out.append((start, prev))
            start = prev = n
    if start is not None:
        out.append((start, prev))
    return ', '.join('%d' % a if a == b else '%d..%d' % (a, b) for a, b in out) or '-'


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    tab = load(sys.argv[1])
    nmin, nmax = int(sys.argv[2]), int(sys.argv[3])
    tau_max = int(sys.argv[4]) if len(sys.argv) > 4 else None
    sync, fails = [], []
    for n in range(nmin, nmax + 1):
        tau, ok = first_fire(tab, n)
        (sync if ok else fails).append((n, tau))
    print('%s, lengths %d..%d' % (sys.argv[1], nmin, nmax))
    print('  synchronized at time 2n-2: n = %s' % ranges([n for n, _ in sync]))
    if fails:
        print('  not synchronized (n:tau of the first F): %s'
              % ' '.join('%d:%s' % (n, 'none' if tau is None else tau) for n, tau in fails))
        early = all(tau is not None and tau <= n - 2 for n, tau in fails)
        print('  every line that is not synchronized has an F at a relative time tau <= n-2: %s' % early)
    if tau_max is not None:
        hit = [(n, tau) for n, tau in fails if tau is not None and tau <= tau_max]
        print('  smallest length with an F at a relative time tau <= %d: %s'
              % (tau_max, 'n = %d (tau = %d)' % hit[0] if hit else 'none'))


if __name__ == '__main__':
    main()
