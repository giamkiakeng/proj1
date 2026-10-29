#!/usr/bin/env python3
"""
figures.py -- the data of the figures and the rule table of the paper.

usage: python3 figures.py OUTDIR

Simulates the rule tables of ../results and writes, into OUTDIR, the files that the paper inputs:
  cells_mazoyer_line24.tex    Mazoyer's rule, line of length 24, times 0..46
  cells_mazoyer_half46.tex    Mazoyer's rule, half-line, times 0..46, cells 1..47
  cells_mazoyer_diff24.tex    where the line of length 24 and the half-line differ (Lemmas 2.1, 2.2, 2.4)
  cells_mazoyer_half90.tex    Mazoyer's rule, half-line, times 0..90
  cells_delta12_half90.tex    delta12 (uniformA_2-12.txt), half-line, times 0..90
  theta_mazoyer.dat, theta_delta12.dat
                              theta(j) observed on these half-lines (Theorem 3.4, Remark 3.5)
  cells_delta14_line14.tex    delta14, line of length 14 up to its firing time 26
  cells_delta14_line15.tex    delta14, line of length 15 up to its first F (time 22)
  cells_delta14_half63.tex    delta14, half-line, times 0..63
  cells_delta14_depth.tex     delta14, depth rows 0..24 at the times 24..130 (Lemma 5.2, Proposition 6.3)
  firstfire_<rule>.dat        relative time of the first F on the lines 15..60 of the five rules of
                              Proposition 6.3
  regions_G6.tex, regions_G4.tex
                              the cells that the formulas of Theorem 6.1 (ii) and (iii) constrain
  cells_germ10_half.tex       the half-line of the germ of Proposition 6.4 used as an example of
                              Lemma 4.1 (germ 10 of results/germs/germs_K14_surv10.txt)
  delta12_1034.png            delta12, half-line on the cells with t + i <= 1034 (Corollary 6.5)
  cells_delta12_zoom.tex      delta12, half-line on the cells 116..145 at the times 889..918
  cells_model_line15.tex      the model d14d_T7c of Section 7, line of length 15 up to time 28
  cones_R15.tex               dependency cones of the right end and of the middle cell of R_15
  tab_delta14.tex             the table of delta14
The cell (t, i) is the unit square [i-1, i] x [-t-1, -t]; consecutive cells of one row in the same
state form one rectangle, and quiescent cells (L) are left blank.  The colours stL, stG, ... are
defined in the paper.  Each part also prints a short check of what the paper says about it.
The statements of the paper are checked by check_quick.sh; this program only draws them.
"""
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results')
sys.path.insert(0, HERE)
import theta as theta_mod          # noqa: E402  (theta.py of this folder)
import firstfire                   # noqa: E402  (firstfire.py of this folder)


def load(name):
    tab = {}
    for ln in open(os.path.join(RESULTS, name) if not os.path.isabs(name) else name):
        w = ln.split()
        if not w or w[0].startswith('#') or w[0] == 'k':
            continue
        tab[tuple(w[:3])] = w[3]
    return tab


def load_germ(path, index):
    """the transitions of germ number index (1-based) of a germ list, with (L,L,L) -> L"""
    lines = [ln for ln in open(path) if ln.startswith('GERM')]
    tab = {('L', 'L', 'L'): 'L'}
    for tr in lines[index - 1].split()[1:]:
        tab[(tr[0], tr[1], tr[2])] = tr[4]
    return tab


def line(tab, n, tmax):
    """configurations of the line of length n at the times 0..tmax, or up to the first F"""
    rows = [['G'] + ['L'] * (n - 1)]
    while len(rows) <= tmax and 'F' not in rows[-1]:
        r = ['*'] + rows[-1] + ['*']
        rows.append([tab[(r[i - 1], r[i], r[i + 1])] for i in range(1, n + 1)])
    return rows


