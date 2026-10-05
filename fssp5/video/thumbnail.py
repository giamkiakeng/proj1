"""thumbnail.py -- the YouTube thumbnail (1280x720): Mazoyer's diagram firing, and the open case 5.

render: manim render -s -r 1280,720 --disable_caching --media_dir build/media_thumb thumbnail.py Thumbnail
"""
from manim import *

import fsspsim as sim
from common import BAD, GOOD, HL, MUTED, TEXT, Diagram, M, T


class Thumbnail(Scene):
    def construct(self):
        n = 24
        dg = Diagram(sim.line(sim.load_rule('mazoyer6'), n), height=7.2)
        dg.mob.move_to(LEFT * 4.55)
        self.add(dg.mob)
        five = M(r'5', font_size=330, color=HL)
        q = M(r'?', font_size=230, color=HL).next_to(five, RIGHT, buff=0.1).align_to(five, DOWN)
        big = VGroup(five, q).move_to(RIGHT * 2.55 + UP * 0.55)
        four = VGroup(M(r'4', font_size=150, color=BAD), M(r'\times', font_size=90, color=BAD)).arrange(DOWN, buff=0.1)
        six = VGroup(M(r'6', font_size=150, color=GOOD), M(r'\checkmark', font_size=90, color=GOOD)).arrange(DOWN, buff=0.1)
        four.next_to(big, LEFT, buff=0.55).align_to(big, UP).shift(DOWN * 0.35)
        six.next_to(big, RIGHT, buff=0.45).align_to(big, UP).shift(DOWN * 0.35)
        row = VGroup(four, big, six)
        lab = T(r'states', font_size=50, color=MUTED).next_to(row, DOWN, buff=0.25)
        sub = T(r'unsolved since 1987', font_size=66, color=TEXT).next_to(lab, DOWN, buff=0.3)
        self.add(four, big, six, lab, sub)
