#!/usr/bin/env python3
"""fix_open.py PARTSFILE... -- collect the nodes that certtree.py reported as 'OPEN (complete, time limit)' (the
half-line is complete, the 4 s were not enough) and write those that are not yet certified in
cert/g14_parts_open.txt to cubes/g14_open_nodes.txt; other kinds of failures are printed."""
import re, sys
done = set()
try:
    for l in open('cert/g14_parts_open.txt'):
        if 'VERIFIED' in l and not l.startswith('#'):
            done.add(l.split(' | ')[0].strip())
except FileNotFoundError:
    pass
todo, other = [], []
for fn in sys.argv[1:]:
    for l in open(fn):
        if l.startswith('# cube') and 'NOT CERTIFIED' in l:
            for item in l.split('NOT CERTIFIED: ')[1].strip().split(' ;; '):
                m = re.match(r'OPEN \((complete|dead), time limit\): (\S+)', item)
                if m:
                    if m.group(2) not in done and m.group(2) not in todo:
                        todo.append(m.group(2))
                else:
                    other.append(item)
open('cubes/g14_open_nodes.txt', 'w').write(''.join(c + '\n' for c in todo))
print('open nodes already certified: %d; to do: %d; other failures: %d' % (len(done), len(todo), len(other)))
for o in other:
    print('OTHER', o[:200])
