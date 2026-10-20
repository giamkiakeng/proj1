# Research after the note

This directory holds ongoing work on the five-state question that goes beyond the note in `../note`.
`LOG.md` records every experiment and its result; nothing here is part of the note's evidence.

| file | content |
|---|---|
| `gfix.py` | encoder for completion constraints on a fixed half-line (a germ file) or a free one (`FREE`). It can encode three kinds of region: full triangles, the cones of the right h+1 firing cells, and left bands of h chains. Option `--fix` checks a given table; `GFIX_REV=1` adds redundant clauses. |
| `gcegar.py` | refinement loop around gfix.py, run with kissat. It solves the current constraints, simulates lengths 2..NMAX, and adds the cones of the failing cells. It stops with FOUND (a table, verified by simulation), with UNSAT (no completion for the lengths involved), or when a budget runs out. `--P` fixes the set of neighbourhoods that give F, `--Pint` only the interior ones (border entries stay free), and `--upf X` adds the redundant clauses "every cell at time 2n−3 is X" for the class with pre-firing configuration X^n. `KISSAT_OPTS` passes solver options. |
| `gcegar_inc.py` | the same loop with one incremental CaDiCaL instance (PySAT) for the whole run, so that clauses learned in earlier rounds are kept; `--fine` adds the cone of the earliest wrong cell only. |
| `certify.sh` | re-solves an unsatisfiable formula with a DRAT proof, converts the proof to LRAT with drat-trim and checks it with lrat-check. |
| `certify_lrat.sh` | the same with CaDiCaL 3, which writes the LRAT proof directly. |
| `asymp.py`, `failall.py` | the early-rows reduction for a fixed germ (periodicity certificate of the depth rows, representative lengths), and the simulation proof that a rule fails for all long lines (`early_rows.tex`, Proposition on the near misses). |
| `allsat.py` | enumerates the completions of a germ (or `FREE`) for the lengths 2..N, one class per projected table, and extends each class by depth-first search. Infeasible at the relevant sizes (LOG.md §25). |
| `dfs_timeorder.c` | an independent re-implementation of `../src/fsspdfs.c` (exhaustive depth-first search in the style of Balzer and Sanders), which evaluates the cells in time order instead of along anti-diagonals and adds return-chain pruning; `--plain` counts the partial rules for the lengths 2..N alone (27 for four states and N = 8, as with the original). Compile with `gcc -O3 -o dfs_timeorder dfs_timeorder.c`. |
| `early_rows.tex` | research notes with proofs: early rows, the formulas G_k(T, N1), pre-firing classes, the right-band lemma, Mazoyer's architecture, the complexity-15 half-line. |
| `ils5.c` | iterated local search over rule tables, in the spirit of Clergue–Verel–Formenti 2018 (calibration only; see LOG.md §10). |
| `germs/K16_remaining16.txt` | the 16 germs of complexity ≤ 16 that survive all tests of the manuscript. Two of them have complexity 15: those of δ14c and δ14d. |
| `germs/K17_irregular187.txt` | the 187 complexity-17 germs that survive germext and are not certified regular. |

The early-row formula G_k(T, N1) of `early_rows.tex` is `gfix.py FREE k full:2-(T+1) early:(T+2)-N1:T` (with `GFIX_SHARE=1`, and `GFIX_SYMBREAK=1` for k = 5). Do not use `GFIX_SHALLOW` for it. That option leaves the deep half-line cells unconstrained, which admits spurious models (LOG.md §26).

### Reproducing the certified four-state results of `early_rows.tex`

```
GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-7 early:8-10:6 --cnf k4_G6.cnf               # G_4(6,10)
./certify_lrat.sh k4_G6.cnf      # c VERIFIED; LRAT ~167 MB
#   CNF sha256 0e0ba286ec7b60d05f6edee470b5cbd4d6655cd184186e630a96bd4187932e03
GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-5 early:6-10:4 cone:6-10 --cnf k4_G4c.cnf    # G_4(4,10,10)
./certify_lrat.sh k4_G4c.cnf     # c VERIFIED; LRAT ~173 MB
#   CNF sha256 124f095450ee725be06f07271e1d752c4cbacce9f4bff190ddea1907d39e4f51
```

The CNF files are generated deterministically (regenerated and compared on 2026-10-20); the digests of the LRAT files are in `LOG.md` (§§26, 28).

The tools expect kissat, drat-trim and lrat-check at the paths of `../README.md`, or in the variables `KISSAT`, `DRATTRIM` and `LRATCHECK`.
