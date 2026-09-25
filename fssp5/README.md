# Five-state minimal-time firing squads — code, data and manuscript

This directory accompanies the manuscript
*Towards five-state minimal-time firing squads: two barriers on the
half-line and certified bounds* by Kia Keng Giam (Temasek Junior College,
Singapore), Beichen Sun and Yaoqi Zhao (Hwa Chong Institution, Singapore)
(`paper/main.tex`, compiled: `paper/fssp5_manuscript.pdf`).

Structure of the manuscript: a one-page *Notation at a glance*; §1 introduction (with the
results-at-a-glance table); §2 preliminaries; §3 the two barriers; §4 encoding; §5 the
certified four-state bound; §6 the five-state frontier; §7 discussion; Appendix A glossary of
all terms and symbols; Appendix B further experiments; Appendix C rule tables; Appendix D
reproducibility.

**Status of the open problem.** The existence of a five-state minimal-time
solution to the firing squad synchronization problem is **not settled** by this
work. What is established (with proofs or checkable certificates):

| Result | Where | How to check |
|---|---|---|
| Glossary of every term and symbol; drawings explaining the problem (Figures 1–5) | paper, Notation at a glance, Appendix A; Figures 1–5 in §1–§3 | — |
| Agreement / reflected-triangle reduction; return-chain lemma | paper §2 | proofs |
| Pumping lemma (all minimal-time solutions, any number of states) | paper §3, Lemma 3.3 | proof; `src/pumping.py` checks it on Mazoyer's rule (0 violations, 4 ≤ n < n' ≤ 120) |
| Speed-1/3 barrier theorem | paper §3, Theorem 3.4 | proof; Mazoyer's rows: θ(j) ∈ {2j+1, 2j+2} (j < 700) |
| Left-border lemma and left-border barrier theorem (any number of states); no minimal-time solution has an eventually regular half-line (Corollary 3.7), with a finite certificate for concrete half-lines (Lemma 3.8); mirrored version for the reflected triangles (Remark 3.9) | paper §3.3, Lemma 3.5, Theorem 3.6, Corollary 3.7, Lemma 3.8, Remark 3.9 | proofs; checked on Mazoyer's rule (periodic stretches ≤ 6 resp. ≤ 7); `src/germpersist.py` certifies eventual regularity of germs |
| No 4-state minimal-time solution (without assuming δ(*,L,L)=L) | paper §5, Theorem 5.1 | LRAT certificate, `lrat-check` VERIFIED in 5.7 s |
| Explicit 5-state rules synchronizing all lengths 2..12 (δ12, uniform pre-firing) and 2..13 (δ13), obeying PUMP up to 40 and never firing on the half-line up to anti-diagonal 78 | paper §6, Theorem 6.1 | `src/fsspcheck`, `src/pumping.py`, `src/check_halfline.py`, `src/germcompare.py` on `results/uniformA_2-12.txt`, `results/delta13.txt` |
| The common half-line of δ12 and δ13 cannot be completed to a solution (fails at n = 518 by the left-border lemma) | paper §6, Corollary 6.2 | `src/germext.c` |
| A 5-state rule δ14 for **all lengths 2..14** (fails at 15), with a chaotic half-line of complexity 16 that escapes both barriers (found via δ′13 for 2..13 with the same half-line) | paper §6.2, Proposition 6.3, Figures 7 and 8 | `src/fsspcheck`, `src/germext.c` on `results/delta14.txt` (and `results/delta13_chaotic.txt`) |
| A second rule δ14b for all lengths 2..14 (fails at 15), on another complexity-16 germ with a periodic half-line | paper §6.2, Appendix B.1 | `src/fsspcheck` on `results/delta14b.txt` |
| A third rule δ14c for all lengths 2..14 (fails at 15), chaotic half-line with 15 neighbourhoods | paper §6.2, Appendix B.1 | `src/fsspcheck` on `results/delta14c.txt` |
| A fourth rule δ14d for all lengths 2..14 (fails at 15) on the other complexity-15 survivor; its half-line equals that of δ14c up to renaming states (t ≥ 1); both end with uniform pre-firing configurations (Gⁿ, Aⁿ) | paper §6.2, Appendix B.1 | `src/fsspcheck` on `results/delta14d.txt`; `src/class_prefire.py` for the pre-firing classes |
| Complexity 17: 43,294 germs → 187 after the half-line lemmas, the certified completion test for 2..10 (LRAT 1.9 GB) and the regularity certificate; a fifth rule δ14e for all lengths 2..14 (fails at 15 by one step) on one of them | paper §6.3, Appendix B.3 | `src/germdfs.c`, `src/germext.c`, `src/germinc.py`, `src/germcert.py`, `src/germpersist.py`; `results/germs/*K17*`, `results/delta14e.txt` |
| Every 5-state minimal-time solution uses ≥ 15 distinct neighbourhoods on its half-line below anti-diagonal 78 | paper §6.3, Proposition 6.4, Table 4 | `src/germdfs.c`, `src/germcert.py` (LRAT), `src/germext.c`; digests in `results/germs/CERTIFICATES.txt` |
| Search-space estimates (Knuth probes): ~25 nodes for 4 states vs 10^11–10^19 for 5 states | paper §6 | `src/knuth.py`, `results/knuth_k4_N9.log`, `results/knuth_k5_N12.log`, `results/knuth_k5_N18.log` |

