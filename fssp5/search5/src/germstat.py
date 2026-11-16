#!/usr/bin/env python3
"""germstat.py FILE... -- half-lines of rules: how many neighbourhoods the half-line uses, up to which anti-diagonal the
listed transitions determine it, and whether it is periodic in time and space on a wedge at the left border.

For each rule (a rule file, or the RULE lines of a dump of fscount) the half-line is simulated with the listed
transitions as far as they determine it (at most up to the anti-diagonal MAXM = 400).  Output per rule:
  top      the largest n with 2..n synchronized
  det      the half-line is determined for t + i <= det (det = MAXM: no undefined neighbourhood was met)
  c        number of neighbourhoods other than LLL used by the cells with t + i <= min(det, 78)
  last     the anti-diagonal on which the last new neighbourhood appears
  wedge    (s, p, q): the half-line is periodic with period p in time and q in space on {s <= i <= t/4, t >= t0} as far as
           determined, for the least s <= 4 (p, q <= 12), with t0 = det/2; '-' if there is no such s
"""
import sys, re, collections
MAXM = 400

def load_many(fn):
    rules = []
    cur = None
    for l in open(fn):
        if l.startswith('RULE'):
            m = re.match(r'RULE run (\d+) lines (\d+)\.\.(\d+): (.*)', l)
            tab = {}
            for it in m.group(4).split():
                e, d = it.split('='); tab[(e[0], e[1], e[2])] = d
            rules.append(('%s run %s level %s' % (fn.split('/')[-1], m.group(1), m.group(3)), tab))
            continue
        l = l.split('#')[0].split()
        if l and '=' in l[0]:
            tab = {}
            for it in l:
                e, d = it.split('='); tab[(e[0], e[1], e[2])] = d
            rules.append((fn.split('/')[-1], tab)); continue
        if len(l) == 4:
            if cur is None:
                cur = {}; rules.append((fn.split('/')[-1], cur))
            cur[tuple(l[:3])] = l[3]
    return rules

def sync(tab, n):
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        es = [(row[i - 1] if i > 0 else '*', row[i], row[i + 1] if i < n - 1 else '*') for i in range(n)]
        if any(e not in tab for e in es):
            return False
        row = [tab[e] for e in es]
        if 'F' in row:
            return t == 2 * n - 2 and all(x == 'F' for x in row)
    return False

def halfline(tab):
    """rows[t][i-1] for t + i <= det; first-use anti-diagonal of every neighbourhood"""
    tab = dict(tab); tab[('L', 'L', 'L')] = 'L'
    rows = [['G'] + ['L'] * MAXM]
    first = {}
    det = MAXM
    for t in range(0, MAXM):
        prev = rows[-1]; new = []
        lim = min(det, MAXM) - (t + 1)          # cells i <= lim of the row t+1 are wanted
        for i in range(1, lim + 1):
            e = (prev[i - 2] if i > 1 else '*', prev[i - 1], prev[i])
            if e not in tab:
                det = min(det, t + 1 + i - 1)     # the cell (t+1, i) is not determined: anti-diagonals < t+1+i are
                break
            if e != ('L', 'L', 'L') and e not in first:
                first[e] = t + 1 + i
            new.append(tab[e])
        if not new:
            break
        rows.append(new + ['?'] * (MAXM + 1 - len(new)))
        if lim <= 1:
            break
    return rows, det, first

def wedge(rows, det, smax=24, pmax=24, qmax=24):
    """the least s <= smax, with the least periods (p, q), such that C(t+p, i) = C(t, i) and C(t, i+q) = C(t, i) on all
    cells of the wedge {s <= i <= t/4, t >= t0}, t0 = T/2, that lie in the determined part (t + p + i + q <= det)"""
    T = det - 2
    t0 = T // 2
    def cells(s):
        for t in range(t0, T):
            for i in range(s, t // 4 + 1):
                yield t, i
    for s in range(1, smax + 1):
        tt = (2 * T) // 3
        hi = tt // 4
        if hi - s < 2 * qmax:
            return None
        row = rows[tt]
        qs = [q for q in range(1, qmax + 1) if all(row[i - 1] == row[i + q - 1] for i in range(s, hi - q + 1))]
        if not qs:
            continue
        q = qs[0]
        ps = [p for p in range(1, pmax + 1) if all(rows[tt + p][i - 1] == row[i - 1] for i in range(s, hi + 1))]
        if not ps:
            continue
        p = ps[0]
        ok = True
        for t, i in cells(s):
            if t + p + i + q > det:
                continue
            a = rows[t][i - 1]
            if rows[t + p][i - 1] != a or (i + q <= t // 4 and rows[t][i + q - 1] != a):
                ok = False; break
        if ok:
            return (s, p, q)
    return None


if __name__ == '__main__':
    stats = collections.Counter()
    for fn in sys.argv[1:]:
        for name, tab in load_many(fn):
            top = 1
            while sync(tab, top + 1):
                top += 1
            rows, det, first = halfline(tab)
            c = sum(1 for e, m in first.items() if m <= min(det, 78))
            last = max(first.values()) if first else 0
            w = wedge(rows, det) if det >= MAXM else None
            key = (top, det if det < MAXM else 'all', c, last, w)
            stats[key] += 1
    print('count  top  det  c  last  wedge(s,p,q)')
    for key, v in sorted(stats.items(), key=lambda x: (-x[0][0], str(x[0]))):
        print('%5d  %s' % (v, '  '.join(str(x) for x in key)))
