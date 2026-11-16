#!/usr/bin/env python3
"""count_scan.py DUMPFILE... -- the rules written by fscount -dump: for every run the deepest pool level, and for
its distinct tables the lengths that they synchronize (simulation up to 120)."""
import sys, re, collections
def sync(tab, n):
    row = ['G'] + ['L'] * (n - 1)
    for t in range(1, 2 * n - 1):
        new = []
        for i in range(n):
            e = (row[i - 1] if i > 0 else '*', row[i], row[i + 1] if i < n - 1 else '*')
            if e not in tab:
                return None
            new.append(tab[e])
        row = new
        if 'F' in row:
            return t == 2 * n - 2 and all(x == 'F' for x in row)
    return False
best = (0, None, None)
for fn in sys.argv[1:]:
    byrun = collections.defaultdict(dict)
    for l in open(fn):
        m = re.match(r'RULE run (\d+) lines (\d+)\.\.(\d+): (.*)', l)
        if not m:
            continue
        byrun[int(m.group(1))].setdefault(int(m.group(3)), set()).add(m.group(4))
    hist = collections.Counter()
    for r in sorted(byrun):
        top = max(byrun[r]); hist[top] += 1
        reach = collections.Counter()
        for ents in byrun[r][top]:
            tab = {}
            for it in ents.split():
                k, v = it.split('='); tab[(k[0], k[1], k[2])] = v
            good = [n for n in range(2, 121) if sync(tab, n) is True]
            run_len = 0
            while run_len + 2 in good:
                run_len += 1
            reach[run_len + 1] += 1
            if run_len + 1 > best[0]:
                best = (run_len + 1, ents, [n for n in good if n > run_len + 1])
        print('%s run %d: deepest pool level %d, %d distinct tables; contiguous from 2 up to: %s' % (fn, r, top, len(byrun[r][top]), dict(sorted(reach.items()))))
    print('%s: runs by deepest dumped level: %s' % (fn, dict(sorted(hist.items()))))
print('best: lines 2..%d; further lengths synchronized: %s' % (best[0], best[2]))
print('RULE', best[1])
