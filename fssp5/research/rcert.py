#!/usr/bin/env python3
"""rcert.py CNF ICNF P1OUT TAG LOG [first] [last] [step]   (certify the cube tree of rcube.py)
   rcert.py --final CNF ICNF P1OUT TAG LOG[,LOG...]         (compose the certificate)

The tree is rebuilt from ICNF and the relative cubes TAG_split/<path>.icnf of rcube.py: the literals of the
node 'i.k1.k2' are the top-level cube i of ICNF, then the k1-th relative cube of the split of 'i', then the
k2-th relative cube of the split of 'i.k1'.  The tree's results (P1OUT, TAG.rlog) only say which nodes are
claimed UNSAT and which are split; nothing below relies on them being correct.

Certify mode, one line per check appended to LOG (checks already VERIFIED in LOG are skipped; first, last
and step select a slice of the list of checks, so several instances can share the work):
  T ICNF h n res chk secs      the n top-level cubes cover: the CNF of their negations is unsatisfiable
  C path h n res chk secs      the n relative cubes of the split of 'path' cover, in the same sense
  L path h res chk secs        CNF + the unit clauses of the leaf 'path' is unsatisfiable
res is CaDiCaL 3.0.1's answer; chk is VERIFIED iff lrat-check (drat-trim) exits 0 and prints the line
'c VERIFIED' for CaDiCaL's text LRAT proof.  h is a hash of the checked object (the cubes of a cover; the
clauses of CNF and the literals of a leaf), so that the final mode only counts checks of the current tree.

Final mode: a node is certified if it has a VERIFIED L line, or it has a VERIFIED C line and all its
sub-cubes are certified.  If the T line is VERIFIED and every top-level cube is certified, CNF is
unsatisfiable (induction over the tree: CNF and node c unsatisfiable for every certified c; the covers make
the disjunction of the sub-cubes of a split, and of the top-level cubes, a tautology)."""
import sys, os, subprocess, tempfile, time, hashlib

CAD = os.environ.get('CADICAL') or '/home/user/tools/cadical/build/cadical'
CHK = os.environ.get('LRATCHECK') or '/home/user/tools/drat-trim/lrat-check'


def load_tree(icnf, p1, tag):
    cubes = [[int(x) for x in l.split()[1:-1]] for l in open(icnf) if l.startswith('a ')]
    st = {}
    for f in ([] if p1 == '-' else p1.split(',')):
        for l in open(f):
            p = l.split()
            if len(p) >= 2 and p[1] in ('UNSAT', 'SAT', 'UNKNOWN') and st.get(p[0]) != 'UNSAT':
                st[p[0]] = p[1]
    split = {}
    sdir = tag + '_split'
    if os.path.exists(tag + '.rlog'):
        for l in open(tag + '.rlog'):
            p = l.split()
            if p and p[0] == 'R' and st.get(p[1]) != 'UNSAT':
                st[p[1]] = p[2]
            elif p and p[0] == 'S' and os.path.exists(os.path.join(sdir, p[1] + '.icnf')):
                split[p[1]] = [[int(x) for x in l.split()[1:-1]]
                               for l in open(os.path.join(sdir, p[1] + '.icnf')) if l.startswith('a ')]
    return cubes, st, split


def walk(cubes, st, split):
    """Leaves claimed UNSAT (path, literals) and splits (path, number of relative cubes), in tree order.
    A split node is followed into its sub-cubes even if it is also claimed UNSAT (rcube.py never does both)."""
    leaves, splits = [], []
    stack = [(str(i), cubes[i]) for i in reversed(range(len(cubes)))]
    while stack:
        path, c = stack.pop()
        if path in split:
            splits.append((path, len(split[path])))
            stack.extend(reversed([('%s.%d' % (path, k), c + q) for k, q in enumerate(split[path])]))
        elif st.get(path) == 'UNSAT':
            leaves.append((path, c))
    return leaves, splits


def h_cubes(nv, cubes):
    return hashlib.sha1(('%d:' % nv + ';'.join(' '.join(map(str, q)) for q in cubes)).encode()).hexdigest()[:12]


def h_leaf(h0, lits):
    return hashlib.sha1((h0 + ':' + ' '.join(map(str, lits))).encode()).hexdigest()[:12]


def read_cnf(cnf):
    with open(cnf) as f:
        hdr = next(l for l in f if l.startswith('p cnf'))
    body = ''.join(l for l in open(cnf) if l[0] not in 'pc')
    return int(hdr.split()[2]), int(hdr.split()[3]), body, hashlib.sha1(body.encode()).hexdigest()


