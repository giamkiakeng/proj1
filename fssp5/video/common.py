"""common.py -- shared pieces of the Manim scenes: palette, narrated scenes, space-time diagrams."""
import contextlib
import json
import os

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, UL, ORIGIN, Create, FadeIn, FadeOut, ImageMobject, Line,
                   Polygon, Rectangle, RoundedRectangle, Scene, Tex, MathTex, UpdateFromAlphaFunc, VGroup,
                   Write, config, linear, smooth)
from manim.constants import RESAMPLING_ALGORITHMS

import fsspsim as sim

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')

# -- palette ------------------------------------------------------------------------------
# Working states G, A, B take the first three slots of the dataviz reference palette (dark
# steps), validated all-pairs on this background (CVD dE 9.4, normal-vision dE 20.9, all >= 3:1).
# C (six-state rules only) is a neutral grey, L a recessive slate, F a white flash.
BG = '#0b0d12'
config.background_color = BG
STATE_COLORS = {'L': '#2a2f3a', 'G': '#3987e5', 'A': '#d95926', 'B': '#199e70', 'C': '#a3a8b3',
                'F': '#f4f4f4', '*': BG}
TEXT = '#ece9e4'
MUTED = '#9b9a97'
HL = '#f7d96f'        # highlight (outlines, emphasis)
BAD = '#e66767'       # too early / refuted
GOOD = '#7bd389'      # verified
REGION = '#4fa3ff'    # region overlays

ORDER = 'LGABCF*'
LUT = np.zeros((len(ORDER) + 1, 4), np.uint8)
for k, s in enumerate(ORDER):
    h = STATE_COLORS[s]
    LUT[k] = (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 0 if s == '*' else 255)
# index len(ORDER) = "empty" (transparent)
EMPTY = len(ORDER)


def T(*s, **kw):
    """text in the video's text colour (LaTeX, as in 3b1b videos)"""
    kw.setdefault('color', TEXT)
    return Tex(*s, **kw)


def M(*s, **kw):
    kw.setdefault('color', TEXT)
    return MathTex(*s, **kw)


# -- narration --------------------------------------------------------------------------------
_MANIFEST = None


def manifest():
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = json.load(open(os.path.join(BUILD, 'audio', 'manifest.json')))
    return _MANIFEST


class NarratedScene(Scene):
    """Scene whose blocks are timed by the narration: `with self.say('c1') as d: ...` adds the
    audio of block c1 at the current time and pads the block with a wait until the audio
    (plus a short pause) has finished; d is the audio duration in seconds."""
    pause = 0.35

    def setup(self):
        self.blocks = {e['id']: e for e in manifest()[type(self).__name__]}
        self.cue_log = []

    @contextlib.contextmanager
    def say(self, bid, pause=None):
        e = self.blocks[bid]
        start = self.renderer.time
        self.add_sound(os.path.join(HERE, e['wav']))
        self.cue_log.append({'id': bid, 'start': round(start, 3), 'dur': e['dur']})
        yield e['dur']
        rest = e['dur'] + (self.pause if pause is None else pause) - (self.renderer.time - start)
        if rest > 1e-3:
            self.wait(rest)

    def tear_down(self):
        os.makedirs(os.path.join(BUILD, 'cues'), exist_ok=True)
        json.dump({'scene': type(self).__name__, 'duration': round(self.renderer.time, 3),
                   'blocks': self.cue_log},
                  open(os.path.join(BUILD, 'cues', type(self).__name__ + '.json'), 'w'), indent=1)


# -- space-time diagrams ----------------------------------------------------------------------
def to_index(rows, width=None):
    """state rows (lists of chars, None = empty) -> int array (T, W)"""
    W = width or max(len(r) for r in rows)
    idx = np.full((len(rows), W), EMPTY, np.int16)
    for t, r in enumerate(rows):
        for i, s in enumerate(r):
            if s is not None:
                idx[t, i] = ORDER.index(s)
    return idx


def unit_px():
    return config.frame_height / config.pixel_height


