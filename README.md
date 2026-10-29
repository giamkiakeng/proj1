# Two barriers for minimal-time firing squads, with applications to four and five states

This repository holds the paper by Kia Keng Giam and its supplementary material.

- **Paper:** `fssp5/paper/paper.pdf`. The LaTeX source is `paper.tex` with the section files `sec*.tex`, the figures in `figures/` and the references in `references.tex`, all in the same directory.
- **Supplementary material:** `fssp5/paper/supplementary/`. It holds the programs, rule tables, germ lists and logs behind every computer-assisted statement of the paper, and the program that draws the figures. Its README maps each statement to the commands that reproduce it and the expected output.

## Checking the computations

```
cd fssp5/paper/supplementary
./check_quick.sh          # about 7 minutes; Python 3 with PySAT, and a C compiler
./check_certificates.sh   # about 30 minutes; also CaDiCaL, Kissat, drat-trim and lrat-check
```

The proofs of Sections 2–5 need no computation. In the computer-assisted statements, every unsatisfiability claim is certified by an LRAT proof, which an independent checker verifies. Everything else is direct simulation, exhaustive enumeration, or a satisfiable formula. `check_certificates.sh` writes about 4 GB to `cnf/`. The supplementary README lists the solver versions used.

## Building the paper

```
cd fssp5/paper
python3 supplementary/src/figures.py figures   # only to regenerate the figure data in figures/
pdflatex paper && python3 make_refs.py && pdflatex paper && pdflatex paper
```

`make_refs.py` writes `references.tex`, numbering the references in the order of their first citation, as the journal requires. The committed `references.tex` and figure data are up to date, so `pdflatex paper` twice suffices.
