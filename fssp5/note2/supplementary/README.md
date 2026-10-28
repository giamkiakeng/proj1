# Supplementary material

for the note

> Kia Keng Giam, *Necessary conditions on minimal-time solutions of the firing squad problem*.

This folder contains the programs and data behind every computer-assisted statement of the note, and two scripts that rerun them. Section and statement numbers below are those of the note.

The proofs of Sections 2–5 need no computation. Section 6, the paragraph after Theorem 3.4 and the two models named in Section 7 do. Unsatisfiability is certified by LRAT proofs, which an independent checker verifies. Everything else is direct simulation, exhaustive enumeration, or a satisfiable formula.

## Quick start

```
./check_quick.sh            # about 7 minutes; Python 3 with PySAT, and a C compiler
./check_certificates.sh     # about 30 minutes; also CaDiCaL, Kissat, drat-trim and lrat-check
```

- **`check_quick.sh`** runs every check that needs no external SAT solver. It also regenerates the three formulas of Theorem 6.1 and compares their SHA-256 digests with those printed in the note.
- **`check_certificates.sh`** generates every unsatisfiable formula of the note, solves it with a proof, and checks the proof:
  - the LRAT proofs come from CaDiCaL directly, or from Kissat's DRAT proof via drat-trim;
  - each proof is checked with `lrat-check`;
  - it writes about 4 GB to `cnf/`, including the directories `cnf/balzer_*/` of `src/balzer.py`.

Both scripts can be started from any directory. Solver binaries are taken from the environment variables `CADICAL`, `KISSAT`, `DRATTRIM` and `LRATCHECK` if they are set, otherwise from the `PATH`.

## Requirements

These are the versions used for the runs reported in the note.
- Python 3.11 with PySAT (`pip install python-sat`; we used 1.9.dev15). PySAT's bundled CaDiCaL decides the satisfiable formulas.
- gcc 13.
- CaDiCaL 3.0.1; any version from 2.0 on writes LRAT. With another version the LRAT proofs differ, but they still verify.
- Kissat 4.0.4.
- drat-trim and lrat-check from https://github.com/marijnheule/drat-trim, commit 2e3b2dc.

## Statements and checks

Each row gives the statement, the commands (as run by the scripts), and the expected result, which the scripts print. Paths are relative to this folder; the scripts run each command in its own directory (`src/` or `research/`).