class Diagram:
    """A space-time diagram drawn as an image at native resolution: one square per cell and time
    step, time running downward, cell 1 on the left. Overlays use cell coordinates (t, i)."""

    def __init__(self, rows, height=None, width=None, gap=None, cell_px=None, idx=None, maxcell=48):
        self.idx = to_index(rows) if idx is None else idx
        self.T, self.W = self.idx.shape
        u = unit_px()
        if cell_px is None:
            c = []
            if height is not None:
                c.append(height / u / self.T)
            if width is not None:
                c.append(width / u / self.W)
            cell_px = max(1, int(min(c) if c else 8))
        self.cell = min(cell_px, maxcell)
        self.gap = (1 if self.cell >= 4 else 0) if gap is None else gap
        if self.cell >= 24 and gap is None:
            self.gap = 2
        self.full = self.render(self.idx)
        self.mob = ImageMobject(self.full.copy())
        self.mob.set_resampling_algorithm(RESAMPLING_ALGORITHMS['nearest'])
        self.mob.height = self.T * self.cell * u

    def render(self, idx):
        img = LUT[idx]
        c, g = self.cell, self.gap
        big = np.repeat(np.repeat(img, c, axis=0), c, axis=1)
        if g:
            big[c - g::c, :, 3] = 0
            for k in range(1, g):
                big[c - k::c, :, 3] = 0
            big[:, c - g::c, 3] = 0
            for k in range(1, g):
                big[:, c - k::c, 3] = 0
        return big

    # geometry ------------------------------------------------------------------------------
    @property
    def s(self):
        """cell size in scene units"""
        return self.mob.height / self.T

    def corner(self, t, i):
        """scene point of the upper-left corner of cell (t, i) (i 1-based); fractional ok"""
        ul = self.mob.get_corner(UL)
        return ul + RIGHT * (i - 1) * self.s + DOWN * t * self.s

    def center(self, t, i):
        return self.corner(t + 0.5, i + 0.5)

    def cells_outline(self, cells, **kw):
        """polygon around a set of cells given as a list of (t, i) staircase vertices (corners)"""
        pts = [self.corner(t, i) for t, i in cells]
        kw.setdefault('stroke_color', HL)
        kw.setdefault('stroke_width', 3)
        return Polygon(*pts, **kw)

    def antidiag(self, c, i0=1, i1=None, **kw):
        """line through the centres of the cells with t + i = c, for i0 <= i <= i1"""
        i1 = i1 or min(self.W, c)
        a = self.center(c - i0, i0)
        b = self.center(c - i1, i1)
        kw.setdefault('color', HL)
        return Line(a, b, **kw)

    # reveal animations --------------------------------------------------------------------
    def set_visible(self, mask):
        arr = self.full.copy()
        m = np.repeat(np.repeat(~mask, self.cell, axis=0), self.cell, axis=1)
        arr[m, 3] = 0
        self.mob.pixel_array = arr

    def reveal(self, key, run_time=2.0, rate_func=linear, start=None):
        """animate: cells appear in increasing order of key (array T x W), e.g. key = t for rows"""
        key = np.asarray(key, float)
        lo = key.min() if start is None else start
        hi = key.max()

        def upd(mob, a):
            self.set_visible(key <= lo + a * (hi - lo) + 1e-9)
        return UpdateFromAlphaFunc(self.mob, upd, run_time=run_time, rate_func=rate_func)

    def rows_key(self):
        return np.repeat(np.arange(self.T)[:, None], self.W, axis=1)

    def antidiag_key(self):
        t = np.arange(self.T)[:, None]
        i = np.arange(1, self.W + 1)[None, :]
        return np.broadcast_to(t + i, (self.T, self.W)).astype(float)

    def hide(self):
        self.set_visible(np.zeros((self.T, self.W), bool))

    def show_all(self):
        self.mob.pixel_array = self.full.copy()

    def recolor(self, idx):
        """replace the picture (same shape)"""
        self.idx = idx
        self.full = self.render(idx)
        self.mob.pixel_array = self.full.copy()

    # masks and highlighting ------------------------------------------------------------------
    def grid(self):
        """arrays t, i (1-based) of shape T x W"""
        return np.meshgrid(np.arange(self.T), np.arange(1, self.W + 1), indexing='ij')

    def focus(self, mask, factor=0.25, run_time=1.0):
        """animate: dim the cells outside mask (mask None: undo all dimming)"""
        target = self.full.copy() if mask is None else dim_outside(self, mask, factor)
        src = self.mob.pixel_array.copy().astype(np.float32)

        def upd(m, a):
            m.pixel_array = (src * (1 - a) + target.astype(np.float32) * a).astype(np.uint8)
        return UpdateFromAlphaFunc(self.mob, upd, run_time=run_time)

    def column_region(self, cols, **kw):
        """polygon around the cells (t, i), t0 <= t <= t1, for (i, t0, t1) in cols (i increasing)"""
        top, bot = [], []
        for i, t0, t1 in cols:
            top += [self.corner(t0, i), self.corner(t0, i + 1)]
            bot += [self.corner(t1 + 1, i), self.corner(t1 + 1, i + 1)]
        kw.setdefault('stroke_color', HL)
        kw.setdefault('stroke_width', 3)
        kw.setdefault('fill_opacity', 0)
        return Polygon(*(top + bot[::-1]), **kw)

    def triangle_R(self, n, **kw):
        """outline of the reflected triangle R_n = {t + i >= 2n-1, t <= 2n-2, i <= n}"""
        return self.column_region([(i, 2 * n - 1 - i, 2 * n - 2) for i in range(1, n + 1)], **kw)

    def above_antidiag(self, c, n, **kw):
        """outline of the cells with t + i <= c, 1 <= i <= n, t >= 0"""
        return self.column_region([(i, 0, c - i) for i in range(1, n + 1) if c - i >= 0], **kw)


