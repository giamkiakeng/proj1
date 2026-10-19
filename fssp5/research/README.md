# Research after the note

This directory holds ongoing work on the five-state question that goes beyond the note in `../note`.
`LOG.md` records every experiment and its result; nothing here is part of the note's evidence.

| file | content |
|---|---|
| `gfix.py` | encoder for completion constraints on a fixed half-line (a germ file) or a free one (`FREE`). It can encode three kinds of region: full triangles, the cones of the right h+1 firing cells, and left bands of h chains. Option `--fix` checks a given table; `GFIX_REV=1` adds redundant clauses. |
| `gcegar.py` | refinement loop around gfix.py, run with kissat. It solves the current constraints, simulates lengths 2..NMAX, and adds the cones of the failing cells. It stops with FOUND (a table, verified by simulation), with UNSAT (no completion for the lengths involved), or when a budget runs out. `--P` fixes the set of neighbourhoods that give F, `--Pint` only the interior ones (border entries stay free), and `--upf X` adds the redundant clauses "every cell at time 2n−3 is X" for the class with pre-firing configuration X^n. `KISSAT_OPTS` passes solver options. |
| `gcegar_inc.py` | the same loop with one incremental CaDiCaL instance (PySAT) for the whole run, so that clauses learned in earlier rounds are kept; `--fine` adds the cone of the earliest wrong cell only. |
| `certify.sh` | re-solves an unsatisfiable formula with a DRAT proof, converts the proof to LRAT with drat-trim and checks it with lrat-check. |
| `ils5.c` | iterated local search over rule tables, in the spirit of Clergue–Verel–Formenti 2018 (calibration only; see LOG.md §10). |
| `germs/K16_remaining16.txt` | the 16 germs of complexity ≤ 16 that survive all tests of the manuscript. Two of them have complexity 15: those of δ14c and δ14d. |
| `germs/K17_irregular187.txt` | the 187 complexity-17 germs that survive germext and are not certified regular. |

The tools expect kissat, drat-trim and lrat-check at the paths of `../README.md`, or in the variables `KISSAT`, `DRATTRIM` and `LRATCHECK`.
