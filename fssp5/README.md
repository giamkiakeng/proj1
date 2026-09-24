# Five-state minimal-time firing squads — code, data and manuscript

This directory accompanies the manuscript
*Towards five-state minimal-time firing squads: a pumping lemma, a speed-1/3
barrier, and certified bounds* (`paper/main.tex`, compiled: `paper/fssp5_manuscript.pdf`).

**Status of the open problem.** The existence of a five-state minimal-time
solution to the firing squad synchronization problem is **not settled** by this
work. What is established (with proofs or checkable certificates):

| Result | Where | How to check |
|---|---|---|
| Agreement / reflected-triangle reduction; return-chain lemma | paper §2 | proofs |
| Pumping lemma (all minimal-time solutions, any number of states) | paper §3, Lemma 3.3 | proof; `src/pumping.py` checks it on Mazoyer's rule (0 violations, 4 ≤ n < n' ≤ 120) |
| Speed-1/3 barrier theorem | paper §3, Theorem 3.4 | proof; Mazoyer's rows: T(j) ∈ {2j+1, 2j+2} (j < 700) |
| No 4-state minimal-time solution (without assuming δ(*,L,L)=L) | paper §5, Theorem 5.1 | LRAT certificate, `lrat-check` VERIFIED in 5.7 s |
| An explicit 5-state rule synchronizing all lengths 2..12, obeying PUMP up to 40 and never firing on the half-line up to anti-diagonal 78 | paper §6, Theorem 6.1 | `src/fsspcheck`, `src/pumping.py`, `src/check_halfline.py` on `results/uniformA_2-12.txt` |
| Search-space estimates (Knuth probes): ~27 nodes for 4 states vs 10^11–10^19 for 5 states | paper §6.3 | `src/knuth.py`, `results/knuth_k5_N12.log` |

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
src/figures.py           Figure 1
results/                 rule tables (Mazoyer; partial 5-state rules), logs
paper/                   LaTeX sources, figure, bibliography
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
