#!/usr/bin/env python3
"""germcompare.py -- half-line neighbourhoods of rules below an anti-diagonal.

Simulates the half-line diagram C_inf of each rule on the cells (t,i) with
t+i <= M, collects the neighbourhoods used there and reports their number
(besides (L,L,L)) and whether all rules agree on them.

usage: germcompare.py rule1 [rule2 ...] M
       germcompare.py --germline rule M     (print the germ in the format of germdfs.c)
"""
import sys


def load(rule):
    tab = {}
    for ln in open(rule):
        t = ln.split('#')[0].split()
        if len(t) == 4:
            tab[tuple(t[:3])] = t[3]
    return tab


def germ(tab, M):
    """neighbourhood -> value, over the half-line cells with t+i <= M"""
    width = M + 2
    cur = ['G'] + ['L'] * (width - 1)      # time 0; cur[i-1] is cell i
    used = {}
    for t in range(M):                      # compute time t+1
        nxt = []
        for i in range(width):
            if t + (i + 1) >= M:            # cell (t+1, i+1) lies beyond anti-diagonal M
                nxt.append('?')
                continue
            e = (cur[i - 1] if i > 0 else '*', cur[i], cur[i + 1] if i + 1 < width else 'L')
            if '?' in e:
                nxt.append('?')
                continue
            used[e] = tab[e]
            nxt.append(tab[e])
        cur = nxt
    return used


def main():
    if sys.argv[1] == '--germline':
        g = germ(load(sys.argv[2]), int(sys.argv[3]))
        print('GERM ' + ' '.join('%s%s%s>%s' % (e[0], e[1], e[2], v)
                                 for e, v in g.items() if e != ('L', 'L', 'L')))
        return
    rules, M = sys.argv[1:-1], int(sys.argv[-1])
    germs = [germ(load(r), M) for r in rules]
    for r, g in zip(rules, germs):
        print("%s: %d neighbourhoods besides (L,L,L) below anti-diagonal %d%s" % (
            r, len(g) - (('L', 'L', 'L') in g), M,
            '; a firing cell occurs' if 'F' in g.values() else ''))
    if len(germs) > 1:
        same = all(g == germs[0] for g in germs[1:])
        print("identical half-line neighbourhoods and values:", same)


if __name__ == '__main__':
    main()
