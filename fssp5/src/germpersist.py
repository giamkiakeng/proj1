#!/usr/bin/env python3
"""germpersist.py -- certify that a germ's half-line is eventually regular.

The half-line diagram determined by a germ is *eventually regular* with
period P from time t1 on if, for every residue r = 0..P-1, the configuration
w(t) (cells 1..t+1) at t = t1+r decomposes as

    w(t) = x_0 y_1^{a_1} x_1 y_2^{a_2} ... y_m^{a_m} x_m

with every block y_j^{a_j} longer than 2P + 2|y_j|, and w(t+P) has the same
decomposition with the same words x_j, y_j and exponents a_j + D_j, D_j >= 0.
By locality (a cell at time t+P depends only on the cells within distance P
at time t), the same then holds for every larger exponent vector, hence for
all times t1 + r + kP by induction; in particular the germ determines the
half-line forever.  The leftmost block with D_j > 0 starts at a bounded
position and grows linearly, and inside it the diagram is periodic in time
(period P) and space (period |y_j|): the half-line is doubly periodic in a
wedge at the left border, so by the left-border barrier (Theorem 3.6 of the
paper) no rule containing the germ is a minimal-time solution.

The decomposition is computed greedily: a block is a maximal run of length
>= LMIN in which w[i] = w[i-q] for the smallest period q <= QMAX; everything
else belongs to the junction words.  The same greedy procedure is applied to
w(t) and w(t+P) and the results are compared.

usage: germpersist.py germfile [t1] [PMAX] [QMAX]
output per germ: "<idx> REGULAR P=.. t1=.. first-growing-block: start=.. q=.. D=.."
                 or "<idx> NOT-CERTIFIED" or "<idx> OPEN".
"""
import sys


def simulate(tab, T):
    """rows[t] = configuration of cells 1..t+1 at time t (list of chars),
    or None if the germ does not determine it"""
    rows = [['G']]
    cur = ['G', 'L', 'L']
    for t in range(1, T + 1):
        nxt = []
        for i in range(t + 1):                      # cells 1..t+1 (0-based i)
            l = cur[i - 1] if i > 0 else '*'
            c = cur[i] if i < len(cur) else 'L'
            r = cur[i + 1] if i + 1 < len(cur) else 'L'
            d = tab.get((l, c, r))
            if d is None:
                return rows, t
            nxt.append(d)
        rows.append(nxt)
        cur = nxt + ['L', 'L']
    return rows, None