| Statement of the note | Commands | Expected result |
|---|---|---|
| §3, paragraph after Theorem 3.4: θ(j) for Mazoyer's solution and for δ12, and PUMP for δ12 | `src/theta.py results/mazoyer6.txt 2600 699 1`<br>`src/theta.py results/uniformA_2-12.txt 1400 300 10`<br>`src/pumping.py results/uniformA_2-12.txt 650` | θ_T(j) − 2j ∈ {1, 2}, period 3<br>θ_T(j) − ⌈3j/2⌉ = 2, period 1<br>0 violations |
| §6, *Encodings and evidence*: Mazoyer's solution | `src/fsspcheck results/mazoyer6.txt 3 3000`<br>`src/validate_mazoyer.py 12 78 40`<br>`research/asymp.py` and `research/gfix.py … --fix results/mazoyer6.txt` | OK for all 3 ≤ n ≤ 3000<br>MT_6({3..12}; 78, 40) satisfiable<br>(G2), (G3) for T = 8 and all n ≥ 15: SAT (21 representative lengths; depth rows periodic from t0 = 42, p = 3) |
| §6, *Encodings and evidence*: the table of δ14 fixed | `research/gfix.py FREE 5 <spec> --fix results/delta14.txt --solve cadical` | full:2-14 SAT; full:2-15 UNSAT; full:2-14 early:15-30:6 SAT; full:2-14 early:15-30:8 UNSAT |
| Theorem 6.1 (i) | `src/gencnf.py 4 9 cnf/mt4_9.cnf`<br>`research/certify_lrat.sh cnf/mt4_9.cnf` | 753 variables, 17,605 clauses, SHA-256 `d18d6548…`; s UNSATISFIABLE; c VERIFIED |
| Theorem 6.1 (ii) | `GFIX_SHARE=1 research/gfix.py FREE 4 full:2-7 early:8-10:6 --cnf cnf/k4_G6.cnf`<br>`research/certify_lrat.sh cnf/k4_G6.cnf` | 919 variables, 22,960 clauses, SHA-256 `0e0ba286…`; c VERIFIED |
| Theorem 6.1 (iii) | `GFIX_SHARE=1 research/gfix.py FREE 4 full:2-5 early:6-10:4 cone:6-10 --cnf cnf/k4_G4c.cnf`<br>`research/certify_lrat.sh cnf/k4_G4c.cnf` | 874 variables, 20,461 clauses, SHA-256 `124f0954…`; c VERIFIED |
| §6, paragraph after Theorem 6.1: enumeration | `src/fsspdfs 4 8 -s`, `src/fsspdfs 4 9` | 27 partial rules for 2..8, none using (∗, L, L); none for 2..9 |
| §6, paragraph after Theorem 6.1: weakenings | `research/gfix.py FREE 4 <spec> --solve cadical` with G_4(5,30) = `full:2-6 early:7-30:5`, G_4(6,9) = `full:2-7 early:8-9:6`, G_4(4,30,9) = `full:2-5 early:6-30:4 cone:6-9`, G_4(3,30,12) = `full:2-4 early:5-30:3 cone:5-12`, G_4(6,10) without (G3) = `GFIX_NORC=8,9,10` with `full:2-7 early:8-10:6`, (G1) for T = 4 with (G5) for 6 ≤ n ≤ 12 = `full:2-5 cone:6-12` | SAT in each case |
| Proposition 6.2 | `src/fsspcheck results/delta14*.txt 2 14`<br>`src/firstfire.py results/delta14*.txt 15 60`<br>`research/failall.py results/<rule>.txt <T>` | OK for 2 ≤ n ≤ 14<br>every line 15 ≤ n ≤ 60 has an F at τ ≤ n − 2<br>(t0, p) = (51, 8), (66, 3), (257, 192), (95, 48), (56, 2) for T = 10, 14, 22, 12, 14; 35, 39, 413, 116, 28 representative lengths, the largest 49, 53, 427, 130, 42; VERIFIED |
| §6, paragraph after Proposition 6.2 | `src/halflines.py values results/delta14.txt 1500`<br>`src/germext 5 10000 3 24 800 < results/germs/germ_delta14.txt`<br>`src/firstfire.py <rule> 2 60 9` | cell 1 ∈ {G, L}, cell 2 ∈ {A, L}, cells ≥ 3 ∈ {B, L}; elementary rule 22 on {L, B}<br>`1 CLOSED reach=10000` (no flag: PUMP holds for n′ ≤ 800, and Lemma 4.1 does not apply for 2n − 2 ≤ 10000, s ≤ 3, ℓ ≤ 24)<br>δ12 synchronizes exactly 2..12 and δ13 exactly 2..13 among 2..60; the smallest length with an F at τ ≤ 9 is 16, 14, 15, 19, 15, 15, 16 for δ12, δ13, δ14, δ14b, …, δ14e |
| Proposition 6.3 | `src/germcompare.py <rule> 78`<br>`src/germdfs 5 78 14 40`<br>`src/germdfs_check.py 14 78 40`<br>`src/germinc.py results/germs/germs_K14.txt 10 78`<br>`src/germcert.py results/germs/K14_refuted10.txt 10 cnf/k14_n10`<br>`src/germext 5 3300 3 12 < results/germs/germs_K14_surv10.txt`<br>`src/germ_k14_check.py` | c_78 = 57, 22, 16 for Mazoyer's rule, δ12, δ14<br>244 germs, identical to `results/germs/germs_K14.txt` (1.0·10^8 nodes)<br>the same 244 germs<br>230 UNSATISFIABLE, 14 SATISFIABLE<br>CaDiCaL UNSAT, lrat-check VERIFIED, formula SHA-256 `4f9306a8…`<br>all 14 CLOSED to anti-diagonal 3300 and REFUTED with s = 1, n ≤ 163, ℓ ≤ 5 (e.g. n = 28, ℓ = 1, Y = 19)<br>the same, by an independent simulation |
| Corollary 6.4 | `src/germcompare.py results/uniformA_2-12.txt results/delta13.txt 78`<br>`src/germcompare.py --germline results/uniformA_2-12.txt 78`<br>`src/antidiag.py results/uniformA_2-12.txt 1034 1034 2 260 1033 2 259`<br>`src/germext 5 1300 3 6 < results/germs/germ_delta12.txt` | identical half-lines below 78<br>the 22 transitions = `results/germs/germ_delta12.txt`<br>the same 22 neighbourhoods on t + i ≤ 1034; cells 2..259 of t + i = 1034 in state A; cells 2..259 of t + i = 1033 in state L<br>REFUTED n = 518, s = 2, ℓ = 1, Y = 259 |
| Proposition 6.5 | `src/balzer.py 10 1234 AB --lrat`, `src/balzer.py 9 1234 LA --lrat`, `src/balzer.py 9 1234 LB --lrat`<br>`src/balzer_k.py 5 12 1234 id --cnf=cnf/w.cnf`, then `kissat`, `drat-trim -L`, `lrat-check`<br>`src/balzer.py 11 1234s id`; `src/fsspcheck results/balzer_sym11.txt 2 11` | UNSATISFIABLE, LRAT VERIFIED (3 times)<br>Kissat: s UNSATISFIABLE; drat-trim writes the LRAT proof; lrat-check: c VERIFIED<br>SATISFIABLE; OK for 2 ≤ n ≤ 11 (and FAIL at n = 12) |
| §7, the two models of the germ of δ14d | `research/models_check.py` | ALL CHECKS PASSED: both models contain the germ; (G1)–(G3) for T = 10 and all n ≥ 12, resp. T = 7 and all n ≥ 9; (G5) for 9 ≤ n ≤ 20; both end cells but not all cells fire at time 2n − 2, and none before, exactly for n = 9, 11..17, 19 among 9..24 |

