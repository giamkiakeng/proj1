#!/usr/bin/env python3
"""farm.py POOLDIR [--par P] [--budget C] [--sched C:D,C:D,...] [--opts "--b3"] [--all M] [--mintop T]

Best-first search over rules with the neighbourhoods of lns2.py.

POOLDIR/rules holds rule files (seeds are put there by hand).  A rule with top t (it synchronizes 2..t, not t+1) has
one task per entry C:D of the schedule: lns2.py RULE t+1 --core C --maxd D.  Tasks of the rules with the largest top
run first, P at a time.  Every model of a task is a rule with top >= t+1; it enters the pool unless a rule with the
same transitions on its lines 2..top is there already.  POOLDIR/farm.log has one line per finished task and per new
rule; POOLDIR/done.txt lists the finished tasks, so that a restart continues.
"""
import argparse, glob, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('pooldir'); ap.add_argument('--par', type=int, default=3)
ap.add_argument('--budget', type=int, default=20000); ap.add_argument('--sched', default='12:2,9:2,12:3')
ap.add_argument('--opts', default='--b3'); ap.add_argument('--all', type=int, default=3)
ap.add_argument('--mintop', type=int, default=0, help='rules with a smaller top are not expanded')
ap.add_argument('--maxtop', type=int, default=99)
a = ap.parse_args()
RD = os.path.join(a.pooldir, 'rules'); TD = os.path.join(a.pooldir, 'tmp'); LD = os.path.join(a.pooldir, 'logs')
for d in (RD, TD, LD):
    os.makedirs(d, exist_ok=True)
log = open(os.path.join(a.pooldir, 'farm.log'), 'a')
sched = [tuple(map(int, x.split(':'))) for x in a.sched.split(',')]


def say(s):
    s = time.strftime('%H:%M:%S ') + s
    print(s, flush=True); log.write(s + '\n'); log.flush()


def load(fn):
    tab = {}
    for l in open(fn):
        l = l.split('#')[0].strip()
        if not l:
            continue
        if l.startswith('RULE'):
            l = l.split(':', 1)[1].strip()
        p = l.split()
        if p[0] == 'k':
            continue
        if '=' in p[0]:
            for it in p:
                e, d = it.split('=')
                tab[(e[0], e[1], e[2])] = d
        else:
            tab[(p[0], p[1], p[2])] = p[3]
    tab.setdefault(('L', 'L', 'L'), 'L'); tab.setdefault(('L', 'L', '*'), 'L')
    return tab


def run(tab, n, used):
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        es = [(row[i - 1] if i > 0 else '*', row[i], row[i + 1] if i < n - 1 else '*') for i in range(n)]
        if any(e not in tab for e in es):
            return False
        used.update(es)
        row = [tab[e] for e in es]
        if 'F' in row:
            return t == 2 * n - 2 and all(x == 'F' for x in row)
    return False


def info(fn):
    """(top, key): the largest t with 2..t synchronized, and the transitions used by the lines 2..t"""
    tab = load(fn); used = set(); n = 2
    while True:
        u = set()
        if not run(tab, n, u):
            break
        used |= u; n += 1
    return n - 1, tuple(sorted((e, tab[e]) for e in used))


pool = {}        # name -> top
keys = {}
for fn in sorted(glob.glob(os.path.join(RD, '*.txt'))):
    t, key = info(fn)
    name = os.path.basename(fn)
    if key in keys:
        say('duplicate in the pool: %s = %s' % (name, keys[key])); continue
    keys[key] = name; pool[name] = t
say('pool: %d rules; tops %s' % (len(pool), {t: sum(1 for v in pool.values() if v == t) for t in sorted(set(pool.values()))}))
donef = os.path.join(a.pooldir, 'done.txt')
done = set()
if os.path.exists(donef):
    done = set(tuple(l.split()[:3]) for l in open(donef) if l.strip())
nextid = 1 + max([int(m.group(1)) for m in (re.match(r'r(\d+)\.txt', x) for x in pool) if m] + [0])
running = {}


def task(name, C, D):
    t = pool[name]; N = t + 1
    tag = '%s_c%dd%d' % (name[:-4], C, D)
    pref = os.path.join(TD, tag)
    out = os.path.join(LD, tag + '.out')
    t0 = time.time()
    with open(out, 'w') as f:
        subprocess.run([sys.executable, os.path.join(here, 'lns2.py'), os.path.join(RD, name), str(N), '--core', str(min(C, t)), '--maxd', str(D),
                        '--budget', str(a.budget), '--all', str(a.all), '--outprefix', pref] + a.opts.split(), stdout=f, stderr=subprocess.STDOUT)
    res = [l for l in open(out) if l.startswith('RESULT')]
    return name, C, D, N, (res[0].strip() if res else 'NO RESULT'), sorted(glob.glob(pref + '_*_top*.txt')), time.time() - t0


def pending():
    c = [(-(pool[n]), j, n) for n in pool for j, (C, D) in enumerate(sched)
         if a.mintop <= pool[n] < a.maxtop and (n, str(sched[j][0]), str(sched[j][1])) not in done and (n, j) not in running.values()]
    return sorted(c)


with ThreadPoolExecutor(max_workers=a.par) as ex:
    while True:
        p = pending()
        while p and len(running) < a.par:
            _, j, n = p.pop(0)
            fut = ex.submit(task, n, sched[j][0], sched[j][1])
            running[fut] = (n, j)
        if not running:
            break
        fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
        for fut in fin:
            del running[fut]
            name, C, D, N, res, files, sec = fut.result()
            done.add((name, str(C), str(D)))
            with open(donef, 'a') as f:
                f.write('%s %d %d %d %s\n' % (name, C, D, N, res))
            say('%s (top %d) target %d core %d maxd %d: %s  (%.0f s)' % (name, pool[name], N, C, D, res, sec))
            for fn in files:
                t, key = info(fn)
                if key in keys:
                    os.remove(fn); continue
                new = 'r%04d.txt' % nextid; nextid += 1
                os.rename(fn, os.path.join(RD, new))
                keys[key] = new; pool[new] = t
                say('   NEW RULE %s: synchronizes 2..%d   (from %s, core %d, maxd %d)' % (new, t, name, C, D))
say('no task left; pool: %d rules; tops %s' % (len(pool), {t: sum(1 for v in pool.values() if v == t) for t in sorted(set(pool.values()))}))
