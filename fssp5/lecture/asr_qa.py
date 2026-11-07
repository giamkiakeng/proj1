"""asr_qa.py -- transcribe every narration sentence and compare it with the text the voice was given."""
import json, os, re, sys, time
import lecture_lib as L
from num2words import num2words
from faster_whisper import WhisperModel

def norm(s):
    s = s.lower().replace('-', ' ').replace('–', ' ')
    s = re.sub(r'(\d+)(st|nd|rd|th)\b', lambda m: num2words(int(m.group(1)), to='ordinal'), s)
    s = re.sub(r'\d+(\.\d+)?', lambda m: ' ' + num2words(float(m.group(0)) if '.' in m.group(0) else int(m.group(0))) + ' ', s)
    s = re.sub(r"[^a-z' ]", ' ', s)
    return s.split()

def wer(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
            prev, d[j] = d[j], cur
    return d[len(hyp)] / max(1, len(ref))

ch, beats = L.parse_script()
model = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=4)
out, t0 = [], time.time()
sents = [(b['id'], s['spoken']) for b in beats for p in b['paragraphs'] for s in p]
for k, (bid, sp) in enumerate(sents):
    wav = L.synth(sp)
    segs, _ = model.transcribe(wav, beam_size=5, language='en')
    hyp = ' '.join(x.text.strip() for x in segs)
    out.append({'beat': bid, 'spoken': sp, 'heard': hyp, 'wer': wer(norm(sp), norm(hyp))})
    if k % 50 == 0:
        print('%d/%d %.0f s' % (k, len(sents), time.time() - t0), flush=True)
json.dump(out, open('asr_qa.json', 'w'), indent=1)
bad = sorted(out, key=lambda r: -r['wer'])
print('mean WER %.3f; sentences with WER > 0.2: %d' % (sum(r['wer'] for r in out) / len(out), sum(r['wer'] > 0.2 for r in out)))