In `src/balzer.py`, the conditions C1–C4 are (B1)–(B4) of the note. `1234` selects the weak reading and `1234s` the strong one; the last argument is the involution I.

## Recorded runs

Times and proof sizes in the note were measured on one core of a cloud virtual machine, and they depend on the machine:

| statement | solver time | proof size | lrat-check time |
|---|---|---|---|
| Theorem 6.1 (i) | 51 s | 177 MB | 5.7 s |
| Theorem 6.1 (ii) | 41 s | 167 MB | 5 s |
| Theorem 6.1 (iii) | 36 s | 173 MB | 4 s |
| Proposition 6.3 | 4 s | 11 MB | 0.6 s |
| Proposition 6.5, Kissat case | 15 min | 3.1 GB | 66 s |

For Proposition 6.5, the lrat-check times of the three CaDiCaL cases are 7.1, 3.5 and 3.3 s. The digests do not depend on the machine:
- **Formulas:** all formulas are generated deterministically; `SHA256SUMS` lists those of Theorem 6.1 and Proposition 6.3.
- **Proofs:** CaDiCaL 3.0.1 writes the same LRAT proof on every run. The recorded digests are:
  - `cnf/mt4_9.lrat` `1d511a75ab25587fa4a3476b95ad3f7133c7375ad96661fd22fa598aec6c8092` (176,861,512 bytes);
  - `cnf/k4_G6.lrat` `7943a69803f934814a80c731060747afeee9317d205b6330c4325a039f6da6fb` (166,919,248 bytes);
  - `cnf/k4_G4c.lrat` `7f76fe69c6158ebf03891cb9aa6fe0fb61b5e7e60f1b5b317f10baa4e944c8d8` (172,820,213 bytes);
  - `cnf/k14_n10.lrat` `b2324436d2d14efa3e61296eb6dd5776bbe6bf84b0562f5972665db932eddea8`.
- **Kissat case of Proposition 6.5:** Kissat 4.0.4 and drat-trim reproduced the recorded proofs byte for byte:
  - `cnf/w.cnf` `023b99e247f9a1616a926d70e03e85f2ad54ad63e498df79b9cc87f3d3acb778`;
  - `cnf/w.drat` `2dd3e052df34254c391030c24e49425030cc88af8aef81d23ecafe03f93e649e` (binary DRAT);
  - `cnf/w.lrat` `e0231f2f50b4278948e832b78a33f295f4df9792789f63af744818be7f3e873e` (3,078,078,538 bytes).
- **Balzer formulas and proofs:** `results/balzer.log` lists their digests.

## Layout

| path | content |
|---|---|
| `check_quick.sh`, `check_certificates.sh` | the two scripts |
| `SHA256SUMS` | digests of the formulas of Theorem 6.1 and Proposition 6.3 |
| `src/` | simulation, enumeration and encoding programs |
| `research/` | the encoder of the formulas G_k(T, N1, C) and the programs of Sections 5–6 that build on it |
| `results/` | rule tables, germ lists and recorded logs |
| `research/models/` | the two models of Section 7 |
| `cnf/` | created by the scripts: formulas and proofs |

