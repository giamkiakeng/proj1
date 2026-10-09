# The note

`note.tex` is the note *Two necessary conditions on minimal-time solutions of the firing squad problem*. It is 10 pages in Elsevier's journal-style `3p` layout, references included.

Build it with `latexmk -pdf note.tex`. `note.pdf` and `note.bbl` are committed.

| file | content |
|---|---|
| `fig_anatomy.tex`, `fig_chains.tex`, `tikzdefs.tex` | the two TikZ figures |
| `refs.bib` | bibliography |
| `REVIEW.md` | report of an independent internal referee on the first version (commit 6603276), with the point-by-point response |

The programs, rule tables, logs and digests behind the computer-assisted statements (Section 5 and Remark 3.5) are in `..`. `../README.md` gives the command that checks each statement.

## Relation to the earlier manuscript

The note condenses a 62-page manuscript. That manuscript is no longer in the tree; the last commit that contains it (`fssp5/paper/`) is cdf33e2.

| note | manuscript |
|---|---|
| §2: Lemmas 2.1–2.3, eq. (2) | §2 |
| §3: Lemmas 3.1–3.3, Theorem 3.4, Fig. 1 | §3.1–3.3 |
| §4: Lemma 4.1, Theorem 4.2, Corollary 4.3, Remark 4.4, Fig. 2 | §3.4–3.5 |
| §5: encoding | §4 |
| §5: Theorem 5.1 | Theorem 5.1 |
| §5: Proposition 5.2, Table 1 | Proposition 6.3 |
| §5: Corollary 5.3 | Corollary 6.2 |
| §5: Proposition 5.4 | Proposition 6.4 |
| §5: Proposition 5.5 | Proposition 6.5 |
| §6 | §7 |

Remark 3.5 is new: its data are in `../results/theta_pump.log`.

Left out of the note:
- the glossary;
- the explanatory figures and the space-time diagrams;
- the regularity certificate (Lemma 3.9) and the results on germs of complexity 16 and 17 that rest on it;
- the "lucky" rules;
- the four-state enumeration table;
- the search-size estimates;
- the cube-and-conquer experiments;
- the printed tables of δ12 and δ13 (their files are in `../results`).
