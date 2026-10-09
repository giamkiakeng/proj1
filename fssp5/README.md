# Two necessary conditions on minimal-time firing squads: code and data

This directory accompanies the note

> Kia Keng Giam, Beichen Sun, Yaoqi Zhao, *Two necessary conditions on minimal-time solutions of
> the firing squad problem*. The source is `note/note.tex` and the compiled PDF is `note/note.pdf`.

The proofs in Sections 2–4 of the note need no computation. This directory holds everything behind its computer-assisted statements, which are in Section 5 and Remark 3.5. For each statement, the commands below regenerate the evidence and print the outcome recorded here. `note/REVIEW.md` contains the report of an internal referee on the first version of the note and the response to it.

## Layout

| path | content |
|---|---|
| `note/` | the note: LaTeX source, PDF, figures, bibliography, `REVIEW.md` |
| `src/` | programs (table below) |
| `results/` | rule tables, logs, germ lists, digests |
| `cnf/` | formulas and proofs written by the commands below (ignored by git) |

| program | used for |
|---|---|
| `src/fsspcheck.c` | independent brute-force checker of rule tables. It simulates every line in full and does not use the agreement lemma. |
| `src/gencnf.py` | the formula MT_k(𝒩; M, N′) of Section 5 |
| `src/pumping.py` | the cones of Lemma 3.2 (breadth-first search); PUMP(n, n′) on the half-line of a rule |
| `src/theta.py` | θ(j) observed on a finite horizon (Remark 3.5) |
| `src/halflines.py` | the values on δ14's half-line (rule 22); comparing half-lines up to renaming (Section 5) |
| `src/fsspdfs.c` | exhaustive enumeration of partial four-state rules (sharpness of Theorem 5.1) |
| `src/mazoyer_from_coq.py` | extraction of Mazoyer's rule from Duprat's Coq development |
| `src/validate_mazoyer.py` | the test of the encoding against Mazoyer's rule |
| `src/germcompare.py` | the neighbourhoods of a half-line below an anti-diagonal: c_M, the common germ of δ12 and δ13, germ files |
| `src/germdfs.c`, `src/germdfs_check.py` | enumeration of the germs of Proposition 5.4, and an independent re-implementation |
| `src/germinc.py` | completion test of germs (CaDiCaL through PySAT) |
| `src/germcert.py` | one LRAT certificate for a list of refuted germs |
| `src/germext.c` | extension of the half-line determined by a germ, with the checks of Lemma 4.1 and PUMP |
| `src/germ_k14_check.py` | independent check of the 14 refutations in Proposition 5.4 |
| `src/balzer.py` | formulas with Balzer's conditions (Proposition 5.5) |
| `src/balzer_k.py` | the same for k states: six states, and the formula of the Kissat case of Proposition 5.5 |
| `src/balzer_mazoyer.py` | Balzer's conditions on the transitions that Mazoyer's rule uses |

Rule tables in `results/` use the format of `fsspcheck.c`: a line `k <number of states>`, then one line `l c r d` per transition, with `*` for the border.

| file | rule |
|---|---|
| `mazoyer6.txt` | Mazoyer's six-state solution as extracted by `mazoyer_from_coq.py`; it synchronizes the lengths n ≥ 3 |
| `uniformA_2-12.txt`, `delta13.txt` | δ12 and δ13 |
| `delta14.txt` | δ14 (Table 1 of the note) |
| `delta14b.txt` … `delta14e.txt` | the four further rules for the lengths up to 14 |
| `balzer_sym11.txt`, `balzer_sym11_weak.txt` | five-state rules for the lengths up to 11 under Balzer's conditions with I = id; strong and weak reading |
| `balzer6_sym14.txt`, `balzer6_LA14.txt` | six-state rules for the lengths up to 14 under the strong reading, I = id and I = (L A) |

Comment lines at the top of some rule files record how the rule was found. The search programs and germ lists they name, such as `lazyk.py`, `germlong.py`, `germcegar.py` and `K16_remaining24.txt`, are not needed to check the rules. They are in the repository history (last in commit cdf33e2).

