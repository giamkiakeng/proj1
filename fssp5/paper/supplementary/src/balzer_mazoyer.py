#!/usr/bin/env python3
"""balzer_mazoyer.py -- Balzer's conditions (B1)-(B4) of Section 6.5 on Mazoyer's six-state solution.

A check of the formalization against the source: Mazoyer (Publ. Dept. Math. Lyon 1986, fascicule
1A, section 7) states that his solution violates Balzer's conditions 1 (stability of G), 2 (image
solution) and 4 (dominance of G) and satisfies only condition 3 (F is produced only by GGG, *GG,
GG*).  The conditions are evaluated on the transitions that the lines of lengths 3..NMAX use before
they fire (the other entries of the table could be changed without changing the solution):

  (B1) a used transition (x,G,y) -> d with d != G and not x, y in {G, *}; weak reading: x, y working
  (B2) for an involution I of {L, A, B, C} (fixing G, F and the border): two used transitions
       e -> d and I(e) -> d' with d' != I(d), where I(x,y,z) = (I(z),I(y),I(x)); for all
       neighbourhoods, and for the neighbourhoods without a border only
  (B3) (G,G,G), (*,G,G), (G,G,*) -> F; strong reading: no other used transition gives F
  (B4) a used transition (G,v,G) -> d with v != G and d != G

usage: python3 balzer_mazoyer.py [NMAX]      (default 150)
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    tab = {}
    for ln in open(path):
        w = ln.split('#')[0].split()
        if len(w) == 4 and w[0] != 'k':
            tab[tuple(w[:3])] = w[3]
    return tab


def used_transitions(tab, nmax):
    used = {}
    for n in range(3, nmax + 1):
        row = ['G'] + ['L'] * (n - 1)
        for t in range(2 * n - 2):
            r = ['*'] + row + ['*']
            nbs = [tuple(r[i - 1:i + 2]) for i in range(1, n + 1)]
            row = [tab[e] for e in nbs]
            for e in nbs:
                used[e] = tab[e]
            if t < 2 * n - 3:
                assert 'F' not in row, (n, t)
        assert all(s == 'F' for s in row), n
    return used


def involutions(states):
    """all involutions of the list of states (as dicts), the identity first"""
    out = []
    for k in range(len(states) // 2 + 1):
        for pairs in itertools.combinations(itertools.combinations(states, 2), k):
            flat = [s for p in pairs for s in p]
            if len(set(flat)) == len(flat):
                I = {s: s for s in states}
                for a, b in pairs:
                    I[a], I[b] = b, a
                out.append(I)
    return out


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    tab = load(os.path.join(HERE, '..', 'results', 'mazoyer6.txt'))
    used = used_transitions(tab, nmax)
    W = ['L', 'G', 'A', 'B', 'C']
    print('Mazoyer\'s solution: %d transitions used on the lines of lengths 3..%d before they fire'
          % (len(used), nmax))
    fmt = lambda es: ', '.join('(%s)->%s' % (','.join(e), used[e]) for e in sorted(es))   # noqa: E731
    b1s = [e for e in used if e[1] == 'G' and not {e[0], e[2]} <= {'G', '*'} and used[e] != 'G']
    b1w = [e for e in b1s if e[0] in W and e[2] in W]
    print('(B1) violated by %d used transitions (weak reading: %d): %s' % (len(b1s), len(b1w), fmt(b1s)))
    pre = [('G', 'G', 'G'), ('*', 'G', 'G'), ('G', 'G', '*')]
    b3 = all(used.get(e, 'F') == 'F' for e in pre)
    b3s = b3 and all(used[e] != 'F' for e in used if e not in pre)
    print('(B3) holds: %s; strong reading (no other used transition gives F): %s' % (b3, b3s))
    b4 = [e for e in used if e[0] == 'G' and e[2] == 'G' and e[1] != 'G' and used[e] != 'G']
    print('(B4) violated by %d used transitions: %s' % (len(b4), fmt(b4)))
    for reading in ('all neighbourhoods', 'only the neighbourhoods without a border'):
        holds = []
        for I0 in involutions(['L', 'A', 'B', 'C']):
            I = dict(I0, G='G', F='F', **{'*': '*'})
            ok = True
            for e, d in used.items():
                if reading != 'all neighbourhoods' and '*' in (e[0], e[2]):
                    continue
                m = (I[e[2]], I[e[1]], I[e[0]])
                if m in used and used[m] != I[d]:
                    ok = False
                    break
            if ok:
                holds.append(''.join(sorted('(%s %s)' % (a, b) for a, b in I0.items() if a < b and I0[a] == b)) or 'id')
        print('(B2) for %s: consistent with the used transitions for %s of the 10 involutions%s'
              % (reading, len(holds), (': ' + ', '.join(holds)) if holds else ''))


if __name__ == '__main__':
    main()
