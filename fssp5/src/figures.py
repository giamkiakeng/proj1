#!/usr/bin/env python3
"""figures.py -- space-time diagrams for the paper (PDF, vector with raster cells).

States: L (quiescent, background), G, A, B, C (working states, categorical hues
in fixed order), F (fire, near-black).  Palette validated with the dataviz
validator (--pairs all): blue, orange, aqua, violet.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ORDER = ['L', 'G', 'A', 'B', 'C', 'F']
COLORS = {'L': '#f4f3f0', 'G': '#2a78d6', 'A': '#eb6834', 'B': '#1baf7a',
          'C': '#4a3aa7', 'F': '#0b0b0b'}
INK = '#0b0b0b'
INK2 = '#52514e'


def load(fn):
    tab = {}
    for ln in open(fn):
        t = ln.split('#')[0].split()
        if len(t) == 4:
            tab[tuple(t[:3])] = t[3]
    return tab


def line_diagram(tab, n, T=None):
    """diagram of the line of length n up to time T (default 2n-2)"""
    T = 2 * n - 2 if T is None else T
    cur = ['G'] + ['L'] * (n - 1)
    rows = [cur]
    for t in range(T):
        nxt = []
        for i in range(n):
            l = cur[i - 1] if i > 0 else '*'
            r = cur[i + 1] if i + 1 < n else '*'
            nxt.append(tab.get((l, cur[i], r), '?'))
        cur = nxt
        rows.append(cur)
        if 'F' in cur:
            break
    return rows


def half_line(tab, T, width):
    cur = ['G'] + ['L'] * (width - 1)
    rows = [cur]
    for t in range(T):
        nxt = []
        for i in range(width):
            l = cur[i - 1] if i > 0 else '*'
            r = cur[i + 1] if i + 1 < width else 'L'
            nxt.append(tab[(l, cur[i], r)])
        cur = nxt
        rows.append(cur)
    return rows


def show(ax, rows, title, states):
    cmap = ListedColormap([COLORS[s] for s in ORDER])
    img = [[ORDER.index(s) for s in row] for row in rows]
    ax.imshow(img, cmap=cmap, vmin=0, vmax=len(ORDER) - 1, interpolation='nearest',
              aspect='equal', rasterized=True)
    ax.set_title(title, fontsize=8.5, color=INK, loc='left')
    ax.set_xlabel('cell $i$', fontsize=7.5, color=INK2)
    ax.set_ylabel('time $t$', fontsize=7.5, color=INK2)
    ax.tick_params(labelsize=6.5, colors=INK2, length=2)
    for sp in ax.spines.values():
        sp.set_color('#c3c2b7')
        sp.set_linewidth(0.6)


def main(out):
    maz = load('../results/mazoyer6.txt')
    lucky = load('../results/partial_2-9_20.txt')
    struct = load('../results/p10_rule.txt')
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.6), gridspec_kw={'wspace': 0.35})
    show(axes[0], line_diagram(maz, 40), '(a) Mazoyer, 6 states, $n=40$', 'LGABCF')
    show(axes[1], half_line(lucky, 60, 61), '(b) lucky rule, $C_\infty$', 'LGABF')
    show(axes[2], half_line(struct, 60, 61), '(c) structured rule, $C_\infty$', 'LGABF')
    handles = [Patch(facecolor=COLORS[s], edgecolor='#c3c2b7', linewidth=0.5, label=s)
               for s in ORDER]
    fig.legend(handles=handles, loc='lower center', ncol=6, fontsize=7.5, frameon=False,
               bbox_to_anchor=(0.5, -0.02), handlelength=1.2, columnspacing=1.4,
               labelcolor=INK)
    fig.savefig(out, bbox_inches='tight', dpi=300)
    fig.savefig(out.replace('.pdf', '.png'), bbox_inches='tight', dpi=160)
    print('wrote', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '../paper/fig_diagrams.pdf')


def halflines(out):
    """Figure 2: half-lines of the two architectures that reach length 13."""
    d13 = load('../results/delta13.txt')
    chaos = load('../results/delta13_chaotic.txt')
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.9), gridspec_kw={'wspace': 0.25})
    show(axes[0], half_line(d13, 120, 121),
         r'(a) $\delta_{13}$: periodic behind the speed-$1/3$ boundary', 'LGABF')
    show(axes[1], half_line(chaos, 120, 121),
         r"(b) $\delta'_{13}$: chaotic half-line", 'LGABF')
    handles = [Patch(facecolor=COLORS[s], edgecolor='#c3c2b7', linewidth=0.5, label=s)
               for s in ['L', 'G', 'A', 'B']]
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=7.5, frameon=False,
               bbox_to_anchor=(0.5, -0.01), handlelength=1.2, columnspacing=1.4,
               labelcolor=INK)
    fig.savefig(out, bbox_inches='tight', dpi=300)
    fig.savefig(out.replace('.pdf', '.png'), bbox_inches='tight', dpi=160)
    print('wrote', out)