| file | content |
|---|---|
| `results/germs/germ_delta12.txt` | the common germ of δ12 and δ13 below anti-diagonal 78 (the 22 transitions printed in the note), in the one-line format of `germdfs.c` |
| `results/germs/germ_delta14.txt` | δ14's germ in the same format |
| `results/germs/germs_K14.txt` | the 244 germs of Proposition 5.4 |
| `results/germs/K14_n10.log` | the completion test of the 244 germs |
| `results/germs/K14_refuted10.txt` | the 230 germs it refutes |
| `results/germs/germs_K14_surv10.txt` | the 14 survivors |
| `results/germs/K14_ext3300.txt` | `germext 5 3300 3 12` on all 244 germs |
| `results/germs/CERTIFICATES.txt` | digests of the formula and the LRAT proof |
| `results/balzer.log` | runs, times and digests for Proposition 5.5 |
| `results/balzer6.log` | the six-state runs |
| `results/theta_pump.log` | Remark 3.5 |

## Requirements

- Python 3 with PySAT (`python-sat`).
- A C compiler.
- For the certificates: CaDiCaL 3.0.1, Kissat 4.0.4, and drat-trim with lrat-check (git version of September 2026). These are the versions used.

The commands are run in `src/` after

```
gcc -O2 -o fsspcheck fsspcheck.c && gcc -O3 -o fsspdfs fsspdfs.c
gcc -O2 -o germdfs germdfs.c && gcc -O2 -o germext germext.c
mkdir -p ../cnf
```

Comments give the output as printed. "Recorded" marks times and sizes from the original runs: they depend on the machine (a single cloud vCPU), whereas the digests do not.

## Section 5: the encoding and its validation

`autom.v` is from Duprat's Coq contribution *FiringSquad*, archived at https://github.com/rocq-archive/firing-squad.

```
python3 mazoyer_from_coq.py autom.v | cmp - ../results/mazoyer6.txt   # no output: identical
./fsspcheck ../results/mazoyer6.txt 3 3000
    # OK: fires exactly at time 2n-2 for all 3 <= n <= 3000
python3 validate_mazoyer.py 12 78 40
    # MT_6({3..12}; 78, 40), symbreak=False: satisfiable under renamings [(2, 3, 4)]
    # MT_6({3..12}; 78, 40), symbreak=True: satisfiable under renamings [(2, 4, 3)]
```

The first answer is the test stated in the note. The formulas of the note use no symmetry breaking. With the optional symmetry breaking, Mazoyer's rule is a model only after exchanging B and C.

SHA-256 of `mazoyer6.txt`: `4b0717ea7319957c1fdcc887fe09c1074cf338e8b849cdd32b4307d0083f417e`.

## Theorem 5.1 (four states)

```
python3 gencnf.py 4 9 ../cnf/mt4_9.cnf               # k=4 N=9 vars=753 clauses=17605
cadical --lrat --binary=false ../cnf/mt4_9.cnf ../cnf/mt4_9.lrat   # s UNSATISFIABLE
lrat-check ../cnf/mt4_9.cnf ../cnf/mt4_9.lrat        # c VERIFIED
./fsspdfs 4 8 -s      # k=4 N=8 nodes=108684650 solutions=27 (rules printed as SOL lines)
./fsspdfs 4 9         # k=4 N=9 nodes=108684650 solutions=0
./fsspdfs 4 8 -s | grep '^SOL' | grep -c '\*LL>'      # 0: no rule uses (*,L,L)
```

| file | SHA-256 |
|---|---|
| `mt4_9.cnf` | `d18d65480e77505193b8f60362badad5e71f8f08505f29befbcd3b2b18cdaabf` |
| `mt4_9.lrat` | `1d511a75ab25587fa4a3476b95ad3f7133c7375ad96661fd22fa598aec6c8092` |

- **Recorded (these are the numbers in the note):** CaDiCaL 51 s; proof 177 MB; lrat-check 5.7 s.
- **Two later reruns:** identical digests and size (176,861,512 bytes), CaDiCaL 45 s and 38 s, lrat-check 4.6 s and 4.4 s.

Sanders' near miss (his Figure 2, 34 transitions, transcribed from the paper) is the rule printed as `SOL 26`.

