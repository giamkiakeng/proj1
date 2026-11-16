#!/usr/bin/env python3
"""nodecert.py K N OUTFILE CUBEFILE [class options of gcert.py] [--tlim SEC] -- certified refutation of single nodes.

For every cube of CUBEFILE (one per line: transitions xyz=d separated by commas; a leading '# SAT ' or 'U ' and
anything after ' | ' are ignored) the formula of gcert.py with the given options, for example the strict formula of
the lines 2..N, is solved with the units of the cube by CaDiCaL with an LRAT proof; lrat-check and cake_lpr check
the proof.  One line 'U cube | seconds | proof bytes | formula SHA-256 | proof SHA-256 | VERIFIED | cake_lpr ...' is
appended to OUTFILE per refuted cube; a satisfiable cube is reported as '# SAT cube' and its rule is simulated.
Use: a node that is satisfiable at the level N-1 of a tree search holds every rule of the class for the lines 2..N
(README, Proposition 7.3); refuting the strict formula of 2..N at these nodes shows that there is none.
"""
import sys, os
argv = sys.argv[1:]
tlim = '100000'
if '--tlim' in argv:
    j = argv.index('--tlim'); tlim = argv[j + 1]; del argv[j:j + 2]
K, N, out, cubefile = argv[0], argv[1], argv[2], argv[3]
here = os.path.dirname(os.path.abspath(__file__))
src_name = 'gcert3.py' if os.path.exists(os.path.join(here, 'gcert3.py')) else 'gcert.py'
sys.argv = [src_name, K, N, '/dev/null'] + argv[4:]
src = open(os.path.join(here, src_name)).read().split("if __name__ == '__main__':")[0]
exec(compile(src, 'gcert-head', 'exec'))
cubes = []
for l in open(cubefile):
    l = l.strip()
    if l.startswith('# SAT '):
        l = l[6:]
    elif l.startswith('U '):
        l = l[2:]
    elif not l or l.startswith('#'):
        continue
    cubes.append(l.split(' | ')[0].strip())
with open(out, 'a') as f:
    f.write('# nodecert.py %s\n# F: k=%s N=%s, %d variables, %d clauses, sha256 of the clause lines %s\n' % (
        ' '.join(sys.argv[1:3] + argv[4:]), K, N, E.nv, NCL, hashlib.sha256(BASE.encode()).hexdigest()))
    for cube in cubes:
        c, status, line = refute(cube, int(tlim))
        if status == 'OK':
            f.write('U ' + line + '\n'); print('refuted and verified:', cube)
        elif status == 'SAT':
            f.write('# SAT ' + cube + '\n'); print('SATISFIABLE:', cube)
        else:
            f.write('# NOT CERTIFIED (%s) %s\n' % (status, cube)); print('NOT CERTIFIED (%s): %s' % (status, cube))
        f.flush()