def line_full(tab, n, tmax):
    """as line(), but continues after a cell is F as long as no cell next to an F is updated"""
    rows = [['G'] + ['L'] * (n - 1)]
    while len(rows) <= tmax:
        r = ['*'] + rows[-1] + ['*']
        new = []
        for i in range(1, n + 1):
            nb = (r[i - 1], r[i], r[i + 1])
            new.append('?' if 'F' in nb or '?' in nb else tab[nb])
        rows.append(new)
    return rows


def halfline(tab, tmax):
    """configurations of the half-line at the times 0..tmax; the one at time t has t+1 cells"""
    rows = [['G']]
    for _ in range(tmax):
        r = ['*'] + rows[-1] + ['L', 'L']
        rows.append([tab[(r[i - 1], r[i], r[i + 1])] for i in range(1, len(r) - 1)])
        assert 'F' not in rows[-1]
    return rows


def at(rows, t, i):
    """state of cell i at time t; cells beyond the stored ones are quiescent"""
    return rows[t][i - 1] if i <= len(rows[t]) else 'L'


def fires(row):
    return [i + 1 for i, s in enumerate(row) if s == 'F']


def write_runs(path, grid, colour):
    """TikZ fills for a grid {t: [classes]} (cell (t, i) = grid[t][i-1]); colour maps a class to a
    colour name, or to None for a blank cell; runs of equal classes in a row form one rectangle"""
    out = []
    for t in sorted(grid):
        row = grid[t]
        i = 0
        while i < len(row):
            j = i
            while j < len(row) and row[j] == row[i]:
                j += 1
            c = colour(row[i])
            if c:
                out.append('\\fill[%s] (%d,%d) rectangle (%d,%d);' % (c, i, -t, j, -t - 1))
            i = j
    with open(path, 'w') as f:
        f.write('%% generated by figures.py; do not edit\n' + '\n'.join(out) + '\n')


def write_cells(path, rows):
    write_runs(path, dict(enumerate(rows)), lambda s: None if s == 'L' else 'st' + s)


def write_table(path, tab):
    """the table of a five-state rule: row (x, y), column z, entry delta(x, y, z)"""
    X = ['*', 'L', 'G', 'A', 'B']
    Z = ['L', 'G', 'A', 'B', '*']

    def cell(s):
        return '--' if s is None else ('$\\ast$' if s == '*' else '$\\mathsf %s$' % s)
    lines = []
    for ya, yb in (('L', 'A'), ('G', 'B')):
        for x in X:
            left = [cell(x), cell(ya)] + [cell(tab.get((x, ya, z))) for z in Z]
            right = [cell(x), cell(yb)] + [cell(tab.get((x, yb, z))) for z in Z]
            lines.append(' & '.join(left + right) + '\\\\')
        lines.append('\\midrule')
    lines[-1] = '\\bottomrule'
    with open(path, 'w') as f:
        f.write('%% generated by figures.py from results/delta14.txt; do not edit\n' + '\n'.join(lines) + '\n')


def write_png(path, width, height, pixel):
    """an RGB PNG image; pixel(x, y) returns an (r, g, b) triple"""
    raw = b''.join(b'\x00' + bytes(c for x in range(width) for c in pixel(x, y)) for y in range(height))

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)


def write_regions(path, T, N1, C):
    """the lines of lengths 2..N1 side by side, each cell coloured by the condition of G_k(T, N1, C)
    (Definition 5.4) that constrains it: (G1) complete line, (G2) early rows, (G3) return chain,
    (G5) cone of the right end (with its return chain and its firing cell), or none"""
    with open(path, 'w') as f:
        f.write('%% generated by figures.py; do not edit\n')
        x = 0
        for n in range(2, N1 + 1):
            grid = {}
            for t in range(2 * n - 1):
                row = []
                for i in range(1, n + 1):
                    tau, kap = t - (n - 1), n - i
                    if n <= T + 1:
                        c = 'stF' if t == 2 * n - 2 else 'gFull'
                    elif t + i == 2 * n - 1 and (tau <= T or (n <= C and 2 * kap <= n - 1)):
                        c = 'gReturn'
                    elif t <= n - 1 + T:
                        c = 'gEarly'
                    elif n <= C and (tau, kap) == (n - 1, 0):
                        c = 'stF'
                    elif n <= C and 0 <= kap <= tau and tau + kap <= n - 1:
                        c = 'gCone'
                    else:
                        c = 'gNone'
                    row.append(c)
                grid[t] = row
            f.write('\\begin{scope}[shift={(%d,0)}]\n' % x)
            for t in sorted(grid):
                row, i = grid[t], 0
                while i < len(row):
                    j = i
                    while j < len(row) and row[j] == row[i]:
                        j += 1
                    f.write('\\fill[%s] (%d,%d) rectangle (%d,%d);\n' % (row[i], i, -t, j, -t - 1))
                    i = j
            f.write('\\draw[grid,line width=0.25pt] (0,0) rectangle (%d,%d);\n' % (n, -(2 * n - 1)))
            f.write('\\node[font=\\scriptsize,anchor=south] at (%g,0.15) {$%d$};\n' % (n / 2, n))
            f.write('\\end{scope}\n')
            x += n + 2


