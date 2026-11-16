#!/usr/bin/env python3
"""hunt_run.py PREFIXFILE OUTDIR WORKERS K N [options of gsat.py] -- first pass of a tree search, one job per prefix.

Job j runs gsat.py K N OPTIONS --prefix <line j of PREFIXFILE> --cubes OUTDIR/cubes_j.txt --out OUTDIR/model_j and
writes OUTDIR/job_j.log; a job whose log already has a '# RESULT' line is skipped, so the run can be continued.
One line per finished job is appended to OUTDIR/summary.txt; models are reported at once in OUTDIR/models.txt.
"""
import os, subprocess, sys, time
from multiprocessing import Pool
pf, outdir, workers = sys.argv[1], sys.argv[2], int(sys.argv[3])
opts = sys.argv[4:]
here = os.path.dirname(os.path.abspath(__file__))
prog = os.path.join(here, 'gsat3.py' if os.path.exists(os.path.join(here, 'gsat3.py')) else 'gsat.py')
prefixes = [l.strip() for l in open(pf) if l.strip()]
os.makedirs(outdir, exist_ok=True)
def job(j):
    log = os.path.join(outdir, 'job_%d.log' % j)
    if os.path.exists(log) and '# RESULT' in open(log).read():
        return j, 'skipped'
    t0 = time.time()
    with open(log, 'w') as lf:
        subprocess.run([sys.executable, prog] + opts + ['--prefix', prefixes[j - 1], '--cubes', os.path.join(outdir, 'cubes_%d.txt' % j),
                        '--out', os.path.join(outdir, 'model_%d' % j)], stdout=lf, stderr=subprocess.STDOUT)
    txt = open(log).read().split('\n')
    res = [l for l in txt if l.startswith('# RESULT')]
    done = [l for l in txt if l.startswith('# done')]
    mods = [l for l in txt if l.startswith('MODEL')]
    with open(os.path.join(outdir, 'summary.txt'), 'a') as f:
        f.write('job %d | %s | %s | %s | %.0f s\n' % (j, prefixes[j - 1], res[-1] if res else 'NO RESULT', done[-1] if done else '', time.time() - t0))
    if mods:
        with open(os.path.join(outdir, 'models.txt'), 'a') as f:
            for m in mods:
                f.write('job %d | %s\n' % (j, m))
    return j, res[-1] if res else 'NO RESULT'
if __name__ == '__main__':
    with Pool(workers) as pool:
        for j, r in pool.imap_unordered(job, range(1, len(prefixes) + 1)):
            print('job %d: %s' % (j, r), flush=True)
    print('ALL JOBS DONE', flush=True)
