#!/usr/bin/env python3
"""narration.py -- synthesize the narration of script.md with Kokoro (local, CPU).

Writes build/audio/<block>.wav (24 kHz mono) for every block and build/audio/manifest.json:
  {scene: [{"id": block, "wav": path, "dur": seconds, "cues": [[start, end, text], ...]}]}
with subtitle cues relative to the start of the block (one or more cues per sentence).

usage: narration.py [--voice=af_heart] [--speed=1.0] [--only=BLOCK,...]
"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'build', 'audio')
SR = 24000
GAP = 0.18            # silence between sentences (s)
OVERRIDE = re.compile(r'\[([^\]]+)\]\(/[^)]*/\)')


def parse(path=os.path.join(HERE, 'script.md')):
    """[(scene, [(block, spoken_text), ...]), ...] in script order"""
    scenes, scene, block, buf = [], None, None, []

    def flush():
        if block is not None:
            scene[1].append((block, ' '.join(buf).strip()))

    for ln in open(path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if ln.startswith('# Scene:'):
            flush()
            block, buf = None, []
            scene = (ln.split(':', 1)[1].strip(), [])
            scenes.append(scene)
        elif ln.startswith('## '):
            flush()
            block, buf = ln[3:].strip(), []
        elif block is not None and ln.strip() and not ln.startswith('>'):
            buf.append(ln.strip())
    flush()
    return scenes


def plain(text):
    """subtitle text: pronunciation hints removed"""
    return OVERRIDE.sub(r'\1', text)


def sentences(text):
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"\[])', text)
    return [p for p in parts if p.strip()]


def cue_split(text, start, end, width=84):
    """split a sentence into cues of at most `width` characters, timed by character count"""
    words, chunks, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            chunks.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        chunks.append(cur)
    total = sum(len(c) for c in chunks)
    cues, t = [], start
    for c in chunks:
        d = (end - start) * len(c) / total
        cues.append([round(t, 3), round(t + d, 3), c])
        t += d
    return cues


def main():
    voice, speed, only = 'af_heart', 1.0, None
    for a in sys.argv[1:]:
        if a.startswith('--voice='):
            voice = a.split('=', 1)[1]
        elif a.startswith('--speed='):
            speed = float(a.split('=', 1)[1])
        elif a.startswith('--only='):
            only = set(a.split('=', 1)[1].split(','))
    from kokoro import KPipeline
    pipe = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    os.makedirs(OUT, exist_ok=True)
    mpath = os.path.join(OUT, 'manifest.json')
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    for scene, blocks in parse():
        entries = {e['id']: e for e in manifest.get(scene, [])}
        for bid, text in blocks:
            if only and bid not in only and bid in entries:
                continue
            pieces, cues, t = [], [], 0.0
            for k, sent in enumerate(sentences(text)):
                audio = [np.asarray(a, dtype=np.float32) for _, _, a in pipe(sent, voice=voice, speed=speed)]
                a = np.concatenate(audio)
                d = len(a) / SR
                cues += cue_split(plain(sent), t, t + d)
                pieces.append(a)
                t += d
                pieces.append(np.zeros(int(GAP * SR), dtype=np.float32))
                t += GAP
            wav = np.concatenate(pieces)
            peak = float(np.max(np.abs(wav))) or 1.0
            wav = 0.89 * wav / peak
            fn = os.path.join(OUT, bid + '.wav')
            sf.write(fn, wav, SR)
            entries[bid] = {'id': bid, 'wav': os.path.relpath(fn, HERE), 'dur': round(len(wav) / SR, 3),
                            'cues': cues}
            print('%-22s %-4s %6.2f s' % (scene, bid, len(wav) / SR), flush=True)
        manifest[scene] = [entries[b] for b, _ in blocks if b in entries]
        json.dump(manifest, open(mpath, 'w'), indent=1)
    tot = sum(e['dur'] for v in manifest.values() for e in v)
    print('total narration %.1f s = %.1f min' % (tot, tot / 60))


if __name__ == '__main__':
    main()
