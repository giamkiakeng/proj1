#!/usr/bin/env python3
"""freeset.py K PATTERNS -- the option value for --set of gsat.py / gcert.py that fixes delta(x,G,y) = G for all
entries (x, y not both in {G,*}) except those matching PATTERNS (xGy with ? as wildcard, comma-separated)."""
import sys
k = int(sys.argv[1]); pats = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else []
st = 'LGAB'[:k - 1] + '*'
out = []
for x in st:
    for y in st:
        if x in 'G*' and y in 'G*':
            continue
        if any(q[0] in ('?', x) and q[2] in ('?', y) for q in pats):
            continue
        out.append('%sG%s=G' % (x, y))
print(','.join(out))