def dim_outside(diagram, mask, factor=0.28):
    """a copy of the diagram's pixels with the cells outside `mask` dimmed (as a new array)"""
    arr = diagram.full.copy()
    m = np.repeat(np.repeat(~mask, diagram.cell, axis=0), diagram.cell, axis=1)
    arr[m, :3] = (arr[m, :3] * factor).astype(np.uint8)
    return arr


# -- a row of cells (the "soldiers") ----------------------------------------------------------
class CellRow(VGroup):
    """n rounded squares showing one configuration; letters optional"""

    def __init__(self, states, size=0.6, buff=0.1, letters=True, font_size=30, **kw):
        super().__init__(**kw)
        self.size, self.letters, self.font_size = size, letters, font_size
        self.boxes = VGroup(*[RoundedRectangle(width=size, height=size, corner_radius=size * 0.18,
                                               stroke_width=0, fill_opacity=1)
                              for _ in states]).arrange(RIGHT, buff=buff)
        self.add(self.boxes)
        self.labels = VGroup()
        self.add(self.labels)
        self.set_states(states)

    def set_states(self, states):
        self.states = list(states)
        for b, s in zip(self.boxes, states):
            b.set_fill(STATE_COLORS[s], opacity=1)
        if self.letters:
            new = VGroup(*[Tex(r'\textsf{%s}' % s, font_size=self.font_size,
                               color=BG if s in 'F' else (MUTED if s == 'L' else '#ffffff'))
                           .move_to(b) for b, s in zip(self.boxes, states)])
            self.remove(self.labels)
            self.labels = new
            self.add(self.labels)
        return self


def legend(states=('L', 'G', 'A', 'B', 'F'), names=None, size=0.32, font_size=26):
    names = names or {'L': 'quiescent', 'G': 'general', 'A': '', 'B': '', 'C': '', 'F': 'fire'}
    items = VGroup()
    for s in states:
        sq = RoundedRectangle(width=size, height=size, corner_radius=0.05, stroke_width=0,
                              fill_color=STATE_COLORS[s], fill_opacity=1)
        lab = Tex(r'\textsf{%s}' % s + ((r'\ \,' + names[s]) if names.get(s) else ''),
                  font_size=font_size, color=TEXT)
        items.add(VGroup(sq, lab.next_to(sq, RIGHT, buff=0.12)))
    return items.arrange(RIGHT, buff=0.4)


def chapter_card(scene, number, title, subtitle=None, run=1.2):
    """3b1b-style chapter title: number and title, then fade out"""
    num = Tex(r'\textsf{%s}' % number, font_size=34, color=MUTED)
    ttl = Tex(title, font_size=60, color=TEXT)
    grp = VGroup(num, ttl).arrange(DOWN, buff=0.3)
    if subtitle:
        grp.add(Tex(subtitle, font_size=32, color=MUTED).next_to(ttl, DOWN, buff=0.3))
    scene.play(FadeIn(grp, shift=0.2 * UP), run_time=run)
    return grp


def chapter_tag(number, title):
    """small chapter label in the upper-left corner"""
    from manim import UL as _UL
    g = VGroup(Tex(r'\textsf{%s}' % number, font_size=26, color=HL),
               Tex(title, font_size=28, color=MUTED)).arrange(RIGHT, buff=0.2)
    return g.to_corner(_UL, buff=0.35)


def cell_rows(rows, size=0.42, buff=0.06, font_size=18):
    """a small space-time diagram made of CellRows (with letters), time downward"""
    return VGroup(*[CellRow(r, size=size, buff=buff, font_size=font_size) for r in rows]).arrange(
        DOWN, buff=buff)