def decompose(w, lmin, qmax):
    """greedy decomposition into junction words and periodic blocks;
    returns list of ('J', word) and ('B', base, count, rest) items where the
    block is base*count + rest (rest a proper prefix of base)"""
    out = []
    i, n = 0, len(w)
    junction = []
    while i < n:
        best = None
        for q in range(1, qmax + 1):
            if i + lmin > n:
                break
            if all(w[k] == w[k - q] for k in range(i + q, i + lmin)):
                j = i + lmin
                while j < n and w[j] == w[j - q]:
                    j += 1
                best = (q, j)
                break
        if best is None:
            junction.append(w[i])
            i += 1
            continue
        q, j = best
        if junction:
            out.append(('J', ''.join(junction)))
            junction = []
        length = j - i
        base = ''.join(w[i:i + q])
        out.append(('B', base, length // q, ''.join(w[i + (length // q) * q:j])))
        i = j
    if junction:
        out.append(('J', ''.join(junction)))
    return out


def build(dec, bump=None):
    """string of a decomposition; bump = index of a block whose count is +1,
    or a dict {block index: extra count}"""
    if bump is None:
        bump = {}
    elif isinstance(bump, int):
        bump = {bump: 1}
    out = []
    for k, item in enumerate(dec):
        if item[0] == 'J':
            out.append(item[1])
        else:
            out.append(item[1] * (item[2] + bump.get(k, 0)) + item[3])
    return ''.join(out)


def evolve(tab, conf, steps):
    """evolve a half-line configuration (cells 1..len, front at the last cell,
    L beyond) for the given number of steps; None if a neighbourhood outside
    the germ is needed"""
    cur = list(conf)
    for _ in range(steps):
        ext = cur + ['L', 'L']
        nxt = []
        for i in range(len(cur) + 1):
            l = ext[i - 1] if i > 0 else '*'
            d = tab.get((l, ext[i], ext[i + 1]))
            if d is None:
                return None
            nxt.append(d)
        cur = nxt
    return ''.join(cur)


def certify(tab, t1, pmax, qmax):
    rows, open_at = simulate(tab, t1 + 4 * pmax + 1)
    if open_at is not None:
        return 'OPEN', open_at
    for P in range(1, pmax + 1):
        lmin = 2 * P + 2 * qmax
        ok = True
        info = None
        for r in range(P):
            t = t1 + r
            d1 = decompose(rows[t], lmin, qmax)
            d2 = decompose(rows[t + P], lmin, qmax)
            if len(d1) != len(d2):
                ok = False
                break
            growth = []
            pos = 0
            for a, b in zip(d1, d2):
                if a[0] != b[0]:
                    ok = False
                    break
                if a[0] == 'J':
                    if a[1] != b[1]:
                        ok = False
                        break
                    pos += len(a[1])
                else:
                    # same base and remainder, count not smaller, long enough
                    if a[1] != b[1] or a[3] != b[3] or b[2] < a[2] or a[2] * len(a[1]) < lmin:
                        ok = False
                        break
                    growth.append((pos, len(a[1]), b[2] - a[2]))
                    pos += a[2] * len(a[1]) + len(a[3])
            if not ok:
                break
            if ok:
                # induction step: one more period in any single block of the input
                # gives one more period in the same block of the output
                for k, item in enumerate(d1):
                    if item[0] != 'B':
                        continue
                    got = evolve(tab, build(d1, k), P)
                    if got is None or got != build(d2, k):
                        ok = False
                        break
                # extra checks: two periods in one block, one in every block
                blocks = [k for k, item in enumerate(d1) if item[0] == 'B']
                for bump in [{k: 2} for k in blocks] + [{k: 1 for k in blocks}]:
                    if not ok:
                        break
                    got = evolve(tab, build(d1, bump), P)
                    if got is None or got != build(d2, bump):
                        ok = False
                # sanity: the decomposition reproduces the actual configurations,
                # and the predicted configurations two and three periods later
                if build(d1) != ''.join(rows[t]) or build(d2) != ''.join(rows[t + P]):
                    ok = False
                D = {k: d2[k][2] - d1[k][2] for k in blocks}
                for mult in (2, 3):
                    if ok and t + mult * P < len(rows):
                        pred = build(d1, {k: mult * D[k] for k in blocks})
                        if pred != ''.join(rows[t + mult * P]):
                            ok = False
            if not ok:
                break
            first = next((g for g in growth if g[2] > 0), None)
            if first is None:
                ok = False
                break
            if info is None or first[0] > info[0]:
                info = first
        if ok:
            return 'REGULAR', (P, info)
    return 'NOT-CERTIFIED', None


def main():
    germfile = sys.argv[1]
    t1 = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    pmax = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    qmax = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    for idx, ln in enumerate(open(germfile), 1):
        if not ln.startswith('GERM'):
            continue
        tab = {('L', 'L', 'L'): 'L'}
        for tok in ln.split()[1:]:
            e, d = tok.split('>')
            tab[tuple(e)] = d
        st, info = certify(tab, t1, pmax, qmax)
        if st == 'REGULAR':
            P, (start, q, D) = info
            print("%d REGULAR P=%d t1=%d first-growing-block: start=%d q=%d D=%d" % (idx, P, t1, start + 1, q, D))
        elif st == 'OPEN':
            print("%d OPEN at t=%d" % (idx, info))
        else:
            print("%d NOT-CERTIFIED" % idx)
        sys.stdout.flush()


if __name__ == '__main__':
    main()
