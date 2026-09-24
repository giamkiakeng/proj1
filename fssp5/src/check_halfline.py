#!/usr/bin/env python3
"""check_halfline.py -- does the half-line diagram of a rule fire on some cell
(t,i) with t+i <= M?   usage: check_halfline.py rulefile M"""
import sys

tab = {}
for ln in open(sys.argv[1]):
    t = ln.split('#')[0].split()
    if len(t) == 4:
        tab[tuple(t[:3])] = t[3]
M = int(sys.argv[2])
width = M + 1
cur = ['G'] + ['L'] * (width - 1)          # time 0, cells 1..width
first = None
for t in range(1, M):
    nxt = []
    for i in range(1, width + 1):           # cell i at time t
        if t + i > M:
            nxt.append('?')
            continue
        l = cur[i - 2] if i > 1 else '*'
        c = cur[i - 1]
        r = cur[i] if i < width else 'L'
        d = tab[(l, c, r)]
        if d == 'F' and first is None:
            first = (t, i)
        nxt.append(d)
    cur = nxt
    if first:
        break
print("half-line fires at (t,i)=%s" % (first,) if first else
      "half-line has no firing cell with t+i <= %d" % M)
