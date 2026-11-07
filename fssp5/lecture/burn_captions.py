#!/usr/bin/env python3
"""burn_captions.py -- a second version of the lecture with the English captions burned into the picture,
for players that do not show soft subtitles (for example most web browsers).

The slide is scaled to 13/15 of its size and placed at the top; the captions are drawn in the band below
it, so they never cover the slide.  Reads out/NAME.mp4 and out/NAME.srt (from build.py) and writes
out/NAME_captioned.mp4 (H.264 + AAC, chapters kept).

usage: burn_captions.py [--out NAME] [--preset medium] [--crf 20]
"""
import argparse
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080
SW, SH = 1664, 936            # the scaled slide: 13/15 of 1920 x 1080
BAND = 'black'                # caption band and side bars


def srt_cues(path):
    """(start, end, text) from an SRT file; times in seconds"""
    def sec(s):
        h, m, rest = s.split(':')
        x, ms = rest.split(',')
        return int(h) * 3600 + int(m) * 60 + int(x) + int(ms) / 1000
    out = []
    for block in re.split(r'\n\s*\n', open(path, encoding='utf-8').read().strip()):
        lines = block.split('\n')
        a, b = lines[1].split(' --> ')
        out.append((sec(a.strip()), sec(b.strip()), '\n'.join(lines[2:])))
    return out


def ass_time(t):
    cs = int(round(t * 100))
    return '%d:%02d:%02d.%02d' % (cs // 360000, cs // 6000 % 60, cs // 100 % 60, cs % 100)


def write_ass(cues, path):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Sans,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,40,40,22,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (W, H)
    ev = []
    for a, b, text in cues:
        t = text.replace('\\', '\\\\').replace('{', '(').replace('}', ')').replace('\n', '\\N')
        ev.append('Dialogue: 0,%s,%s,Cap,,0,0,0,,%s' % (ass_time(a), ass_time(b), t))
    open(path, 'w', encoding='utf-8').write(head + '\n'.join(ev) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='lecture')
    ap.add_argument('--preset', default='medium')
    ap.add_argument('--crf', default='20')
    a = ap.parse_args()
    outdir = os.path.join(HERE, 'out')
    src = os.path.join(outdir, a.out + '.mp4')
    ass = os.path.join(outdir, a.out + '.ass')
    write_ass(srt_cues(os.path.join(outdir, a.out + '.srt')), ass)
    dst = os.path.join(outdir, a.out + '_captioned.mp4')
    vf = ('scale=%d:%d:flags=lanczos,pad=%d:%d:%d:0:color=%s,ass=%s'
          % (SW, SH, W, H, (W - SW) // 2, BAND, ass.replace(':', '\\:')))
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-stats', '-i', src,
           '-map', '0:v', '-map', '0:a', '-map_metadata', '0', '-map_chapters', '0', '-vf', vf,
           '-c:v', 'libx264', '-preset', a.preset, '-crf', a.crf, '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
           '-g', '300', '-c:a', 'copy', '-movflags', '+faststart', dst]
    r = subprocess.run(cmd)
    if r.returncode:
        raise SystemExit('ffmpeg failed')
    print('wrote', dst)


if __name__ == '__main__':
    main()