def cone(n, k0):
    """the backward dependency cone, inside R_n, of the cell kappa = k0 of the firing row"""
    cells, frontier = set(), {(n - 1, k0)}
    while frontier:
        cells |= frontier
        frontier = {(t - 1, k + d) for (t, k) in frontier for d in (-1, 0, 1) if 0 <= k + d <= t - 1} - cells
    return cells


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    maz, d12, d14 = load('mazoyer6.txt'), load('uniformA_2-12.txt'), load('delta14.txt')

    # Mazoyer's rule: the line of length 24, the half-line, and where they differ
    rows = line(maz, 24, 46)
    assert len(rows) == 47 and fires(rows[46]) == list(range(1, 25)) and not any(fires(r) for r in rows[:46])
    half = halfline(maz, 46)
    agree = all(at(rows, t, i) == at(half, t, i) for t in range(47) for i in range(1, 25) if t + i <= 46)
    differ = all(at(rows, t, i) != at(half, t, i) for t in range(47) for i in range(1, 25) if t + i == 47)
    cone_lc = all(at(rows, t, i) == 'L' for t in range(47) for i in range(1, 25) if t < i - 1)
    print('Mazoyer, n = 24: fires at t = 46; quiescent where t < i-1: %s; agrees with the half-line for'
          ' t+i <= 46: %s; differs on the return chain t+i = 47: %s' % (cone_lc, agree, differ))
    write_cells(os.path.join(out, 'cells_mazoyer_line24.tex'), rows)
    write_cells(os.path.join(out, 'cells_mazoyer_half46.tex'), half)
    diff = {t: [('Q' if t < i - 1 else ('S' if at(rows, t, i) == at(half, t, i) else 'D'))
                for i in range(1, 25)] for t in range(47)}
    write_runs(os.path.join(out, 'cells_mazoyer_diff24.tex'), diff,
               lambda c: {'Q': None, 'S': 'diffSame', 'D': 'diffDiff'}[c])

    # the half-lines of Mazoyer's rule and of delta12, and theta(j)
    write_cells(os.path.join(out, 'cells_mazoyer_half90.tex'), halfline(maz, 90))
    h12 = halfline(d12, 90)
    write_cells(os.path.join(out, 'cells_delta12_half90.tex'), h12)
    left = set(h12[t][i - 1] for t in range(30, 91) for i in range(2, t // 3 - 1))
    print('delta12 half-line: states in the cells 2 <= i <= t/3 - 2 for t = 30..90: %s' % sorted(left))
    th = {}
    for name, rule, jmin in (('mazoyer', 'mazoyer6.txt', 1), ('delta12', 'uniformA_2-12.txt', 10)):
        hr = theta_mod.halfline(theta_mod.load(os.path.join(RESULTS, rule)), 700)
        th[name] = {j: theta_mod.theta(hr, j, 12)[0] for j in range(jmin, 151)}
        with open(os.path.join(out, 'theta_%s.dat' % name), 'w') as f:
            f.write('j theta\n' + ''.join('%d %d\n' % (j, v) for j, v in sorted(th[name].items())))
    print('theta(j): Mazoyer, 1 <= j <= 150: theta(j) - 2j in %s; delta12, 10 <= j <= 150: theta(j) - '
          'ceil(3j/2) in %s' % (sorted({v - 2 * j for j, v in th['mazoyer'].items()}),
                                sorted({v - (3 * j + 1) // 2 for j, v in th['delta12'].items()})))

    # delta14: the lines of lengths 14 and 15, the half-line, and the depth rows of Lemma 5.2
    r14 = line(d14, 14, 26)
    assert len(r14) == 27 and fires(r14[26]) == list(range(1, 15)) and not any(fires(r) for r in r14[:26])
    r15 = line(d14, 15, 28)
    print('delta14: line 14 fires at t = 26; line 15 first F at t = %d in cells %s'
          % (len(r15) - 1, fires(r15[-1])))
    write_cells(os.path.join(out, 'cells_delta14_line14.tex'), r14)
    write_cells(os.path.join(out, 'cells_delta14_line15.tex'), r15)
    h14 = halfline(d14, 160)
    write_cells(os.path.join(out, 'cells_delta14_half63.tex'), h14[:64])
    print('delta14 half-line, t = 3..63: cell 1 %s, cell 2 %s, cells >= 3 %s' % (
        sorted(set(h14[t][0] for t in range(3, 64))), sorted(set(h14[t][1] for t in range(3, 64))),
        sorted(set(s for t in range(3, 64) for s in h14[t][2:]))))
    D, t0, p = 24, 51, 8
    V = {t: [h14[t][t - j] for j in range(D + 1)] for t in range(D, 161)}   # V_t(j) = Phi_t(j)
    first = min(t for t in range(D, 161 - p) if all(V[u] == V[u + p] for u in range(t, 161 - p)))
    print('delta14 depth rows 0..%d: V_t = V_{t+%d} for all %d <= t <= %d: %s; least such start in the '
          'window: %d' % (D, p, t0, 160 - p, all(V[u] == V[u + p] for u in range(t0, 161 - p)), first))
    T14 = 10

    def J(n, k):        # the input word of R_n at kappa = k >= 1, from the depth rows (Section 3.3)
        return (V[n - 3 + k][2 * k - 2], V[n - 2 + k][2 * k - 1])
    same = all(J(60, k) == J(60 + p, k) for k in range(1, T14 + 2))
    print('delta14: J_60 = J_%d on 1 <= kappa <= %d (depths <= %d, times >= 58 > t0): %s'
          % (60 + p, T14 + 1, 2 * T14 + 1, same))
    assert same
    write_runs(os.path.join(out, 'cells_delta14_depth.tex'),
               {j: [V[t][j] for t in range(D, 131)] for j in range(D + 1)},
               lambda s: None if s == 'L' else 'st' + s)

    # the five rules of Proposition 6.3: relative time of the first F on the lines 15..60
    for name, T in (('delta14', 10), ('delta14b', 14), ('delta14c', 22), ('delta14d', 12), ('delta14e', 14)):
        tab = firstfire.load(os.path.join(RESULTS, name + '.txt'))
        data = [(n, firstfire.first_fire(tab, n)[0]) for n in range(15, 61)]
        assert all(tau is not None and tau <= min(T, n - 2) for n, tau in data)
        with open(os.path.join(out, 'firstfire_%s.dat' % name), 'w') as f:
            f.write('n tau\n' + ''.join('%d %d\n' % d for d in data))
        print('%s: first F on the lines 15..60 at relative times %d..%d, always <= min(%d, n-2)' % (
            name, min(tau for _, tau in data), max(tau for _, tau in data), T))

    # the cells that the formulas G_4(6, 10) and G_4(4, 10, 10) of Theorem 6.1 (ii), (iii) constrain
    write_regions(os.path.join(out, 'regions_G6.tex'), 6, 10, 7)
    write_regions(os.path.join(out, 'regions_G4.tex'), 4, 10, 10)
    print('G_4(6,10): complete lines 2..7; early rows and return chains (tau <= 6) of 8..10.  G_4(4,10,10): '
          'complete lines 2..5; early rows, return chains (tau <= 4) and right-end cones of 6..10')

    # the example of Lemma 4.1 in Proposition 6.4: germ 10 of the 14 survivors
    g = load_germ(os.path.join(RESULTS, 'germs', 'germs_K14_surv10.txt'), 10)
    hg = halfline(g, 60)
    n, s, Y = 28, 1, 19
    up = [at(hg, 2 * n - 2 - y, y) for y in range(s, Y + 1)]
    lo = [at(hg, 2 * n - 3 - y, y) for y in range(s, Y)]
    print('germ 10: on t+i = %d the cells %d..%d are %s; on t+i = %d the cells %d..%d are %s; Y - s = %d > 4^2 = 16'
          % (2 * n - 2, s, Y, ''.join(sorted(set(up))), 2 * n - 3, s, Y - 1, ''.join(sorted(set(lo))), Y - s))
    assert len(set(up)) == 1 and len(set(lo)) == 1 and Y - s > 16
    write_cells(os.path.join(out, 'cells_germ10_half.tex'), hg[:56])

    # delta12 on the cells with t + i <= 1034 (Corollary 6.5)
    h = halfline(d12, 1033)
    assert all(h[1034 - y][y - 1] == 'A' for y in range(2, 260)) and all(h[1033 - y][y - 1] == 'L' for y in range(2, 259))
    print('delta12: on t+i = 1034 the cells 2..259 are A; on t+i = 1033 the cells 2..258 are L')
    rgb = {'L': (255, 255, 255), 'G': (0x1A, 0x26, 0x38), 'A': (0x7C, 0x9D, 0xC2), 'B': (0xC6, 0xD5, 0xE6)}
    write_png(os.path.join(out, 'delta12_1034.png'), 1034, 1034,
              lambda x, y: rgb[at(h, y, x + 1)] if y + x + 1 <= 1034 else (0xF2, 0xF2, 0xF2))
    # a window of 30 x 30 cells around the cell 130 of t + i = 1034; cell (t, i) is drawn at
    # [i - 116, i - 115] x [888 - t, 889 - t], and the cells with t + i > 1034 are left blank
    zoom = {t - 889: [at(h, t, i) if t + i <= 1034 else 'X' for i in range(116, 146)] for t in range(889, 919)}
    write_runs(os.path.join(out, 'cells_delta12_zoom.tex'), zoom,
               lambda s: None if s in 'LX' else 'st' + s)

    # the model d14d_T7c of Section 7 on the line of length 15, and two dependency cones of R_15
    model = load(os.path.join(HERE, '..', 'research', 'models', 'd14d_T7c.txt'))
    m15 = line_full(model, 15, 28)
    print('model d14d_T7c, n = 15: F before time 28: %s; cells F at time 28: %s'
          % (any('F' in r for r in m15[:28]), fires(m15[28])))
    write_runs(os.path.join(out, 'cells_model_line15.tex'), dict(enumerate(m15)),
               lambda s: None if s == 'L' else ('stUnknown' if s == '?' else 'st' + s))
    mid, right = cone(15, 7), cone(15, 0)
    print('R_15: the dependency cone of the middle cell (kappa = 7) of the firing row contains %d of the %d '
          'cells; the cone of the right end contains %d' % (len(mid), 15 * 16 // 2, len(right)))
    with open(os.path.join(out, 'cones_R15.tex'), 'w') as f:
        f.write('%% generated by figures.py; do not edit\n')
        for tau in range(15):
            for kap in range(tau + 1):
                c = ('coneBoth' if (tau, kap) in mid and (tau, kap) in right else
                     'coneMid' if (tau, kap) in mid else 'coneRight' if (tau, kap) in right else 'coneNone')
                # relative cell (tau, kappa) is the cell i = 15 - kappa at time 14 + tau
                f.write('\\fill[%s] (%d,%d) rectangle (%d,%d);\n' % (c, 14 - kap, -tau, 15 - kap, -tau - 1))

    write_table(os.path.join(out, 'tab_delta14.tex'), d14)


if __name__ == '__main__':
    main()
