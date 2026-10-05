"""fsspsim.py -- space-time diagrams for the video, computed from the rule tables in ../results.

Every diagram shown in the video is produced here from a machine-readable rule table
(results/delta14.txt, results/mazoyer6.txt, ...), with the same semantics as the paper:
cell 1 starts as G, the others as L, the border is '*', and the diagram of a line of
length n runs until the first firing cell (or a time limit).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results')


def load_rule(name):
    """rule table {(x, y, z): d} from results/<name>.txt (lines 'x y z d', '#' comments)"""
    path = name if os.path.exists(name) else os.path.join(RESULTS, name + '.txt')
    tab = {}
    for ln in open(path):
        t = ln.split('#')[0].split()
        if len(t) == 4:
            tab[tuple(t[:3])] = t[3]
    return tab


def line(tab, n, T=None):
    """rows[t][i-1] = C_n(t, i) for t = 0..T (default 2n-2); stops after the first row containing F"""
    T = 2 * n - 2 if T is None else T
    row = ['G'] + ['L'] * (n - 1)
    rows = [row]
    for _ in range(T):
        ext = ['*'] + row + ['*']
        row = [tab[(ext[i - 1], ext[i], ext[i + 1])] for i in range(1, n + 1)]
        rows.append(row)
        if 'F' in row:
            break
    return rows


def halfline(tab, T, width=None):
    """rows[t][i-1] = C_inf(t, i) for t = 0..T and 1 <= i <= width (default T + 2)"""
    width = T + 2 if width is None else width
    row = ['G'] + ['L'] * (width - 1)
    rows = [row]
    for _ in range(T):
        ext = ['*'] + row + ['L']          # the cells beyond `width` are still quiescent
        row = [tab[(ext[i - 1], ext[i], ext[i + 1])] for i in range(1, width + 1)]
        rows.append(row)
    return rows


def first_fire(rows):
    """(t, [cells firing at t]) for the first row containing F, or None"""
    for t, r in enumerate(rows):
        if 'F' in r:
            return t, [i + 1 for i, s in enumerate(r) if s == 'F']
    return None


def synchronizes(tab, n):
    rows = line(tab, n)
    ff = first_fire(rows)
    return ff is not None and ff[0] == 2 * n - 2 and len(ff[1]) == n


if __name__ == '__main__':
    d14 = load_rule('delta14')
    print('delta14 sync:', [n for n in range(2, 16) if synchronizes(d14, n)])
    print('delta14 n=15 first fire:', first_fire(line(d14, 15, 40)))
    for nm in ('delta13', 'mazoyer6'):
        r = load_rule(nm)
        print(nm, 'sync:', [n for n in range(2, 41) if synchronizes(r, n)][:20], '...')
    print('delta13 n=14 first fire:', first_fire(line(load_rule('delta13'), 14, 40)))
