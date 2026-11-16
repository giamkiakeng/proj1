#!/usr/bin/env python3
"""climb.py RULE OUTDIR [--par P] [--budget C] [--dist D0,D1,...] [--mincore M] [--opts "--b3"] [--maxtop T]

Repeated neighbourhood search (lns.py).  The current rule synchronizes the lines 2..top.  For the target top+1 and for
every C = top, top-1, ..., M one call of lns.py asks for a rule that synchronizes 2..top+1 and differs from the
current rule in at most D of the transitions that it uses on the lines 2..C (D = D0, D1, ... until the conflict
budget is exhausted).  The calls run P at a time.  If some call has a model, the model with the largest top becomes
the current rule (ties: the smallest C first); otherwise the budget is multiplied by 4 (at most twice) and then the
climb stops.  Every model is kept in OUTDIR; OUTDIR/climb.log has one line per call.
"""
import argparse, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('rule'); ap.add_argument('outdir')
ap.add_argument('--par', type=int, default=3); ap.add_argument('--budget', type=int, default=400000)
ap.add_argument('--dist', default='0,1,2,3,4'); ap.add_argument('--mincore', type=int, default=6)
ap.add_argument('--opts', default='--b3'); ap.add_argument('--maxtop', type=int, default=60)
ap.add_argument('--retries', type=int, default=2)
a = ap.parse_args()
os.makedirs(a.outdir, exist_ok=True)
log = open(os.path.join(a.outdir, 'climb.log'), 'a')


def say(s):
    print(s, flush=True); log.write(s + '\n'); log.flush()


def top_of(fn):
    r = subprocess.run([sys.executable, os.path.join(here, 'lns.py'), fn, '2', '--dist', '0', '--budget', '1000'] + a.opts.split(),
                       capture_output=True, text=True)
    m = re.search(r'synchronizes 2\.\.(\d+);', r.stdout)
    return int(m.group(1))


def call(cur, N, core, budget, tag):
    out = os.path.join(a.outdir, 'N%d_core%d_%s.txt' % (N, core, tag))
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(here, 'lns.py'), cur, str(N), '--core', str(core), '--dist', a.dist,
                        '--budget', str(budget), '--out', out] + a.opts.split(), capture_output=True, text=True)
    ans = ' '.join(re.findall(r'D <= (\d+: \w+)', r.stdout)).replace(': ', ':')
    m = re.search(r'RESULT found (\d+)', r.stdout)
    d = re.search(r'distance (\d+) on U', r.stdout)
    return core, (int(m.group(1)) if m else 0), out, ans, time.time() - t0, (int(d.group(1)) if d else -1)


cur = a.rule
step = 0
while True:
    top = top_of(cur)
    say('### current rule %s synchronizes 2..%d   [%s]' % (cur, top, time.strftime('%H:%M:%S')))
    if top >= a.maxtop:
        break
    N = top + 1
    budget, best = a.budget, None
    for attempt in range(a.retries + 1):
        cores = list(range(top, a.mincore - 1, -1))
        tag = 's%d_b%d' % (step, attempt)
        with ThreadPoolExecutor(max_workers=a.par) as ex:
            res = list(ex.map(lambda c: call(cur, N, c, budget, tag), cores))
        for core, ntop, out, ans, sec, dd in res:
            say('target %d core %d budget %d: %s%s  (%.0f s)' % (N, core, budget, ans, ('  -> rule for 2..%d at distance %d: %s' % (ntop, dd, out)) if ntop else '', sec))
        good = [x for x in res if x[1]]
        if good:
            best = max(good, key=lambda x: (x[1], -x[0]))
            break
        budget *= 4
    if not best:
        say('### no model for the target %d; the climb stops at 2..%d' % (N, top))
        break
    cur = best[2]; step += 1
