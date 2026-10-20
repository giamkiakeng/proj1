# The second note

`note2.tex` is the note *Necessary conditions on minimal-time solutions of the firing squad problem*. It is 9 pages in Elsevier's journal-style `3p` layout, references included. It collects the statements proved in `../note/note.tex` and in `../research/early_rows.tex`; the exceptions are listed below.

Build it with `latexmk -pdf note2.tex`, or with `pdflatex note2; bibtex note2; pdflatex note2; pdflatex note2`. `note2.pdf` and `note2.bbl` are committed, and `refs.bib` is a copy of `../note/refs.bib`.

| note2 | source |
|---|---|
| §2: Lemmas 2.1–2.3, eq. (2) | note §2 |
| §3: Lemmas 3.1–3.3, Theorem 3.4 | note §3 |
| §3: Lemma 3.5 (right band) | early_rows.tex, Lemma "right band" |
| §4: Lemma 4.1, Theorem 4.2, Corollary 4.3 | note §4 |
| §5: Lemmas 5.1 and 5.2, Corollary 5.3, Definition 5.4, Lemma 5.5 | early_rows.tex §§1–2 |
| §6: Theorem 6.1 (i) | note Theorem 5.1 |
| §6: Theorem 6.1 (ii), (iii) and the paragraph after it | early_rows.tex, Propositions "G4" and "G4cone" |
| §6: Proposition 6.2 | early_rows.tex, Proposition "nearmiss" (its table is written out in the proof) |
| §6: the paragraph after Proposition 6.2 | note, text after Proposition 5.2; early_rows.tex, Proposition "nearmissearly" |
| §6: Proposition 6.3, Corollary 6.4, Proposition 6.5 | note Proposition 5.4, Corollary 5.3, Proposition 5.5 |
| §7: the two models of the germ of δ14d | early_rows.tex, Proposition "germmodels" (i), (ii) |

## Changes with respect to the sources

- Lines and the half-line are partial maps with a local definedness convention: a cell is defined when its three predecessors are defined and none of them is `F`. Lemmas 2.2, 3.1 and 5.1 are stated for partial values ("both undefined or both defined and equal"). As a result, condition (G5) is stated directly on the cells of R_n; early_rows.tex needed the determinacy map Ψ for it. The encoding is unchanged.
- Lemma 5.2 (periodicity certificate) assumes only that the depth vectors are working states over one period, not that the whole half-line never fires. This is what the proof of Proposition 6.2 checks.
- Definition 5.4 requires C ≤ N₁, so (G4) covers every half-line cell that (G5) uses. Every formula of Theorem 6.1 and of the paragraph after it satisfies this; the one exception, "(G1) for T = 4 with (G5) for 6 ≤ n ≤ 12", is stated separately.
- Proposition 6.2 now says "τ ≤ min(T, n−2)". Lines of length 15 ≤ n < T+3 are covered by direct simulation, and every line of length 15..60 fires before time 2n−2. The proof also says why the early firing cell lies in E(T): for each of the five rules, the half-line has no `F` before time 3000 (`../research/failall.py` asserts this).
- The test with δ14's table fixed uses the early rows T = 8 (unsatisfiable) and T = 6 (satisfiable) of the lines 15..30, as recorded in `../research/LOG.md` §22.

## Left out

These items were left out because none of them supports a statement of the note, and the page budget is 9 pages:
- the figures of `../note`;
- Remark 4.4 of `../note` (the mirror image of Lemma 4.1);
- the six-state remark after Proposition 5.5 of `../note`;
- from early_rows.tex:
  - Lemma "class" (uniform pre-firing configurations);
  - Lemma "labellings" (the common relaxation of the two complexity-15 germs);
  - Proposition "mazoyer" (observations on Mazoyer's solution);
  - Proposition "germmodels" (iii).

The programs, rule tables, logs and digests behind the computer-assisted statements are in `..`. `../research/README.md` gives the commands that regenerate the formulas of Theorem 6.1 (ii), (iii). `../README.md` gives those for the other statements, under the numbering of `../note` (see the table above).
