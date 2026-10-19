#!/usr/bin/env python3
"""
allsat.py -- enumerate the completions of a germ for the lengths 2..N, projected on the entries
they use, and try to extend each one to longer lengths by depth-first search.

A table synchronizes the lines 2..N iff its restriction to the entries those lines use does, and two
tables with the same restriction produce the same lines.  So the completions for 2..N form finitely
many classes, one per projected table (germ + the used entries).  This script finds them one by one
with an incremental solver (CaDiCaL, PySAT) and a refinement loop as in gcegar_inc.py: a model that
fails some line adds the cone of its failing cells; a model that synchronizes all lines 2..N is
recorded and blocked by the clause "some used entry takes another value".

Each recorded class is then extended by depth-first search to the lengths N+1..NEXT: the lines are
simulated in order, and an entry that is not yet defined is branched on when it is first needed
(value F if it is needed for the firing step 2n-2, a working state otherwise).  A class with no
extension is closed.  If every class is closed and the enumeration ends with UNSAT, no table
extending the germ synchronizes the lines 2..NEXT, which refutes the germ.

usage: allsat.py GERMFILE|FREE N NEXT OUT [--budget S] [--limit M] [--k K]
   prints one line per class and a summary; OUT receives the classes (projected tables).
   With FREE the half-line is part of the table; with NEXT <= N the classes are only counted.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfix  # noqa: E402
from gcegar import simulate  # noqa: E402
from gcegar_inc import Inc  # noqa: E402


def used_entries(tab, n):
    """the neighbourhoods read by the line of length n at the steps 1..2n-2"""
    U = set()
    c = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        r = ['*'] + c + ['*']
        nbs = [(r[i - 1], r[i], r[i + 1]) for i in range(1, n + 1)]
        U.update(nbs)
        c = [tab[nb] for nb in nbs]
    return U


def sim_partial(tab, n):
    """simulate line n with a partial table: 'ok', 'fail', or ('need', nbhd, must_fire)"""
    c = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        r = ['*'] + c + ['*']
        nxt = []
        for i in range(1, n + 1):
            nb = (r[i - 1], r[i], r[i + 1])
            if nb not in tab:
                return ('need', nb, t == 2 * n - 2)
            x = tab[nb]
            if (x == 'F') != (t == 2 * n - 2):
                return 'fail'
            nxt.append(x)
        c = nxt
    return 'ok'


def extend(tab, lengths, W, stats, nodes_max=10 ** 6):
    """depth-first search for an extension of the partial table TAB that synchronizes LENGTHS"""
    stats['nodes'] += 1
    if stats['nodes'] > nodes_max:
        raise TimeoutError
    for n in lengths:
        r = sim_partial(tab, n)
        if r == 'ok':
            continue
        if r == 'fail':
            return None
        _, nb, fire = r
        for v in (['F'] if fire else W):
            tab[nb] = v
            got = extend(tab, lengths, W, stats, nodes_max)
            if got is not None:
                return got
            del tab[nb]
        return None
    return dict(tab)


def main():
    a = sys.argv[1:]
    germ = gfix.parse_germ(a[0])
    N, NEXT, out = int(a[1]), int(a[2]), a[3]
    budget, limit, k = None, None, 5
    it = iter(a[4:])
    for x in it:
        if x == '--budget':
            budget = float(next(it))
        elif x == '--limit':
            limit = int(next(it))
        elif x == '--k':
            k = int(next(it))
    I = Inc(germ, k, None)
    W = I.E.W
    for n in range(2, min(7, N + 1)):
        I.add(n, gfix.region(n, 'full'))
    cone_h = {n: n - 1 for n in range(2, min(7, N + 1))}
    start = time.time()
    classes, open_classes, rounds = 0, 0, 0
    fh = open(out, 'w')
    while True:
        if budget is not None and time.time() - start > budget:
            print('STOP: budget exhausted after %d classes (%d open), %d rounds' % (classes, open_classes, rounds))
            break
        if limit is not None and classes >= limit:
            print('STOP: limit of %d classes reached (%d open), %d rounds' % (classes, open_classes, rounds))
            break
        rounds += 1
        if rounds % 100 == 0:
            print('  ... round %d, %d classes, %.0f s' % (rounds, classes, time.time() - start), flush=True)
        r, model = I.solve()
        if not r:
            print('DONE: UNSAT after %d classes (%d open), %d rounds, %.0f s' % (
                classes, open_classes, rounds, time.time() - start))
            break
        tab = I.table(model)
        fail = None
        for n in range(2, N + 1):
            f = simulate(tab, n)
            if f:
                fail = (n, f)
                break
        if fail is not None:
            n, (what, left) = fail
            h = max(n - left, cone_h.get(n, 0))
            cone_h[n] = h
            I.add(n, gfix.region(n, 'cone', h))
            continue
        U = set()
        for n in range(2, N + 1):
            U |= used_entries(tab, n)
        free_used = sorted(nb for nb in U if nb in I.E.T)
        part = {nb: tab[nb] for nb in U}
        part.update(I.E.germ)
        classes += 1
        stats = {'nodes': 0}
        if NEXT <= N:
            ext, verdict = None, 'counted'
        else:
            try:
                ext = extend(dict(part), range(N + 1, NEXT + 1), W, stats)
                verdict = 'EXTENDS to %d' % NEXT if ext is not None else 'closed'
            except TimeoutError:
                ext, verdict = None, 'undecided'
        if ext is not None or verdict in ('undecided', 'counted'):
            open_classes += 1
        print('class %d: %d used free entries, %s (%d nodes), %.0f s' % (
            classes, len(free_used), verdict, stats['nodes'], time.time() - start), flush=True)
        fh.write('CLASS %d %s %s\n' % (classes, verdict.replace(' ', '_'),
                                       ' '.join('%s>%s' % (''.join(nb), part[nb]) for nb in free_used)))
        if ext is not None:
            fh.write('EXT %d %s\n' % (classes, ' '.join('%s>%s' % (''.join(nb), ext[nb])
                                                         for nb in sorted(ext) if nb in I.E.T)))
        fh.flush()
        I.E.cls.append([-I.E.T[nb][tab[nb]] for nb in free_used])
    fh.close()


if __name__ == '__main__':
    main()