### Programs

| program | purpose |
|---|---|
| `src/fsspcheck.c` | brute-force checker of rule tables: simulates every line in full |
| `src/firstfire.py` | relative time of the first F on each line of a range of lengths |
| `src/antidiag.py` | neighbourhoods and anti-diagonals of a half-line (Corollary 6.4) |
| `src/gencnf.py` | the formula MT_k(𝒩; M, N′) |
| `src/pumping.py` | the cone of Lemma 3.2 and PUMP(n, n′) on the half-line of a rule |
| `src/theta.py` | θ(j) observed on a finite horizon |
| `src/halflines.py` | the values on δ14's half-line; comparison of half-lines up to renaming |
| `src/fsspdfs.c` | exhaustive enumeration of partial four-state rules |
| `src/mazoyer_from_coq.py` | extraction of Mazoyer's rule from Duprat's Coq development (see below) |
| `src/validate_mazoyer.py` | Mazoyer's rule against the encoding |
| `src/germcompare.py` | germs below an anti-diagonal; c_M; comparison of two half-lines |
| `src/germdfs.c`, `src/germdfs_check.py` | enumeration of the germs of Proposition 6.3; independent re-implementation |
| `src/germinc.py` | completion test of germs (PySAT) |
| `src/germcert.py` | one LRAT certificate for a list of refuted germs |
| `src/germext.c` | extension of a germ's half-line, with the checks of Lemma 4.1 and PUMP |
| `src/germ_k14_check.py` | independent check of the 14 half-line refutations of Proposition 6.3 |
| `src/balzer.py`, `src/balzer_k.py` | formulas with Balzer's conditions |
| `research/gfix.py` | the formulas of Definition 5.4, MT-type formulas and variants (regions `full`, `early`, `cone`), optionally with a germ or a whole table fixed |
| `research/asymp.py` | the periodicity certificate (Lemma 5.2) and the representative lengths (Corollary 5.3) for a germ |
| `research/failall.py` | Proposition 6.2: early firing of every line n ≥ 15 |
| `research/models_check.py` | the models of Section 7 |
| `research/certify_lrat.sh` | solve with CaDiCaL writing LRAT, check with lrat-check, print digests |

`firstfire.py`, `antidiag.py` and `models_check.py` were written for this supplement and are independent of the other programs. `certify_lrat.sh` takes its solver paths from the environment or the `PATH`. All other files are identical to the versions in the repository.

### Data

| file | content |
|---|---|
| `results/mazoyer6.txt` | Mazoyer's six-state solution, as extracted from Duprat's Coq development; it synchronizes the lengths n ≥ 3 |
| `results/uniformA_2-12.txt`, `results/delta13.txt` | δ12 and δ13 |
| `results/delta14.txt`, `results/delta14b.txt` … `results/delta14e.txt` | the five rules of Proposition 6.2 |
| `results/balzer_sym11.txt` | the rule of Proposition 6.5 for the lengths up to 11 |
| `results/germs/germ_delta12.txt`, `germ_delta14.txt` | germs of δ12 (the 22 transitions of Corollary 6.4) and δ14 |
| `results/germs/germs_K14.txt` | the 244 germs of Proposition 6.3 |
| `results/germs/K14_n10.log`, `K14_refuted10.txt`, `germs_K14_surv10.txt` | the completion test of the 244 germs, the 230 refuted ones, the 14 others |
| `results/germs/K14_ext3300.txt`, `CERTIFICATES.txt` | half-line extension of all 244 germs; digests of the germ certificate |
| `results/balzer.log`, `results/theta_pump.log` | recorded runs for Proposition 6.5 and for the paragraph after Theorem 3.4 |
| `research/models/germ14d_T10.txt`, `d14d_T7c.txt` | the two models of Section 7 |

Rule tables have a line `k <number of states>`, then one line `l c r d` per transition, with `*` for the border; lines starting with `#` are comments. Some of these comments name search programs that produced a rule; those programs are not needed to check anything here. A germ is one line `GERM lcr>d …`.

Mazoyer's table was extracted by `src/mazoyer_from_coq.py` from the file `autom.v` of J. Duprat's Coq contribution *FiringSquad*, archived at https://github.com/rocq-archive/firing-squad. To repeat the extraction, download that file and run `python3 src/mazoyer_from_coq.py autom.v | cmp - results/mazoyer6.txt`; the file itself is not included here.
