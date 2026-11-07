import time, lecture_lib as L
ch, beats = L.parse_script()
sents = [s['spoken'] for b in beats for p in b['paragraphs'] for s in p]
t = time.time()
for i, s in enumerate(sents):
    L.synth(s)
    if i % 50 == 0:
        print('%d/%d sentences, %.0f s' % (i, len(sents), time.time() - t), flush=True)
print('done: %d sentences in %.0f s' % (len(sents), time.time() - t), flush=True)
