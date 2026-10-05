"""Scenes 6-10: the haystack, the half-line, the two barriers, the certified four-state bound."""
import random

from manim import *

import fsspsim as sim
from common import (BAD, BG, GOOD, HL, MUTED, REGION, STATE_COLORS, TEXT, CellRow, Diagram, M,
                    NarratedScene, T, cell_rows, chapter_tag, dim_outside, legend, to_index, unit_px)

MAZ = sim.load_rule('mazoyer6')
D14 = sim.load_rule('delta14')
D12 = sim.load_rule('uniformA_2-12')


def cone_cells(n, nn=None):
    """backward cone of the relative cell (tau, kappa) = (n-1, 0) in the line of length nn >= n:
    {cell: backward depth}; the input cells (t + i in {2nn-3, 2nn-2}) are leaves"""
    nn = nn or n
    start = (nn + n - 2, nn)
    seen, frontier = {start: 0}, [start]
    while frontier:
        new = []
        for (t, i) in frontier:
            for di in (-1, 0, 1):
                c = (t - 1, i + di)
                if c[1] < 1 or c[1] > nn or c in seen:
                    continue
                seen[c] = seen[(t, i)] + 1
                if c[0] + c[1] not in (2 * nn - 3, 2 * nn - 2):
                    new.append(c)
        frontier = new
    return seen


def box(*lines, width=None, color=MUTED, font_size=30, buff=0.3):
    g = VGroup(*[l if isinstance(l, Mobject) else T(l, font_size=font_size) for l in lines])
    g.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
    fr = SurroundingRectangle(g, color=color, buff=buff, corner_radius=0.12, stroke_width=2)
    return VGroup(fr, g)


