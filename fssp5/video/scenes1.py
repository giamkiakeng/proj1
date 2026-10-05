"""Scenes 1-5: the puzzle, the speed limit, the history, the classical solutions."""
from manim import *

import fsspsim as sim
from common import (BAD, BG, GOOD, HL, MUTED, REGION, STATE_COLORS, TEXT, CellRow, Diagram, M,
                    NarratedScene, T, dim_outside, legend, to_index, unit_px)

MAZ = sim.load_rule('mazoyer6')
D14 = sim.load_rule('delta14')


class S01_ColdOpen(NarratedScene):
    def construct(self):
        n = 24
        rows = sim.line(MAZ, n)                      # 2n - 1 = 47 rows, last row all F
        row = CellRow(rows[0], size=0.44, buff=0.07, font_size=19).to_edge(UP, buff=0.9)

        with self.say('c1') as d:
            self.play(LaggedStart(*[FadeIn(b, scale=0.6) for b in row.boxes], lag_ratio=0.04),
                      FadeIn(row.labels), run_time=2.0)
            gen = row.boxes[0]
            glab = T(r'general', font_size=30, color=STATE_COLORS['G']).next_to(gen, DOWN, buff=0.35)
            garr = Arrow(glab.get_top(), gen.get_bottom(), buff=0.06, stroke_width=3,
                         color=STATE_COLORS['G'], max_tip_length_to_length_ratio=0.3)
            self.play(FadeIn(glab, shift=0.1 * UP), GrowArrow(garr), run_time=1.0)
            self.wait(max(0.1, d * 0.45 - 3.0))
            goal = T(r'goal: everybody fires at the \emph{same} instant', font_size=34)
            goal.next_to(row, DOWN, buff=1.4)
            self.play(Write(goal), run_time=1.6)

        with self.say('c2') as d:
            self.play(FadeOut(goal), FadeOut(glab), FadeOut(garr), run_time=0.6)
            k = 11
            focus = SurroundingRectangle(row.boxes[k], color=HL, buff=0.05, stroke_width=3)
            nb = VGroup(*[SurroundingRectangle(row.boxes[j], color=HL, buff=0.05, stroke_width=2,
                                               stroke_opacity=0.6) for j in (k - 1, k + 1)])
            eyes = VGroup(CurvedArrow(row.boxes[k].get_bottom() + 0.05 * DOWN,
                                      row.boxes[k - 1].get_bottom() + 0.05 * DOWN, angle=-TAU / 4,
                                      color=HL, stroke_width=2.5, tip_length=0.15),
                          CurvedArrow(row.boxes[k].get_bottom() + 0.05 * DOWN,
                                      row.boxes[k + 1].get_bottom() + 0.05 * DOWN, angle=TAU / 4,
                                      color=HL, stroke_width=2.5, tip_length=0.15))
            seen = T(r'sees only its two neighbours', font_size=30, color=HL).next_to(eyes, DOWN, buff=0.3)
            self.play(Create(focus), run_time=0.6)
            self.play(Create(nb), Create(eyes), FadeIn(seen), run_time=1.2)
            self.wait(max(0.1, d * 0.5 - 2.4))
            book = VGroup(RoundedRectangle(width=3.2, height=1.9, corner_radius=0.12, color=MUTED,
                                           stroke_width=2),
                          T(r'\textsf{rule book}', font_size=26, color=MUTED))
            # the transitions of Mazoyer's rule used in the first step of the diagram below
            entries = VGroup(*[M(r'%s\,\mathsf{%s\,%s}\ \to\ \mathsf{%s}' % (a, b, c, e), font_size=26)
                               for a, b, c, e in ((r'\ast', 'G', 'L', 'A'), (r'\mathsf{G}', 'L', 'L', 'C'),
                                                  (r'\mathsf{L}', 'L', 'L', 'L'))])
            entries.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
            book[1].next_to(book[0].get_top(), DOWN, buff=0.15)
            entries.next_to(book[1], DOWN, buff=0.15)
            book.add(entries)
            book.next_to(seen, DOWN, buff=0.5)
            same = T(r'the same for every soldier and every length', font_size=28, color=TEXT)
            same.next_to(book, DOWN, buff=0.25)
            self.play(FadeIn(book, shift=0.2 * UP), run_time=0.9)
            self.play(Write(same), run_time=1.2)

        # the line unfolds into its space-time diagram
        dg = Diagram(rows[:-1] + [['F'] * n], height=6.9)
        dg.mob.move_to(DOWN * 0.15)
        with self.say('c3') as d:
            self.play(FadeOut(VGroup(focus, nb, eyes, seen, book, same)), run_time=0.6)
            self.play(row.animate.scale_to_fit_width(dg.mob.width).move_to(dg.center(0, (n + 1) / 2)),
                      run_time=1.3)
            dg.set_visible(dg.rows_key() == 0)
            self.add(dg.mob)
            self.remove(row)
            tl = Arrow(dg.corner(0, 1) + LEFT * 0.45, dg.corner(dg.T * 0.35, 1) + LEFT * 0.45, buff=0,
                       color=MUTED, stroke_width=3)
            tlab = T('time', font_size=28, color=MUTED).next_to(tl, LEFT, buff=0.15)
            cl = Arrow(dg.corner(0, 1) + UP * 0.35, dg.corner(0, 1) + UP * 0.35 + RIGHT * 1.6, buff=0,
                       color=MUTED, stroke_width=3)
            clab = T('soldiers', font_size=28, color=MUTED).next_to(cl, UP, buff=0.1)
            self.play(GrowArrow(tl), FadeIn(tlab), GrowArrow(cl), FadeIn(clab), run_time=0.8)
            key = dg.rows_key().astype(float)
            key[-1] = 1e6                              # the firing row is revealed in c4
            self.play(UpdateFromAlphaFunc(dg.mob, lambda m, a: dg.set_visible(
                dg.rows_key() <= a * (dg.T - 2) + 1e-9), run_time=max(2.0, d - 3.2), rate_func=linear))

        with self.say('c4') as d:
            dg.show_all()
            last = Rectangle(width=dg.mob.width + 0.1, height=dg.s * 1.4, stroke_width=0,
                             fill_color=WHITE, fill_opacity=0.9).move_to(dg.center(dg.T - 1, (n + 1) / 2))
            fire = T(r'\textbf{FIRE!}', font_size=44, color=HL).next_to(last, RIGHT, buff=0.4)
            t30 = M(r't = 2n-2 = 46', font_size=32, color=TEXT).next_to(last, LEFT, buff=0.4)
            self.add(last)
            self.play(FadeOut(last, run_time=0.9), FadeIn(fire, scale=1.4), FadeIn(t30))
            self.wait(1.2)
            grp = Group(dg.mob, tl, tlab, cl, clab, fire, t30)
            self.play(grp.animate.scale(0.82).to_edge(LEFT, buff=0.6), run_time=1.2)
            title = T(r'The Firing Squad\\Synchronization Problem', font_size=64)
            title.move_to(RIGHT * 2.6 + UP * 1.0)
            who = T(r'posed by John Myhill, 1957', font_size=34, color=MUTED).next_to(title, DOWN, buff=0.45)
            self.play(Write(title), run_time=2.0)
            self.play(FadeIn(who, shift=0.1 * UP), run_time=0.8)

        with self.say('c5') as d:
            items = VGroup(T(r'where it came from', font_size=34),
                           T(r'why it is so hard', font_size=34),
                           T(r'what we could prove', font_size=34)).arrange(DOWN, buff=0.28,
                                                                             aligned_edge=LEFT)
            dots = VGroup(*[Dot(radius=0.05, color=HL).next_to(it, LEFT, buff=0.2) for it in items])
            VGroup(items, dots).next_to(who, DOWN, buff=0.7)
            for it, dt in zip(items, dots):
                self.play(FadeIn(dt), FadeIn(it, shift=0.1 * RIGHT), run_time=0.7)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)


