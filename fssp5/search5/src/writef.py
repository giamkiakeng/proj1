#!/usr/bin/env python3
"""writef.py OUT.cnf K N [class options of gcert.py] -- write the formula F of gcert.py (no cube) as DIMACS"""
import sys, os
out = sys.argv[1]
sys.argv = ['gcert.py', sys.argv[2], sys.argv[3], '/dev/null'] + sys.argv[4:]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gcert.py')).read().split("if __name__ == '__main__':")[0]
exec(compile(src, 'gcert-head', 'exec'))
import hashlib
with open(out, 'w') as f:
    f.write('p cnf %d %d\n' % (E.nv, NCL)); f.write(BASE)
print('%s: %d variables, %d clauses, sha256 of the clause lines %s' % (out, E.nv, NCL, hashlib.sha256(BASE.encode()).hexdigest()))
