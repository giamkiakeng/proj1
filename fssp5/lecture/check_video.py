#!/usr/bin/env python3
"""check_video.py -- checks of a built lecture video against its timeline.

For every beat, the frame in the middle of the beat is decoded from the MP4 and compared with the slide
page of that beat (beats with an animation are compared outside the animation box). Also compares the
durations of the streams with the timeline and lists the streams and chapters.

usage: check_video.py [--out NAME]
"""
import argparse
import json
import os
import subprocess

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def frame_at(mp4, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.3f' % t, '-i', mp4, '-frames:v', '1',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, check=True).stdout
    return small(Image.frombuffer('RGB', (1920, 1080), raw, 'raw', 'RGB', 0, 1))


def small(im):
    """a quarter-size copy (480 x 270) as an int16 array: enough to tell the slides apart"""
    return np.asarray(im.convert('RGB').resize((480, 270), Image.BOX)).astype(np.int16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='lecture')
    a = ap.parse_args()
    out = os.path.join(HERE, 'out')
    mp4 = os.path.join(out, a.out + '.mp4')
    tl = json.load(open(os.path.join(out, a.out + '.timeline.json')))
    probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_chapters', '-show_format',
                                       '-of', 'json', mp4], stdout=subprocess.PIPE, check=True).stdout)
    for s in probe['streams']:
        print('stream %d: %s %s %s %s s' % (s['index'], s['codec_type'], s['codec_name'],
                                            s.get('width', s.get('sample_rate', '')), s.get('duration')))
    print('format: %.3f s, %.1f MB; timeline: %.3f s' % (float(probe['format']['duration']),
                                                         int(probe['format']['size']) / 1e6, tl['total']))
    print('chapters: %d' % len(probe['chapters']))
    pages = [small(Image.open(e['page'])) for e in tl['beats']]
    worst, closer = [], []
    for k, e in enumerate(tl['beats']):
        t = (e['start'] + e['end']) / 2
        f = frame_at(mp4, t)
        p = pages[k]
        mask = np.ones(p.shape[:2], bool)
        if e['anim']:
            box = (p[:, :, 0] > 200) & (p[:, :, 1] < 60) & (p[:, :, 2] > 200)
            ys, xs = np.nonzero(box)
            mask[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3] = False
        d = np.abs(f - p)[mask].mean()
        worst.append((d, e['beat'], t))
        # the frame must be closer to its own page than to the pages of the neighbouring beats
        for j in (k - 1, k + 1):
            if 0 <= j < len(pages) and not np.array_equal(pages[j], p):
                dj = np.abs(f - pages[j])[mask].mean()
                if dj <= d:
                    closer.append((e['beat'], tl['beats'][j]['beat'], d, dj))
    worst.sort(reverse=True)
    print('frame vs page, mean absolute difference (0-255): max %.2f (%s at %.1f s), median %.2f'
          % (worst[0][0], worst[0][1], worst[0][2], worst[len(worst) // 2][0]))
    bad = [w for w in worst if w[0] > 6]
    print('beats whose middle frame differs from their page: %d' % len(bad))
    for w in bad[:10]:
        print('  %s at %.1f s: %.2f' % (w[1], w[2], w[0]))
    print('beats whose middle frame is as close to a neighbouring page: %d' % len(closer))
    for c in closer[:10]:
        print('  %s: own page %.2f, page of %s %.2f' % (c[0], c[2], c[1], c[3]))


if __name__ == '__main__':
    main()
