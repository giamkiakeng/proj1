#!/usr/bin/env python3
"""check_balzer.py RULE [I] [NMAX] -- which of Balzer's conditions hold on the table of a five-state rule?

(B1) stable general: delta(x,G,y) = G; weak reading: for working x, y, not both G; strong reading: also with a
     border on one side, the other neighbour not G.
(B2) image condition delta(I(z),I(y),I(x)) = I(delta(x,y,z)) for the involution I of the working states
     (id, AB, LA, LB, LG, GA, GB, LG+AB, LA+GB, LB+GA; default id), without and with the border neighbourhoods.
(B3) weak: GGG, *GG, GG* give F; strong: no other neighbourhood gives F.
(B4) delta(G,v,G) = G for v != G.
Entries that the file does not define count as violations.  Then the lines 2..NMAX (default 60) are simulated.
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simlib import load, ok
k, tab = load(sys.argv[1]); spec = sys.argv[2] if len(sys.argv) > 2 else 'id'; NMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 60
assert k == 5
W = 'LGAB'
I = {s: s for s in W + 'F*'}
if spec != 'id':
    for part in spec.split('+'):
        I[part[0]], I[part[1]] = part[1], part[0]
def show(name, bad):
    print('  %-34s %s' % (name, 'holds' if not bad else 'violated at ' + ' '.join(''.join(t) for t in bad)))
print('%s: %d entries' % (os.path.basename(sys.argv[1]), len(tab)))
inner = [t for t in itertools.product(W, repeat=3)]
left = [('*', y, z) for y in W for z in W]; right = [(x, y, '*') for x in W for y in W]
b1w = [(x, 'G', y) for x in W for y in W if not (x == 'G' and y == 'G') and tab.get((x, 'G', y)) != 'G']
b1b = [('*', 'G', y) for y in W if y != 'G' and tab.get(('*', 'G', y)) != 'G'] + [(x, 'G', '*') for x in W if x != 'G' and tab.get((x, 'G', '*')) != 'G']
show('(B1) weak', b1w); show('(B1) strong', b1w + b1b)
def img(ts):
    return [t for t in ts if t not in tab or tab.get((I[t[2]], I[t[1]], I[t[0]])) != I[tab[t]]]
show('(B2) without borders, I = %s' % spec, img(inner)); show('(B2) with borders, I = %s' % spec, img(inner + left + right))
fire = [('G', 'G', 'G'), ('*', 'G', 'G'), ('G', 'G', '*')]
show('(B3) weak', [t for t in fire if tab.get(t) != 'F'])
show('(B3) strong', [t for t in fire if tab.get(t) != 'F'] + [t for t in inner + left + right if t not in fire and tab.get(t) == 'F'])
show('(B4)', [('G', v, 'G') for v in W if v != 'G' and tab.get(('G', v, 'G')) != 'G'])
print('  synchronized lengths among 2..%d: %s' % (NMAX, [n for n in range(2, NMAX + 1) if ok(tab, n)]))
