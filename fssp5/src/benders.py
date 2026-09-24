#!/usr/bin/env python3
"""
benders.py -- germ decomposition (logic-based Benders / CEGAR) for MT(5).

master : half-line C_inf up to anti-diagonal M, pumping pairs up to N',
         full lengths 2..N1, symmetry breaking, plus learned nogoods.
worker : the same half-line plus full lengths 2..N2 and determinacy links.

Loop: solve master -> read the germ (all transitions used by the master's
half-line) -> solve worker under the germ as assumptions.  If the worker is
UNSAT, its failed-assumption core (optionally shrunk) is a set of transitions
that no minimal-time solution can contain simultaneously; its negation is
added to master and worker.  If the worker is SAT, the full rule is simulated;
a rule passing every length up to NMAX is reported as a candidate, otherwise
the first failing length is added to the worker.

All learned clauses are implied by the definition of minimal time and the
lemmas of the paper, so master UNSAT proves that no five-state minimal-time
solution exists.  Every nogood is logged with the lengths used to derive it.

usage: benders.py N1 N2 [--M 78] [--pump 40] [--nmax 80] [--shrink 1] [--log f]
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gencnf  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def half_line_germ(E, inf_cells, model_true):
    """transitions used by the half-line cells of the model: set of T-literals"""
    W = E.W
    val = {}
    for (t, i), vs in inf_cells.items():
        for s in W:
            if vs[s] in model_true:
                val[(t, i)] = s
                break

    def v(t, i):
        if i == 0:
            return gencnf.BND
        if t == 0:
            return 1 if i == 1 else 0
        if i > t + 1:
            return 0
        return val[(t, i)]
    lits = set()
    for (t, i) in inf_cells:
        e = (v(t - 1, i - 1), v(t - 1, i), v(t - 1, i + 1))
        d = val[(t, i)]
        lits.add(E.T[e][d])
    return lits


def build(k, N, M, pump, links, lengths):
    E = gencnf.build(k, N, minf=M, pump=pump, links=links, fire_n=lengths)
    return E


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('N1', type=int)
    ap.add_argument('N2', type=int)
    ap.add_argument('--M', type=int, default=78)
    ap.add_argument('--pump', type=int, default=40)
    ap.add_argument('--nmax', type=int, default=80)
    ap.add_argument('--shrink', type=int, default=1)
    ap.add_argument('--log', default='/tmp/claude-0/benders.log')
    a = ap.parse_args()
    k = 5
    t0 = time.time()

    def say(msg):
        line = "[%8.1fs] %s" % (time.time() - t0, msg)
        print(line)
        sys.stdout.flush()
        with open(a.log, 'a') as fh:
            fh.write(line + "\n")

    # Both formulas are built by the same generator, hence share the numbering
    # of the table variables (created first, in the same order).
    Em = build(k, a.N1, a.M, a.pump, False, list(range(2, a.N1 + 1)))
    worker_lengths = list(range(2, a.N2 + 1))
    Ew = build(k, a.N2, a.M, a.pump, True, worker_lengths)
    assert all(Em.T[e] == Ew.T[e] for e in Em.T)
    inf_cells = Em.inf
    master = Solver(name='cd19', bootstrap_with=Em.clauses)
    worker = Solver(name='cd19', bootstrap_with=Ew.clauses)
    say("master vars=%d clauses=%d; worker vars=%d clauses=%d" % (
        Em.nv, len(Em.clauses), Ew.nv, len(Ew.clauses)))
    it = 0
    nog_sizes = []
    while True:
        it += 1
        if not master.solve():
            say("MASTER UNSAT after %d iterations: no 5-state minimal-time solution" % it)
            return
        m = set(x for x in master.get_model() if x > 0)
        germ = half_line_germ(Em, inf_cells, m)
        if worker.solve(assumptions=sorted(germ)):
            wm = set(x for x in worker.get_model() if x > 0)
            rule = a.log + '.rule.txt'
            with open(rule, 'w') as fh:
                gencnf.decode(Ew, wm, fh)
            r = subprocess.run([os.path.join(HERE, 'fsspcheck'), rule, '2', str(a.nmax)],
                               capture_output=True, text=True)
            out = r.stdout.strip()
            say("iter %d: germ completable for worker lengths; check: %s" % (it, out))
            if out.startswith('OK'):
                os.rename(rule, rule + '.candidate%d' % it)
                say("CANDIDATE found")
                return
            n = int(out.split('n=')[1].split(':')[0].split()[0])
            # add length n to the worker (rebuild; learned clauses are lost)
            worker_lengths.append(n)
            Ew = build(k, max(worker_lengths), a.M, a.pump, True, sorted(worker_lengths))
            worker.delete()
            worker = Solver(name='cd19', bootstrap_with=Ew.clauses)
            continue
        core = list(worker.get_core())
        if a.shrink:
            i = 0
            while i < len(core):
                trial = core[:i] + core[i + 1:]
                if not worker.solve(assumptions=trial):
                    c2 = set(worker.get_core())
                    core = [x for x in trial if x in c2]
                else:
                    i += 1
        nog = [-x for x in core]
        master.add_clause(nog)
        worker.add_clause(nog)
        nog_sizes.append(len(core))
        with open(a.log + '.nogoods', 'a') as fh:
            fh.write("%s  # worker lengths %s\n" % (" ".join(map(str, nog)), worker_lengths[-1]))
        if it % 10 == 0 or it < 20:
            say("iter %d: germ %d transitions, nogood of size %d (mean %.1f)" % (
                it, len(germ), len(core), sum(nog_sizes) / len(nog_sizes)))


if __name__ == '__main__':
    main()
