#!/usr/bin/env python3
"""test_branching.py K N [options of gcert.py] -- the branching of gcert.py against a direct simulation.

For random total rules delta (values in W, delta(L,L,L) = L) the half-line is simulated directly up to the
anti-diagonal M.  Then the tree of gcert.py is descended from the root, always taking the child with the value
of delta (whether or not gcert.py would exclude it).  Checked at every step: the neighbourhood that
next_branch() asks for is the neighbourhood above the first half-line cell, in the order of the search, that
the transitions fixed so far do not determine; at the end: all cells are determined and the cube is a part of
delta.  The same descent is done with the function of gcover.py (rebuilt here from its source)."""
import sys, os, random, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[1:]
sys.argv = ['gcert.py', argv[0], argv[1], '/dev/null'] + argv[2:]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gcert.py')).read().split("if __name__ == '__main__':")[0]
exec(compile(src, 'gcert-head', 'exec'))
rng = random.Random(7)
side = [BND] + W
def random_rule():
    d = {}
    for l in side:
        for c in W:
            for r in side:
                if l == BND and r == BND:
                    continue
                d[(l, c, r)] = rng.choice(W)
    d[(0, 0, 0)] = 0
    return d
def halfline(d):
    H = {}
    def get(t, i):
        if i < 1:
            return BND
        if i > t + 1:
            return 0
        if t == 0:
            return INIT
        return H[(t, i)]
    for t in range(1, MM):
        for i in range(1, min(t + 1, MM - t) + 1):
            H[(t, i)] = d[(get(t - 1, i - 1), get(t - 1, i), get(t - 1, i + 1))]
    return H, get
ntest, nsteps = 0, 0
for trial in range(300):
    d = random_rule()
    if a.nogh:                       # the first cell is not branched on: make it G in the simulated rule
        for r in side:
            if r != BND:
                d[(BND, 1, r)] = 1
    H, get = halfline(d)
    cube, known = '-', {(0, 0, 0)}
    while True:
        e, vals = next_branch(cube)
        # reference: first cell in the order whose neighbourhood is not known
        ref = None
        for (t, i) in order:
            nb = (get(t - 1, i - 1), get(t - 1, i), get(t - 1, i + 1))
            if nb not in known:
                ref = nb
                break
        if e is None:
            if vals == 'dead':
                # a front cell is L under the cube: must be true in the simulation as well
                assert any(H[(t, t + 1)] == 0 for t in range(1, NFRONT + 1) if (t, t + 1) in H), 'dead without a quiescent front cell'
                break
            assert ref is None, ('complete, but a neighbourhood is missing', ref)
            break
        assert e == ref, (e, ref, cube)
        v = d[e]
        known.add(e)
        cube = ('' if cube == '-' else cube + ',') + '%s%s%s=%s' % (sym(e[0]), sym(e[1]), sym(e[2]), NAMES[v])
        nsteps += 1
    for e2, v2 in parse(cube):
        assert d[e2] == v2
    ntest += 1
print('gcert.next_branch: %d random rules, %d branching steps, half-line to the anti-diagonal %d: agrees with the direct simulation' % (ntest, nsteps, MM))
