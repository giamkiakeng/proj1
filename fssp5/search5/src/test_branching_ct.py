#!/usr/bin/env python3
"""test_branching_ct.py N -- next_branch() of certtree.py (stable generals) against a direct simulation on random
rules over {L, A, B} with the first cell constant G (see test_branching.py)."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
N_ = sys.argv[1]
sys.argv = ['certtree.py', N_, '/dev/null', '/dev/null']
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certtree.py')).read().split("if __name__ == '__main__':")[0]
exec(compile(src, 'certtree-head', 'exec'))
rng = random.Random(11)
Wp = [0, 2, 3]
ntest = nsteps = 0
for trial in range(300):
    d = {}
    for l in [1] + Wp:
        for c in Wp:
            for r in Wp:
                d[(l, c, r)] = rng.choice(Wp)
    d[(0, 0, 0)] = 0
    d[(1, 0, 0)] = 2                      # root: delta(G,L,L) = A
    H = {}
    def get(t, i):
        if i == 1:
            return 1
        if i > t + 1:
            return 0
        return H[(t, i)]
    for t in range(1, MM):
        for i in range(2, min(t + 1, MM - t) + 1):
            H[(t, i)] = d[(get(t - 1, i - 1), get(t - 1, i), get(t - 1, i + 1))]
    cube, known = 'GLL=A', {(0, 0, 0), (1, 0, 0)}
    while True:
        e, vals = next_branch(cube)
        ref = None
        for (t, i) in order:
            nb = (get(t - 1, i - 1), get(t - 1, i), get(t - 1, i + 1))
            if nb not in known:
                ref = nb
                break
        if e is None:
            if vals == 'dead':
                assert any(H[(t, t + 1)] == 0 for t in range(1, MM) if (t, t + 1) in H)
            else:
                assert ref is None
            break
        assert e == ref, (e, ref, cube)
        known.add(e)
        cube += ',%s%s%s=%s' % (NAMES[e[0]], NAMES[e[1]], NAMES[e[2]], NAMES[d[e]])
        nsteps += 1
    ntest += 1
print('certtree.next_branch: %d random rules, %d branching steps, half-line to the anti-diagonal %d: agrees with the direct simulation' % (ntest, nsteps, MM))