def run_check(cnf_path, tmp):
    """CaDiCaL with a text LRAT proof, then lrat-check; returns (res, chk)."""
    prf = os.path.join(tmp, 'f.lrat')
    r = subprocess.run([CAD, '-q', '--lrat', '--binary=false', cnf_path, prf], capture_output=True, text=True)
    res = next((l.split()[1] for l in r.stdout.splitlines() if l.startswith('s ')), 'NONE')
    chk = 'NOCHECK'
    if res == 'UNSATISFIABLE':
        c = subprocess.run([CHK, cnf_path, prf], capture_output=True, text=True)
        chk = 'VERIFIED' if c.returncode == 0 and 'c VERIFIED' in c.stdout.splitlines() else 'NOTVERIFIED'
    if os.path.exists(prf):
        os.remove(prf)
    return res, chk


def cover_cnf(fn, nv, cubes):
    with open(fn, 'w') as fo:
        fo.write('p cnf %d %d\n' % (nv, len(cubes)))
        fo.write(''.join(' '.join(str(-x) for x in q) + ' 0\n' for q in cubes))


def certify(cnf, icnf, p1, tag, logf, first, last, step):
    cubes, st, split = load_tree(icnf, p1, tag)
    leaves, splits = walk(cubes, st, split)
    done = set()
    if os.path.exists(logf):
        for l in open(logf):
            p = l.split()
            if p and p[-2] == 'VERIFIED':
                done.add((p[0], p[1], p[2]))
    nv, nc, body, h0 = read_cnf(cnf)
    checks = ([('T', icnf, h_cubes(nv, cubes), None)] + [('C', p, h_cubes(nv, split[p]), n) for p, n in splits]
              + [('L', p, h_leaf(h0, c), c) for p, c in leaves])
    checks = checks[first:last:step]
    print('%s: %d leaves, %d splits; %d checks in this slice, %d already verified'
          % (tag, len(leaves), len(splits), len(checks), sum(1 for k, p, h, _ in checks if (k, p, h) in done)),
          flush=True)
    tmp = tempfile.mkdtemp(prefix='rcert.', dir=os.path.dirname(os.path.abspath(logf)))
    fn = os.path.join(tmp, 'f.cnf')
    log = open(logf, 'a')
    t00 = time.time()
    for kind, path, h, x in checks:
        if (kind, path, h) in done:
            continue
        t0 = time.time()
        if kind == 'T':
            cover_cnf(fn, nv, cubes)
            res, chk = run_check(fn, tmp)
            line = 'T %s %s %d %s %s %.1f' % (path, h, len(cubes), res, chk, time.time() - t0)
        elif kind == 'C':
            cover_cnf(fn, nv, split[path])
            res, chk = run_check(fn, tmp)
            line = 'C %s %s %d %s %s %.1f' % (path, h, x, res, chk, time.time() - t0)
        else:
            with open(fn, 'w') as fo:
                fo.write('p cnf %d %d\n' % (nv, nc + len(x)))
                fo.write(body)
                fo.write(''.join('%d 0\n' % l for l in x))
            res, chk = run_check(fn, tmp)
            line = 'L %s %s %s %s %.1f' % (path, h, res, chk, time.time() - t0)
        log.write(line + '\n')
        log.flush()
        if chk != 'VERIFIED':
            print('FAILED:', line, flush=True)
    os.remove(fn) if os.path.exists(fn) else None
    os.rmdir(tmp)
    print('done, %.0f s' % (time.time() - t00), flush=True)


def final(cnf, icnf, p1, tag, logs):
    cubes, st, split = load_tree(icnf, p1, tag)
    nv, nc, body, h0 = read_cnf(cnf)
    ver = set()
    for logf in logs.split(','):
        for l in open(logf):
            p = l.split()
            if p and p[-2] == 'VERIFIED':
                ver.add((p[0], p[1], p[2]))
    nv_leaf = nv_cov = 0
    missing = []

    def cert(path, c):
        nonlocal nv_leaf, nv_cov
        if ('L', path, h_leaf(h0, c)) in ver:
            nv_leaf += 1
            return True
        if path in split and ('C', path, h_cubes(nv, split[path])) in ver:
            nv_cov += 1
            ok = True
            for k, q in enumerate(split[path]):
                ok = cert('%s.%d' % (path, k), c + q) and ok
            return ok
        missing.append(path)
        return False

    top = sum(1 for i in range(len(cubes)) if cert(str(i), cubes[i]))
    tv = ('T', icnf, h_cubes(nv, cubes)) in ver
    print('%s: top-level cover %s; %d/%d top-level cubes certified; %d verified leaf refutations, %d verified '
          'split covers; %d nodes uncertified%s'
          % (cnf, 'VERIFIED' if tv else 'NOT VERIFIED', top, len(cubes), nv_leaf, nv_cov, len(missing),
             ('; first: ' + ' '.join(missing[:8])) if missing else ''))
    if tv and top == len(cubes):
        print('CERTIFIED: %s is unsatisfiable' % cnf)


if __name__ == '__main__':
    if sys.argv[1] == '--final':
        final(*sys.argv[2:7])
    else:
        a = sys.argv[1:]
        certify(a[0], a[1], a[2], a[3], a[4], int(a[5]) if len(a) > 5 else 0,
                int(a[6]) if len(a) > 6 else None, int(a[7]) if len(a) > 7 else 1)
