#!/usr/bin/env python3
"""germ_witness_check.py GERMFILE EXTFILE [k]

Independent check (no code shared with germext.c) of the half-line refutations that germext reports.
Line j of EXTFILE ('j CLOSED reach=R FLAGS...') belongs to the j-th germ of GERMFILE.  For every germ whose
line has a witness:
  REFUTED n=.. s=.. L=.. Y=..   Lemma 4.1 (left border) of the note applies: s <= Y <= n - s, the words
                                 y -> C(2n-2-y, y) (s <= y <= Y) and y -> C(2n-3-y, y) (s <= y <= Y-1) are
                                 L-periodic, and Y - s > (k-1)^(2s) L;
  PUMPFAIL n=.. n2=..            PUMP(n, n2) fails: cone(n) of pumping.py avoids the left border and the input
                                 words J_n and J_n2 agree on it (Lemma 4.2 of the note);
the half-line C is simulated from the germ alone and every neighbourhood used on the anti-diagonals the witness
reads (t + i <= D) must be a neighbourhood of the germ or (L, L, L).  Germs without a witness are listed.
The witness is taken from EXTFILE, but every hypothesis is re-checked here."""
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'note2', 'supplementary', 'src'))
import pumping  # noqa: E402


def load(p):
    return [ln.split()[1:] for ln in open(p) if ln.startswith('GERM')]


def simulate(germ, D):
    """C(t, i) for t + i <= D, from the germ alone; None if another neighbourhood is needed.
    Row by row with numpy: the states are coded 0..5 (5 = the border *), a neighbourhood (l, c, r) by
    36 l + 6 c + r, and the transition table is an array with -1 for the neighbourhoods outside the germ."""
    code = {'L': 0, 'G': 1, 'A': 2, 'B': 3, 'F': 4, '*': 5}
    table = np.full(216, -1, dtype=np.int16)
    table[0] = 0                                    # (L, L, L) -> L
    for tok in germ:
        nb, v = tok.split('>')
        table[36 * code[nb[0]] + 6 * code[nb[1]] + code[nb[2]]] = code[v]
    rows = [np.array([1], dtype=np.int16)]          # C(0, 1) = G
    for t in range(1, D):
        prev = rows[-1]
        w = min(t + 1, D - t)
        ext = np.zeros(w + 2, dtype=np.int16)       # ext[i] = C(t-1, i) for i = 0..w+1; ext[0] = *, L beyond
        ext[0] = 5
        m = min(len(prev), w + 1)
        ext[1:m + 1] = prev[:m]
        row = table[36 * ext[0:w] + 6 * ext[1:w + 1] + ext[2:w + 2]]
        if (row < 0).any():
            return None
        rows.append(row)
    name = 'LGABF*'

    def C(t, i):
        assert t + i <= D, (t, i, D)
        return name[rows[t][i - 1]] if i - 1 < len(rows[t]) else 'L'
    return C


def periodic(w, L):
    return all(w[j] == w[j + L] for j in range(len(w) - L))


def main():
    germs = load(sys.argv[1])
    k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    ext = {}
    for ln in open(sys.argv[2]):
        p = ln.split(None, 1)
        ext[int(p[0])] = p[1] if len(p) > 1 else ''
    assert len(ext) == len(germs), (len(ext), len(germs))
    ok = bad = 0
    nowit = []
    for j, g in enumerate(germs, 1):
        s_ext = ext[j]
        m = re.search(r'REFUTED n=(\d+) s=(\d+) L=(\d+) Y=(\d+)', s_ext)
        mp = re.search(r'PUMPFAIL n=(\d+) n2=(\d+)', s_ext)
        if m:
            n, s, L, Y = map(int, m.groups())
            C = simulate(g, 2 * n - 2)
            good = (C is not None and s <= Y <= n - s and Y - s > (k - 1) ** (2 * s) * L
                    and periodic([C(2 * n - 2 - y, y) for y in range(s, Y + 1)], L)
                    and periodic([C(2 * n - 3 - y, y) for y in range(s, Y)], L))
            what = 'lemma 4.1 at n=%d s=%d L=%d Y=%d' % (n, s, L, Y)
        elif mp:
            n, n2 = map(int, mp.groups())
            cn = pumping.cone(n)
            C = simulate(g, 2 * n2 - 2)
            good = (cn is not None and C is not None
                    and all(C(*pumping.input_cell(n, kk, d)) == C(*pumping.input_cell(n2, kk, d)) for kk, d in cn))
            what = 'PUMP(%d,%d) fails' % (n, n2)
        else:
            nowit.append(j)
            continue
        if good:
            ok += 1
        else:
            bad += 1
            print('germ %d: witness NOT confirmed (%s)' % (j, what))
    print('%d germs: %d witnesses confirmed, %d not confirmed; no witness: %s' % (len(germs), ok, bad, nowit))


if __name__ == '__main__':
    main()
