#!/usr/bin/env python3
"""extras.py -- companion files of the lecture: animation stills, the slide handout (PDF), and a
chapter list with timestamps (for video platforms).  Run after build.py (needs out/lecture.timeline.json)."""
import json
import os
import subprocess

import anim

HERE = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(HERE, 'out')
tl = json.load(open(os.path.join(out, 'lecture.timeline.json')))

# 1. stills: the last frame of each animation, at the size of its box
os.makedirs(os.path.join(HERE, 'stills'), exist_ok=True)
for name in anim.ANIMS:
    frames = list(anim.ANIMS[name](1680, 792, 12.0, 4))
    frames[-1].save(os.path.join(HERE, 'stills', name + '.png'))

# 2. the handout: the slides with the stills in place of the animation boxes
for _ in range(2):
    r = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'lecture_handout.tex'],
                       cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode:
        raise SystemExit('handout failed')
os.replace(os.path.join(HERE, 'lecture_handout.pdf'), os.path.join(out, 'lecture_slides.pdf'))

# 3. chapter list with timestamps
starts = []
for e in tl['beats']:
    if not starts or starts[-1][0] != e['chapter']:
        starts.append((e['chapter'], e['start']))
chap = [l.strip()[6:] for l in open(os.path.join(out, 'lecture.chapters.txt')) if l.startswith('title=Chapter') or l.strip() == 'title=Welcome']
lines = []
for (cid, st), title in zip(starts, chap):
    s = int(st)
    stamp = '%d:%02d:%02d' % (s // 3600, s // 60 % 60, s % 60) if tl['total'] >= 3600 else '%02d:%02d' % (s // 60, s % 60)
    lines.append('%s %s' % (stamp, title))
open(os.path.join(out, 'lecture_chapters.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))

# 4. a description for a video platform: summary, chapters, links
mins = int(tl['total'] / 60 + 0.5)
desc = """Two barriers for minimal-time firing squads: a lecture

A narrated lecture (%d minutes) on the paper "Two barriers for minimal-time firing squads, with \
applications to four and five states" by Kia Keng Giam, accepted for publication in the Journal of \
Cellular Automata. It explains every result of the paper, from the firing squad synchronization problem \
itself to the certified computer proofs. Chapters 1-3 need no mathematics; chapters 4-8 explain the \
proofs; chapters 9-13 explain the computer-assisted results and how they are checked; chapter 14 lists \
the open questions.

The narration uses a computer-generated clone of the author's voice, made from recordings of the author \
(Qwen3-TTS). English captions are included.

Chapters
%s

Supplementary material (programs, rule tables, formulas):
https://github.com/giamkiakeng/proj1/tree/8f3996cc242690d139bac913f5de652914ecb5ae/fssp5/paper/supplementary
All data, including the LRAT proofs: https://doi.org/10.5281/zenodo.24002680
""" % (mins, '\n'.join(lines))
open(os.path.join(out, 'lecture_description.txt'), 'w').write(desc)