## Proposition 5.2 (δ14) and the four further rules

```
./fsspcheck ../results/delta14.txt 2 14       # OK: fires exactly at time 2n-2 for all 2 <= n <= 14
./fsspcheck ../results/delta14.txt 15 15 -v   # FAIL n=15: a cell fires at time 22 < 28 (cells 13-15)
./germext 5 10000 3 24 800 < ../results/germs/germ_delta14.txt
    # 1 CLOSED reach=10000      (no FIRE, FRONTL, REFUTED or PUMPFAIL flag)
python3 halflines.py values ../results/delta14.txt 1500
    # cell 1 ['G', 'L'], cell 2 ['A', 'L'], cells i >= 3 ['B', 'L']
    # rule restricted to {L,B}^3 (L = 0, B = 1): elementary CA 22
for r in delta14b delta14c delta14d delta14e; do
  ./fsspcheck ../results/$r.txt 2 14; ./fsspcheck ../results/$r.txt 15 15
done
    # OK for 2..14 each; FAIL n=15 at times 25, 21, 22, 27
python3 halflines.py compare 300 ../results/delta14.txt ../results/delta14[b-e].txt
    # 5 rules, 4 distinct half-lines up to renaming (delta14c and delta14d agree)
```

For each germ, `germext k MBIG SMAX LMAX [PMAX]` simulates the half-line on t + i ≤ MBIG with the germ's transitions only. It always prints CLOSED, or OPEN if a neighbourhood outside the germ occurs. It then adds one flag for each check that fails:
- FIRE if a half-line cell fires;
- FRONTL if the front is L;
- REFUTED if Lemma 4.1 applies to some line n with 2n − 2 ≤ MBIG, with s ≤ SMAX and ℓ ≤ LMAX;
- PUMPFAIL if PUMP(n, n′) fails for some n′ ≤ PMAX.

## δ12, δ13 and Corollary 5.3

```
./fsspcheck ../results/uniformA_2-12.txt 2 12    # OK ... for all 2 <= n <= 12
./fsspcheck ../results/uniformA_2-12.txt 13 13   # FAIL n=13: a cell fires at time 23 < 24
./fsspcheck ../results/delta13.txt 2 13          # OK ... for all 2 <= n <= 13
./fsspcheck ../results/delta13.txt 14 14         # FAIL n=14: a cell fires at time 21 < 26
python3 germcompare.py ../results/uniformA_2-12.txt ../results/delta13.txt 78
    # 22 neighbourhoods besides (L,L,L) each; identical half-line neighbourhoods and values: True
python3 germcompare.py --germline ../results/uniformA_2-12.txt 78   # = results/germs/germ_delta12.txt
./germext 5 1300 3 6 < ../results/germs/germ_delta12.txt
    # 1 CLOSED reach=1300 REFUTED n=518 s=2 L=1 Y=259
```

SHA-256 digests:
- `uniformA_2-12.txt` (δ12): `b62abbcac0653a661cd1bbe344dee9dbba0cddee37448ea16681d436166c3aad`
- `delta13.txt`: `99dbe526792323b2f77786bcb3dee4fbee624e2efac5dc8a52c02cb8fb45b891`

## Germs and Proposition 5.4

```
python3 germcompare.py ../results/mazoyer6.txt 78   # 57 neighbourhoods besides (L,L,L) below anti-diagonal 78
python3 germcompare.py ../results/delta14.txt 78    # 16 ...
./germdfs 5 78 14 40 | cmp - ../results/germs/germs_K14.txt
    # k=5 M=78 K=14 NP=40: nodes=100396178 germs=244 ...   (on stderr; cmp: no output)
python3 germdfs_check.py 14 78 40
    # K=14 M=78 NP=40 nodes=99527730 germs=244 (the same 244 germs, in another order)
python3 germinc.py ../results/germs/germs_K14.txt 10 78
    # SUMMARY {'UNSATISFIABLE': 230, 'SATISFIABLE': 14}   (results/germs/K14_n10.log)
python3 germcert.py ../results/germs/K14_refuted10.txt 10 ../cnf/k14_n10
    # CaDiCaL UNSAT, lrat-check VERIFIED
./germext 5 3300 3 12 < ../results/germs/germs_K14_surv10.txt
    # 14 x CLOSED reach=3300 REFUTED, all with s=1, n <= 163, L <= 5 (e.g. n=28 s=1 L=1 Y=19)
python3 germ_k14_check.py                            # the same conclusion by an independent simulation
```

