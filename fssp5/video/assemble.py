#!/usr/bin/env python3
"""assemble.py -- join the rendered scenes into one video with subtitles and chapter markers.

Reads build/media_<Scene>/videos/<file>/<quality>/<Scene>.mp4, the narration manifest
(build/audio/manifest.json) and the block start times logged by each render (build/cues/<Scene>.json).
Writes build/five_state_question.mp4 (H.264 + AAC, soft English subtitles, chapters) and
build/five_state_question.srt.

usage: assemble.py [--quality=1080p30] [--crf=23] [--out=build/five_state_question]
"""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, 'build')
SCENES = [('S01_ColdOpen', 'The firing squad'), ('S02_Puzzle', '1 The puzzle'),
          ('S03_SpeedLimit', '2 A speed limit'), ('S04_History', '3 How few states?'),
          ('S05_HowSolutionsWork', '4 How solutions work'), ('S06_Haystack', '5 A cosmic haystack'),
          ('S07_HalfLine', '6 One half-line, many triangles'), ('S08_Pumping', '7 Barrier one: pumping'),
          ('S09_LeftBorder', '8 Barrier two: the left border'),
          ('S10_FourStates', '9 Four states, with a certificate'), ('S11_Frontier', '10 The five-state frontier'),
          ('S12_Germs', '11 Half-lines of low complexity'), ('S13_Balzer', "12 Balzer's conditions"),
          ('S14_Outlook', '13 Where this leaves us')]


def duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def ts(x):
    ms = int(round(x * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def main():
    q, crf, out = '1080p30', None, os.path.join(B, 'five_state_question')
    for a in sys.argv[1:]:
        if a.startswith('--quality='):
            q = a.split('=', 1)[1]
        elif a.startswith('--crf='):
            crf = a.split('=', 1)[1]
        elif a.startswith('--out='):
            out = a.split('=', 1)[1]
    manifest = json.load(open(os.path.join(B, 'audio', 'manifest.json')))
    files, cues, chapters, t = [], [], [], 0.0
    for scene, title in SCENES:
        mp4 = glob.glob(os.path.join(B, 'media_' + scene, 'videos', '*', q, scene + '.mp4'))
        if not mp4:
            sys.exit('missing render of %s at %s' % (scene, q))
        mp4 = mp4[0]
        dur = duration(mp4)
        log = json.load(open(os.path.join(B, 'cues', scene + '.json')))
        blocks = {e['id']: e for e in manifest[scene]}
        for b in log['blocks']:
            for s0, s1, text in blocks[b['id']]['cues']:
                cues.append((t + b['start'] + s0, t + b['start'] + s1, text))
        chapters.append((t, t + dur, title))
        files.append(mp4)
        t += dur
    with open(out + '.srt', 'w') as fh:
        for k, (a, b, text) in enumerate(cues, 1):
            fh.write('%d\n%s --> %s\n%s\n\n' % (k, ts(a), ts(b), text))
    meta = os.path.join(B, 'chapters.txt')
    with open(meta, 'w') as fh:
        fh.write(';FFMETADATA1\ntitle=The Five-State Question\n')
        for a, b, title in chapters:
            fh.write('[CHAPTER]\nTIMEBASE=1/1000\nSTART=%d\nEND=%d\ntitle=%s\n' % (a * 1000, b * 1000, title))
    lst = os.path.join(B, 'concat.txt')
    with open(lst, 'w') as fh:
        for f in files:
            fh.write("file '%s'\n" % f)
    vcodec = ['-c:v', 'copy'] if crf is None else ['-c:v', 'libx264', '-preset', 'slow', '-tune', 'animation',
                                                    '-crf', crf, '-pix_fmt', 'yuv420p']
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', out + '.srt',
           '-i', meta, '-map', '0:v', '-map', '0:a', '-map', '1:s', '-map_metadata', '2', '-map_chapters', '2',
           *vcodec, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
           '-c:s', 'mov_text', '-metadata:s:s:0', 'language=eng', '-movflags', '+faststart', out + '.mp4']
    subprocess.run(cmd, check=True)
    print('%s.mp4: %.1f min, %d subtitle cues, %d chapters, %.1f MB' % (
        out, t / 60, len(cues), len(chapters), os.path.getsize(out + '.mp4') / 1e6))


if __name__ == '__main__':
    main()