class S06_Haystack(NarratedScene):
    def construct(self):
        chap = chapter_tag('5', 'A cosmic haystack')
        rng = random.Random(5)
        with self.say('f1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            eq = M(r'\underbrace{5}_{\ast\mathsf{LGAB}}\times\underbrace{4}_{\mathsf{LGAB}}\times'
                   r'\underbrace{5}_{\ast\mathsf{LGAB}}', r'\;-\;4', r'\;-\;2', r'\;=\;94', font_size=46)
            eq.move_to(UP * 2.4)
            sub = VGroup(T(r'unused $(\ast,y,\ast)$', font_size=24, color=MUTED).next_to(eq[1], DOWN, buff=0.55),
                         T(r'fixed: $\mathsf{LLL},\mathsf{LL}\ast$', font_size=24, color=MUTED).next_to(eq[2], DOWN,
                                                                                                    buff=0.55))
            sub[0].next_to(eq[1], UP, buff=0.3)
            sub[1].next_to(eq[2], DOWN, buff=0.35).shift(RIGHT * 0.5)
            self.play(Write(eq[0]), run_time=1.6)
            self.play(Write(eq[1]), FadeIn(sub[0]), run_time=0.8)
            self.play(Write(eq[2]), FadeIn(sub[1]), run_time=0.8)
            self.play(Write(eq[3]), run_time=0.7)
            grid = VGroup(*[Square(0.3, stroke_width=0, fill_opacity=1,
                                   fill_color=STATE_COLORS[rng.choice('LGABF')]) for _ in range(94)])
            grid.arrange_in_grid(rows=4, buff=0.06).move_to(DOWN * 0.2)
            self.play(LaggedStart(*[FadeIn(g, scale=0.5) for g in grid], lag_ratio=0.01), run_time=1.5)

            def flicker(m, a):
                for sq in m:
                    if rng.random() < 0.15:
                        sq.set_fill(STATE_COLORS[rng.choice('LGABF')])
            self.play(UpdateFromAlphaFunc(grid, flicker), run_time=max(1.5, d * 0.25), rate_func=linear)
            big = 5 ** 94
            digits = str(big)
            num = VGroup(M(r'5^{94} \;=\;', font_size=40),
                         T(r'\texttt{%s}' % digits, font_size=24))
            num.arrange(RIGHT, buff=0.2).move_to(DOWN * 2.3)
            if num.width > 13.4:
                num.scale_to_fit_width(13.4)
            dl = T(r'a number with %d digits' % len(digits), font_size=30, color=HL).next_to(num, DOWN, buff=0.25)
            self.play(FadeIn(num), run_time=1.0)
            self.play(FadeIn(dl), run_time=0.6)

        with self.say('f2') as d:
            f4 = M(r'4^{43} \approx 7.7\cdot 10^{25}', font_size=46)
            f5 = M(r'5^{94} \approx 5.0\cdot 10^{65}', font_size=46)
            pair = VGroup(VGroup(T(r'four states:', font_size=34), f4).arrange(RIGHT, buff=0.3),
                          VGroup(T(r'five states:', font_size=34), f5).arrange(RIGHT, buff=0.3))
            pair.arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to(DOWN * 0.2)
            self.play(FadeOut(VGroup(grid, num, dl, sub)), FadeOut(eq), run_time=0.6)
            self.play(FadeIn(pair[0]), run_time=0.8)
            self.play(FadeIn(pair[1]), run_time=0.8)
            gap = T(r'$\approx 40$ more orders of magnitude', font_size=34, color=HL).next_to(pair, DOWN, buff=0.5)
            self.play(Write(gap), run_time=1.2)

        with self.say('f3') as d:
            self.play(FadeOut(VGroup(pair, gap)), run_time=0.6)
            # a search tree with pruning
            root = Dot(UP * 2.7, radius=0.08, color=TEXT)
            levels, edges, cuts = [[root]], VGroup(), VGroup()
            for depth in range(1, 4):
                row = []
                parents = levels[-1]
                width = 11.0
                count = len(parents) * 3
                for k, p in enumerate(parents):
                    if getattr(p, 'dead', False):
                        continue
                    for c in range(3):
                        x = -width / 2 + width * (len(row) + 0.5) / count
                        q = Dot([x, 2.7 - 1.3 * depth, 0], radius=0.06, color=TEXT)
                        q.dead = rng.random() < 0.45
                        edges.add(Line(p.get_center(), q.get_center(), stroke_width=1.5, color=MUTED))
                        if q.dead:
                            q.set_color(BAD)
                            cuts.add(M(r'\times', font_size=28, color=BAD).move_to(q))
                        row.append(q)
                levels.append(row)
            dots = VGroup(*[q for lv in levels for q in lv])
            self.play(Create(edges), FadeIn(dots), run_time=max(2.5, d * 0.12))
            self.play(FadeIn(cuts), run_time=0.9)
            how = T(r'fill entries only when needed; abandon a partial table as soon as a line misbehaves',
                    font_size=26, color=MUTED).to_edge(DOWN, buff=1.8)
            self.play(FadeIn(how), run_time=0.8)
            self.wait(max(0.1, d * 0.35 - 4.5))
            self.play(FadeOut(VGroup(edges, dots, cuts, how)), run_time=0.6)
            f_b = box(T(r'Balzer, 1967: stopped the five-state search', font_size=30),
                      T(r'after 3 hours and about $570{,}000$ partial rules', font_size=30))
            f_s = box(T(r'Sanders, 1994 (16{,}384 processors): a five-state', font_size=30),
                      T(r'search would take about $10^{16}$ times the age of the universe', font_size=30))
            VGroup(f_b, f_s).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
            self.play(FadeIn(f_b, shift=0.2 * UP), run_time=1.0)
            self.wait(max(0.1, d * 0.2 - 1.0))
            self.play(FadeIn(f_s, shift=0.2 * UP), run_time=1.0)

        with self.say('f4') as d:
            self.play(FadeOut(VGroup(f_b, f_s)), run_time=0.6)
            hay = Circle(radius=2.6, color=MUTED, fill_color=MUTED, fill_opacity=0.12).shift(LEFT * 2.5 + DOWN * 0.3)
            hl_ = T(r'all five-state rules', font_size=28, color=MUTED).next_to(hay, UP, buff=0.15)
            self.play(FadeIn(hay), FadeIn(hl_), run_time=0.8)
            nec = T(r'necessary conditions', font_size=34, color=HL).move_to(RIGHT * 3.4 + UP * 1.0)
            small = Circle(radius=0.6, color=HL, fill_color=HL, fill_opacity=0.2).move_to(hay)
            self.play(Write(nec), run_time=1.0)
            self.play(ReplacementTransform(hay.copy(), small), run_time=1.6)
            sl = T(r'what survives (not to scale)', font_size=26, color=HL).next_to(nec, DOWN, buff=0.3)
            self.play(FadeIn(sl), run_time=0.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S07_HalfLine(NarratedScene):
    def construct(self):
        chap = chapter_tag('6', 'One half-line, many triangles')
        n0 = 12
        Tm, Wm = 2 * n0 - 2, 2 * n0
        cs = int(0.24 / unit_px())
        half = Diagram(sim.halfline(D14, Tm, Wm), cell_px=cs)
        half.mob.move_to(LEFT * 3.3 + DOWN * 0.35)
        with self.say('l1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            msg = VGroup(T(r'every line behaves like an infinite line', font_size=36),
                         T(r'until the echo of its right end comes back', font_size=36)).arrange(DOWN, buff=0.2)
            self.play(Write(msg), run_time=2.4)

        with self.say('l2') as d:
            self.play(msg.animate.scale(0.75).to_edge(UP, buff=0.75), run_time=0.8)
            half.hide()
            self.add(half.mob)
            lab = T(r'the half-line (rule $\delta_{14}$)', font_size=28, color=MUTED).next_to(half.mob, RIGHT,
                                                                                           buff=0.3)
            lab.align_to(half.mob, UP)
            self.play(FadeIn(lab), half.reveal(half.rows_key(), run_time=max(3, d * 0.7)), rate_func=linear)

        line = Diagram(sim.line(D14, n0), cell_px=cs)
        line.mob.align_to(half.mob, UL)
        with self.say('l3') as d:
            tt, ii = half.grid()
            self.play(half.focus(ii <= n0, factor=0.3, run_time=1.0))
            anti = half.above_antidiag(2 * n0 - 2, n0, stroke_color=REGION)
            same = T(r'line of length $n=12$ = half-line here', font_size=28, color=REGION)
            same.next_to(lab, DOWN, buff=0.4).align_to(lab, LEFT)
            self.play(Create(anti), FadeIn(same), run_time=1.4)
            self.wait(max(0.1, d * 0.3 - 2.4))
            line.hide()
            self.add(line.mob)
            tl, il = line.grid()
            self.play(line.reveal(np.where(tl + il >= 2 * n0 - 1, tl, -1), run_time=max(2, d * 0.3)),
                      rate_func=linear)
            tri = line.triangle_R(n0, stroke_color=HL)
            trl = T(r'the reflected triangle $R_{12}$', font_size=28, color=HL).next_to(same, DOWN, buff=0.35)
            trl.align_to(lab, LEFT)
            self.play(Create(tri), FadeIn(trl), run_time=1.2)

        with self.say('l4') as d:
            inp = VGroup(line.column_region([(i, 2 * n0 - 3 - i, 2 * n0 - 2 - i) for i in range(1, n0 + 1)],
                                            stroke_color=HL, stroke_width=4, fill_color=HL, fill_opacity=0.25))
            il_ = T(r'two input anti-diagonals: $t+i=2n-3,\ 2n-2$', font_size=28, color=HL)
            il_.next_to(trl, DOWN, buff=0.35).align_to(lab, LEFT)
            self.play(FadeIn(inp), FadeIn(il_), run_time=1.4)
            self.wait(max(0.1, d * 0.35 - 1.4))
            fn = M(r'R_n \;=\; \Psi\big(\text{two anti-diagonals}\big)', font_size=34, color=TEXT)
            fn.next_to(il_, DOWN, buff=0.45).align_to(lab, LEFT)
            self.play(Write(fn), run_time=1.6)

        with self.say('l5') as d:
            self.play(FadeOut(VGroup(anti, same, trl, il_, fn, inp, tri, msg, lab)), FadeOut(line.mob),
                      half.focus(None, run_time=0.8), run_time=0.8)
            self.play(half.mob.animate.scale(0.8).to_edge(LEFT, buff=0.5).shift(DOWN * 0.2), run_time=1.0)
            hl_lab = T(r'one half-line', font_size=30, color=TEXT).next_to(half.mob, UP, buff=0.2)
            self.play(FadeIn(hl_lab), run_time=0.5)
            tris, arrows = Group(), VGroup()
            colors = [GOOD, HL, REGION]
            for k, n in enumerate((6, 9, 12)):
                rows = sim.line(D14, n)
                part = [[s if t + i + 1 >= 2 * n - 3 else None for i, s in enumerate(r)] for t, r in enumerate(rows)]
                part = part[n - 3:]
                dg = Diagram(part, cell_px=int(0.17 / unit_px()))
                tris.add(dg.mob)
                dg.color_ = colors[k]
                dg.n_ = n
                arrows.add(VGroup())
                setattr(self, 'tri%d' % k, dg)
            tris.arrange(RIGHT, buff=0.6, aligned_edge=DOWN).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.4)
            labs = VGroup()
            for k in range(3):
                dg = getattr(self, 'tri%d' % k)
                labs.add(M('R_{%d}' % dg.n_, font_size=30, color=dg.color_).next_to(dg.mob, DOWN, buff=0.2))
            self.play(LaggedStart(*[FadeIn(m, shift=0.2 * LEFT) for m in tris], lag_ratio=0.3), FadeIn(labs),
                      run_time=1.8)
            for k in range(3):
                dg = getattr(self, 'tri%d' % k)
                n = dg.n_
                hlr = half.column_region([(i, 2 * n - 3 - i, 2 * n - 2 - i) for i in range(1, n + 1)],
                                         stroke_color=dg.color_, stroke_width=3)
                arr = CurvedArrow(hlr.get_right() + RIGHT * 0.05, dg.mob.get_top() + UP * 0.05, angle=-0.6,
                                  color=dg.color_, stroke_width=3, tip_length=0.18)
                self.play(Create(hlr), Create(arr), run_time=0.9)
            self.wait(max(0.1, d * 0.4 - 3.0))
            sumy = T(r'a solution = one half-line + one triangle per length', font_size=32, color=HL)
            sumy.to_edge(DOWN, buff=0.35)
            self.play(Write(sumy), run_time=1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S08_Pumping(NarratedScene):
    def construct(self):
        chap = chapter_tag('7', 'Barrier one: pumping')
        n, nn = 12, 16
        cs = int(0.165 / unit_px())
        # a genuine minimal-time solution for both lengths (delta14 fails for n >= 15)
        A = Diagram(sim.line(MAZ, n), cell_px=cs)
        B = Diagram(sim.line(MAZ, nn), cell_px=cs)
        Group(A.mob, B.mob).arrange(RIGHT, buff=1.0, aligned_edge=UP).to_edge(LEFT, buff=0.8).shift(DOWN * 0.25)
        cA = cone_cells(n)
        with self.say('u1') as d:
            self.play(FadeIn(chap), FadeIn(A.mob), run_time=0.8)
            lA = M('n=12', font_size=28, color=MUTED).next_to(A.mob, UP, buff=0.15)
            star = Star(n=5, outer_radius=A.s * 0.75, color=HL, fill_opacity=1).move_to(A.center(2 * n - 2, n))
            self.play(FadeIn(lA), FadeIn(star, scale=2), run_time=0.9)
            fl = T(r'the right end fires at $t=2n-2$', font_size=28, color=HL).move_to(RIGHT * 3.6 + UP * 0.6)
            self.play(FadeIn(fl), run_time=0.6)
            self.wait(max(0.1, d * 0.2 - 1.5))
            tt, ii = A.grid()
            depth = np.full(tt.shape, 1e9)
            for (t, i), dd in cA.items():
                depth[t, i - 1] = dd
            maxd = max(cA.values())

            def grow(m, a):
                k = a * maxd
                mask = depth <= k + 1e-9
                A.mob.pixel_array = dim_outside(A, mask, 0.3)
            self.play(UpdateFromAlphaFunc(A.mob, grow), run_time=max(3, d * 0.4), rate_func=linear)
            inputs = [(t, i) for (t, i) in cA if t + i in (2 * n - 3, 2 * n - 2)]
            cols = sorted({i for _, i in inputs})
            reg = A.column_region([(i, min(t for t, j in inputs if j == i), max(t for t, j in inputs if j == i))
                                   for i in cols], stroke_color=HL, stroke_width=4)
            cl = T(r'its cone: about $n/2$ input cells', font_size=28, color=HL).next_to(fl, UP, buff=0.4)
            cl.align_to(fl, LEFT)
            self.play(Create(reg), FadeIn(cl), run_time=1.2)

        cB = cone_cells(n, nn)
        with self.say('u2') as d:
            self.play(FadeOut(fl), FadeOut(cl), run_time=0.5)
            lB = M("n'=16", font_size=28, color=MUTED).next_to(B.mob, UP, buff=0.15)
            self.play(FadeIn(B.mob), FadeIn(lB), run_time=0.9)
            tt, ii = B.grid()
            maskB = np.zeros(tt.shape, bool)
            for (t, i) in cB:
                maskB[t, i - 1] = True
            starB = Star(n=5, outer_radius=B.s * 0.75, color=BAD, fill_opacity=1).move_to(B.center(nn + n - 2, nn))
            self.play(B.focus(maskB, factor=0.3, run_time=1.4), FadeIn(starB, scale=2))
            same = T(r"same relative position, at time $n'+n-2<2n'-2$", font_size=28)
            same.move_to(RIGHT * 3.7 + DOWN * 0.6)
            self.play(FadeIn(same), run_time=0.8)
            self.wait(max(0.1, d * 0.45 - 3.6))
            inputsB = [(t, i) for (t, i) in cB if t + i in (2 * nn - 3, 2 * nn - 2)]
            colsB = sorted({i for _, i in inputsB})
            regB = B.column_region([(i, min(t for t, j in inputsB if j == i), max(t for t, j in inputsB if j == i))
                                    for i in colsB], stroke_color=HL, stroke_width=4)
            self.play(Create(regB), run_time=0.9)
            iff = VGroup(T(r'same input on the cone $\Rightarrow$', font_size=28, color=BAD),
                         T(r'the longer line fires \emph{too early}', font_size=28, color=BAD)).arrange(DOWN, buff=0.1)
            iff.next_to(same, DOWN, buff=0.35)
            self.play(FadeIn(iff), Indicate(starB, color=BAD, scale_factor=1.8), run_time=1.4)

        with self.say('u3') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            lem = box(T(r"\textbf{Pumping lemma.} Let $\delta$ be a minimal-time solution and $4\le n<n'$.",
                        font_size=32),
                      T(r"Then the input words $J_n$ and $J_{n'}$ differ on the cone of the right end of $R_n$.",
                        font_size=32), color=HL)
            lem.move_to(UP * 1.2)
            self.play(Create(lem[0]), FadeIn(lem[1]), run_time=1.6)
            self.wait(max(0.1, d * 0.4 - 1.6))
            only = T(r'a condition on the half-line alone: no triangle has to be computed', font_size=30,
                     color=MUTED).next_to(lem, DOWN, buff=0.6)
            self.play(FadeIn(only), run_time=1.0)

        # the half-line in the frame of the front: row j = depth j behind the front, columns = time
        Tm = 56
        h = sim.halfline(MAZ, Tm, Tm + 2)
        J = 24
        rows = [[(h[t][t - j] if j <= t else None) for t in range(Tm + 1)] for j in range(J + 1)]
        F = Diagram(rows, cell_px=int(0.16 / unit_px()))
        F.mob.move_to(UP * 0.0)
        with self.say('u4') as d:
            self.play(FadeOut(VGroup(lem, only)), run_time=0.6)
            ttl = T(r'riding with the front: row $j$ = the cell at depth $j$ behind the front', font_size=30)
            ttl.to_edge(UP, buff=0.55).shift(RIGHT * 1.6)
            F.hide()
            self.add(F.mob)
            ax_t = Arrow(F.corner(0, 1) + UP * 0.3, F.corner(0, 1) + UP * 0.3 + RIGHT * 2.0, buff=0, color=MUTED,
                         stroke_width=3)
            ax_tl = T('time', font_size=24, color=MUTED).next_to(ax_t, UP, buff=0.08)
            ax_j = Arrow(F.corner(0, 1) + LEFT * 0.3, F.corner(10, 1) + LEFT * 0.3, buff=0, color=MUTED,
                         stroke_width=3)
            ax_jl = T('depth', font_size=24, color=MUTED).next_to(ax_j, LEFT, buff=0.08)
            self.play(FadeIn(ttl), GrowArrow(ax_t), FadeIn(ax_tl), GrowArrow(ax_j), FadeIn(ax_jl), run_time=1.0)
            tt, jj = F.grid()
            self.play(F.reveal(tt.astype(float), run_time=max(3, d * 0.3)), rate_func=linear)
            # periodic tails: theta(j) in {2j+1, 2j+2} (checked numerically for j < 120)
            per = np.zeros(tt.shape, bool)
            for j in range(J + 1):
                r = [h[t][t - j] for t in range(j, Tm + 1)]
                k = len(r) - 1
                while k - 3 >= 0 and r[k - 3] == r[k]:
                    k -= 1
                per[j, j + k - 2:] = True
            per &= ~(F.idx == 7)
            self.wait(max(0.1, d * 0.2 - 1.0))
            self.play(F.focus(per, factor=0.3, run_time=1.4))
            pl = T(r'each row eventually repeats', font_size=28, color=HL).next_to(F.mob, DOWN, buff=0.3)
            self.play(FadeIn(pl), run_time=0.7)
            self.wait(max(0.1, d * 0.15 - 0.7))
            idea = T(r'if the cone only met periodic parts, the lengths $n$ and $n+P$ would look alike',
                     font_size=28, color=BAD).next_to(pl, DOWN, buff=0.2)
            self.play(FadeIn(idea), run_time=1.0)

        with self.say('u5') as d:
            self.play(FadeOut(VGroup(pl, idea, ttl)), F.focus(None, run_time=0.6),
                      Group(F.mob, ax_t, ax_tl, ax_j, ax_jl).animate.shift(UP * 0.45), run_time=0.8)
            thm = box(T(r'\textbf{Theorem (speed-$\tfrac13$ barrier).} In every minimal-time solution,',
                        font_size=30),
                      M(r'\limsup_{j\to\infty}\ \theta(j)/j\ \ge\ 3/2,', font_size=34),
                      T(r'where row $j$ is periodic from time $\theta(j)$ on: the non-periodic part', font_size=30),
                      T(r'reaches the line $i=t/3$.', font_size=30), color=HL)
            thm.scale(0.8).to_edge(DOWN, buff=0.2)
            bar = Line(F.corner(0, 1), F.corner(J + 1, 1 + 1.5 * (J + 1)), color=HL, stroke_width=4)
            bl = M(r'\theta=\tfrac32 j', font_size=28, color=HL).next_to(bar.get_end(), RIGHT, buff=0.1)
            self.play(Create(bar), FadeIn(bl), run_time=1.2)
            self.play(FadeIn(thm, shift=0.2 * UP), run_time=1.2)

        with self.say('u6') as d:
            maz = Line(F.corner(0, 1), F.corner(J + 1, 1 + 2 * (J + 1)), color=GOOD, stroke_width=4)
            ml = M(r'\theta\approx 2j', font_size=28, color=GOOD).next_to(maz.get_end(), RIGHT, buff=0.1)
            self.play(Create(maz), FadeIn(ml), run_time=1.2)
            note = T(r"Mazoyer's rule: every row $j<700$ is periodic from time $2j+1$ or $2j+2$", font_size=28,
                     color=GOOD).next_to(F.mob, UP, buff=0.25)
            self.play(FadeIn(note), run_time=0.8)
            self.wait(max(0.1, d * 0.3 - 2.0))
            # back to the usual coordinates
            self.play(FadeOut(Group(F.mob, bar, bl, maz, ml, thm, ax_t, ax_tl, ax_j, ax_jl)), FadeOut(note),
                      run_time=0.8)
            H = Diagram(sim.halfline(MAZ, 90, 92), height=6.6)
            H.mob.move_to(LEFT * 2.2 + DOWN * 0.3)
            self.play(FadeIn(H.mob), run_time=0.8)
            l2 = DashedLine(H.corner(0, 1), H.corner(H.T, 1 + H.T / 2), color=GOOD, stroke_width=4)
            l3 = DashedLine(H.corner(0, 1), H.corner(H.T, 1 + H.T / 3), color=HL, stroke_width=4)
            t2 = M(r'i=t/2', font_size=30, color=GOOD).next_to(l2.get_end(), DOWN, buff=0.1)
            t3 = M(r'i=t/3', font_size=30, color=HL).next_to(l3.get_end(), DOWN, buff=0.1).shift(LEFT * 0.3)
            self.play(Create(l2), FadeIn(t2), Create(l3), FadeIn(t3), run_time=1.4)
            exp = VGroup(T(r'periodic zone behind the front', font_size=28, color=GOOD),
                         T(r'ends at speed $\tfrac12$:', font_size=28, color=GOOD),
                         T(r'comfortably within the bound', font_size=28, color=TEXT)).arrange(DOWN, buff=0.12,
                                                                                              aligned_edge=LEFT)
            exp.move_to(RIGHT * 4.0 + UP * 0.5)
            self.play(FadeIn(exp), run_time=1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S09_LeftBorder(NarratedScene):
    def construct(self):
        chap = chapter_tag('8', 'Barrier two: the left border')
        n = 14
        rows = sim.line(D14, n)                      # rows 0..26
        t0, W = 13, 9
        crop = [r[:W] for r in rows[t0:]]
        C = Diagram(crop, cell_px=int(0.4 / unit_px()))
        C.mob.move_to(LEFT * 3.0 + DOWN * 0.2)

        def chain(c, color, width=5):
            pts = [C.center(2 * n - 2 + c - i - t0, i) for i in range(max(1, c), W + 1)
                   if 0 <= 2 * n - 2 + c - i - t0 < C.T]
            return VMobject(color=color, stroke_width=width).set_points_as_corners(pts)

        with self.say('e1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            lab = T(r'the lower left corner of the line of length $n=14$', font_size=28, color=MUTED)
            lab.next_to(C.mob, UP, buff=0.25)
            self.play(FadeIn(C.mob), FadeIn(lab), run_time=1.0)
            border = DashedLine(C.corner(0, 1) + LEFT * 0.05, C.corner(C.T, 1) + LEFT * 0.05, color=BAD,
                                stroke_width=3)
            self.play(Create(border), run_time=0.6)
            wave = chain(1, BAD, 6)
            wl = T(r'the reflected wave arrives last', font_size=28, color=BAD).move_to(RIGHT * 3.2 + UP * 2.0)
            self.play(Create(wave), FadeIn(wl), run_time=1.4)
            self.wait(max(0.1, d * 0.3 - 3.6))
            inputs = VGroup(chain(-1, HL, 7), chain(0, HL, 7))
            il = T(r'input anti-diagonals: what the half-line stored', font_size=28, color=HL)
            il.next_to(wl, DOWN, buff=0.35)
            self.play(Create(inputs), FadeIn(il), run_time=1.4)
            band = VGroup(*[chain(c, REGION, 3) for c in (2, 3, 4)])
            bl = T(r'a narrow band of chains behind the wave', font_size=28, color=REGION).next_to(il, DOWN, buff=0.35)
            self.play(Create(band), FadeIn(bl), run_time=1.4)
            fire = SurroundingRectangle(Group(*[Square(C.s).move_to(C.center(C.T - 1, i)) for i in range(1, W + 1)]),
                                        color=TEXT, buff=0.02, stroke_width=3)
            fl = T(r'and every cell must fire exactly at $t=2n-2$', font_size=28).next_to(bl, DOWN, buff=0.35)
            self.play(Create(fire), FadeIn(fl), run_time=1.2)

        with self.say('e2') as d:
            self.play(FadeOut(Group(C.mob, lab, border, wave, wl, inputs, il, band, bl, fire, fl)), run_time=0.7)
            rng = random.Random(3)
            pal = [STATE_COLORS[s] for s in 'LGAB']
            period = ['A', 'L']
            K = 13
            slices = VGroup()
            states = []
            for y in range(K):
                if y < 6:
                    st = [rng.choice(pal) for _ in range(4)]
                else:
                    st = states[y - 2]                   # eventually periodic with period 2
                states.append(st)
                stack = VGroup(*[Square(0.36, stroke_width=0, fill_color=c, fill_opacity=1) for c in st])
                stack.arrange(DOWN, buff=0.05)
                inp = VGroup(*[Square(0.36, stroke_width=2, stroke_color=HL, fill_color=STATE_COLORS[s],
                                      fill_opacity=1) for s in (period[y % 2], period[(y + 1) % 2])])
                inp.arrange(DOWN, buff=0.05)
                slices.add(VGroup(inp, stack).arrange(DOWN, buff=0.18))
            slices.arrange(LEFT, buff=0.22).move_to(DOWN * 0.1)
            cap = T(r'schematic: slices of the band, read from right to left', font_size=26, color=MUTED)
            cap.to_edge(UP, buff=0.9)
            il2 = T(r'periodic input', font_size=26, color=HL).next_to(slices, LEFT, buff=0.3).align_to(slices, UP)
            bl2 = T(r'band state', font_size=26, color=REGION).next_to(slices, LEFT, buff=0.3).shift(DOWN * 0.45)
            self.play(FadeIn(cap), FadeIn(il2), FadeIn(bl2), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(s, shift=0.1 * LEFT) for s in slices], lag_ratio=0.12),
                      run_time=max(3, d * 0.3))
            a, b = slices[6], slices[8]
            ra = SurroundingRectangle(a, color=BAD, buff=0.06)
            rb = SurroundingRectangle(b, color=BAD, buff=0.06)
            loop = CurvedArrow(rb.get_top() + UP * 0.05, ra.get_top() + UP * 0.05, angle=-1.0, color=BAD,
                               stroke_width=3)
            pig = T(r'finitely many band states: one must repeat (pigeonhole)', font_size=28, color=BAD)
            pig.next_to(slices, DOWN, buff=0.5)
            self.play(Create(ra), Create(rb), Create(loop), FadeIn(pig), run_time=1.4)
            self.wait(max(0.1, d * 0.2 - 1.4))
            then = VGroup(T(r'then it cannot tell where it is,', font_size=28),
                          T(r'and some cell near the border fires at the wrong time', font_size=28)).arrange(DOWN, buff=0.1)
            then.next_to(pig, DOWN, buff=0.25)
            self.play(FadeIn(then), run_time=1.0)

        with self.say('e3') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.6)
            lem = box(T(r'\textbf{Left-border lemma.} If $\delta$ has $k$ states and synchronizes the line of length $n$',
                        font_size=30),
                      T(r'at time $2n-2$, and its two input anti-diagonals are $L$-periodic on the cells', font_size=30),
                      T(r'$s\le y\le Y$, then', font_size=30),
                      M(r'Y-s\ \le\ (k-1)^{2s}\,L .', font_size=40), color=HL)
            lem[1][-1].shift(RIGHT * 4)
            lem.move_to(UP * 0.4)
            self.play(Create(lem[0]), FadeIn(lem[1]), run_time=1.6)

        with self.say('e4') as d:
            self.play(lem.animate.scale(0.62).to_edge(UP, buff=0.7).to_edge(LEFT, buff=0.5), run_time=0.8)
            thm = box(T(r'\textbf{Theorem.} The half-line of a minimal-time solution is not periodic', font_size=30),
                      T(r'in any wedge $\{s\le i\le\alpha t,\ t\ge t_0\}$ at the left border.', font_size=30),
                      T(r'\textbf{Corollary.} It is never eventually regular.', font_size=30), color=HL)
            thm.scale(0.8).next_to(lem, DOWN, buff=0.4).align_to(lem, LEFT)
            self.play(Create(thm[0]), FadeIn(thm[1]), run_time=1.6)
            self.wait(max(0.1, d * 0.35 - 2.4))
            H = Diagram(sim.halfline(MAZ, 100, 102), height=5.6)
            H.mob.to_edge(RIGHT, buff=0.5).shift(DOWN * 0.6)
            self.play(FadeIn(H.mob), run_time=0.8)
            tt, ii = H.grid()
            self.play(H.focus(ii <= tt / 4 + 2, factor=0.35, run_time=1.2))
            cl = VGroup(T(r'in the classical constructions:', font_size=26, color=MUTED),
                        T(r'ever slower signals, recursive division points,', font_size=26),
                        T(r'piling up at the border', font_size=26)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            cl.next_to(thm, DOWN, buff=0.5).align_to(thm, LEFT)
            self.play(FadeIn(cl), run_time=1.0)

        with self.say('e5') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            T12 = 150
            H = Diagram(sim.halfline(D12, T12, T12 + 2), height=5.8)
            H.mob.to_edge(LEFT, buff=0.5).shift(DOWN * 0.2)
            lab = T(r'the half-line of $\delta_{12}$ and $\delta_{13}$', font_size=30)
            lab.next_to(H.mob, RIGHT, buff=0.5).align_to(H.mob, UP)
            H.hide()
            self.add(H.mob)
            self.play(FadeIn(lab), H.reveal(H.rows_key(), run_time=max(3, d * 0.12)), rate_func=linear)
            parts = VGroup(T(r'front and wake of \textsf{G}', font_size=28, color=STATE_COLORS['G']),
                           T(r'boundary of speed exactly $\tfrac13$', font_size=28, color=HL),
                           T(r'periodic pattern of \textsf{A} and \textsf{L}', font_size=28,
                             color=STATE_COLORS['A'])).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
            parts.next_to(lab, DOWN, buff=0.4)
            l3 = DashedLine(H.corner(0, 1), H.corner(H.T, 1 + H.T / 3), color=HL, stroke_width=4)
            for k, p in enumerate(parts):  # noqa: B007
                self.play(FadeIn(p, shift=0.1 * RIGHT), *( [Create(l3)] if k == 1 else []), run_time=0.9)
            self.wait(max(0.1, d * 0.12 - 1.0))
            ok = T(r'barrier one: passes, exactly at the limit', font_size=28, color=GOOD).next_to(parts, DOWN,
                                                                                                buff=0.45)
            ok.align_to(parts, LEFT)
            self.play(FadeIn(ok), run_time=0.8)
            self.wait(max(0.1, d * 0.1 - 0.8))
            wedge = Polygon(H.corner(30, 2), H.corner(H.T, 2), H.corner(H.T, 2 + 0.28 * H.T),
                            color=BAD, stroke_width=3, fill_color=BAD, fill_opacity=0.25)
            bad = T(r'barrier two: periodic in a wedge at the border', font_size=28, color=BAD).next_to(ok, DOWN,
                                                                                                     buff=0.3)
            bad.align_to(parts, LEFT)
            self.play(FadeIn(wedge), FadeIn(bad), run_time=1.2)
            self.wait(max(0.1, d * 0.1 - 1.2))
            calc = VGroup(T(r'line of length $n=518$ ($k=5$, $s=2$, $L=1$):', font_size=26),
                          T(r'cells $2,\dots,259$ periodic on both input anti-diagonals', font_size=26),
                          M(r'\text{lemma: } Y-s\;\le\;(k-1)^{2s}L\;=\;4^4\;=\;256', font_size=30),
                          M(r'\text{but } Y-s\;=\;259-2\;=\;257', font_size=30, color=BAD))
            calc.arrange(DOWN, buff=0.18, aligned_edge=LEFT).next_to(bad, DOWN, buff=0.45).align_to(parts, LEFT)
            self.play(FadeIn(calc[0]), run_time=0.8)
            self.play(FadeIn(calc[1]), run_time=0.8)
            self.play(Write(calc[2]), run_time=1.3)
            self.play(Write(calc[3]), run_time=1.0)
            cross = M(r'\times', font_size=44, color=BAD).next_to(calc[3], RIGHT, buff=0.3)
            self.play(FadeIn(cross, scale=1.5), run_time=0.6)
            self.wait(max(0.1, d * 0.12 - 0.6))
            dead = T(r'no completion of this half-line is a solution', font_size=30, color=BAD)
            dead.next_to(calc, DOWN, buff=0.4).align_to(parts, LEFT)
            self.play(Write(dead), run_time=1.2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S10_FourStates(NarratedScene):
    def construct(self):
        chap = chapter_tag('9', 'Four states, with a certificate')
        with self.say('r1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            vars_ = box(T(r'variables:', font_size=30, color=HL),
                        M(r'x_{e,d}\;\equiv\;\delta(e)=d', font_size=34),
                        M(r'c_{n,t,i,s}\;\equiv\;C_n(t,i)=s', font_size=34), color=MUTED)
            cls = box(T(r'clauses:', font_size=30, color=HL),
                      T(r'every cell follows the rule', font_size=28),
                      T(r'every line of length $n\in\{2,\dots,9\}$ fires at exactly $2n-2$', font_size=28),
                      T(r'no cell fires earlier; quiescence', font_size=28),
                      T(r'+ consequences of the barriers', font_size=28), color=MUTED)
            Group(vars_, cls).arrange(RIGHT, buff=0.6, aligned_edge=UP).move_to(UP * 1.2)
            self.play(FadeIn(vars_, shift=0.2 * UP), run_time=1.2)
            self.play(FadeIn(cls, shift=0.2 * UP), run_time=1.2)
            self.wait(max(0.1, d * 0.3 - 2.4))
            real = ['p cnf 753 17605', '1 2 3 4 0', '-1 -2 0', '...',
                    '-233 -235 -240 -98 254 0', '-233 -235 -240 -99 255 0', '-233 -235 -240 -100 0', '...']
            cnf = VGroup(*[T(r'\texttt{%s}' % l.replace(' ', r'\ '), font_size=26, color=MUTED) for l in real])
            cnf.arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            cnf_box = VGroup(SurroundingRectangle(cnf, color=MUTED, buff=0.2, corner_radius=0.08, stroke_width=1.5),
                             cnf)
            cnf_box.next_to(Group(vars_, cls), DOWN, buff=0.5).shift(LEFT * 2.5)
            cl = T(r'the actual four-state formula: 753 variables, 17{,}605 clauses', font_size=26, color=MUTED)
            cl.next_to(cnf_box, RIGHT, buff=0.4).align_to(cnf_box, UP)
            self.play(FadeIn(cnf_box), FadeIn(cl), run_time=1.2)
            sat = VGroup(RoundedRectangle(width=2.6, height=1.0, corner_radius=0.15, color=HL),
                         T(r'SAT solver', font_size=32, color=HL))
            sat.next_to(cl, DOWN, buff=0.5)
            arr = Arrow(cnf_box.get_right(), sat.get_left(), color=HL, buff=0.15)
            self.play(Create(sat[0]), FadeIn(sat[1]), GrowArrow(arr), run_time=1.2)
            nos = T(r'no solution $\Rightarrow$ no such rule exists', font_size=28, color=TEXT).next_to(sat, DOWN,
                                                                                                    buff=0.25)
            self.play(FadeIn(nos), run_time=0.8)

        with self.say('r2') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.6)
            val = VGroup(T(r"Mazoyer's six-state rule", font_size=34),
                         T(r"(extracted from Jean Duprat's formal proof of its correctness)", font_size=26,
                           color=MUTED),
                         M(r'\Downarrow', font_size=40),
                         T(r'satisfies the encoding \checkmark', font_size=34, color=GOOD)).arrange(DOWN, buff=0.25)
            self.play(FadeIn(val[0]), FadeIn(val[1]), run_time=1.0)
            self.play(FadeIn(val[2]), run_time=0.5)
            self.play(FadeIn(val[3], scale=1.2), run_time=0.8)

        with self.say('r3') as d:
            self.play(FadeOut(val), run_time=0.6)
            f = M(r'\mathrm{MT}_4(\{2,\dots,9\};16)', font_size=40)
            s_ = VGroup(RoundedRectangle(width=2.8, height=1.0, corner_radius=0.15, color=HL),
                        T(r'CaDiCaL', font_size=32, color=HL))
            r_ = T(r'\textsf{UNSATISFIABLE}', font_size=36, color=BAD)
            row = VGroup(f, s_, r_).arrange(RIGHT, buff=1.0).move_to(UP * 1.6)
            a1 = Arrow(f.get_right(), s_.get_left(), buff=0.15, color=MUTED)
            a2 = Arrow(s_.get_right(), r_.get_left(), buff=0.15, color=MUTED)
            self.play(FadeIn(f), run_time=0.7)
            self.play(GrowArrow(a1), Create(s_[0]), FadeIn(s_[1]), run_time=0.9)
            tm = T(r'51 s', font_size=28, color=MUTED).next_to(s_, DOWN, buff=0.15)
            self.play(GrowArrow(a2), FadeIn(r_), FadeIn(tm), run_time=1.0)
            mean = T(r'no four-state rule synchronizes all lines of lengths $2,\dots,9$ in minimal time',
                     font_size=30).next_to(row, DOWN, buff=0.9)
            self.play(FadeIn(mean), run_time=1.0)
            self.wait(max(0.1, d * 0.4 - 3.6))
            why = T(r'but why trust a solver?', font_size=40, color=HL).next_to(mean, DOWN, buff=0.7)
            self.play(Write(why), run_time=1.2)

        with self.say('r4') as d:
            self.play(FadeOut(VGroup(mean, why, tm)), run_time=0.5)
            cert = VGroup(RoundedRectangle(width=2.6, height=1.5, corner_radius=0.1, color=TEXT),
                          T(r'LRAT proof', font_size=28),
                          T(r'177 MB', font_size=26, color=MUTED)).arrange(DOWN, buff=0.1)
            cert[1:].move_to(cert[0])
            cert[1].shift(UP * 0.2); cert[2].shift(DOWN * 0.3)
            chk = VGroup(RoundedRectangle(width=2.6, height=1.0, corner_radius=0.15, color=GOOD),
                         T(r'\texttt{lrat-check}', font_size=28, color=GOOD))
            ver = T(r'\textsf{VERIFIED}', font_size=36, color=GOOD)
            row2 = VGroup(cert, chk, ver).arrange(RIGHT, buff=1.0).next_to(row, DOWN, buff=1.3)
            down = Arrow(s_.get_bottom(), cert.get_top(), buff=0.15, color=MUTED)
            b1 = Arrow(cert.get_right(), chk.get_left(), buff=0.15, color=MUTED)
            b2 = Arrow(chk.get_right(), ver.get_left(), buff=0.15, color=MUTED)
            self.play(GrowArrow(down), Create(cert[0]), FadeIn(cert[1:]), run_time=1.2)
            lines = VGroup(*[T(r'\texttt{%s}' % l.replace(' ', r'\ '), font_size=22, color=MUTED) for l in
                             ('17606 -42 0 316 72 0', '17607 -43 0 316 73 0', '17608 -44 0 316 74 0', '...')])
            lines.arrange(DOWN, buff=0.05, aligned_edge=LEFT).next_to(cert, DOWN, buff=0.3)
            self.play(FadeIn(lines), run_time=0.8)
            self.wait(max(0.1, d * 0.25 - 2.0))
            self.play(GrowArrow(b1), Create(chk[0]), FadeIn(chk[1]), run_time=1.0)
            ct = T(r'5.7 s', font_size=28, color=MUTED).next_to(chk, DOWN, buff=0.15)
            self.play(GrowArrow(b2), FadeIn(ver, scale=1.3), FadeIn(ct), run_time=1.0)
            self.wait(max(0.1, d * 0.2 - 1.0))
            trust = T(r'trust only the formula and a small checker', font_size=32, color=HL).to_edge(DOWN, buff=0.4)
            self.play(Write(trust), run_time=1.2)

        with self.say('r5') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.6)
            tl = VGroup(*[VGroup(T(y, font_size=30, color=HL), T(w, font_size=26))
                          .arrange(DOWN, buff=0.12) for y, w in
                          (('1967', 'Balzer: search'), ('1993', r'Yun\`es: lengths $2..9$'),
                           ('1994', 'Sanders: corrected search'), ('now', 'checked certificate'))])
            tl.arrange(RIGHT, buff=0.8).move_to(UP * 1.6)
            ln = Line(tl.get_left() + LEFT * 0.3, tl.get_right() + RIGHT * 0.3, color=MUTED).next_to(tl, DOWN, buff=0.2)
            self.play(Create(ln), LaggedStart(*[FadeIn(x, shift=0.1 * UP) for x in tl], lag_ratio=0.25),
                      run_time=2.0)
            tree = VGroup()
            rng = random.Random(1)
            pts = [np.array([0, -0.4, 0])]
            nodes = VGroup(Dot(pts[0], radius=0.06, color=TEXT))
            frontier = [pts[0]]
            count = 1
            for depth in range(1, 5):
                new = []
                for p in frontier:
                    kids = 2 if depth < 4 else rng.choice([1, 2])
                    for c in range(kids):
                        if count >= 25:
                            break
                        q = p + np.array([(c - (kids - 1) / 2) * 2.4 / depth, -0.6, 0])
                        tree.add(Line(p, q, stroke_width=1.5, color=MUTED))
                        nodes.add(Dot(q, radius=0.06, color=TEXT))
                        new.append(q)
                        count += 1
                frontier = new
            tg = VGroup(tree, nodes)
            tlab = T(r'estimated size of the whole four-state search tree: about 25 nodes', font_size=28,
                     color=MUTED).next_to(tg, DOWN, buff=0.3)
            self.play(Create(tree), FadeIn(nodes), FadeIn(tlab), run_time=1.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
