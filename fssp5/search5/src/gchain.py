#!/usr/bin/env python3
"""gchain.py -- raise N until the tree of gcert.py closes.

    gchain.py K OUTPREFIX N0 NMAX [--workers W] [--tlim T] [--maxtime SEC] -- [class options of gcert.py]

Level N0: gcert.py K N0 OUTPREFIX_N0.txt [options] from the root.  A node at which the formula for N is
satisfiable is recorded and not split.  If there are such nodes, level N+1 runs gcert.py K N+1 on these nodes
only (--prefixfile), and so on.  Every model of the formula F_{N+1} is a model of F_N (F_{N+1} has the clauses
of F_N for the same lines and cells, when the options include --front1 and exclude --strict), so the nodes
closed at the levels N0, ..., N are a complete case split for F_N as soon as a level has no satisfiable node:
then no rule of the class synchronizes all lines 2..N+2.  gcover.py K N FILES... (all levels) checks the split.
Interrupted levels are continued by the same command.  One summary line per level is appended to
OUTPREFIX.summary.txt."""
import os, subprocess, sys, time
args = sys.argv[1:]
if '--' in args:
    j = args.index('--'); opts = args[j + 1:]; args = args[:j]
else:
    opts = []
def opt(name, default):
    if name in args:
        j = args.index(name); v = args[j + 1]; del args[j:j + 2]; return v
    return default
workers, tlim, maxtime = opt('--workers', '3'), opt('--tlim', '4'), float(opt('--maxtime', '0'))
K, prefix, N0, NMAX = args[0], args[1], int(args[2]), int(args[3])
here = os.path.dirname(os.path.abspath(__file__))
cubes = None
summary = prefix + '.summary.txt'
def note(msg):
    with open(summary, 'a') as f:
        f.write(msg + '\n')
    print(msg, flush=True)
for N in range(N0, NMAX + 1):
    out, log = '%s_%d.txt' % (prefix, N), '%s_%d.log' % (prefix, N)
    cmd = [sys.executable, os.path.join(here, 'gcert2.py' if os.path.exists(os.path.join(here, 'gcert2.py')) else 'gcert.py'), K, str(N), out] + opts + ['--tlim', tlim, '--workers', workers]
    if cubes is not None:
        pf = '%s_%d.prefix.txt' % (prefix, N)
        with open(pf, 'w') as f:
            f.write(''.join(c + '\n' for c in cubes))
        cmd += ['--prefixfile', pf]
    t0 = time.time()
    with open(log, 'a') as lf:
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            p.wait(timeout=maxtime if maxtime else None)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, 15)
            note('N=%d: stopped after %.0f s (time limit); the level can be continued' % (N, time.time() - t0))
            break
    U = S = 0; sat, bad = [], []
    for l in open(out):
        if l.startswith('U '):
            U += 1
        elif l.startswith('S '):
            S += 1
        elif l.startswith('# SAT '):
            sat.append(l[6:].strip())
        elif l.startswith('# NOT CERTIFIED'):
            bad.append(l.strip())
    tail = open(log).read().strip().split('\n')
    finished = any(x.startswith('# done') for x in tail[-60:])
    note('N=%d: %d nodes closed, %d split, %d satisfiable, %d not certified, %.0f s%s%s' % (
        N, U, S, len(sat), len(bad), time.time() - t0, '' if cubes is None else ' (from %d nodes of level %d)' % (len(cubes), N - 1),
        '' if finished else '  [the run did not finish]'))
    if not finished or bad:
        break
    if not sat:
        note('CLOSED at N=%d: no rule of the class synchronizes all lines 2..%d' % (N, N + 2))
        break
    cubes = sat
else:
    note('NOT CLOSED up to N=%d' % NMAX)