## Layout

```
src/fsspcheck.c          brute-force simulator / checker of rule tables (independent of the encoder)
src/gencnf.py            CNF generator MT_k(N; M, N') (+ pumping, links, restricted classes)
src/solve.py             build + kissat + decode + re-check
src/lazy.py, lazyk.py    counterexample-guided loops (CaDiCaL incremental / kissat)
src/fsspdfs.c            exhaustive DFS enumeration of partial rules (4-state counts)
src/pumping.py           cones of the pumping lemma, PUMP check on a rule
src/check_halfline.py    half-line non-firing check
src/mazoyer_from_coq.py  extracts Mazoyer's rule from Duprat's Coq file autom.v
src/validate_mazoyer.py  soundness test of the encoding against Mazoyer's rule
src/fixgerm.py, coresize.py, benders.py, knuth.py, cubescan.py   experiments of §6
src/germdfs.c            enumeration of half-line germs of bounded complexity
src/germinc.py           incremental completion test of germs (CaDiCaL via PySAT)
src/germcert.py          one LRAT certificate for a whole list of refuted germs
src/germext.c            extends germ half-lines; left-border lemma and pumping checks
src/germext2.c           streaming left-border check on one very long line
src/germpersist.py       certificate of eventual regularity of a germ's half-line (Lemma 3.8)
src/germcompare.py       half-line neighbourhoods of rules below an anti-diagonal
src/germpipe.sh          the classification pipeline
src/germlong.py, germband.py, equiv.py, reflsym.py   further (inconclusive) experiments
src/ruletable.py         LaTeX tables of rules
src/figures.py           Figures 6-8 (space-time diagrams)
results/                 rule tables (Mazoyer; partial 5-state rules; delta13), logs
results/germs/           germ lists, classification logs, certificate digests
paper/                   LaTeX sources, figures, bibliography
paper/sections/terms.tex glossary of all terms and symbols (Appendix A); notation.tex the one-page summary
paper/sections/pic_*.tex, tikzdefs.tex   TikZ drawings (Figures 1-5); further.tex Appendix B
```

## Reproducing the main certificates

```
cd src && gcc -O2 -o fsspcheck fsspcheck.c && gcc -O3 -o fsspdfs fsspdfs.c
python3 gencnf.py 4 9 ../cnf/mt4_9.cnf
cadical --lrat --binary=false ../cnf/mt4_9.cnf ../cnf/mt4_9.lrat      # UNSAT, ~50 s
lrat-check ../cnf/mt4_9.cnf ../cnf/mt4_9.lrat                          # VERIFIED
./fsspcheck ../results/uniformA_2-12.txt 2 12                          # OK
python3 pumping.py ../results/uniformA_2-12.txt 40                     # 0 violations
python3 check_halfline.py ../results/uniformA_2-12.txt 78              # no firing cell
```
Solvers used: Kissat 4.0.4, CaDiCaL 3.0.1 (and 1.9.5 via PySAT), drat-trim/lrat-check (git, 2026-09).
