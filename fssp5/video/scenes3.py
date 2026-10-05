"""Scenes 11-14: the five-state frontier, low-complexity half-lines, Balzer's conditions, outlook."""
from manim import *

import fsspsim as sim
from common import (BAD, BG, GOOD, HL, MUTED, REGION, STATE_COLORS, TEXT, CellRow, Diagram, M,
                    NarratedScene, T, chapter_tag, dim_outside, legend, unit_px)
from scenes2 import box

MAZ = sim.load_rule('mazoyer6')
D14 = sim.load_rule('delta14')
D12 = sim.load_rule('uniformA_2-12')


def complexity_curve(rule, M=78):
    """number of distinct neighbourhoods (other than LLL) used by the cells with t + i <= c, for c <= M"""
    h = sim.halfline(rule, M, M + 2)
    first = {}
    for t in range(1, M + 1):
        for i in range(1, M - t + 1):
            e = (h[t - 1][i - 2] if i >= 2 else '*', h[t - 1][i - 1], h[t - 1][i])
            if e != ('L', 'L', 'L'):
                first[e] = min(first.get(e, 10 ** 9), t + i)
    return [sum(1 for v in first.values() if v <= c) for c in range(M + 1)]


class S11_Frontier(NarratedScene):
    def construct(self):
        chap = chapter_tag('10', 'The five-state frontier')
        with self.say('d1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            wall = T(r'a wall of very lucky rules', font_size=52)
            self.play(Write(wall), run_time=1.4)

        ns = (10, 11, 12, 13, 14)
        cs = int(0.19 / unit_px())
        dgs = [Diagram(sim.line(D14, k), cell_px=cs) for k in ns]
        grp = Group(*[g.mob for g in dgs]).arrange(RIGHT, buff=0.3, aligned_edge=UP).move_to(DOWN * 0.1)
        with self.say('d2') as d:
            self.play(wall.animate.scale(0.6).to_edge(UP, buff=0.3).shift(RIGHT * 2.5), run_time=0.7)
            name = T(r'the five-state rule $\delta_{14}$', font_size=30, color=MUTED).next_to(grp, UP, buff=0.35)
            self.play(FadeIn(name), run_time=0.5)
            base = grp.get_bottom()[1] - 0.35
            fracs = (0.05, 0.42, 0.58, 0.72, 0.84)
            t0 = self.renderer.time
            for k, (g, n) in enumerate(zip(dgs, ns)):
                wait = t0 + fracs[k] * d - self.renderer.time
                if wait > 0.05:
                    self.wait(wait)
                g.hide()
                self.add(g.mob)
                lab = VGroup(M('n=%d' % n, font_size=28), M(r'\checkmark', font_size=30, color=GOOD))
                lab.arrange(RIGHT, buff=0.15).move_to([g.mob.get_center()[0], base, 0])
                self.play(g.reveal(g.rows_key(), run_time=1.6 if k == 0 else 1.1), FadeIn(lab), rate_func=linear)
                if k == 0:
                    ft = M(r't=18', font_size=26, color=HL).next_to(g.mob, LEFT, buff=0.12).align_to(g.mob, DOWN)
                    self.play(FadeIn(ft), run_time=0.5)

        with self.say('d3') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m not in (chap, wall)])), run_time=0.7)
            rows = sim.line(D14, 15, 40)                  # stops at the first firing row, t = 22
            pad = rows + [[None] * 15 for _ in range(28 - 22)]
            g = Diagram(pad, cell_px=int(0.2 / unit_px()))
            g.mob.move_to(LEFT * 2.8 + DOWN * 0.15)
            lab = M('n=15', font_size=30).next_to(g.mob, UP, buff=0.2)
            g.hide()
            self.add(g.mob)
            self.play(FadeIn(lab), g.reveal(g.rows_key(), run_time=max(3, d * 0.3)), rate_func=linear)
            early = SurroundingRectangle(Group(*[Square(g.s).move_to(g.center(22, i)) for i in (13, 14, 15)]),
                                         color=BAD, buff=0.03, stroke_width=4)
            should = DashedLine(g.corner(29, 1), g.corner(29, 16), color=MUTED, stroke_width=3)
            sl = M(r't=28=2n-2', font_size=26, color=MUTED).next_to(should, LEFT, buff=0.15)
            el = T(r'cells 13, 14, 15 fire at $t=22$', font_size=30, color=BAD).move_to(RIGHT * 3.4 + UP * 1.0)
            self.play(Create(early), FadeIn(el), Create(should), FadeIn(sl), run_time=1.4)
            six = T(r'six steps too early', font_size=30, color=BAD).next_to(el, DOWN, buff=0.2)
            self.play(FadeIn(six), run_time=0.6)
            self.wait(max(0.1, d * 0.3 - 2.0))
            more = T(r'four more five-state rules do the same', font_size=28, color=MUTED).next_to(six, DOWN,
                                                                                                buff=0.6)
            self.play(FadeIn(more), run_time=0.8)

        with self.say('d4') as d:
            msg = box(T(r'every refutation along these lines', font_size=32),
                      T(r'must use lines of length $n\ge 15$', font_size=32), color=HL)
            msg.next_to(more, DOWN, buff=0.6)
            self.play(Create(msg[0]), FadeIn(msg[1]), run_time=1.2)

        with self.say('d5') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            H = Diagram(sim.halfline(D14, 200, 202), height=6.8)
            H.mob.to_edge(LEFT, buff=0.6).shift(DOWN * 0.15)
            H.hide()
            self.add(H.mob)
            lab = T(r'the half-line of $\delta_{14}$', font_size=32).next_to(H.mob, RIGHT, buff=0.5).align_to(H.mob, UP)
            self.play(FadeIn(lab), H.reveal(H.rows_key(), run_time=max(4, d * 0.45)), rate_func=linear)
            pts = VGroup(T(r'irregular, essentially the elementary', font_size=28),
                         T(r'cellular automaton rule 22', font_size=28),
                         T(r'passes both barriers', font_size=28, color=GOOD),
                         T(r'(in the ranges we checked)', font_size=24, color=MUTED))
            pts.arrange(DOWN, buff=0.14, aligned_edge=LEFT).next_to(lab, DOWN, buff=0.5).align_to(lab, LEFT)
            pts[2].shift(DOWN * 0.3)
            pts[3].shift(DOWN * 0.3)
            self.play(FadeIn(pts[:2]), run_time=1.0)
            self.wait(max(0.1, d * 0.15 - 1.0))
            self.play(FadeIn(pts[2:]), run_time=1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S12_Germs(NarratedScene):
    def construct(self):
        chap = chapter_tag('11', 'Half-lines of low complexity')
        Mx = 78
        H = Diagram(sim.halfline(MAZ, Mx, Mx), height=6.4)
        H.mob.to_edge(LEFT, buff=0.6).shift(DOWN * 0.2)
        tt, ii = H.grid()
        below = tt + ii <= Mx
        curve = complexity_curve(MAZ, Mx)
        with self.say('g1') as d:
            self.play(FadeIn(chap), FadeIn(H.mob), run_time=0.9)
            self.play(H.focus(below, factor=0.25, run_time=1.0))
            ad = Line(H.corner(Mx, 1), H.corner(0, Mx + 1), color=HL, stroke_width=4)
            adl = M(r't+i=78', font_size=30, color=HL).next_to(ad.get_center(), UR, buff=0.15)
            self.play(Create(ad), FadeIn(adl), run_time=1.0)
            dfn = VGroup(T(r'complexity $c_{78}$ = number of distinct', font_size=30),
                         T(r'neighbourhoods used below this line', font_size=30),
                         T(r'(other than $\mathsf{LLL}$)', font_size=26, color=MUTED))
            dfn.arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to(RIGHT * 3.4 + UP * 2.2)
            self.play(FadeIn(dfn), run_time=1.0)
            self.wait(max(0.1, d * 0.2 - 1.0))
            ctr = Integer(0, font_size=60, color=HL)
            cl = T(r"Mazoyer's rule:", font_size=32).move_to(RIGHT * 2.6 + DOWN * 0.2)
            ctr.next_to(cl, RIGHT, buff=0.3)
            sweep = ValueTracker(2)
            line = always_redraw(lambda: Line(H.corner(sweep.get_value(), 1), H.corner(0, sweep.get_value() + 1),
                                              color=TEXT, stroke_width=2))
            ctr.add_updater(lambda m: m.set_value(curve[min(Mx, int(sweep.get_value()))]))
            self.add(line)
            self.play(FadeIn(cl), FadeIn(ctr), run_time=0.5)
            self.play(sweep.animate.set_value(Mx), run_time=max(3, d * 0.3), rate_func=linear)
            ctr.clear_updaters()
            self.remove(line)
            d12 = VGroup(T(r'$\delta_{12}$, $\delta_{13}$:', font_size=32), Integer(22, font_size=60, color=HL))
            d12.arrange(RIGHT, buff=0.3).next_to(VGroup(cl, ctr), DOWN, buff=0.4).align_to(cl, LEFT)
            self.play(FadeIn(d12), run_time=0.8)

        with self.say('g2') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            ttl = T(r'list every half-line of complexity $c_{78}\le 14$ that passes the basic tests',
                    font_size=30).to_edge(UP, buff=0.9)
            sub = T(r'(no firing cell, front never quiescent, pumping constraints)', font_size=26,
                    color=MUTED).next_to(ttl, DOWN, buff=0.15)
            self.play(FadeIn(ttl), FadeIn(sub), run_time=1.0)
            nodes = Integer(0, group_with_commas=True, font_size=56, color=TEXT)
            nl = T(r'search nodes', font_size=30, color=MUTED)
            nodes_g = VGroup(nodes, nl).arrange(RIGHT, buff=0.3).move_to(UP * 0.3)
            tr = ValueTracker(0)
            nodes.add_updater(lambda m: m.set_value(int(tr.get_value())))
            self.add(nodes_g)
            self.play(tr.animate.set_value(100000000), run_time=max(3, d * 0.3), rate_func=rate_functions.ease_in_quad)
            nodes.clear_updaters()
            self.play(Transform(nodes_g, VGroup(M(r'1.0\cdot 10^8', font_size=56), nl.copy()).arrange(
                RIGHT, buff=0.3).move_to(UP * 0.3)), run_time=0.6)
            res = VGroup(M('244', font_size=72, color=HL), T(r'candidate half-lines', font_size=32))
            res.arrange(RIGHT, buff=0.3).next_to(nodes_g, DOWN, buff=0.6)
            self.play(FadeIn(res, scale=1.2), run_time=0.9)
            self.wait(max(0.1, d * 0.2 - 0.9))
            ind = T(r'an independent re-implementation finds the same 244 \checkmark', font_size=28, color=GOOD)
            ind.next_to(res, DOWN, buff=0.5)
            self.play(FadeIn(ind), run_time=0.8)

        with self.say('g3') as d:
            self.play(FadeOut(VGroup(nodes_g, ind, sub)), res.animate.next_to(ttl, DOWN, buff=0.4), run_time=0.8)
            sq = VGroup(*[Square(0.2, stroke_width=0, fill_color=TEXT, fill_opacity=0.9) for _ in range(244)])
            sq.arrange_in_grid(rows=8, buff=0.06).move_to(DOWN * 0.3)
            self.play(LaggedStart(*[FadeIn(q) for q in sq], lag_ratio=0.003), run_time=1.0)
            a = VGroup(*sq[:230])
            b = VGroup(*sq[230:])
            self.play(a.animate.set_fill(BAD), run_time=1.0)
            al = T(r'230: no completion for the lengths $2,\dots,10$ (one certified solver call)', font_size=28,
                   color=BAD).next_to(sq, DOWN, buff=0.4)
            self.play(FadeIn(al), run_time=0.8)
            self.wait(max(0.1, d * 0.35 - 2.6))
            self.play(b.animate.set_fill(STATE_COLORS['A']), run_time=0.8)
            bl = T(r'14: periodic near the border, ruled out by the left-border lemma', font_size=28,
                   color=STATE_COLORS['A']).next_to(al, DOWN, buff=0.2)
            self.play(FadeIn(bl), run_time=0.8)

        with self.say('g4') as d:
            self.play(FadeOut(VGroup(sq, al, bl, res, ttl)), run_time=0.7)
            prop = box(T(r'\textbf{Proposition.} Every five-state minimal-time solution uses at least',
                         font_size=30),
                       T(r'15 distinct neighbourhoods on its half-line below $t+i=78$:\quad $c_{78}\ge 15$.',
                         font_size=30), color=HL)
            prop.to_edge(UP, buff=0.8)
            self.play(Create(prop[0]), FadeIn(prop[1]), run_time=1.4)
            self.wait(max(0.1, d * 0.2 - 1.4))
            rows = [('9{,}787', r'half-lines with $c_{78}\le 16$', TEXT),
                    (r'$-\,8{,}824$', r'no completion for $2,\dots,10$ (certified)', BAD),
                    (r'$-\,931$', r'pumping or left-border lemma', STATE_COLORS['A']),
                    (r'$-\,8$', r'no completion for $2,\dots,13$', BAD),
                    (r'$-\,8$', r'regularity certificate', STATE_COLORS['A']),
                    (r'$=\,16$', r'survivors, irregular as far as we can tell', HL)]
            tab = VGroup()
            for num, txt, col in rows:
                tab.add(VGroup(T(num, font_size=34, color=col), T(txt, font_size=28, color=col)))
            for r in tab:
                r[0].set_width(r[0].width)
            nums = VGroup(*[r[0] for r in tab]).arrange(DOWN, buff=0.28, aligned_edge=RIGHT)
            for r in tab:
                r[1].next_to(r[0], RIGHT, buff=0.4)
            tab.move_to(DOWN * 0.9)
            for k, r in enumerate(tab):
                self.play(FadeIn(r, shift=0.1 * RIGHT), run_time=0.7)
            self.wait(max(0.1, d * 0.3 - 4.2))
            d14 = T(r'one of them: the half-line of $\delta_{14}$', font_size=28, color=MUTED).next_to(tab, DOWN,
                                                                                                    buff=0.3)
            self.play(FadeIn(d14), run_time=0.8)

        with self.say('g5') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            Hc = Diagram(sim.halfline(D14, 120, 122), height=5.0)
            Hr = Diagram(sim.halfline(D12, 120, 122), height=5.0)
            Group(Hr.mob, Hc.mob).arrange(RIGHT, buff=1.2).shift(DOWN * 0.3)
            lr = T(r'orderly: eliminated', font_size=30, color=BAD).next_to(Hr.mob, UP, buff=0.25)
            lc = T(r'chaotic: what remains', font_size=30, color=HL).next_to(Hc.mob, UP, buff=0.25)
            self.play(FadeIn(Hr.mob), FadeIn(lr), run_time=0.8)
            self.play(FadeIn(Hc.mob), FadeIn(lc), run_time=0.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S13_Balzer(NarratedScene):
    def construct(self):
        chap = chapter_tag('12', "Balzer's conditions")
        with self.say('z1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            ttl = T(r'image solutions', font_size=44).to_edge(UP, buff=0.9)
            self.play(Write(ttl), run_time=1.0)
            left = VGroup(CellRow(['G', 'A', 'L'], size=0.7, font_size=30), M(r'\mapsto', font_size=40),
                          CellRow(['B'], size=0.7, font_size=30)).arrange(RIGHT, buff=0.3)
            right = VGroup(CellRow(['L', 'B', 'G'], size=0.7, font_size=30), M(r'\mapsto', font_size=40),
                           CellRow(['A'], size=0.7, font_size=30)).arrange(RIGHT, buff=0.3)
            pair = VGroup(left, right).arrange(RIGHT, buff=2.4).move_to(UP * 1.2)
            arr = DoubleArrow(left.get_right(), right.get_left(), buff=0.2, color=HL, stroke_width=3)
            al = T(r'mirror, then swap $\mathsf A\leftrightarrow\mathsf B$', font_size=26, color=HL).next_to(pair, UP,
                                                                                                           buff=0.3)
            self.play(FadeIn(left), run_time=0.8)
            self.play(GrowFromCenter(arr), FadeIn(al), FadeIn(right), run_time=1.2)
            fm = M(r'\delta\big(I(z),I(y),I(x)\big)=I\big(\delta(x,y,z)\big)', font_size=36).next_to(pair, DOWN,
                                                                                                   buff=0.45)
            ex = T(r'(an illustration with the swap $I=(\mathsf A\,\mathsf B)$)', font_size=24, color=MUTED)
            ex.next_to(fm, DOWN, buff=0.15)
            self.play(Write(fm), FadeIn(ex), run_time=1.4)
            self.wait(max(0.1, d * 0.35 - 4.4))
            conds = VGroup(T(r'(B1)\ a general stays a general', font_size=28),
                           T(r'(B2)\ image solution for a fixed swap $I$', font_size=28),
                           T(r'(B3)\ only $\mathsf{GGG}$, $\ast\mathsf{GG}$, $\mathsf{GG}\ast$ trigger the firing',
                             font_size=28),
                           T(r'(B4)\ a cell between two generals becomes a general', font_size=28))
            conds.arrange(DOWN, buff=0.15, aligned_edge=LEFT).to_edge(DOWN, buff=0.6)
            self.play(FadeOut(ex), fm.animate.scale(0.8).next_to(pair, DOWN, buff=0.3), run_time=0.6)
            for c in (conds[1], conds[0], conds[3], conds[2]):
                self.play(FadeIn(c, shift=0.1 * RIGHT), run_time=0.7)

        with self.say('z2') as d:
            self.play(FadeOut(VGroup(left, right, arr, al, fm, ttl)), conds.animate.to_edge(UP, buff=0.9),
                      run_time=0.8)
            q = VGroup(T(r"``the weakest conditions we found which enabled the program", font_size=30),
                       T(r"to prove that no five state minimal time solution existed''", font_size=30),
                       T(r'--- Balzer 1967, p.~37', font_size=26, color=MUTED))
            q.arrange(DOWN, buff=0.12).next_to(conds, DOWN, buff=0.6)
            q[2].align_to(q[1], RIGHT)
            self.play(FadeIn(q), run_time=1.4)
            self.wait(max(0.1, d * 0.35 - 1.4))
            six = T(r'six states: his program could not decide', font_size=28, color=MUTED).next_to(q, DOWN, buff=0.4)
            self.play(FadeIn(six), run_time=0.8)
            self.wait(max(0.1, d * 0.15 - 0.8))
            chk = VGroup(T(r'a backtracking search of the kind Sanders found incomplete:', font_size=26, color=HL),
                         T(r'worth an independent check', font_size=26, color=HL)).arrange(DOWN, buff=0.1)
            chk.next_to(six, DOWN, buff=0.35)
            self.play(FadeIn(chk), run_time=0.9)

        with self.say('z3') as d:
            self.play(FadeOut(VGroup(q, six, chk)), conds.animate.scale(0.75).to_edge(UP, buff=0.75), run_time=0.8)
            hdr = VGroup(T(r'swap $I$', font_size=28, color=MUTED), T(r'no rule for the lengths', font_size=28,
                                                                     color=MUTED),
                         T(r'certificate', font_size=28, color=MUTED))
            data = [(r'$(\mathsf A\,\mathsf B)$', r'$2,\dots,10$', r'LRAT, checked in 7.1 s'),
                    (r'$(\mathsf L\,\mathsf A)$', r'$2,\dots,9$', r'LRAT, checked in 3.5 s'),
                    (r'$(\mathsf L\,\mathsf B)$', r'$2,\dots,9$', r'LRAT, checked in 3.3 s'),
                    (r'identity', r'$2,\dots,12$', r'LRAT, 3.1 GB, checked in 66 s')]
            table = VGroup(hdr, *[VGroup(*[T(c, font_size=30) for c in row]) for row in data])
            xs = [-4.2, -0.6, 3.4]
            for r in table:
                for c, x in zip(r, xs):
                    c.move_to([x, 0, 0])
            table.arrange(DOWN, buff=0.32)
            for r in table:
                for c, x in zip(r, xs):
                    c.set_x(x)
            table.next_to(conds, DOWN, buff=0.55)
            line = Line(LEFT * 6, RIGHT * 6, color=MUTED, stroke_width=1.5).next_to(hdr, DOWN, buff=0.15)
            self.play(FadeIn(hdr), Create(line), run_time=0.8)
            for r in table[1:]:
                self.play(FadeIn(r, shift=0.1 * UP), run_time=0.8)
            weak = VGroup(T(r'already under the weaker reading of the conditions;', font_size=24, color=MUTED),
                          T(r'the strong reading only adds conditions', font_size=24, color=MUTED)).arrange(DOWN, buff=0.08)
            weak.next_to(table, DOWN, buff=0.4)
            self.play(FadeIn(weak), run_time=0.8)
            for r in table[1:]:
                r[2].set_color(GOOD)

        with self.say('z4') as d:
            sym = T(r'but symmetric rules satisfying the conditions synchronize every line up to length 11',
                    font_size=28).next_to(weak, DOWN, buff=0.4)
            self.play(FadeIn(sym), run_time=0.9)
            right_ = T(r"so length 12 is needed, and Balzer's 1967 claim holds", font_size=32, color=HL)
            right_.next_to(sym, DOWN, buff=0.3)
            self.play(Write(right_), run_time=1.4)

        with self.say('z5') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            six = VGroup(T(r"six states, Balzer's conditions (strong reading):", font_size=32),
                         T(r'rules for all lengths up to 13, for every type of swap', font_size=30),
                         T(r'up to 14 for $I=$ identity and $I=(\mathsf L\,\mathsf A)$', font_size=30),
                         T(r'the next length: undecided after 30 minutes', font_size=28, color=MUTED))
            six.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(UP * 0.6)
            for r in six:
                self.play(FadeIn(r, shift=0.1 * RIGHT), run_time=0.8)
            op = T(r'open, as it was for Balzer', font_size=40, color=HL).next_to(six, DOWN, buff=0.7)
            self.play(Write(op), run_time=1.2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S14_Outlook(NarratedScene):
    def construct(self):
        chap = chapter_tag('13', 'Where this leaves us')
        with self.say('o1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            ks = VGroup(*[M(str(k), font_size=64) for k in (4, 5, 6)]).arrange(RIGHT, buff=2.8).shift(DOWN * 0.4)
            stat = VGroup(VGroup(M(r'\times', font_size=60, color=BAD), T(r'\textsf{impossible}', font_size=28, color=BAD),
                                 T(r'now certified', font_size=24)).arrange(DOWN, buff=0.12),
                          VGroup(M(r'?', font_size=72, color=HL), T(r'\textsf{open}', font_size=28, color=HL),
                                 T(r'since 1987', font_size=24)).arrange(DOWN, buff=0.12),
                          VGroup(M(r'\checkmark', font_size=60, color=GOOD), T(r'\textsf{solved}', font_size=28,
                                                                               color=GOOD),
                                 T(r'Mazoyer 1987', font_size=24)).arrange(DOWN, buff=0.12))
            for s_, k in zip(stat, ks):
                s_.next_to(k, UP, buff=0.4)
            kl = T(r'number of states', font_size=28, color=MUTED).next_to(ks, DOWN, buff=0.4)
            self.play(LaggedStart(*[FadeIn(VGroup(k, s_), shift=0.2 * UP) for k, s_ in zip(ks, stat)],
                                  lag_ratio=0.4), FadeIn(kl), run_time=2.4)
            self.play(Indicate(stat[1][0], color=HL, scale_factor=1.4), run_time=1.2)

        with self.say('o2') as d:
            self.play(FadeOut(VGroup(ks, stat, kl)), run_time=0.6)
            ax = NumberLine(x_range=[0, 20, 1], length=11, include_numbers=False, color=MUTED,
                            tick_size=0.06).move_to(UP * 1.4)
            labels = VGroup(*[M(r'10^{%d}' % e, font_size=26, color=MUTED).next_to(ax.n2p(e), DOWN, buff=0.15)
                              for e in (0, 5, 10, 15, 20)])
            ttl = T(r'estimated size of the search tree (log scale)', font_size=28, color=MUTED).next_to(ax, UP,
                                                                                                       buff=0.6)
            self.play(Create(ax), FadeIn(labels), FadeIn(ttl), run_time=1.2)
            p4 = Dot(ax.n2p(np.log10(25.5)), radius=0.11, color=GOOD)
            l4 = T(r'four states: about 25 nodes', font_size=26, color=GOOD).next_to(p4, UP, buff=0.2)
            self.play(FadeIn(p4, scale=2), FadeIn(l4), run_time=0.9)
            probes = [4.2e11, 3.1e17, 8.3e18]
            p5 = VGroup(*[Dot(ax.n2p(np.log10(v)), radius=0.11, color=BAD) for v in probes])
            l5 = T(r'five states: three probes, $10^{11}$ to $10^{19}$', font_size=26, color=BAD)
            l5.next_to(p5, UP, buff=0.2)
            self.play(LaggedStart(*[FadeIn(p, scale=2) for p in p5], lag_ratio=0.3), FadeIn(l5), run_time=1.4)
            self.wait(max(0.1, d * 0.25 - 3.5))
            know = VGroup(T(r'every five-state solution has a half-line that', font_size=30, color=HL),
                          T(r'$\bullet$ is never eventually regular', font_size=28),
                          T(r'$\bullet$ has non-periodic structure reaching the line $i=t/3$', font_size=28),
                          T(r'$\bullet$ uses at least 15 neighbourhoods below $t+i=78$', font_size=28),
                          T(r'and refutations along our lines need lines of length $n\ge 15$', font_size=30,
                            color=HL))
            know.arrange(DOWN, buff=0.16, aligned_edge=LEFT).next_to(labels, DOWN, buff=0.8)
            for k in know:
                self.play(FadeIn(k, shift=0.1 * RIGHT), run_time=0.8)

        with self.say('o3') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            n = 16
            g = Diagram(sim.line(MAZ, n), height=6.4)
            g.mob.to_edge(LEFT, buff=1.0).shift(DOWN * 0.2)
            self.play(FadeIn(g.mob), run_time=0.8)
            tt, ii = g.grid()
            R = (tt + ii >= 2 * n - 1)
            self.play(g.focus(R, factor=0.3, run_time=1.2))
            tri = g.triangle_R(n, stroke_color=HL)
            self.play(Create(tri), run_time=0.8)
            txt = VGroup(T(r'inside each reflected triangle:', font_size=30),
                         T(r'a mirrored synchronization, run on the', font_size=30),
                         T(r'background left behind the front', font_size=30))
            txt.arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to(RIGHT * 2.8 + UP * 1.6)
            self.play(FadeIn(txt), run_time=1.0)
            self.wait(max(0.1, d * 0.25 - 3.8))
            both = VGroup(T(r'five states: both constructions', font_size=30, color=HL),
                          T(r'with the same four working states', font_size=30, color=HL))
            both.arrange(DOWN, buff=0.12, aligned_edge=LEFT).next_to(txt, DOWN, buff=0.6).align_to(txt, LEFT)
            self.play(FadeIn(both), run_time=1.0)
            self.wait(max(0.1, d * 0.2 - 1.0))
            heur = T(r'a heuristic, not a theorem', font_size=28, color=MUTED).next_to(both, DOWN, buff=0.6)
            heur.align_to(txt, LEFT)
            self.play(FadeIn(heur), run_time=0.8)

        with self.say('o4') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            axes = Axes(x_range=[10, 24, 2], y_range=[-80, 140, 40], x_length=7.5, y_length=4.2,
                        axis_config={'color': MUTED, 'include_numbers': True, 'font_size': 24},
                        tips=False).shift(DOWN * 0.6 + LEFT * 1.2)
            xl = T(r'largest length $N$', font_size=26, color=MUTED).next_to(axes.x_axis, DOWN, buff=0.45)
            yl = T(r'$\log_2$(surviving completions)', font_size=26, color=MUTED).rotate(PI / 2).next_to(
                axes.y_axis, LEFT, buff=0.6)
            curve = axes.plot(lambda N: 181 - N * N / 2, x_range=[10, 22], color=HL)
            zero = DashedLine(axes.c2p(10, 0), axes.c2p(24, 0), color=MUTED, stroke_width=2)
            self.play(Create(axes), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(Create(curve), Create(zero), run_time=1.4)
            cross = Dot(axes.c2p(np.sqrt(362), 0), color=BAD, radius=0.1)
            cl = M(r'N\approx 20', font_size=32, color=BAD).next_to(cross, UR, buff=0.15)
            fm = M(r'2^{\,181-N^2/2}', font_size=40, color=HL).move_to(RIGHT * 4.6 + UP * 1.6)
            hl_ = T(r'heuristic: independent conditions', font_size=24, color=MUTED).next_to(fm, DOWN, buff=0.2)
            self.play(FadeIn(cross, scale=2), FadeIn(cl), FadeIn(fm), FadeIn(hl_), run_time=1.0)

        with self.say('o5') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            ttl = T(r'open problems', font_size=44, color=HL).to_edge(UP, buff=0.9)
            qs = VGroup(T(r'1.\ Does a five-state minimal-time solution exist?', font_size=32),
                        T(r'2.\ Is there a necessary condition on the reflected triangles', font_size=32),
                        T(r'\phantom{2.}\ themselves, not only on the half-line?', font_size=32),
                        T(r'3.\ If five-state rules stop working at some length,', font_size=32),
                        T(r'\phantom{3.}\ at which one? (We know: beyond 14.)', font_size=32))
            qs.arrange(DOWN, buff=0.22, aligned_edge=LEFT).next_to(ttl, DOWN, buff=0.6)
            qs[2].shift(RIGHT * 0.45)
            qs[4].shift(RIGHT * 0.45)
            self.play(Write(ttl), run_time=0.8)
            t0 = self.renderer.time
            for k, frac in zip(range(5), (0.1, 0.32, 0.36, 0.62, 0.66)):
                wait = t0 + frac * d - self.renderer.time
                if wait > 0.05:
                    self.wait(wait)
                self.play(FadeIn(qs[k], shift=0.1 * RIGHT), run_time=0.7)

        with self.say('o6') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), FadeOut(chap), run_time=0.7)
            n = 24
            g = Diagram(sim.line(MAZ, n), height=7.0)
            g.mob.move_to(LEFT * 3.6)
            g.hide()
            self.add(g.mob)
            key = g.rows_key().astype(float)
            self.play(g.reveal(key, run_time=max(6, d * 0.55)), rate_func=linear)
            flash = Rectangle(width=g.mob.width + 0.1, height=g.s * 1.4, stroke_width=0, fill_color=WHITE,
                              fill_opacity=0.9).move_to(g.center(g.T - 1, (n + 1) / 2))
            self.add(flash)
            self.play(FadeOut(flash), run_time=0.9)
            q = VGroup(T(r'between four and six,', font_size=40), T(r'one number is still waiting:', font_size=40),
                       M(r'5\ ?', font_size=110, color=HL)).arrange(DOWN, buff=0.3).move_to(RIGHT * 2.8)
            self.play(FadeIn(q[:2]), run_time=1.0)
            self.play(Write(q[2]), run_time=1.2)

        with self.say('o7') as d:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
            cred = VGroup(T(r'based on the paper', font_size=28, color=MUTED),
                          T(r'\emph{Towards five-state minimal-time firing squads:}', font_size=34),
                          T(r'\emph{two barriers on the half-line and certified bounds}', font_size=34),
                          T(r'Kia Keng Giam, Beichen Sun, Yaoqi Zhao', font_size=30),
                          T(r'animations: Manim Community \quad voice: Kokoro-82M (synthetic)', font_size=24,
                            color=MUTED),
                          T(r"every diagram is computed from the rule tables in the paper's repository",
                            font_size=24, color=MUTED))
            cred.arrange(DOWN, buff=0.22)
            cred[3].shift(DOWN * 0.2)
            cred[4:].shift(DOWN * 0.5)
            self.play(FadeIn(cred, shift=0.2 * UP), run_time=1.4)
        self.wait(1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