How the files fit together:
- `germinc.py` and `germcert.py` use the lengths 2..10, the half-line to anti-diagonal 78, PUMP pairs up to 39 and no symmetry breaking.
- `K14_refuted10.txt` consists of the germs of `germs_K14.txt` that are UNSATISFIABLE in `K14_n10.log`.
- `germs_K14_surv10.txt` consists of the other 14.

| file | SHA-256 |
|---|---|
| `germs_K14.txt` | `8493d2bfcaf922f52b4700d25056a25a76b776c097abbd428e6bd13456bbffb5` |
| `K14_refuted10.txt` | `13a0ec36dd9db0e594376c87245c2db985e88af7b4abe5212d34e8c2333cead8` |
| `k14_n10.cnf` | `4f9306a87efd10912cc37de2e674f833bdbf3ac413fd722732b9608ce909c097` |
| `k14_n10.lrat` | `b2324436d2d14efa3e61296eb6dd5776bbe6bf84b0562f5972665db932eddea8` |

Recorded: CaDiCaL 4.4 s, proof 11 MB, lrat-check 0.6 s.

## Proposition 5.5 (Balzer's conditions)

```
python3 balzer_mazoyer.py 150      # Mazoyer's rule: B1, B2, B4 violated; B3 holds (strong reading)
python3 balzer.py 10 1234 AB --lrat     # UNSATISFIABLE, LRAT VERIFIED
python3 balzer.py 9 1234 LA --lrat      # UNSATISFIABLE, LRAT VERIFIED
python3 balzer.py 9 1234 LB --lrat      # UNSATISFIABLE, LRAT VERIFIED
python3 balzer_k.py 5 12 1234 id --cnf=../cnf/w.cnf
kissat ../cnf/w.cnf ../cnf/w.drat                       # s UNSATISFIABLE
drat-trim ../cnf/w.cnf ../cnf/w.drat -L ../cnf/w.lrat   # s VERIFIED
lrat-check ../cnf/w.cnf ../cnf/w.lrat                   # c VERIFIED
python3 balzer.py 11 1234s id           # SATISFIABLE: a rule for 2..11 (results/balzer_sym11.txt)
./fsspcheck ../results/balzer_sym11.txt 2 11   # OK ... for all 2 <= n <= 11
./fsspcheck ../results/balzer_sym11.txt 12 12  # FAIL n=12: a cell fires at time 20 < 22
```

Arguments of `balzer.py N CONDS I`:
- the lengths 2..N;
- `1234` means the weak reading, `1234s` the strong one;
- I is the involution: `id`, `AB`, `LA` or `LB`.

The weak reading is implied by the strong one, so these runs cover both readings. The times, proof sizes and SHA-256 digests of every formula and proof are in `results/balzer.log`. The six-state rules come from `python3 balzer_k.py 6 N 1234s I` with I ∈ {id, AB, LA, LA_BC}; the runs are in `results/balzer6.log`.

## Remark 3.5

```
python3 theta.py ../results/mazoyer6.txt 2600 699 1        # theta_T(j) - 2j in {1, 2}, period 3
python3 theta.py ../results/uniformA_2-12.txt 1400 300 10  # theta_T(j) - ceil(3j/2) = 2, period 1
python3 pumping.py ../results/uniformA_2-12.txt 650        # 0 violations
```

The output is in `results/theta_pump.log`.

## History

The following were removed from the tree when it was reduced to what the note needs:
- the 62-page manuscript the note condenses;
- the research log;
- the record of the literature search;
- the programs and logs of experiments the note does not use (germs of complexity 16 and 17, cube-and-conquer, search-size estimates, restricted classes of rules);
- an explainer video.

They remain in the history of the repository; commit cdf33e2 is the last one that contains them.
