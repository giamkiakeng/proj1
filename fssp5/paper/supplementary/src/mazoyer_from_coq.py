#!/usr/bin/env python3
"""
mazoyer_from_coq.py -- extract Mazoyer's 6-state minimal-time rule from the
Coq development of J. Duprat (github.com/rocq-archive/firing-squad, autom.v)
and write it as a bordered rule table for fsspcheck / the CNF encoder.

In autom.v the left border behaves like L (Etat (S t) 0 = Transition L ..)
and the right border is emulated by a wall cell that stays in G, so
    delta(*, x, y) = T(L, x, y)      delta(x, y, *) = T(x, y, G).
"""
import re
import sys

src = open(sys.argv[1]).read()
src = re.sub(r'\(\*.*?\*\)', ' ', src, flags=re.S)
S = ['A', 'B', 'C', 'L', 'G', 'F']
defs = {}
for m in re.finditer(r'Definition\s+(Transition\w*)\s*\(([^)]*)\)\s*:=\s*match\s+(\w+)\s+return\s+Couleur\s+with(.*?)end\.', src, flags=re.S):
    name, params, var, body = m.group(1), m.group(2), m.group(3), m.group(4)
    cases = re.findall(r'\|\s*(\w+)\s*=>\s*([^|]+)', body)
    defs[name] = (params, var, [(p, r.strip()) for p, r in cases])


def ev(name, env):
    params, var, cases = defs[name]
    val = env[var]
    for p, r in cases:
        if p == val:
            toks = r.split()
            if len(toks) == 1:
                return toks[0]
            return ev(toks[0], env)
    raise KeyError((name, val))


def T(l, c, r):
    # Transition (c0 c1 c2) matches on c1 and dispatches with c0 c2
    params, var, cases = defs['Transition']
    env = {'c0': l, 'c1': c, 'c2': r}
    for p, res in cases:
        if p == c:
            toks = res.split()
            if len(toks) == 1:
                return toks[0]
            return ev(toks[0], env)


W = ['L', 'G', 'A', 'B', 'C']
out = ["k 6", "# Mazoyer (1987) six-state minimal-time solution, extracted from",
       "# J. Duprat's Coq development (autom.v); borders: left ~ L, right ~ G"]
for l in W + ['*']:
    for c in W:
        for r in W + ['*']:
            if l == '*' and r == '*':
                continue
            d = T('L' if l == '*' else l, c, 'G' if r == '*' else r)
            out.append("%s %s %s %s" % (l, c, r, d))
print("\n".join(out))
