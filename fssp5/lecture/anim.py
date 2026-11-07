"""anim.py -- animations of the rules, drawn into the magenta box of a slide page.

Each animation is a function (box_w, box_h, duration, fps) -> iterator of PIL images of the box size.
The rules are simulated from the transition tables of the supplementary material (rules/*.txt).
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
COL = {'L': (255, 255, 255), 'G': (0x1A, 0x26, 0x38), 'A': (0x7C, 0x9D, 0xC2), 'B': (0xC6, 0xD5, 0xE6),
       'C': (0x3F, 0x68, 0x94), 'F': (0xE8, 0x65, 0x0E)}
TXT = {'L': (60, 60, 60), 'G': (255, 255, 255), 'A': (255, 255, 255), 'B': (30, 30, 30), 'C': (255, 255, 255),
       'F': (255, 255, 255)}
INK = (17, 17, 17)
GRID = (138, 138, 138)
MUTE = (91, 101, 115)
ACCENT = (0xE8, 0x65, 0x0E)
NAMES = {'L': 'L  quiescent', 'G': 'G  general', 'A': 'A', 'B': 'B', 'C': 'C', 'F': 'F  firing'}


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


def load_rule(name):
    tab = {}
    for ln in open(os.path.join(HERE, 'rules', name + '.txt')):
        w = ln.split('#')[0].split()
        if len(w) == 4 and w[0] != 'k':
            tab[tuple(w[:3])] = w[3]
    return tab


def simulate_line(tab, n, tmax):
    """rows[t] for t = 0..; stops after the first row that contains F (or at tmax)"""
    rows = [['G'] + ['L'] * (n - 1)]
    while len(rows) <= tmax:
        if 'F' in rows[-1]:
            break
        r = ['*'] + rows[-1] + ['*']
        rows.append([tab[tuple(r[i - 1:i + 2])] for i in range(1, n + 1)])
    return rows


def draw_cells(d, x0, y0, row, cs, letters=False, f=None, outline=GRID):
    for i, s in enumerate(row):
        x = x0 + i * cs
        d.rectangle([x, y0, x + cs - 1, y0 + cs - 1], fill=COL[s], outline=outline)
        if letters:
            w = d.textlength(s, font=f)
            d.text((x + (cs - w) / 2, y0 + cs * 0.14), s, fill=TXT[s], font=f)


def legend(d, x, y, states, f, sw=28, gap=34):
    for s in states:
        d.rectangle([x, y, x + sw, y + sw], fill=COL[s], outline=GRID)
        d.text((x + sw + 10, y + 1), NAMES[s], fill=INK, font=f)
        x += sw + 10 + d.textlength(NAMES[s], font=f) + gap


def schedule(duration, fps, nsteps, hold0=2.0, hold1=4.0):
    """step index shown at each frame: hold the start, advance evenly, hold the end"""
    nf = max(1, round(duration * fps))
    run = max(0.5, duration - hold0 - hold1)
    out = []
    for k in range(nf):
        t = k / fps
        if t < hold0:
            out.append(0)
        else:
            out.append(min(nsteps, int((t - hold0) / run * nsteps) + 1) if nsteps else 0)
    return out


def mazoyer24(W, H, duration, fps):
    tab = load_rule('mazoyer6')
    n = 24
    rows = simulate_line(tab, n, 2 * n - 2)
    T = len(rows) - 1                                    # 46
    cs = (H - 70) // (T + 1)                             # small cells of the diagram
    fsm, fmd, flg = font(22), font(26), font(30, True)
    dx0, dy0 = 70, 40
    bx0 = dx0 + n * cs + 120
    big = min(54, (W - bx0 - 30) // n)
    for step in schedule(duration, fps, T):
        im = Image.new('RGB', (W, H), (255, 255, 255))
        d = ImageDraw.Draw(im)
        d.text((dx0 - 60, dy0 - 34), 'space-time diagram (time runs down)', fill=MUTE, font=fsm)
        for t in range(step + 1):
            draw_cells(d, dx0, dy0 + t * cs, rows[t], cs, outline=None)
        d.rectangle([dx0 - 1, dy0 - 1, dx0 + n * cs, dy0 + (T + 1) * cs], outline=GRID)
        d.text((dx0 - 62, dy0 - 4), 't = 0', fill=INK, font=fsm)
        d.text((dx0 - 66, dy0 + T * cs - 6), 't = 46', fill=INK, font=fsm)
        if step:
            y = dy0 + step * cs
            d.polygon([(dx0 + n * cs + 6, y + cs // 2), (dx0 + n * cs + 22, y - 4), (dx0 + n * cs + 22, y + cs + 4)],
                      fill=ACCENT)
        # the line itself, large, with the letters of the states
        d.text((bx0, dy0 - 4), 'the line of 24 cells at time t = %d' % step, fill=INK, font=flg)
        by = dy0 + 60
        draw_cells(d, bx0, by, rows[step], big, letters=True, f=fmd, outline=GRID)
        d.text((bx0, by + big + 12), 'cell 1', fill=MUTE, font=fsm)
        w = d.textlength('cell 24', font=fsm)
        d.text((bx0 + n * big - w, by + big + 12), 'cell 24', fill=MUTE, font=fsm)
        legend(d, bx0, by + big + 70, ['L', 'G', 'A', 'B', 'C', 'F'], fsm)
        if step == T:
            msg = 'All 24 cells fire together at t = 2n − 2 = 46'
            d.rounded_rectangle([bx0 - 10, by + big + 140, bx0 + 20 + d.textlength(msg, font=flg), by + big + 210], radius=10, fill=ACCENT)
            d.text((bx0 + 10, by + big + 155), msg, fill=(255, 255, 255), font=flg)
        elif step:
            d.text((bx0, by + big + 150), 'no cell may fire before every cell does', fill=MUTE, font=fmd)
        yield im


def delta14(W, H, duration, fps):
    tab = load_rule('delta14')
    r14 = simulate_line(tab, 14, 26)
    r15 = simulate_line(tab, 15, 28)                     # stops at t = 22 (cells 13-15 fire)
    TT = 28
    cs = (H - 120) // (TT + 1)
    fsm, fmd, flg = font(22), font(24), font(28, True)
    xA, xB, y0 = 150, 150 + 14 * cs + 330, 70
    end15 = len(r15) - 1                                 # 22
    for step in schedule(duration, fps, 26, hold0=2.0, hold1=5.0):
        im = Image.new('RGB', (W, H), (255, 255, 255))
        d = ImageDraw.Draw(im)
        d.text((xA, 10), 'line of length 14', fill=INK, font=flg)
        d.text((xB, 10), 'line of length 15', fill=INK, font=flg)
        for x0, rows, n in ((xA, r14, 14), (xB, r15, 15)):
            for t in range(min(step, len(rows) - 1) + 1):
                draw_cells(d, x0, y0 + t * cs, rows[t], cs, outline=None)
            d.rectangle([x0 - 1, y0 - 1, x0 + n * cs, y0 + (TT + 1) * cs], outline=GRID)
            for t in (0, 22, 26, 28):
                d.text((x0 - 80, y0 + t * cs - 4), 't = %d' % t, fill=MUTE, font=fsm)
        # minimal times 2n - 2: 26 and 28 (dashed)
        for x0, n, tm in ((xA, 14, 26), (xB, 15, 28)):
            yy = y0 + tm * cs + cs // 2
            for xx in range(x0 - 10, x0 + n * cs + 10, 16):
                d.line([xx, yy, xx + 8, yy], fill=ACCENT, width=3)
            d.text((x0 + n * cs + 16, yy - 13), '2n − 2 = %d' % tm, fill=ACCENT, font=fsm)
        tx = 1000
        if step >= end15:
            yy = y0 + end15 * cs
            d.rectangle([xB + 12 * cs - 3, yy - 3, xB + 15 * cs + 2, yy + cs + 2], outline=(200, 0, 0), width=4)
            d.text((xB + 15 * cs + 16, yy - 6), 'cells 13–15 fire at t = 22', fill=(200, 0, 0), font=fmd)
            d.text((xB + 15 * cs + 16, yy + 24), 'six steps too early', fill=(200, 0, 0), font=fmd)
        if step >= 26:
            yy = y0 + 26 * cs
            d.text((xA + 14 * cs + 16, yy - 40), 'all 14 cells fire', fill=(0x2E, 0x7D, 0x32), font=fmd)
        yield im


def front_echo(W, H, duration, fps):
    """a signal from the general to the far end and back: 2n - 2 steps, on the line of length 24"""
    n = 24
    cs = min(60, (W - 80) // n)
    x0, y0 = (W - n * cs) // 2, 260
    f, fb, fs = font(30), font(34, True), font(24)
    steps = 2 * n - 2
    for step in schedule(duration, fps, steps, hold0=2.0, hold1=4.0):
        im = Image.new('RGB', (W, H), (255, 255, 255))
        d = ImageDraw.Draw(im)
        pos = step if step <= n - 1 else 2 * (n - 1) - step         # 0-based cell of the signal
        going = step <= n - 1
        for i in range(n):
            fill = COL['G'] if i == 0 else (255, 255, 255)
            d.rectangle([x0 + i * cs, y0, x0 + (i + 1) * cs - 1, y0 + cs - 1], fill=fill, outline=GRID, width=2)
        d.text((x0, y0 + cs + 14), 'general (cell 1)', fill=MUTE, font=fs)
        far = 'far end (cell n = %d)' % n
        w = d.textlength(far, font=fs)
        d.text((x0 + n * cs - w, y0 + cs + 14), far, fill=MUTE, font=fs)
        cx, cy = x0 + pos * cs + cs // 2, y0 + cs // 2
        col = ACCENT if going else (0x2E, 0x7D, 0x32)
        r = cs * 0.28
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        lab = 'the order travels right: %d of n − 1 = %d steps' % (min(step, n - 1), n - 1) if going else \
            'the news "the line ends here" travels back: %d of %d steps' % (step - (n - 1), n - 1)
        d.text((x0, 110), 'time t = %d' % step, fill=INK, font=fb)
        d.text((x0, 170), lab, fill=col, font=f)
        if step == steps:
            msg = 'back at the general after (n − 1) + (n − 1) = 2n − 2 = %d steps' % steps
            d.rounded_rectangle([x0, 480, x0 + 40 + d.textlength(msg, font=fb), 560], radius=10, fill=ACCENT)
            d.text((x0 + 20, 500), msg, fill=(255, 255, 255), font=fb)
        yield im


ANIMS = {'mazoyer24': mazoyer24, 'delta14': delta14, 'front_echo': front_echo}