from common import cell_rows, chapter_tag  # noqa: E402


class S02_Puzzle(NarratedScene):
    def construct(self):
        chap = chapter_tag('1', 'The puzzle')
        n = 7
        with self.say('p1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            row = CellRow(['L'] * n, size=0.8, buff=0.14, font_size=34).move_to(UP * 1.7)
            brace = Brace(row, DOWN, color=MUTED, buff=0.15)
            blab = T(r'$n$ cells', font_size=32, color=MUTED).next_to(brace, DOWN, buff=0.1)
            self.play(LaggedStart(*[FadeIn(b, scale=0.7) for b in row.boxes], lag_ratio=0.08),
                      FadeIn(row.labels), run_time=1.3)
            self.play(GrowFromCenter(brace), FadeIn(blab), run_time=0.8)
            leg = legend(('L', 'G', 'A', 'B', 'F'), names={'L': 'quiescent', 'G': 'general', 'F': 'fire'},
                         size=0.42, font_size=30).move_to(DOWN * 1.0)
            stl = T(r'each cell: one of finitely many \emph{states}', font_size=32).next_to(leg, UP, buff=0.4)
            self.play(FadeIn(stl), LaggedStart(*[FadeIn(x, shift=0.1 * UP) for x in leg], lag_ratio=0.15),
                      run_time=1.8)
            clock = T(r'time: $t = 0,\ 1,\ 2,\ \dots$', font_size=32, color=MUTED).next_to(leg, DOWN, buff=0.6)
            self.play(FadeIn(clock), run_time=0.8)

        with self.say('p2') as d:
            self.play(FadeOut(VGroup(row, brace, blab, leg, stl, clock)), run_time=0.6)
            trio = VGroup(*[RoundedRectangle(width=1.0, height=1.0, corner_radius=0.16, color=TEXT,
                                             stroke_width=2.5) for _ in range(3)]).arrange(RIGHT, buff=0.18)
            trio.move_to(UP * 1.5 + LEFT * 2.8)
            xyz = VGroup(*[M(c, font_size=44).move_to(b) for c, b in zip('xyz', trio)])
            names = VGroup(*[T(s, font_size=24, color=MUTED).next_to(b, UP, buff=0.15)
                             for s, b in zip(('left', 'itself', 'right'), trio)])
            out = RoundedRectangle(width=1.0, height=1.0, corner_radius=0.16, color=HL, stroke_width=3)
            out.next_to(trio[1], DOWN, buff=1.3)
            outl = M(r'\delta(x,y,z)', font_size=34, color=HL).next_to(out, DOWN, buff=0.2)
            lines = VGroup(*[Arrow(b.get_bottom(), out.get_top(), buff=0.08, stroke_width=3, color=MUTED,
                                   max_tip_length_to_length_ratio=0.12) for b in trio])
            tlab = T(r'time $t$', font_size=26, color=MUTED).next_to(trio, LEFT, buff=0.4)
            t1lab = T(r'time $t+1$', font_size=26, color=MUTED).next_to(out, LEFT, buff=0.4).align_to(tlab, RIGHT)
            self.play(LaggedStart(*[Create(b) for b in trio], lag_ratio=0.2), FadeIn(xyz), FadeIn(names),
                      FadeIn(tlab), run_time=1.5)
            self.play(LaggedStart(*[GrowArrow(a) for a in lines], lag_ratio=0.15), Create(out), FadeIn(t1lab),
                      run_time=1.3)
            self.play(Write(outl), run_time=0.8)
            self.wait(max(0.1, d * 0.35 - 3.6))
            # borders
            brow = CellRow(['G', 'L', 'L', 'L', 'L'], size=0.5, buff=0.08, font_size=22)
            star_l = VGroup(DashedVMobject(RoundedRectangle(width=0.5, height=0.5, corner_radius=0.08,
                                                            color=MUTED, stroke_width=2)),
                            M(r'\ast', font_size=30, color=MUTED))
            star_r = star_l.copy()
            line5 = VGroup(star_l, brow, star_r).arrange(RIGHT, buff=0.08)
            line5.move_to(DOWN * 2.6 + LEFT * 2.8)
            star_l[1].move_to(star_l[0]); star_r[1].move_to(star_r[0])
            bl = T(r'border $\ast$', font_size=26, color=MUTED).next_to(line5, DOWN, buff=0.2)
            self.play(FadeIn(line5), FadeIn(bl), run_time=1.0)
            # the rule table
            table = VGroup(T(r'the rule $\delta$', font_size=32, color=HL))
            ents = VGroup(*[M(r'%s\ \mapsto\ \mathsf{%s}' % (e, v), font_size=30) for e, v in (
                (r'\mathsf{L\,L\,L}', 'L'), (r'\mathsf{G\,L\,L}', 'A'), (r'\mathsf{L\,G\,L}', 'A'),
                (r'\mathsf{A\,L\,L}', 'B'), (r'\vdots', r'\vdots'))])
            ents[-1] = M(r'\vdots', font_size=30)
            ents.arrange(DOWN, buff=0.16)
            table.add(ents.next_to(table[0], DOWN, buff=0.3))
            frame = SurroundingRectangle(table, color=MUTED, buff=0.3, corner_radius=0.12, stroke_width=2)
            VGroup(table, frame).move_to(RIGHT * 3.6 + UP * 0.2)
            self.play(Create(frame), FadeIn(table, shift=0.1 * LEFT), run_time=1.4)

        with self.say('p3') as d:
            ex = VGroup(*[M(r'\mathsf{%s}' % s, font_size=44) for s in 'GLL'])
            fills = VGroup(*[b.copy().set_fill(STATE_COLORS[s], 1).set_stroke(width=0)
                             for b, s in zip(trio, 'GLL')])
            for m, b in zip(ex, trio):
                m.move_to(b)
            self.play(*[FadeOut(x) for x in xyz], *[FadeIn(f) for f in fills], *[FadeIn(m) for m in ex],
                      run_time=1.0)
            hrow = SurroundingRectangle(ents[1], color=HL, buff=0.08, stroke_width=3)
            self.play(Create(hrow), run_time=0.7)
            res = out.copy().set_fill(STATE_COLORS['A'], 1).set_stroke(width=0)
            resl = M(r'\mathsf{A}', font_size=44).move_to(out)
            self.play(FadeIn(res), FadeIn(resl), FadeOut(outl), run_time=0.9)
            self.wait(max(0.1, d * 0.45 - 2.6))
            # the whole line updates at once (delta14, n = 7)
            r0, r1 = sim.line(D14, 7)[:2]
            g0 = CellRow(r0, size=0.5, buff=0.08, font_size=22)
            g1 = CellRow(r1, size=0.5, buff=0.08, font_size=22)
            pair = VGroup(g0, g1).arrange(DOWN, buff=0.35).move_to(DOWN * 2.3 + LEFT * 2.8)
            l0 = M('t=0', font_size=26, color=MUTED).next_to(g0, LEFT, buff=0.3)
            l1 = M('t=1', font_size=26, color=MUTED).next_to(g1, LEFT, buff=0.3)
            self.play(FadeOut(VGroup(line5, bl)), FadeIn(g0), FadeIn(l0), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(b, shift=0.15 * DOWN) for b in g1.boxes], lag_ratio=0.0),
                      FadeIn(g1.labels), FadeIn(l1), run_time=0.9)
            same = T(r'all cells, same table, same moment', font_size=28, color=HL).next_to(pair, RIGHT, buff=0.5)
            self.play(FadeIn(same), run_time=0.6)

        with self.say('p4') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            rows = sim.line(D14, 7)
            dia = cell_rows(rows, size=0.36, buff=0.05, font_size=15).move_to(LEFT * 3.2 + DOWN * 0.25)
            for r in dia[1:]:
                r.set_opacity(0)
            tl = M('t=0', font_size=26, color=MUTED).next_to(dia[0], LEFT, buff=0.25)
            self.play(FadeIn(dia[0]), FadeIn(tl), run_time=0.8)
            q = VGroup(T(r'a sleeping cell between sleeping cells stays asleep:', font_size=28),
                       M(r'\delta(\mathsf{L},\mathsf{L},\mathsf{L})=\mathsf{L},\qquad '
                         r'\delta(\mathsf{L},\mathsf{L},\ast)=\mathsf{L}', font_size=32)).arrange(DOWN, buff=0.25)
            q.move_to(RIGHT * 2.9 + UP * 2.1)
            self.play(FadeIn(q[0]), Write(q[1]), run_time=1.6)
            goal = VGroup(T(r'\textbf{goal:} one table such that for \emph{every} length $n$', font_size=28),
                          T(r'all cells enter $\mathsf{F}$ at the same moment,', font_size=28),
                          T(r'and no cell fires before that moment', font_size=28)).arrange(DOWN, buff=0.15,
                                                                                             aligned_edge=LEFT)
            goal.next_to(q, DOWN, buff=0.7)
            self.play(FadeIn(goal, shift=0.1 * UP), run_time=1.2)
            self.wait(max(0.1, d * 0.35 - 3.6))
            steps = len(rows) - 1

            def grow(m, a):
                k = int(a * steps + 1e-9)
                for j, r in enumerate(dia):
                    r.set_opacity(1 if j <= k else 0)
            self.play(UpdateFromAlphaFunc(dia, grow), run_time=max(2.5, d * 0.45), rate_func=linear)
            tl2 = M(r't=12=2\cdot 7-2', font_size=26, color=HL).next_to(dia[-1], LEFT, buff=0.25)
            flash = SurroundingRectangle(dia[-1], color=HL, buff=0.06, stroke_width=4)
            self.play(Create(flash), FadeIn(tl2), run_time=0.8)

        with self.say('p5') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            ns = (3, 5, 8, 11, 14)
            dgs = [Diagram(sim.line(D14, k), cell_px=int(0.17 / unit_px())) for k in ns]
            grp = Group(*[g.mob for g in dgs]).arrange(RIGHT, buff=0.5, aligned_edge=UP)
            grp.move_to(UP * 0.6)
            base = grp.get_bottom()[1] - 0.35
            labs = VGroup(*[M('n=%d' % k, font_size=28, color=MUTED).move_to([g.mob.get_center()[0], base, 0])
                            for k, g in zip(ns, dgs)])
            for g in dgs:
                g.hide()
            self.add(*[g.mob for g in dgs])
            self.play(*[g.reveal(g.rows_key(), run_time=max(2.0, d * 0.3)) for g in dgs],
                      FadeIn(labs), rate_func=linear)
            same = T(r'one rule with a fixed number of states, every length', font_size=30, color=HL)
            same.to_edge(DOWN, buff=1.2)
            self.play(FadeIn(same), run_time=0.8)
            self.wait(max(0.1, d * 0.25 - 0.8))
            # a very long line
            self.play(FadeOut(Group(grp, labs, same)), run_time=0.6)
            strip = Diagram([['G'] + ['L'] * 399], cell_px=int(0.5 / unit_px()), maxcell=200)
            strip.mob.move_to(UP * 0.4).align_to(LEFT * 6.5, LEFT)
            cnt = Integer(7, group_with_commas=True, font_size=44, color=TEXT)
            nl = M('n=', font_size=44).next_to(cnt, LEFT, buff=0.15)
            ctr = VGroup(nl, cnt).move_to(DOWN * 1.4)
            self.add(strip.mob)
            self.play(FadeIn(ctr), run_time=0.5)
            tr = ValueTracker(7)
            cnt.add_updater(lambda m: m.set_value(int(tr.get_value())))
            self.play(strip.mob.animate.scale(0.03, about_edge=LEFT), tr.animate.set_value(1000000),
                      run_time=max(2.5, d * 0.25), rate_func=rate_functions.ease_in_quad)
            cnt.clear_updaters()
            msg = T(r'nobody can count to $n$ with five or six states of mind', font_size=32, color=HL)
            msg.next_to(ctr, DOWN, buff=0.6)
            self.play(Write(msg), run_time=1.4)

        with self.say('p6') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.6)
            ask = T(r'How would \emph{you} do it?', font_size=56)
            self.play(Write(ask), run_time=1.2)
        self.wait(1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S03_SpeedLimit(NarratedScene):
    def construct(self):
        chap = chapter_tag('2', 'A speed limit')
        cs = int(0.3 / unit_px())
        d9 = Diagram(sim.line(D14, 9), cell_px=cs)
        d9.mob.move_to(RIGHT * 2.5 + DOWN * 0.3)
        with self.say('s1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            d9.hide()
            self.add(d9.mob)
            nl = M('n=9', font_size=30, color=MUTED).next_to(d9.mob, UP, buff=0.25)
            self.play(FadeIn(nl), run_time=0.5)
            front = VMobject(color=HL, stroke_width=4).set_points_as_corners(
                [d9.center(i - 1, i) for i in range(1, 10)])
            self.play(d9.reveal(d9.rows_key(), run_time=max(3.0, d * 0.45), rate_func=linear),
                      Create(front, run_time=max(3.0, d * 0.45), rate_func=linear))
            info = VGroup(T(r'information travels', font_size=30), T(r'at most one cell per step', font_size=30))
            info.arrange(DOWN, buff=0.12).move_to(LEFT * 3.6 + UP * 1.2)
            self.play(FadeIn(info), run_time=0.8)
            far = Circle(radius=d9.s * 0.75, color=HL, stroke_width=4).move_to(d9.center(8, 9))
            fl = M(r'\text{cell } n \text{ wakes at } t=n-1', font_size=30, color=HL).move_to(LEFT * 3.6 + DOWN * 0.4)
            self.play(Create(far), Write(fl), run_time=1.3)

        cs2 = int(0.27 / unit_px())
        d6 = Diagram(sim.line(D14, 6), cell_px=cs2)
        e9 = Diagram(sim.line(D14, 9), cell_px=cs2)
        Group(d6.mob, e9.mob).arrange(RIGHT, buff=1.6, aligned_edge=UP).move_to(DOWN * 0.15)
        with self.say('s2') as d:
            self.play(FadeOut(VGroup(info, fl, far, front, nl)), FadeOut(d9.mob), run_time=0.7)
            l6 = M('n=6', font_size=30, color=MUTED).next_to(d6.mob, UP, buff=0.2)
            l9 = M('n=9', font_size=30, color=MUTED).next_to(e9.mob, UP, buff=0.2)
            self.play(FadeIn(d6.mob), FadeIn(e9.mob), FadeIn(l6), FadeIn(l9), run_time=1.0)
            self.wait(max(0.1, d * 0.2 - 1.7))
            tt, ii = d6.grid()
            m6 = tt + ii <= 10
            tt9, ii9 = e9.grid()
            m9 = (tt9 + ii9 <= 10) & (ii9 <= 6)
            o6 = d6.above_antidiag(10, 6, stroke_color=REGION)
            o9 = e9.above_antidiag(10, 6, stroke_color=REGION)
            self.play(d6.focus(m6), e9.focus(m9), Create(o6), Create(o9), run_time=1.5)
            same = T(r'identical for $t+i\le 10$', font_size=30, color=REGION).next_to(Group(d6.mob, e9.mob), DOWN,
                                                                                    buff=0.3)
            self.play(FadeIn(same), run_time=0.7)
            self.wait(max(0.1, d * 0.35 - 2.2))
            ring = Circle(radius=d6.s * 0.8, color=BAD, stroke_width=4).move_to(d6.center(5, 6))
            feel = T(r'the last cell feels the border', font_size=26, color=BAD).next_to(d6.mob, LEFT, buff=0.3)
            feel.align_to(ring, UP)
            self.play(Create(ring), FadeIn(feel), run_time=0.9)
            echo = Arrow(d6.center(5, 6), d6.center(10, 1), buff=0.1, color=BAD, stroke_width=4)
            self.play(GrowArrow(echo), run_time=1.6)

        with self.say('s3') as d:
            path = VMobject(color=HL, stroke_width=5).set_points_as_corners(
                [d6.center(0, 1), d6.center(5, 6), d6.center(10, 1)])
            self.play(Create(path), run_time=1.6)
            eq = M(r'(n-1)', r'+', r'(n-1)', r'=', r'2n-2', font_size=44).to_edge(DOWN, buff=0.45)
            b1 = Brace(eq[0], UP, buff=0.08, color=MUTED)
            b2 = Brace(eq[2], UP, buff=0.08, color=MUTED)
            t1 = T(r'wave out', font_size=24, color=MUTED).next_to(b1, UP, buff=0.05)
            t2 = T(r'echo back', font_size=24, color=MUTED).next_to(b2, UP, buff=0.05)
            self.play(FadeOut(same), Write(eq), run_time=1.4)
            self.play(GrowFromCenter(b1), GrowFromCenter(b2), FadeIn(t1), FadeIn(t2), run_time=0.9)
            first = Circle(radius=d6.s * 0.8, color=HL, stroke_width=4).move_to(d6.center(10, 1))
            fl = T(r'cell 1 learns $n$ at $t=10$', font_size=26, color=HL).next_to(first, LEFT, buff=0.25)
            self.play(Create(first), FadeIn(fl), run_time=0.9)

        with self.say('s4') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            Tf = 10
            hl = Diagram(sim.halfline(D14, Tf, 30), cell_px=int(0.36 / unit_px()))
            hl.mob.move_to(DOWN * 0.2)
            sup = T(r'suppose the line of length $n$ fired at some time $T<2n-2$', font_size=32)
            sup.to_edge(UP, buff=1.0)
            self.play(FadeIn(sup), run_time=0.9)
            hl.hide()
            self.add(hl.mob)
            self.play(hl.reveal(hl.rows_key(), run_time=max(2.0, d * 0.25)), rate_func=linear)
            lab = T(r'a much longer line', font_size=26, color=MUTED).next_to(hl.mob, UP, buff=0.15)
            self.play(FadeIn(lab), run_time=0.5)
            c1 = Circle(radius=hl.s * 0.85, color=BAD, stroke_width=4).move_to(hl.center(Tf, 1))
            c1l = T(r'cell 1 would fire at $T$', font_size=26, color=BAD).next_to(c1, DOWN, buff=0.2)
            c1l.align_to(hl.mob, LEFT)
            self.play(Create(c1), FadeIn(c1l), run_time=0.9)
            asleep = hl.column_region([(i, Tf, Tf) for i in range(Tf + 2, 31)], stroke_color=MUTED)
            al = T(r'\dots while these cells are still asleep', font_size=26, color=MUTED).next_to(asleep, DOWN,
                                                                                              buff=0.2)
            al.align_to(asleep, RIGHT)
            self.play(Create(asleep), FadeIn(al), run_time=1.0)
            no = T(r'not a synchronized firing', font_size=34, color=BAD).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(no, scale=1.2), run_time=0.8)

        with self.say('s5') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.7)
            big = M(r't \;\ge\; 2n-2', font_size=96).move_to(UP * 1.6)
            self.play(Write(big), run_time=1.4)
            lb = T(r'a hard lower bound', font_size=32, color=MUTED).next_to(big, DOWN, buff=0.3)
            self.play(FadeIn(lb), run_time=0.6)
            self.wait(max(0.1, d * 0.22 - 2.0))
            who = T(r'reached by Goto (1962) and Waksman (1966)', font_size=34, color=HL).next_to(lb, DOWN, buff=0.6)
            self.play(FadeIn(who, shift=0.1 * UP), run_time=1.0)
            self.wait(max(0.1, d * 0.2 - 1.0))
            dfn = VGroup(T(r'\textbf{minimal-time solution:} a rule that synchronizes', font_size=32),
                         T(r'the line of length $n$ at time exactly $2n-2$, for every $n\ge 2$', font_size=32))
            dfn.arrange(DOWN, buff=0.15)
            box = SurroundingRectangle(dfn, color=MUTED, buff=0.3, corner_radius=0.12, stroke_width=2)
            Group(dfn, box).next_to(who, DOWN, buff=0.6)
            self.play(Create(box), FadeIn(dfn), run_time=1.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S04_History(NarratedScene):
    def construct(self):
        chap = chapter_tag('3', 'How few states?')
        ks = [4, 5, 6, 7, 8, 16]
        xs = [-5.0, -3.0, -1.0, 1.0, 3.0, 5.6]
        axis = Line(LEFT * 6.3, RIGHT * 6.4, color=MUTED, stroke_width=2).shift(DOWN * 2.2)
        ticks = VGroup(*[M(str(k), font_size=40).move_to([x, -2.75, 0]) for k, x in zip(ks, xs)])
        dots = M(r'\cdots', font_size=40, color=MUTED).move_to([4.3, -2.75, 0])
        klab = T(r'number of states $k$', font_size=28, color=MUTED).next_to(axis, DOWN, buff=0.85)

        def stone(x, status, lines, color):
            sym = {'solved': r'\checkmark', 'impossible': r'\times', 'open': r'?'}[status]
            icon = M(sym, font_size=54, color=color)
            st = T(r'\textsf{%s}' % status, font_size=26, color=color)
            who = VGroup(*[T(l, font_size=24, color=TEXT) for l in lines]).arrange(DOWN, buff=0.08)
            g = VGroup(icon, st, who).arrange(DOWN, buff=0.15)
            return g.move_to([x, -0.6, 0])

        with self.say('h1') as d:
            self.play(FadeIn(chap), Create(axis), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(t, shift=0.2 * UP) for t in ticks], lag_ratio=0.1), FadeIn(dots),
                      FadeIn(klab), run_time=1.4)
            golf = T(r'like golf: the lower the score, the better', font_size=34, color=HL).to_edge(UP, buff=1.0)
            self.play(Write(golf), run_time=1.3)

        with self.say('h2') as d:
            entries = [(5, ['Waksman', '1966']), (4, ['Balzer', '1967']), (3, ['Gerken', '1987']),
                       (2, ['Mazoyer', '1987'])]
            times = [0.03, 0.2, 0.5, 0.72]
            stones = {}
            t0 = self.renderer.time
            for (j, who), frac in zip(entries, times):
                wait = t0 + frac * d - self.renderer.time
                if wait > 0.05:
                    self.wait(wait)
                stones[j] = stone(xs[j], 'solved', who, GOOD)
                self.play(FadeIn(stones[j], shift=0.25 * DOWN), ticks[j].animate.set_color(GOOD), run_time=0.9)
            rec = SurroundingRectangle(VGroup(stones[2], ticks[2]), color=HL, buff=0.2, corner_radius=0.1)
            recl = T(r'the record since 1987', font_size=26, color=HL).next_to(rec, UP, buff=0.15)
            self.play(Create(rec), FadeIn(recl), run_time=1.0)

        with self.say('h3') as d:
            self.play(FadeOut(rec), FadeOut(recl), FadeOut(golf), run_time=0.6)
            imp = stone(xs[0], 'impossible', [], BAD)
            self.play(FadeIn(imp, shift=0.25 * DOWN), ticks[0].animate.set_color(BAD), run_time=0.9)
            cites = VGroup(T(r'Balzer 1967: computer search', font_size=28),
                           T(r'Yun\`es 1993: lengths $2,\dots,9$ suffice', font_size=28),
                           T(r"Sanders 1994: Balzer's backtracking was incomplete;", font_size=28),
                           T(r'a corrected search confirms the result', font_size=28))
            cites.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to(UP * 2.3 + LEFT * 1.6)
            cites[3].shift(RIGHT * T(r'Sanders 1994: ', font_size=28).width)
            arrow = Arrow(cites.get_bottom() + LEFT * 2.2, imp.get_top() + UP * 0.05, color=BAD, stroke_width=3,
                          buff=0.1)
            t0 = self.renderer.time
            for k, frac in zip(range(4), (0.05, 0.3, 0.55, 0.62)):
                wait = t0 + frac * d - self.renderer.time
                if wait > 0.05:
                    self.wait(wait)
                self.play(FadeIn(cites[k], shift=0.1 * RIGHT), run_time=0.8)
            self.play(GrowArrow(arrow), run_time=0.7)

        with self.say('h4') as d:
            self.play(FadeOut(cites), FadeOut(arrow), run_time=0.6)
            q = stone(xs[1], 'open', ['since 1987'], HL)
            self.play(FadeIn(q, scale=1.3), ticks[1].animate.set_color(HL), run_time=1.0)
            self.play(Indicate(q[0], color=HL, scale_factor=1.4), run_time=1.2)
            many = T(r'many six-state solutions known today', font_size=28, color=MUTED).move_to(UP * 2.4)
            self.wait(max(0.1, d * 0.4 - 2.8))
            self.play(FadeIn(many), run_time=0.8)
            nob = VGroup(T(r'no five-state solution found', font_size=30),
                         T(r'no proof that none exists', font_size=30)).arrange(DOWN, buff=0.15)
            nob.next_to(many, DOWN, buff=0.35)
            self.play(FadeIn(nob[0]), run_time=0.7)
            self.play(FadeIn(nob[1]), run_time=0.7)

        with self.say('h5') as d:
            self.play(FadeOut(many), FadeOut(nob), run_time=0.6)
            box = VGroup(T(r'Balzer 1967 (computer search):', font_size=28, color=TEXT),
                         T(r'no five-state solution satisfies', font_size=28),
                         T(r'four extra conditions', font_size=28),
                         T(r'(his eight-state solution satisfies them)', font_size=24, color=MUTED))
            box.arrange(DOWN, buff=0.12)
            frame = SurroundingRectangle(box, color=HL, buff=0.25, corner_radius=0.12, stroke_width=2)
            call = VGroup(frame, box).move_to(UP * 2.2 + RIGHT * 0.2)
            line = Line(frame.get_bottom(), q.get_top() + UP * 0.05, color=HL, stroke_width=2)
            self.play(Create(frame), FadeIn(box), Create(line), run_time=1.4)
            self.wait(max(0.1, d * 0.55 - 2.0))
            later = T(r'checked with a certificate later in this video', font_size=26, color=HL)
            later.next_to(frame, RIGHT, buff=0.3)
            if later.get_right()[0] > 6.9:
                later.next_to(frame, DOWN, buff=0.15).shift(RIGHT * 3.2)
            self.play(FadeIn(later), run_time=0.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class S05_HowSolutionsWork(NarratedScene):
    def construct(self):
        chap = chapter_tag('4', 'How solutions work')
        X0, X1, Y0 = -5.0, 5.0, 2.6
        N = 1.0

        def P(x, t, H, tmax):
            return np.array([X0 + (X1 - X0) * x / N, Y0 - H * t / tmax, 0])

        with self.say('w1') as d:
            self.play(FadeIn(chap), run_time=0.6)
            ttl = T(r'divide and conquer', font_size=60)
            self.play(Write(ttl), run_time=1.4)

        H, TM = 5.6, 3.0
        with self.say('w2') as d:
            self.play(ttl.animate.scale(0.6).to_edge(UP, buff=0.3).shift(RIGHT * 2.5), run_time=0.8)
            bar = Line(P(0, 0, H, TM), P(N, 0, H, TM), color=MUTED, stroke_width=6)
            gdot = Dot(P(0, 0, H, TM), color=STATE_COLORS['G'], radius=0.12)
            ends = VGroup(T('cell 1', font_size=24, color=MUTED).next_to(bar.get_start(), UP, buff=0.15),
                          T('cell $n$', font_size=24, color=MUTED).next_to(bar.get_end(), UP, buff=0.15))
            tarrow = Arrow(P(0, 0, H, TM) + LEFT * 0.6, P(0, 0.9, H, TM) + LEFT * 0.6, buff=0, color=MUTED,
                           stroke_width=3)
            tl = T('time', font_size=24, color=MUTED).next_to(tarrow, LEFT, buff=0.1)
            rb = DashedLine(P(N, 0, H, TM), P(N, TM, H, TM), color=BAD, stroke_width=2, dash_length=0.08)
            lb = DashedLine(P(0, 0, H, TM), P(0, TM, H, TM), color=BAD, stroke_width=2, dash_length=0.08)
            self.play(Create(bar), FadeIn(gdot), FadeIn(ends), GrowArrow(tarrow), FadeIn(tl), Create(rb),
                      Create(lb), run_time=1.4)
            tt = ValueTracker(0)

            def hare_x(t):
                return t if t <= N else 2 * N - t
            hare = always_redraw(lambda: Dot(P(hare_x(tt.get_value()), tt.get_value(), H, TM), color=HL,
                                             radius=0.09))
            tort = always_redraw(lambda: Dot(P(tt.get_value() / 3, tt.get_value(), H, TM), color=GOOD,
                                             radius=0.09))
            hpath = always_redraw(lambda: VMobject(color=HL, stroke_width=4).set_points_as_corners(
                [P(0, 0, H, TM)] + ([P(N, N, H, TM)] if tt.get_value() > N else []) +
                [P(hare_x(tt.get_value()), tt.get_value(), H, TM)]))
            tpath = always_redraw(lambda: Line(P(0, 0, H, TM), P(tt.get_value() / 3, tt.get_value(), H, TM),
                                               color=GOOD, stroke_width=4))
            hl_ = T(r'hare: 1 cell per step', font_size=28, color=HL).move_to(P(0.62, 0.35, H, TM))
            tl_ = T(r'tortoise: 1 cell per 3 steps', font_size=28, color=GOOD).move_to(P(0.2, 1.25, H, TM)
                                                                                      ).shift(LEFT * 0.5)
            self.add(hpath, tpath, hare, tort)
            self.play(FadeIn(hl_), FadeIn(tl_), tt.animate.set_value(1.25 * N), run_time=max(4, d * 0.6),
                      rate_func=linear)
            where = T(r'where do they meet?', font_size=32, color=TEXT).move_to(P(0.75, 2.2, H, TM))
            self.play(FadeIn(where), run_time=0.7)

        with self.say('w3') as d:
            self.play(tt.animate.set_value(1.5 * N), run_time=2.0, rate_func=linear)
            hpath.clear_updaters(); tpath.clear_updaters(); hare.clear_updaters(); tort.clear_updaters()
            meet = Dot(P(0.5, 1.5, H, TM), color=STATE_COLORS['G'], radius=0.14)
            self.play(FadeOut(where), FadeIn(meet, scale=2), FadeOut(hare), FadeOut(tort), run_time=0.8)
            alg = VGroup(M(r'\tfrac{t}{3} \;=\; 2(n-1) - t', font_size=36),
                         M(r'\Rightarrow\ t=\tfrac32(n-1),\quad x=\tfrac{n-1}{2}', font_size=36))
            alg.arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(P(0.8, 2.55, H, TM))
            self.play(Write(alg[0]), run_time=1.4)
            self.play(Write(alg[1]), run_time=1.4)
            mid = T(r'the middle!', font_size=30, color=STATE_COLORS['G']).next_to(meet, DOWN, buff=0.3)
            self.play(FadeIn(mid), run_time=0.6)
            self.wait(max(0.1, d * 0.45 - 6.2))
            ng = T(r'a new general: two half-size squads', font_size=28, color=STATE_COLORS['G'])
            ng.next_to(mid, DOWN, buff=0.25)
            halves = VGroup(Line(P(0, 1.5, H, TM), P(0.495, 1.5, H, TM), color=STATE_COLORS['G'], stroke_width=5),
                            Line(P(0.505, 1.5, H, TM), P(1, 1.5, H, TM), color=STATE_COLORS['G'], stroke_width=5))
            self.play(FadeIn(ng), Create(halves), run_time=1.2)

        with self.say('w4') as d:
            self.play(FadeOut(VGroup(alg, mid, ng, hl_, tl_)), run_time=0.6)
            segs = VGroup()
            pieces = [(0.0, 0.5, 0.5)]           # (left, right, general position) at level 2
            t_start, L = 1.5, 0.5
            level_dots = VGroup()
            for level in range(4):
                new = []
                for a, b, g in pieces:
                    # signals from g into [a, b], reflected at the far end
                    far = a if g == b else b
                    m = (a + b) / 2
                    segs.add(Line(P(g, t_start, H, TM), P(far, t_start + L, H, TM), color=HL, stroke_width=2.5))
                    segs.add(Line(P(far, t_start + L, H, TM), P(m, t_start + 1.5 * L, H, TM), color=HL,
                                  stroke_width=2.5))
                    segs.add(Line(P(g, t_start, H, TM), P(m, t_start + 1.5 * L, H, TM), color=GOOD,
                                  stroke_width=2.5))
                    level_dots.add(Dot(P(m, t_start + 1.5 * L, H, TM), radius=0.07, color=STATE_COLORS['G']))
                    new += [(a, m, m), (m, b, m)]
                pieces = new
                t_start += 1.5 * L
                L /= 2
            # the right half, mirrored, uses the same picture
            right = VGroup(*[s.copy() for s in segs]).apply_function(
                lambda p: np.array([2 * P(0.5, 0, H, TM)[0] - p[0], p[1], p[2]]))
            rdots = level_dots.copy().apply_function(
                lambda p: np.array([2 * P(0.5, 0, H, TM)[0] - p[0], p[1], p[2]]))
            self.play(Create(segs), Create(right), FadeIn(level_dots), FadeIn(rdots), run_time=max(3, d * 0.45))
            fire = DashedLine(P(0, 3.0, H, TM), P(1, 3.0, H, TM), color=TEXT, stroke_width=3)
            fl = M(r't\approx 3n', font_size=36).next_to(fire, RIGHT, buff=0.2)
            ok = T(r'correct, but not minimal', font_size=30, color=BAD).next_to(fire, DOWN, buff=0.15)
            self.play(Create(fire), FadeIn(fl), run_time=1.0)
            self.play(FadeIn(ok), run_time=0.7)

        H2, TM2 = 5.6, 2.0
        with self.say('w5') as d:
            self.play(FadeOut(VGroup(segs, right, level_dots, rdots, fire, fl, ok, hpath, tpath, meet, halves, rb,
                                     lb)), run_time=0.8)
            rb2 = DashedLine(P(N, 0, H2, TM2), P(N, TM2, H2, TM2), color=BAD, stroke_width=2, dash_length=0.08)
            lb2 = DashedLine(P(0, 0, H2, TM2), P(0, TM2, H2, TM2), color=BAD, stroke_width=2, dash_length=0.08)
            frontl = VMobject(color=HL, stroke_width=4).set_points_as_corners(
                [P(0, 0, H2, TM2), P(N, N, H2, TM2), P(0, 2 * N, H2, TM2)])
            self.play(Create(rb2), Create(lb2), Create(frontl), run_time=1.6)
            sig, mdots, mlabs, slabs = VGroup(), VGroup(), VGroup(), VGroup()
            for j, (sp, nm) in enumerate(((3, r'\tfrac13'), (7, r'\tfrac17'), (15, r'\tfrac1{15}'))):
                x = 2 * N / 2 ** (j + 2)              # meeting point x = 2N / 2^j for speed 1/(2^j - 1)
                tm = 2 * N - x
                sig.add(Line(P(0, 0, H2, TM2), P(x, tm, H2, TM2), color=GOOD, stroke_width=3))
                mdots.add(Dot(P(x, tm, H2, TM2), radius=0.08, color=STATE_COLORS['G']))
                mlabs.add(M([r'\tfrac n2', r'\tfrac n4', r'\tfrac n8'][j], font_size=36,
                            color=STATE_COLORS['G']).next_to(mdots[-1], DR, buff=0.08))
                slabs.add(M(nm, font_size=28, color=GOOD).move_to(P(x * 0.55, tm * 0.55, H2, TM2) + UP * 0.25))
            self.play(LaggedStart(*[Create(s) for s in sig], lag_ratio=0.3), FadeIn(slabs), run_time=2.4)
            sp = T(r'speeds $\tfrac13,\ \tfrac17,\ \tfrac1{15},\ \dots$', font_size=30, color=GOOD)
            sp.move_to(P(0.78, 0.55, H2, TM2))
            self.play(FadeIn(sp), run_time=0.7)
            self.wait(max(0.1, d * 0.3 - 4.0))
            self.play(LaggedStart(*[FadeIn(m, scale=2) for m in mdots], lag_ratio=0.3), FadeIn(mlabs),
                      run_time=1.6)
            fire2 = DashedLine(P(0, 2.0, H2, TM2), P(1, 2.0, H2, TM2), color=TEXT, stroke_width=3)
            fl2 = M(r't=2n-2', font_size=36).next_to(fire2, RIGHT, buff=0.2)
            self.wait(max(0.1, d * 0.3 - 1.6))
            self.play(Create(fire2), FadeIn(fl2), run_time=1.0)
            allp = T(r'every piece fires at the same moment', font_size=28).next_to(fire2, DOWN, buff=0.15)
            self.play(FadeIn(allp), run_time=0.7)

        with self.say('w6') as d:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not chap])), run_time=0.8)
            n = 40
            dg = Diagram(sim.line(MAZ, n), height=7.1)
            dg.mob.move_to(LEFT * 3.4 + DOWN * 0.1)
            lab = T(r"Mazoyer's six-state rule, $n=40$", font_size=30).move_to(RIGHT * 2.6 + UP * 2.6)
            leg = legend(('L', 'G', 'A', 'B', 'C', 'F'), names={'L': '', 'G': '', 'F': ''}, size=0.3,
                         font_size=26).next_to(lab, DOWN, buff=0.35)
            dg.hide()
            self.add(dg.mob)
            self.play(FadeIn(lab), FadeIn(leg), run_time=0.8)
            self.play(dg.reveal(dg.rows_key(), run_time=max(4, d * 0.4)), rate_func=linear)
            gmask = (dg.idx == 1) | (dg.idx == 5)       # G and F cells
            gl = T(r'the generals (state \textsf{G}) mark the pieces', font_size=28, color=STATE_COLORS['G'])
            gl.next_to(leg, DOWN, buff=0.5)
            self.play(dg.focus(gmask, factor=0.18, run_time=1.4), FadeIn(gl))
            self.wait(max(0.1, d * 0.25 - 1.4))
            pr = VGroup(T(r'correct for every length: Mazoyer (1987)', font_size=28),
                        T(r'machine-checked proof in Coq: Duprat', font_size=28)).arrange(DOWN, buff=0.15)
            pr.next_to(gl, DOWN, buff=0.5)
            self.play(dg.focus(None, run_time=1.0), FadeIn(pr), run_time=1.0)

        with self.say('w7') as d:
            quote = VGroup(T(r'Mazoyer (1996): all the solutions he had built', font_size=28),
                           T(r'divide the line recursively, at ratios in $[\tfrac12,1)$', font_size=28))
            quote.arrange(DOWN, buff=0.12).move_to(RIGHT * 2.6 + DOWN * 1.2)
            self.play(FadeOut(pr), FadeOut(gl), FadeIn(quote), run_time=1.0)
            self.wait(max(0.1, d * 0.3 - 1.0))
            third = DashedLine(dg.corner(0, 1), dg.corner(dg.T, 1 + dg.T / 3), color=HL, stroke_width=3)
            tl3 = M(r'i=t/3', font_size=28, color=HL).next_to(third.get_end(), RIGHT, buff=0.1)
            wedge = Polygon(dg.corner(dg.T * 0.3, 1), dg.corner(dg.T, 1), dg.corner(dg.T, 1 + dg.T * 0.12),
                            color=HL, stroke_width=3, fill_color=HL, fill_opacity=0.22)
            tl3.move_to(third.get_start() + 0.55 * (third.get_end() - third.get_start()) + RIGHT * 0.45)
            third.set_stroke(width=5)
            self.play(dg.focus(np.zeros_like(gmask), factor=0.4, run_time=0.8))
            self.play(Create(third), FadeIn(tl3), run_time=1.2)
            self.play(FadeIn(wedge), run_time=1.0)
            note = VGroup(T(r'our barriers: some non-periodic structure', font_size=28, color=HL),
                          T(r'must appear along $i=t/3$ and near the left border', font_size=28, color=HL))
            note.arrange(DOWN, buff=0.12).next_to(quote, DOWN, buff=0.5)
            self.play(FadeIn(note), run_time=1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
