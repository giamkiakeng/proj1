#!/usr/bin/env python3
"""germ_regular_check.py GERMFILE IDX:P:T1 [IDX:P:T1 ...] [--qmax Q]

Independent check (no code shared with germpersist.py) that the half-line of a germ is eventually regular
in the sense of the note (Corollary 'regular'): for every residue r = 0..P-1 and t = T1 + r,

    C(t)   = w_0 z_1^a_1 w_1 ... z_m^a_m w_m,
    C(t+P) = w_0 z_1^(a_1+D_1) w_1 ... z_m^(a_m+D_m) w_m,     D_j >= 0,

where C(t) = C(t,1) ... C(t,t+1) is computed from the germ alone (plus (L,L,L) -> L), and every block
z_j^a_j has length a_j |z_j| >= 2P + 2|z_j|.  Then C(t + nu P) = w_0 z_1^(a_1 + nu D_1) ... for all nu >= 0:
a cell at time t+P depends on the cells within distance P at time t, so inserting further copies of z_j at a
point of block j at distance >= P from both of its ends, aligned with the period, inserts the same number of
copies into block j of the image, where the image is |z_j|-periodic (it contains the interior of the block,
of length >= |z_j|).  Induction on nu, as the blocks only grow.  The decomposition used here: the blocks are
the maximal runs, scanned from the left, of a smallest period q <= QMAX and length >= 2P + 2q; the rest of a
block that is not a full period belongs to the next junction word.  All vectors D are searched (depth first,
block by block; a prefix of the inflated word that differs from C(t+P) is abandoned, and so is every larger d_j
once d_j copies do not match), and exactly one must fit.  The predicted configuration 10 periods later is also
compared with direct simulation (sanity check only)."""
import sys


def load(p):
    return [ln.split()[1:] for ln in open(p) if ln.startswith('GERM')]


def half_line(germ, T):
    rule = {('L', 'L', 'L'): 'L'}
    for tok in germ:
        nb, v = tok.split('>')
        rule[tuple(nb)] = v
    conf = ['G']
    rows = [''.join(conf)]
    for t in range(1, T + 1):
        pad = ['*'] + conf + ['L', 'L']
        new = []
        for i in range(1, t + 2):           # cells 1..t+1; pad[i] is cell i
            v = rule.get((pad[i - 1], pad[i], pad[i + 1]))
            if v is None:
                return None
            new.append(v)
        conf = new
        rows.append(''.join(conf))
    return rows


def blocks(w, P, qmax):
    """[(start, q, count)]: maximal runs w[s:e] with w[k] = w[k-q] (s+q <= k < e), q smallest, of
    count = (e-s)//q full periods with count*q >= 2P+2q"""
    out, i, n = [], 0, len(w)
    while i < n:
        found = None
        for q in range(1, qmax + 1):
            e = i + q
            while e < n and w[e] == w[e - q]:
                e += 1
            if ((e - i) // q) * q >= 2 * P + 2 * q:
                found = (q, e)
                break
        if found:
            q, e = found
            out.append((i, q, (e - i) // q))
            i = i + ((e - i) // q) * q
        else:
            i += 1
    return out


def inflate(w, bl, D):
    out, pos = [], 0
    for (s, q, a), d in zip(bl, D):
        out.append(w[pos:s + a * q])
        out.append(w[s:s + q] * d)
        pos = s + a * q
    out.append(w[pos:])
    return ''.join(out)


def growth_vectors(x, y, bl, P):
    """all D with inflate(x, bl, D) == y (then sum d_j q_j = len(y) - len(x)), by depth-first search"""
    hits = []

    def rec(j, px, py, D):
        if j == len(bl):
            if y[py:] == x[px:]:
                hits.append(tuple(D))
            return
        s, q, a = bl[j]
        seg = x[px:s + a * q]
        if y[py:py + len(seg)] != seg:
            return
        o = py + len(seg)
        d = 0
        while d * q <= P and y[o:o + d * q] == x[s:s + q] * d:
            rec(j + 1, s + a * q, o + d * q, D + [d])
            d += 1

    rec(0, 0, 0, [])
    return hits


def check(germ, P, T1, qmax):
    rows = half_line(germ, T1 + 11 * P)
    if rows is None:
        return 'the germ does not determine the half-line up to time %d' % (T1 + 11 * P)
    for r in range(P):
        t = T1 + r
        x, y = rows[t], rows[t + P]
        bl = blocks(x, P, qmax)
        if not bl:
            return 'residue %d: no block' % r
        hits = [D for D in growth_vectors(x, y, bl, P) if sum(d * q for d, (_, q, _) in zip(D, bl)) == P]
        if len(hits) != 1:
            return 'residue %d: %d growth vectors' % (r, len(hits))
        D = hits[0]
        if inflate(x, bl, [10 * d for d in D]) != rows[t + 10 * P]:
            return 'residue %d: prediction 10 periods later fails' % r
    return 'REGULAR'


def main():
    args = sys.argv[1:]
    qmax = 24
    if '--qmax' in args:
        k = args.index('--qmax')
        qmax = int(args[k + 1])
        del args[k:k + 2]
    germs = load(args[0])
    for spec in args[1:]:
        idx, P, T1 = map(int, spec.split(':'))
        print('germ %d (P=%d, t1=%d): %s' % (idx, P, T1, check(germs[idx - 1], P, T1, qmax)), flush=True)


if __name__ == '__main__':
    main()
