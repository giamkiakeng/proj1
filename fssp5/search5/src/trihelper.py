#!/usr/bin/env python3
"""trihelper.py GERMFILE N CUBEFILE HELPERFILE PIDFILE [--maxdepth D] [--tlim SEC] [--solver PATH] [--tmp DIR] [--stopmin S]

Top-down companion of trisplit2.py: solves open nodes of the tree directly (one solver process from scratch, on the
formula of gfix.py full:2-N with the units of the node, time limit SEC), shallowest first.

Candidates: the open nodes of the tree recorded in CUBEFILE + HELPERFILE (nodes that are neither closed nor ancestors
of closed nodes, reached from the root by the split rule), and the children (by the same rule) of the nodes on which
the solver ran out of time, up to depth D.  Results are appended to HELPERFILE:
    U cube                  the solver proved the node unsatisfiable (a closed node for trisplit2.py --extra)
    T cube | SEC            time limit reached (the children become candidates)
    SAT cube                a model: written with its table (TABLE line) and the lines it synchronizes
After a U line for a node that took at least S seconds (--stopmin) the search of PIDFILE is stopped (its workers
first), so that a driver restarts it with the new closed node (trisplit2.py --extra HELPERFILE).  HELPERFILE is only
written by this program; CUBEFILE is only read.
"""
import argparse, os, signal, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument('germfile'); ap.add_argument('N', type=int); ap.add_argument('cubefile'); ap.add_argument('helperfile')
ap.add_argument('pidfile')
ap.add_argument('--maxdepth', type=int, default=14)
ap.add_argument('--tlim', type=int, default=1800)
ap.add_argument('--solver', default=os.environ.get('CADICAL', 'cadical'))
ap.add_argument('--tmp', default='.')
ap.add_argument('--stopmin', type=float, default=30, help='stop the search only after closing a node that took at least this many seconds')
a = ap.parse_args()
sys.argv = [sys.argv[0], a.germfile, str(a.N), a.cubefile, '/dev/null', '--enc', 'gfix', '--verdict-only']
CERTGFIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certgfix.py')
src = open(CERTGFIX).read().split("if not a.verdict_only:")[0]
H = a
__file__ = CERTGFIX
exec(compile(src, 'certgfix', 'exec'))
a = H


def read_lines(fn, tags):
    out = {t: [] for t in tags}
    if os.path.exists(fn):
        for ln in open(fn):
            if not ln.endswith('\n'):
                continue
            tag, _, rest = ln.partition(' ')
            if tag in out:
                out[tag].append(rest.split(' | ')[0].rstrip('\n'))
    return out


def stop_search():
    try:
        pid = int(open(a.pidfile).read().split()[0])
        if 'trisplit2' not in open('/proc/%d/cmdline' % pid).read():
            return
        for ch in subprocess.run(['pgrep', '-P', str(pid)], capture_output=True, text=True).stdout.split():
            os.kill(int(ch), signal.SIGTERM)
        os.kill(pid, signal.SIGTERM)
        print('# %s: stopped the search %d' % (time.strftime('%H:%M:%S'), pid), flush=True)
    except FileNotFoundError:
        pass                # the search is not running
    except Exception as e:
        print('# could not stop the search: %r' % e, flush=True)


while True:
    main = read_lines(a.cubefile, ['U'])
    hel = read_lines(a.helperfile, ['U', 'T', 'SAT'])
    if hel['SAT']:
        print('# a model was found; stopping', flush=True)
        break
    closed = set(main['U']) | set(hel['U'])
    tried = set(hel['T'])
    found, holes = leaves(closed)
    cand = []
    stack = list(holes)
    while stack:
        k = stack.pop()
        if k in closed or len(k.split(',')) > a.maxdepth:
            continue
        if k in tried:
            ch = children(parse(k))
            if ch:
                stack.extend(key_of(c) for c in ch)
            continue
        cand.append(k)
    if not cand:
        print('# no candidate up to depth %d; %d open nodes in all' % (a.maxdepth, len(holes)), flush=True)
        if not holes:
            break
        time.sleep(300)
        continue
    cand.sort(key=lambda k: (len(k.split(',')) if k else 0, k))
    k = cand[0]
    units = [T[nb][d] for nb, d in parse(k).items()]
    cnf = os.path.join(a.tmp, 'helper_%d.cnf' % os.getpid())
    with open(cnf, 'w') as fh:
        fh.write('p cnf %d %d\n' % (NV, len(CLS) + len(units)))
        fh.write(BASE)
        for u in units:
            fh.write('%d 0\n' % u)
    t0 = time.time()
    try:
        p = subprocess.run([a.solver, '-q', cnf], capture_output=True, text=True, timeout=a.tlim)
        st = [x for x in p.stdout.splitlines() if x.startswith('s ')]
        res = st[0] if st else '?'
    except subprocess.TimeoutExpired:
        res = 'timeout'
        p = None
    sec = time.time() - t0
    with open(a.helperfile, 'a') as out:
        if res == 's UNSATISFIABLE':
            out.write('# closed by a direct run of %s in %.0f s\nU %s\n' % (os.path.basename(a.solver), sec, k))
        elif res == 's SATISFIABLE':
            m = set(int(x) for ln in p.stdout.splitlines() if ln.startswith('v ') for x in ln.split()[1:] if int(x) > 0)
            tab = {nb: d for nb, vs in T.items() for d, v in vs.items() if v in m}
            tab.update(G)
            good = [n for n in range(2, 61) if line_needs(n, tab) == 'ok']
            out.write('SAT %s\n# synchronizes %s\n# TABLE %s\n' % (k, good, ' '.join('%s>%s' % (''.join(nb), d) for nb, d in sorted(tab.items()))))
        else:
            out.write('T %s | %.0f\n' % (k, sec))
    os.remove(cnf)
    print('# %s: depth %d, %s in %.0f s: %s' % (time.strftime('%H:%M:%S'), len(units), res, sec, k[:150]), flush=True)
    if res == 's UNSATISFIABLE' and sec >= a.stopmin:
        stop_search()      # only for hard nodes; the search closes easy nodes quickly by itself
