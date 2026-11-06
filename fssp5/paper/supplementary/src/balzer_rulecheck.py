#!/usr/bin/env python3
"""balzer_rulecheck.py -- Balzer's conditions (B1)-(B4) of Section 6.5, evaluated directly on a
five-state rule table, and the lengths whose lines it synchronizes in minimal time.

The evaluation is that of encoding_check.py (direct_B and synchronized), written from the
definitions of the paper; it does not use the formula generators.  CONDS as in balzer.py:
1234 = weak reading, 1234s = strong reading, a 'b' restricts (B2) to the neighbourhoods without a
border.

usage: python3 balzer_rulecheck.py TABLE I [NMAX]      (I: id, AB, LA, LB; NMAX default 40)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encoding_check as ec   # noqa: E402


def main():
    path, inv = sys.argv[1], sys.argv[2]
    nmax = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    tab = ec.load_table(path)
    missing = [nb for nb in ec.neighbourhoods(5) if nb not in tab]
    if missing:
        sys.exit('%s: no value for %d neighbourhoods' % (path, len(missing)))
    print('%s, I = %s:' % (os.path.basename(path), inv))
    for conds, name in (('1234s', 'strong reading'), ('1234', 'weak reading'),
                        ('1234bs', 'strong reading, (B2) only without borders'),
                        ('1234b', 'weak reading, (B2) only without borders')):
        print('  (B1)-(B4), %-43s %s' % (name + ':', ec.direct_B(tab, conds, inv)))
    sync = [n for n in range(2, nmax + 1) if ec.synchronized(tab, n)]
    print('  lines synchronized at time 2n-2 among 2 <= n <= %d: %s' % (nmax, sync))


if __name__ == '__main__':
    main()
