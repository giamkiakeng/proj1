"""lecture_lib.py -- script parsing, speech synthesis, page/beat mapping and timing for the lecture.

Script format (script*.txt, read in file-name order):
    # CHAPTER <id> | <title>
    @ <beat-id> [anim=<name>]
    narration ...            (paragraphs separated by blank lines)
Markup in narration: {display|spoken}  -- captions show `display`, the voice says `spoken`.
A global pronunciation table (SPOKEN) is applied to the spoken text only.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.environ.get('PIPER_VOICE') or os.path.join(HERE, 'voices', 'en_US-ryan-high.onnx')
LENGTH_SCALE = 1.20
CACHE = os.path.join(HERE, 'cache_tts')
SR = 22050

# pronunciation for the voice only (captions keep the written form); applied as whole words
SPOKEN = [
    ('Mazoyer', 'Mazwah-yay'), ('Yunès', 'You-ness'), ('Myhill', 'My-hill'), ('Goto', 'Go-toe'),
    ('CaDiCaL', 'Kah-dee-kal'), ('Kissat', 'Kiss-at'), ('drat-trim', 'D-RAT trim'),
    ('lrat-check', 'L-RAT check'), ('cake_lpr', 'Cake L P R'), ('LRAT', 'L-RAT'), ('DRAT', 'D-RAT'),
    ('HOL4', 'hol four'), ('CakeML', 'Cake M L'), ('SAT', 'sat'), ('Zenodo', 'Zen-oh-doe'),
    ('GitHub', 'Git-hub'), ('SHA-256', 'S H A two fifty-six'), ('PUMP', 'pump'), ('Duprat', 'Dew-prah'), ('Balzer', 'Bal-zer'), ('Gerken', 'Gher-ken'),
    ('Umeo', 'Oo-meh-oh'), ('Sanders', 'Sanders'), ('δ₁₂', 'delta twelve'), ('δ₁₃', 'delta thirteen'),
    ('δ₁₄ᵇ', 'delta fourteen b'), ('δ₁₄ᶜ', 'delta fourteen c'), ('δ₁₄ᵈ', 'delta fourteen d'),
    ('δ₁₄ᵉ', 'delta fourteen e'), ('δ₁₄', 'delta fourteen'),
]


# for a narrator that reads plain English (voice_take.py): symbols and acronyms only, no respelled names;
# letter-digit labels (B1, G4) are split so that the digit is read as a number
CLONE_SPOKEN = [
    ('drat-trim', 'DRAT trim'), ('lrat-check', 'LRAT check'), ('cake_lpr', 'cake L P R'), ('HOL4', 'HOL four'),
    ('CakeML', 'Cake M L'), ('SHA-256', 'S H A two fifty-six'), ('PUMP', 'pump'), ('SAT', 'sat'),
    ('δ₁₂', 'delta twelve'), ('δ₁₃', 'delta thirteen'), ('δ₁₄ᵇ', 'delta fourteen b'), ('δ₁₄ᶜ', 'delta fourteen c'),
    ('δ₁₄ᵈ', 'delta fourteen d'), ('δ₁₄ᵉ', 'delta fourteen e'), ('δ₁₄', 'delta fourteen'),
    # respelled only where the clone's audio (phoneme check) proved the plain spelling wrong
    ('Mazoyer', 'Mah-zwah-yay'), ('LRAT', 'L-RAT'), ('DRAT', 'D-RAT'), ('Zenodo', 'Zen-oh-doe'),
]
# what the speech recognizer writes for those respellings, so that the narrator's re-listen accepts them
CLONE_HEARD = {
    'Mah-zwah-yay': ['ma soie', 'maswaye', 'mazwaye', 'mazoya', 'maths ya', 'ma swa ye', 'mazwa ye', 'mazoyer'],
    'L-RAT': ['lret', 'lrat', 'l ret', 'el rat', 'l red', 'larrat', 'el ret', 'elrat'],
    'D-RAT': ['dred', 'd red', 'drat', 'dee rat', 'd ret', 'dee red'],
    'Zen-oh-doe': ['zenodo', 'zen odo', 'zenoda', 'zen oh doe'],
}


def spoken_form(text, table=None):
    s = re.sub(r'\{([^{}|]*)\|([^{}]*)\}', lambda m: m.group(2), text)
    for a, b in (SPOKEN if table is None else table):
        s = re.sub(r'(?<![\w-])' + re.escape(a) + r'(?![\w])', b, s)
    if table is CLONE_SPOKEN:
        s = re.sub(r'\b([A-Z])([0-9])\b', r'\1 \2', s)
    return s


def display_form(text):
    return re.sub(r'\{([^{}|]*)\|([^{}]*)\}', lambda m: m.group(1), text)


def split_sentences(par):
    """split a paragraph into sentences, keeping {..|..} groups intact"""
    out, buf, depth = [], '', 0
    i = 0
    while i < len(par):
        ch = par[i]
        buf += ch
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch in '.?!' and depth == 0:
            nxt = par[i + 1] if i + 1 < len(par) else ' '
            if nxt in ' \n' and not re.search(r'(?:\be\.g|\bi\.e|\bvs|\bProf|\bDr|\bSec|\bFig|\bet al)\.$', buf):
                out.append(buf.strip())
                buf = ''
        i += 1
    if buf.strip():
        out.append(buf.strip())
    return out


def parse_script(paths=None):
    paths = paths or sorted(glob.glob(os.path.join(HERE, 'script*.txt')))
    chapters, beats, cur, beat = [], [], None, None
    for p in paths:
        for raw in open(p, encoding='utf-8'):
            line = raw.rstrip('\n')
            if line.startswith('%%'):
                continue
            m = re.match(r'^# CHAPTER (\S+) \| (.*)$', line)
            if m:
                cur = {'id': m.group(1), 'title': m.group(2).strip()}
                chapters.append(cur)
                continue
            m = re.match(r'^@ (\S+)(.*)$', line)
            if m:
                opts = dict(kv.split('=', 1) for kv in m.group(2).split() if '=' in kv)
                beat = {'id': m.group(1), 'chapter': cur['id'], 'opts': opts, 'text': ''}
                beats.append(beat)
                continue
            if beat is not None:
                beat['text'] += line + '\n'
    for b in beats:
        pars = [re.sub(r'\s+', ' ', q).strip() for q in re.split(r'\n\s*\n', b['text']) if q.strip()]
        b['paragraphs'] = [[{'display': display_form(s), 'spoken': spoken_form(s), 'raw': s} for s in split_sentences(q)]
                           for q in pars]
    ids = [b['id'] for b in beats]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    if dup:
        raise SystemExit('duplicate beat ids: %s' % dup)
    return chapters, beats


_voice = None


def synth(text):
    """synthesize one sentence (cached); returns the wav path"""
    global _voice
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(('%s|%s|%s' % (os.path.basename(VOICE), LENGTH_SCALE, text)).encode()).hexdigest()
    path = os.path.join(CACHE, key + '.wav')
    if not os.path.exists(path):
        if _voice is None:
            from piper import PiperVoice
            _voice = PiperVoice.load(VOICE)
        from piper import SynthesisConfig
        tmp = path + '.%d.tmp' % os.getpid()
        with wave.open(tmp, 'wb') as w:
            _voice.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=LENGTH_SCALE))
        os.replace(tmp, path)
    return path


def wav_frames(path):
    with wave.open(path, 'rb') as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2, path
        return w.readframes(w.getnframes())


def page_beats(pdf):
    """the beat id on each page of the slide PDF"""
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.check_output(['pdfinfo', pdf]).decode()).group(1))
    txt = subprocess.check_output(['pdftotext', '-layout', pdf, '-']).decode('utf-8', 'replace').split('\f')
    out = []
    for i in range(n):
        ms = sorted(set(re.findall(r'BEAT:([A-Za-z0-9_.\-]+):END', txt[i])))
        if len(ms) != 1:
            raise SystemExit('page %d has beat markers %s' % (i + 1, ms))
        out.append(ms[0])
    return out


def write_json(path, obj):
    with open(path, 'w') as fh:
        json.dump(obj, fh, indent=1)
