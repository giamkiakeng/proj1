#!/usr/bin/env python3
"""build.py -- build the lecture video from the slides (lecture.tex) and the narration (script*.txt).

usage: build.py [--tex lecture.tex] [--out NAME] [--preset medium] [--crf 20] [--chapters 00,01,...]
                [--audio-only] [--no-video]
Writes NAME.mp4 (H.264 + AAC, English soft subtitles, chapters), NAME.srt, NAME.chapters.txt,
NAME.timeline.json and NAME.transcript.md into out/.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import wave

import lecture_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
ANIM_FPS = 15
PAD_START, GAP_SENT, GAP_PAR, PAD_END, PAD_CHAPTER_END = 0.35, 0.45, 0.90, 0.80, 1.50


def sh(cmd, **kw):
    r = subprocess.run(cmd, **kw)
    if r.returncode:
        raise SystemExit('command failed: %s' % ' '.join(cmd))
    return r


def compile_slides(tex):
    base = os.path.splitext(tex)[0]
    for _ in range(2):
        r = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', tex],
                           cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode:
            log = open(os.path.join(HERE, base + '.log'), errors='replace').read()
            i = log.find('\n!')
            raise SystemExit('pdflatex failed:\n' + log[i:i + 1500])
    log = open(os.path.join(HERE, base + '.log'), errors='replace').read()
    bad = [m for m in re.findall(r'(Overfull \\[hv]box \((\d+\.\d+)pt too \w+\)[^\n]*)', log) if float(m[1]) > 3]
    if bad:
        print('warning: %d overfull boxes > 3pt, e.g. %s' % (len(bad), bad[0][0]))
    if 'Reference' in log and 'undefined' in log:
        print('warning: undefined references in the slides')
    return os.path.join(HERE, base + '.pdf')


def rasterize(pdf, outdir):
    h = hashlib.sha1(open(pdf, 'rb').read()).hexdigest()[:12]
    d = os.path.join(outdir, 'pages_' + h)
    if not os.path.isdir(d):
        os.makedirs(d + '.tmp', exist_ok=True)
        sh(['pdftoppm', '-png', '-scale-to-x', '1920', '-scale-to-y', '1080', pdf, os.path.join(d + '.tmp', 'p')])
        os.rename(d + '.tmp', d)
    files = sorted(os.listdir(d), key=lambda s: int(re.search(r'(\d+)', s).group(1)))
    return [os.path.join(d, f) for f in files]


def silence(sec):
    return b'\x00\x00' * int(round(sec * L.SR))


def beat_audio(beat, is_chapter):
    """audio of one beat and the times of its sentences (relative to the beat start)"""
    pcm = bytearray(silence(PAD_START))
    cues = []
    for pi, par in enumerate(beat['paragraphs']):
        if pi:
            pcm += silence(GAP_PAR - GAP_SENT)
        for si, s in enumerate(par):
            if pi or si:
                pcm += silence(GAP_SENT)
            a = L.wav_frames(L.synth(s['spoken']))
            t0 = len(pcm) / 2 / L.SR
            pcm += a
            cues.append({'start': t0, 'end': len(pcm) / 2 / L.SR, 'text': s['display'], 'spoken': s['spoken']})
    pcm += silence(PAD_CHAPTER_END if is_chapter else PAD_END)
    return bytes(pcm), cues


def chunk_caption(text, maxlen=84):
    """split a caption into as few pieces of at most maxlen characters as possible, of balanced lengths
    (no short leftover piece), preferring breaks after a comma, semicolon or colon"""
    words = text.split()
    n = len(words)
    total = len(' '.join(words))
    if total <= maxlen:
        return [' '.join(words)]

    def seg(i, j):
        return len(' '.join(words[i:j]))

    k = -(-total // maxlen)
    while True:
        if k > n:                       # a single word longer than maxlen
            return words
        target = total / k
        best = {(0, 0): (0.0, None)}
        for j in range(1, n + 1):
            for m in range(1, k + 1):
                cand = None
                for i in range(j - 1, -1, -1):
                    if seg(i, j) > maxlen:
                        break
                    if (i, m - 1) not in best:
                        continue
                    c = best[(i, m - 1)][0] + (seg(i, j) - target) ** 2
                    if j < n and words[j - 1][-1] in ',;:':
                        c -= (0.3 * target) ** 2
                    if cand is None or c < cand[0]:
                        cand = (c, i)
                if cand:
                    best[(j, m)] = cand
        if (n, k) in best:
            out, j, m = [], n, k
            while m:
                i = best[(j, m)][1]
                out.append(' '.join(words[i:j]))
                j, m = i, m - 1
            return out[::-1]
        k += 1


def two_lines(s, width=42):
    if len(s) <= width:
        return s
    best = None
    for m in re.finditer(' ', s):
        k = m.start()
        score = abs(k - len(s) / 2)
        if best is None or score < best[0]:
            best = (score, k)
    k = best[1]
    return s[:k] + '\n' + s[k + 1:]


def srt_time(t):
    ms = int(round(t * 1000))
    return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tex', default='lecture.tex')
    ap.add_argument('--out', default='lecture')
    ap.add_argument('--preset', default='medium')
    ap.add_argument('--crf', default='20')
    ap.add_argument('--chapters', default=None, help='comma-separated chapter ids to include (test builds)')
    ap.add_argument('--no-video', action='store_true')
    ap.add_argument('--script', default=None, help='glob of script files (default script*.txt)')
    a = ap.parse_args()
    outdir = os.path.join(HERE, 'out')
    os.makedirs(outdir, exist_ok=True)

    import glob as _g
    chapters, beats = L.parse_script(sorted(_g.glob(os.path.join(HERE, a.script))) if a.script else None)
    pdf = compile_slides(a.tex)
    pb = L.page_beats(pdf)
    ids = [b['id'] for b in beats]
    if pb != ids:
        for i, (x, y) in enumerate(zip(pb, ids)):
            if x != y:
                raise SystemExit('slides and script differ at position %d: page beat %s, script beat %s' % (i + 1, x, y))
        raise SystemExit('slides have %d pages, the script %d beats' % (len(pb), len(ids)))
    pages = rasterize(pdf, outdir)
    assert len(pages) == len(beats)
    sel = set(a.chapters.split(',')) if a.chapters else None
    chap_title = {c['id']: c['title'] for c in chapters}

    # ---- audio, cues and timeline
    pcm = bytearray()
    timeline, cues = [], []
    for b, page in zip(beats, pages):
        if sel and b['chapter'] not in sel:
            continue
        is_ch = b['id'].startswith('ch')
        audio, bc = beat_audio(b, is_ch)
        t0 = len(pcm) / 2 / L.SR
        pcm += audio
        t1 = len(pcm) / 2 / L.SR
        timeline.append({'beat': b['id'], 'chapter': b['chapter'], 'start': t0, 'end': t1, 'page': page,
                         'anim': b['opts'].get('anim')})
        for c in bc:
            cues.append(dict(c, start=c['start'] + t0, end=c['end'] + t0))
    total = len(pcm) / 2 / L.SR
    wav = os.path.join(outdir, a.out + '.wav')
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(L.SR)
        w.writeframes(bytes(pcm))
    print('narration: %d beats, %d sentences, %.1f min' % (len(timeline), len(cues), total / 60))

    # ---- captions (SRT)
    srt, k = [], 1
    for c in cues:
        pieces = chunk_caption(c['text'])
        n = sum(len(p) for p in pieces)
        t = c['start']
        for p in pieces:
            dt = (c['end'] - c['start']) * len(p) / n
            srt.append('%d\n%s --> %s\n%s\n' % (k, srt_time(t), srt_time(t + dt), two_lines(p)))
            t += dt
            k += 1
    srt_path = os.path.join(outdir, a.out + '.srt')
    open(srt_path, 'w', encoding='utf-8').write('\n'.join(srt))

    # ---- chapters
    starts = []
    for e in timeline:
        if not starts or starts[-1][0] != e['chapter']:
            starts.append((e['chapter'], e['start']))
    meta = [';FFMETADATA1', 'title=Two barriers for minimal-time firing squads: a lecture',
            'artist=Lecture on the paper by Kia Keng Giam', 'language=eng']
    for i, (cid, st) in enumerate(starts):
        en = starts[i + 1][1] if i + 1 < len(starts) else total
        meta += ['[CHAPTER]', 'TIMEBASE=1/1000', 'START=%d' % int(st * 1000), 'END=%d' % int(en * 1000),
                 'title=Chapter %d: %s' % (int(cid), chap_title[cid]) if int(cid) else 'title=%s' % chap_title[cid]]
    chap_path = os.path.join(outdir, a.out + '.chapters.txt')
    open(chap_path, 'w').write('\n'.join(meta) + '\n')
    L.write_json(os.path.join(outdir, a.out + '.timeline.json'), {'total': total, 'beats': timeline, 'cues': cues})

    # ---- transcript
    md = ['# Two barriers for minimal-time firing squads — lecture transcript', '']
    cur = None
    for b in beats:
        if sel and b['chapter'] not in sel:
            continue
        if b['chapter'] != cur:
            cur = b['chapter']
            st = dict(starts)[cur]
            md += ['', '## %s. %s  (%d:%02d)' % (int(cur), chap_title[cur], st // 60, st % 60), '']
        for par in b['paragraphs']:
            md.append(' '.join(s['display'] for s in par))
            md.append('')
    open(os.path.join(outdir, a.out + '.transcript.md'), 'w', encoding='utf-8').write('\n'.join(md))
    if a.no_video:
        return

    # ---- video frames: pages and animations
    import anim
    from PIL import Image
    lines = ['ffconcat version 1.0']
    last = None
    for e in timeline:
        f0, f1 = round(e['start'] * FPS), round(e['end'] * FPS)
        if not e['anim']:
            lines += ["file '%s'" % e['page'], 'duration %.6f' % ((f1 - f0) / FPS)]
            last = e['page']
            continue
        page = Image.open(e['page']).convert('RGB')
        import numpy as np
        arr = np.asarray(page).astype(int)
        m = (arr[:, :, 0] > 240) & (arr[:, :, 1] < 20) & (arr[:, :, 2] > 240)
        ys, xs = np.nonzero(m)
        if not len(xs):
            raise SystemExit('beat %s: no animation box on its page' % e['beat'])
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        d = os.path.join(outdir, 'anim_' + e['beat'])
        os.makedirs(d, exist_ok=True)
        dur = (f1 - f0) / FPS
        frames = list(anim.ANIMS[e['anim']](x1 - x0, y1 - y0, dur, ANIM_FPS))
        nframes = len(frames)
        for i, fr in enumerate(frames):
            canvas = page.copy()
            canvas.paste(fr, (x0, y0))
            p = os.path.join(d, '%05d.png' % i)
            canvas.save(p, compress_level=1)
            # frame i covers [i, i+1)/ANIM_FPS, clipped to the beat
            fa, fb = round(e['start'] * FPS + i * FPS / ANIM_FPS), round(e['start'] * FPS + (i + 1) * FPS / ANIM_FPS)
            if i == nframes - 1:
                fb = f1
            fa, fb = max(fa, f0), min(fb, f1)
            if fb > fa:
                lines += ["file '%s'" % p, 'duration %.6f' % ((fb - fa) / FPS)]
                last = p
        print('animation %s: %d frames, %.1f s' % (e['anim'], nframes, dur))
    lines += ["file '%s'" % last]
    cc = os.path.join(outdir, a.out + '.ffconcat')
    open(cc, 'w').write('\n'.join(lines) + '\n')
    mp4 = os.path.join(outdir, a.out + '.mp4')
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-stats',
           '-f', 'concat', '-safe', '0', '-i', cc, '-i', wav, '-i', srt_path, '-i', chap_path,
           '-map', '0:v', '-map', '1:a', '-map', '2:s', '-map_metadata', '3', '-map_chapters', '3',
           '-c:v', 'libx264', '-preset', a.preset, '-crf', a.crf, '-tune', 'stillimage', '-pix_fmt', 'yuv420p',
           '-r', str(FPS), '-fps_mode', 'cfr', '-g', '300',
           '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '96k', '-ar', '48000',
           '-c:s', 'mov_text', '-metadata:s:s:0', 'language=eng', '-metadata:s:a:0', 'language=eng',
           '-t', '%.3f' % total, '-movflags', '+faststart', mp4]
    sh(cmd)
    print('wrote', mp4)


if __name__ == '__main__':
    main()
