# Necessary conditions on minimal-time solutions of the firing squad problem

This repository holds the paper by Kia Keng Giam, submitted to *Theoretical Computer Science*, and its supplementary material.

- **Paper:** `fssp5/note2/note2.pdf`. The LaTeX source is `note2.tex`, with `refs.bib` and `note2.bbl`, in the same directory. Build it with `latexmk -pdf note2.tex`, which needs Elsevier's `elsarticle` class.
- **Supplementary material:** `fssp5/note2/supplementary/`. It holds the programs, rule tables, germ lists and logs behind every computer-assisted statement of the paper. Its README maps each statement to the commands that reproduce it and the expected output.

## Checking the computations

```
cd fssp5/note2/supplementary
./check_quick.sh          # about 7 minutes; Python 3 with PySAT, and a C compiler
./check_certificates.sh   # about 30 minutes; also CaDiCaL, Kissat, drat-trim and lrat-check
```

The proofs of Sections 2–5 need no computation. In the computer-assisted statements, every unsatisfiability claim is certified by an LRAT proof, which an independent checker verifies. Everything else is direct simulation, exhaustive enumeration, or a satisfiable formula. `check_certificates.sh` writes about 4 GB to `cnf/`. The supplementary README lists the solver versions used.
