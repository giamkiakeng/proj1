"""simlib.py -- simulation of rule tables (same file format as the supplementary material)."""
import os
SUPP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'paper', 'supplementary')

def load(path):
    if not os.path.exists(path):
        path = os.path.join(SUPP, 'results', path)
    tab, k = {}, None
    for ln in open(path):
        w = ln.split('#')[0].split()
        if len(w) == 2 and w[0] == 'k':
            k = int(w[1])
        elif len(w) == 4:
            tab[tuple(w[:3])] = w[3]
    return k, tab

def sim(tab, n, tmax=None):
    """rows[t] for t = 0.. until the first row containing F (inclusive) or tmax; '?' = undefined transition"""
    if tmax is None:
        tmax = 2 * n + 5
    rows = [['G'] + ['L'] * (n - 1)]
    while len(rows) <= tmax:
        if 'F' in rows[-1] or '?' in rows[-1]:
            break
        r = ['*'] + rows[-1] + ['*']
        rows.append([tab.get(tuple(r[i - 1:i + 2]), '?') for i in range(1, n + 1)])
    return rows

def ok(tab, n):
    rows = sim(tab, n)
    return len(rows) - 1 == 2 * n - 2 and all(c == 'F' for c in rows[-1])

def show(rows):
    return '\n'.join('%3d %s' % (t, ''.join(r).replace('L', '.')) for t, r in enumerate(rows))
