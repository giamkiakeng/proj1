#!/usr/bin/env python3
"""family_max.py DUMPFILE [CORE] [TIMEOUT] -- for the deepest rule of every run in a dump of fscount: fix the
transitions that it uses in the lines 2..CORE (default 11) and enumerate all completions (fsdfs -max, class -b3s
if the rule fires from GGG, *GG, GG* only): the deepest line that a rule of this family synchronizes from 2 on."""
import sys, re, collections, subprocess, os
here = os.path.dirname(os.path.abspath(__file__))
fn = sys.argv[1]; core = int(sys.argv[2]) if len(sys.argv) > 2 else 11; tmo = int(sys.argv[3]) if len(sys.argv) > 3 else 600
byrun = collections.defaultdict(dict)
for l in open(fn):
    m = re.match(r'RULE run (\d+) lines (\d+)\.\.(\d+): (.*)', l)
    if m:
        byrun[int(m.group(1))].setdefault(int(m.group(3)), []).append(m.group(4))
for r in sorted(byrun):
    top = max(byrun[r]); tab = {}
    for it in byrun[r][top][0].split():
        k, v = it.split('='); tab[(k[0], k[1], k[2])] = v
    u = {}
    for n in range(2, min(core, top) + 1):
        row = ['G'] + ['L'] * (n - 1)
        for t in range(1, 2 * n - 1):
            es = [(row[i - 1] if i > 0 else '*', row[i], row[i + 1] if i < n - 1 else '*') for i in range(n)]
            for e in es:
                u[e] = tab[e]
            row = [tab[e] for e in es]
    fire = sorted(''.join(e) for e in tab if tab[e] == 'F')
    opts = ['-b3s'] if fire == ['*GG', 'GG*', 'GGG'] else []
    setl = ','.join(''.join(k) + '=' + v for k, v in sorted(u.items()) if k not in (('L', 'L', 'L'), ('L', 'L', '*')))
    try:
        q = subprocess.run([os.path.join(here, 'fsdfs'), '5', '44'] + opts + ['-nosym', '-set', setl, '-max'], capture_output=True, text=True, timeout=tmo)
        line = [x for x in q.stdout.split('\n') if x.startswith('nodes')]
        res = line[0] if line else '?'
        rule = [x for x in q.stdout.split('\n') if x.startswith('RULE')]
        if rule:
            open('%s.family_run%d.txt' % (fn, r), 'w').write(rule[-1] + '\n')
    except subprocess.TimeoutExpired:
        res = 'not finished in %d s' % tmo
    print('%s run %d: sampled 2..%d; core of %d transitions (lines 2..%d); all completions: %s' % (os.path.basename(fn), r, top, len(u), min(core, top), res), flush=True)
