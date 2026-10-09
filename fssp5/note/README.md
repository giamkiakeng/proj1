# Short version of the paper (note)

`note.tex` condenses the 62-page manuscript in `../paper` to its contributions. It is 10 pages in
Elsevier's journal-style `3p` layout, references included (16 pages in the manuscript's own
`preprint,11pt` layout). Build with `latexmk -pdf note.tex`.

`REVIEW.md` contains the report of an independent internal referee on the first version (commit
6603276) and, point by point, the changes made in response.

## What the note contains

| note | manuscript | content |
|---|---|---|
| §2, Lemmas 2.1–2.3, eq. (2) | §2, Lemmas 2.1–2.3, Remark 2.4, eq. (2) | light cone, agreement, return chain, lower bound 2n−2 |
| §3, Lemmas 3.1–3.3, Theorem 3.4, Fig. 1 | §3.1–3.3, Lemmas 3.1–3.3, Theorem 3.4, Fig. 5 | determinacy, cone, pumping lemma, speed-1/3 barrier (complete proofs) |
| Remark 3.5 | (new) | θ(j) for Mazoyer's rule and for delta12; 3/2 appears optimal for Lemma 3.3 alone (`../results/theta_pump.log`, from `../src/theta.py` and `../src/pumping.py`) |
| §4, Lemma 4.1, Theorem 4.2, Corollary 4.3, Remark 4.4, Fig. 2 | §3.4–3.5, Lemma 3.5, Theorem 3.6, Remark 3.7, Corollary 3.8, Fig. 6 | left-border lemma, wedge barrier, no eventually regular half-line (complete proofs) |
| §5, encoding paragraph | §4 | the formula MT_k(N; M, N'), its validation against Mazoyer's rule, LRAT checking |
| Theorem 5.1 | Theorem 5.1 | LRAT-certified four-state bound |
| Proposition 5.2, Table 1 | Proposition 6.3, Table C.10 | delta14: all lengths up to 14 |
| Corollary 5.3 | Theorem 6.1(c), Corollary 6.2 | the delta12/delta13 half-line is refuted at length 518 |
| Proposition 5.4 | Proposition 6.4, Table 5 | c78 >= 15 for every five-state solution |
| Proposition 5.5 | Section 6.4, Proposition 6.5 | Balzer's conditions, certified |
| §6 | §7 | open problems |

## What was left out

The notation page and glossary (Appendix A); the regularity certificate (Lemma 3.9)
and the complexity-16 results that rest on it; the lucky rules of §6.1 (Table 4); the four-state enumeration (Table 3); the search-size
estimates of §6.5; the further experiments of Appendix B (complexity 16 and 17,
cube-and-conquer, length 15); the rule tables of Appendix C other than delta14 and the reproduction
commands and digests of Appendix D (both in the repository); the explanatory Figures 1–4 and 7
and the space-time diagrams of Figures 8–10. Every number in the note is taken from the manuscript or
recomputed from the files in `../results` (Remark 3.5: `../results/theta_pump.log`).
