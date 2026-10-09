# Internal review of the note

The first version of the note was commit 6603276, titled "Two barriers for minimal-time firing squads, and certified bounds for four and five states" (9 pages). An independent agent, working in a separate context, reviewed it as a referee.

- **Method.** It checked every proof line by line. It also re-ran the simulations, enumerations and formula generation with its own programs. It did not re-run the SAT solvers or the LRAT checks.
- **Recommendation.** Major revision, assuming a short-communication venue such as IPL or a cellular-automata journal. It judged the note not suitable for TCS.
- **Correctness.** It found no error in the proofs of §§2–4. Its objections concerned:
  - positioning;
  - the word "certified";
  - four statements that were wrong or unsupported as written;
  - the literature.

The report is reproduced at the end of this file. Line numbers in it refer to `note.tex` at commit 6603276.

## Response: what changed

| point | change |
|---|---|
| M1 positioning | **Title:** "Two necessary conditions on minimal-time solutions of the firing squad problem".<br>**Abstract and introduction:** both now open with Theorem 3.4, Theorem 4.2 and Corollary 4.3.<br>**Folklore:** Lemmas 2.1–2.3 and 3.1 are marked as elementary.<br>**New Remark 3.5, optimality:** on the half-line of δ12, θ(j) = ⌈3j/2⌉+2 for 10 ≤ j ≤ 300 (observed up to time 1400), and PUMP(n,n′) holds for n′ ≤ 650. So 3/2 appears to be the limit of Lemma 3.3 alone, and this half-line is caught only by Lemma 4.1 (Corollary 5.3). The data are in `results/theta_pump.log` and come from `src/theta.py` and `src/pumping.py`.<br>**Section 5:** now titled "Applications to four and five states". Every item is kept because it either applies a barrier or bounds what the barriers can do. |
| M2 "certified" | **Trust statement:** the LRAT proofs certify the generated formulas; the generator, the enumeration and the simulations are trusted programs, tested as described.<br>**Wording:** Propositions 5.4 and 5.5 are now "computer-assisted; the SAT part is LRAT-certified".<br>**Theorem 5.1:** prints the SHA-256 of its formula.<br>**Proposition 5.4:** reports the second, independent enumeration (244 germs).<br>**Not done:** a formally verified checker (cake_lpr) and a second encoder. |
| M3 symmetry breaking | The order is now specified: first occurrence of the auxiliary states, in time-major order. The note states that none of the formulas uses it, and Propositions 5.4 and 5.5 say "without symmetry breaking". This matches the runs (`symbreak=False`). |
| M4(a) Cor 5.3 | Now reads "No five-state rule …". Proposition 5.4 already concerns five-state solutions. |
| M4(b) I(G) = G | Replaced by the referee's argument from (B1), (B2) and (B4), which holds in both readings. |
| M4(c) six states | Reworded. For every type of involution there are rules for lengths up to 13, and for two types up to 14. This was re-checked on `balzer6_sym14.txt` and `balzer6_LA14.txt`, which both satisfy the strong reading and fail at 15. |
| M4(d) δ14 | Qualified as "in the ranges of Proposition 5.2". |
| M5(a) attributions | **Mazoyer [Prop. 2]:** described as comparing the lengths 2, 3 and 4.<br>**Pigeonhole arguments for variants:** cited through the sources actually read: "we follow the description in [Kobayashi 2019]".<br>**Settle's thesis:** "as described in [Correa et al.]".<br>**Novelty:** worded as "We are not aware of …". |
| M5(b) missing references | Added Yunès 2008, Umeo–Yanagihara 2007, Berthiaume et al. 2004, Kobayashi 2019, D'Antonio–Delzanno 2004 and Mazoyer–Terrier 1999. |
| M5(c) bibliography | **Wetzler et al.:** author list corrected in both `refs.bib` files.<br>**Duprat:** both sources are now cited. The 1997 Coq contribution is the development the table was extracted from; the 2002 LIP report (hal-02101837) describes its proof. |
| 1 | The non-r.e. sentence is now a parenthetical contrast: existence versus non-existence. |
| 2 | "explains a priori" is removed; the text now says "reaching the line i = t/3". |
| 3 | "five-state minimal-time solution" is used throughout. |
| 4 | L, G and F are now pairwise distinct; working and auxiliary states are defined. |
| 5 | "first applicable case" fixes the precedence of the border case. |
| 6 | **Lemma 3.2:** now stated for n ≥ 2.<br>**Lemma 3.3:** now for 2 ≤ n < n′, assuming only that the lines n and n′ are synchronized.<br>**Name:** "pumping" is kept, because Theorem 3.4 applies the lemma to n and n + P. |
| 7 | Range 0 ≤ j ≤ t+1 and the border term are given; row j starts at time j. |
| 8 | θ(j) is defined as the least t0 ≥ j from which the row is periodic. |
| 9 | Uses P_0, …, P_{n−1} and "each of them". |
| 10 | Conventions are stated for n = 2, κ = 0 and for chain −1. |
| 11 | s + ℓ ≤ Y is dropped, "ℓ-periodic" is defined, and the period is renamed ℓ. |
| 12 | m, w_j, z_j, a_j and D_j now depend explicitly on r. |
| 13 | MT_k(𝒩; M) is defined: it has no PUMP clauses. |
| 14 | "n ≥ 3" for the extracted Mazoyer table. |
| 15 | Yunès's convention δ(∗,L,L) = L is stated (none of the 27 rules uses it), and Sanders' example is described correctly. |
| 16 | The unverifiable sentence is removed. |
| 17 | **Rule 22:** cells i ≥ 3 are described as "rule 22 driven at its left end by the cells 1 and 2"; cell 3 sees cell 2.<br>**Wording:** "chaotic" is replaced by "irregular". |
| 18 | The files are named, and the 22 transitions are printed. |
| 19 | **Selectors:** now described as one selector per germ plus an at-least-one clause.<br>**Intervals:** upper on [1,Y], lower on [1,Y−1].<br>**No change:**<br>• N′ = 39: with the germ fixed, C∞ below 78 is determined and was checked for PUMP up to 40 during the enumeration.<br>• "anti-diagonal 3300": this is the range actually computed (`results/germs/K14_ext3300.txt`). |
| 20 | The sentence that relied on the extended version (9,787 germs) is removed. The extended version is mentioned only under data availability. |
| 21 | Proposition 5.5 now has a proof block that gives the base formula, the solvers and the checking times. |
| 22 | The legend inside Figure 2 is removed; its content is in the caption. |
| 23 | The path length in the proof of Lemma 3.2 is r, and the length argument of Ψ is m. "Partial rules" is defined. |
| 24 | **Not done:**<br>• archiving the data with a DOI;<br>• purging the two publisher PDFs from the git history. This needs a history rewrite by the repository owner. |
| 25 | **Not done:** checking the AI-use statement against the target journal's policy. |

Further changes in the revision:
- §5: two existential statements are now worded as "there are rules …":
  - the five-state Balzer rules for lengths up to 11, re-checked on `results/balzer_sym11.txt` (strong reading, fails at 12);
  - the six-state sentence.
- Remark 3.5: the observation horizons are stated.

After the revision, two claims the referee could not verify were checked with `src/halflines.py`:
- **The four further rules.** All four lie on half-lines other than δ14's, and δ14c and δ14d share a half-line up to renaming of states. §5 now says "on three other half-lines (up to renaming of states)".
- **The rule-22 description of δ14.** It was re-checked for 3 ≤ t < 1500.

## Referee report: "Two barriers for minimal-time firing squads, and certified bounds for four and five states"

Files reviewed: `note/note.tex` at commit 6603276 (9 pp., 3p layout), cross-checked against `paper/` and `results/`. I changed no repository files. [The referee's own scripts (`sim.py`, `lemmas.py`, `refdfs.c`, `ref4.c`, `check_*.py`) were kept in a temporary directory and are not part of the repository.]

### Summary of the note
- **Setup.** Below the anti-diagonal t+i = 2n−2, every line of length n agrees with the half-line C_∞. The rest of the line, the reflected triangle R_n, is a function of two anti-diagonals of C_∞.
- **Two necessary conditions, for any number of states:**
  - A "pumping lemma": the input words of R_n and R_{n'} must differ on the dependency cone of the right end. This gives limsup θ(j)/j ≥ 3/2 for the times θ(j) at which the depth-rows behind the front become periodic (Thm 3.4).
  - A left-border lemma with bound (k−1)^{2s}L (Lemma 4.1). It gives that C_∞ is not doubly periodic in any wedge at the left border (Thm 4.2), so it is never eventually regular (Cor 4.3).
- **Computer-assisted results (Section 5):**
  - an LRAT-certified re-proof that four states do not suffice (lengths 2..9);
  - c_78 ≥ 15 for every five-state minimal-time solution, by germ enumeration, a certified completion test and Lemma 4.1;
  - a certified confirmation of Balzer's 1967 conditional five-state claim;
  - a five-state rule δ_14 that synchronizes all lengths ≤ 14.

### Recommendation: major revision
This assumes a short-communication venue such as IPL or a journal specialised in cellular automata. In its present form the note is not suitable for TCS.
- **Correctness is not the problem.** The proofs in §§2–4 are correct up to small imprecisions, and every number I could recompute matches.
- **What needs revision:**
  - Significance is asserted rather than argued. The note contains the same results as the desk-rejected manuscript, only compressed, so it does not answer the editor's objection by itself.
  - "Certified" overstates what the certificates cover.
  - Several statements are wrong or unsupported as written: the omitted "without symmetry breaking", Cor 5.3 without "five-state", the weak-reading step (B3) ⇒ I(G)=G, and the six-state claim.
  - Section 5 depends on the repository and on an unrefereed extended version.
  - The related-work coverage has misattributions and omissions.

### Contribution and novelty
**Relation to known work**
- **Lemma 3.3** generalises the indistinguishability idea behind Mazoyer 1996, Prop. 2. According to the authors' own reading, that proposition compares lengths 2, 3 and 4 in the one-way model. The note applies the idea to all lengths of the two-way problem, where it constrains solutions rather than excluding them.
- **Yamashita et al. 2014 and Kobayashi 2019** use repeated-state pigeonhole arguments to exclude minimal time for variants of the problem. Kobayashi is not cited in the note.
- **Mazoyer–Terrier** supply the eventual periodicity of the cells at bounded depth behind the front, which is step 1 of Thm 3.4. This is credited.
- **Balzer, Yunès, Sanders** established the four-state result (only the certificate is new) and Balzer's conditional result (independently certified here for the first time).
- **Settle's thesis** is cited only second-hand.

**Novelty**
- I know of no published statement equivalent to Thm 3.4 or Thm 4.2/Cor 4.3, and a quick search found none. That is not conclusive.
- Both are short pigeonhole or indistinguishability arguments that experts may regard as folklore.
- By the authors' own record (`related_work_review.md`), Mazoyer's 1989 habilitation was not consulted. The novelty claims should be worded cautiously ("we are not aware of …").

**Significance**
- **Thm 3.4 is weak.**
  - Mazoyer's solution meets it with room to spare: θ(j) ∈ {2j+1, 2j+2}.
  - It is the best that Lemma 3.3 alone can give. The regular half-line of δ_12 has θ(j) = 3j/2 + 2 and satisfies PUMP(n,n') for all 4 ≤ n < n' ≤ 650 (my computation).
  - Its claim to "explain a priori" the speed-1/3 signal is heuristic.
- **Thm 4.2/Cor 4.3 is the more interesting result:** a clean qualitative obstruction for every number of states. But:
  - Lemma 4.1 is exponential in s and bites only on long lines (n = 518 for δ_12).
  - It has no grip on chaotic half-lines such as δ_14's, which is exactly where the five-state question now sits.
- **The computational results are useful data but incremental:** a known theorem re-certified, an ad hoc complexity measure c_78, a 1967 conditional claim, and a near-miss rule.

**Enough for a journal note?**
- For TCS, no: the same verdict as for the long version is likely.
- For IPL, possibly, if refocused on the two barriers with an argued significance and made self-contained. A short computational companion paper is an alternative.

**Framing**
- The title promises "certified bounds for four and five states". The four-state bound is known, and Balzer's result is not a bound.
- The abstract opens with background and compresses the long abstract.
- The introduction has no single main theorem, no motivation beyond pruning searches, and a four-sentence related-work paragraph.
- A resubmission to the editor who desk-rejected the long version should state the relation in the cover letter.

**Venues:** IPL (focused theory note); Natural Computing, Journal of Cellular Automata or Fundamenta Informaticae; AUTOMATA (IFIP WG 1.5), MCU or UCNC proceedings for the combined material.

### Correctness, statement by statement
- **Lemma 2.1:** correct. Small technicality: C_n is only "considered up to the first F" and δ is undefined on F, so read the lemma as "whenever defined"; the same applies to Lemmas 2.2 and 3.1.
- **Lemma 2.2:** correct.
- **Lemma 2.3:** correct. Index ranges check, the i = n step is right, and n = 2 is consistent because f_1 = G. The proof only needs that line n+1 does not fire before time 2n.
- **Lower bound (l.184–185):** correct, but no argument is given; add one line.
- **"Cell i leaves L exactly at time i−1" and eq. (2):** correct.
- **Relative coordinates, R_n, J_n and the claim about predecessors (l.196–208):** correct.
- **Lemma 3.1:** correct. At κ = τ = N−1, the position κ' = N meets both the "∗" case and the "lower input" case; the border must take precedence (it is listed first; say so).
- **Lemma 3.2:** correct. An independent BFS for 2 ≤ n ≤ 300 confirms the closed formula for every n ≥ 2, so "n ≥ 4" is unnecessary. "Negative time" at l.249 means negative relative time τ.
- **Lemma 3.3:** correct. The proof also works for 2 ≤ n < n' and needs only that the lines n and n' are synchronised in minimal time.
- **Eq. (3):** correct for 0 ≤ j ≤ t. The range is missing, and at j = t+1 the left neighbour is the border.
- **Thm 3.4:** correct.
  - Checked: lower cell j = 2κ−2 gives θ > n + j/2 − 2; upper cell j = 2κ−1 gives θ > n + j/2 − 3/2; the limsup step needs α ≥ 1/2, which is arranged.
  - Harmless slack: P_0..P_{n−1} suffice instead of P_0..P_{n+1}. The phrase "all cone positions κ ≥ 1" includes, for odd n, the upper cell at κ = (n+1)/2, which is not in the cone; it has depth n ≤ n, so the conclusion still holds.
- **Mazoyer remark (l.315–318):** verified numerically.
- **Eqs. (4), (5):** correct. Checked ⌊c/2⌋ − ⌊(c−1)/2⌋ = ε_c, the formulas for u_{−1} and u_0, the time 2n−2+⌈c/2⌉−y, and that the cell is F iff ⌈c/2⌉ = y.
- **Lemma 4.1:** correct.
  - Cells are defined because y+⌊c/2⌋ ≤ Y+s ≤ n and ⌈c/2⌉ ≤ s ≤ y.
  - Γ is used only for s+1 ≤ y ≤ Y−1, where u_{−1}(y) is not the border even when s = 1; Γ' covers y = s.
  - The pigeonhole count and the downward-induction ranges check: y+h < y_2 ≤ Y and s+h ≤ Y−1.
  - The hypothesis s+L ≤ Y is redundant.
- **Thm 4.2:** correct. The intermediate cells lie in Ω, and Y_n ≥ 2αn/(1+α) − 4 holds.
- **Definition of eventually regular and Cor 4.3:** correct. β is uniform over the P residues, and the wedge lies inside block j(r) for large t.
- **Remark 4.4:** correct. The mirror argument is valid, and for 2y < n both words lie in R_n.
- **Thm 5.1:** the logic is correct, given that the encoder is faithful. The soundness argument checks: Lemmas 2.1 and 2.2 with n = 9, and return chains for n ≤ 8.
- **Prop 5.2:** reproduced.
- **Cor 5.3:** correct for five-state rules only; see M4.
- **Prop 5.4:** sound, provided the completion formulas are used without symmetry breaking, which the code does and the note does not say (M3).
- **Balzer reduction (l.630–633):** there is a gap in the weak reading (M4). Once it is repaired, Prop 5.5 follows from the stated runs.
- **Six-state sentence (l.648–650):** not supported.

### Major issues
**M1. Positioning and framing** (l.29–30, 43–58, 88–116, 653–665).
- Lead with Thm 3.4 and Thm 4.2/Cor 4.3, one sentence each, in the abstract and in the first paragraph of the introduction.
- Mark Lemmas 2.1–3.1 as folklore.
- Add an optimality remark: δ_12's half-line attains θ(j)/j → 3/2 and passes PUMP for n' ≤ 650. So 3/2 is optimal for Lemma 3.3, and that half-line is caught only by the left-border barrier, which is a crisp illustration of how the two barriers complement each other. A proof of PUMP for this regular half-line should be easy.
- Trim Section 5 to what illustrates the barriers plus Thm 5.1 and Prop 5.5, or move the rest to a companion paper.
- Retitle; for example: "Two necessary conditions on minimal-time firing squad solutions".
- Do not resubmit to TCS.

**M2. "Certified" overstates what the certificates cover** (l.51–55, 99–107, 468–470, 588–611).
- The LRAT proofs certify only that the generated CNF is unsatisfiable. Thm 5.1 also trusts the encoder (`gencnf.py`). Prop 5.4 also trusts an uncertified enumeration and simulations.
- Checking the encoder against Mazoyer's rule and re-simulating models are tests, not proofs.
- Fixes:
  - State what is trusted. Call Prop 5.4 "computer-assisted; the SAT part is LRAT-certified".
  - Report the enumeration cross-checks. My third implementation, with a different cell order and no symmetry breaking during the search, also finds 244 germs (and 9,787 for complexity ≤ 16).
  - Consider a formally verified checker (e.g. cake_lpr) and a second, independently written encoder.
  - Print the SHA-256 of `mt4_9.cnf` in the paper.

**M3. Symmetry breaking makes the procedure as written unsound** (l.455–467, 600–604).
- The note's MT_k includes an unspecified symmetry breaking. The encoder breaks symmetry by first occurrence in time-major order, while Prop 5.4 normalises germs in anti-diagonal order. The two orders can disagree.
- With both active, a germ whose first B precedes its first A in time-major order could be refuted spuriously.
- The actual runs are fine (`germinc.py` and `germcert.py` use `symbreak=False`, and the long version says so), but the note omits this.
- Fix:
  - Specify the order in the definition.
  - Say which formulas use it, and write "without symmetry breaking" in Prop 5.4.
  - Add that Mazoyer's rule satisfies MT_6 with symmetry breaking only after renaming.

**M4. Statements that are wrong or unsupported as written**
- **(a) Cor 5.3 (l.568), and l.609–610.** The proof uses Lemma 4.1 with k = 5. For k ≥ 6 the bound is (k−1)^4 ≥ 625 > 257, so there is no contradiction. Write "No five-state rule", and likewise in Prop 5.4.
- **(b) l.631, "(B3) forces I(G)=G".** This uses (B3)'s "no other neighbourhood gives F", which the weak reading drops, yet Prop 5.5 is stated for the weak reading. Repair: let g = I(G) ≠ G, so g ∈ W∖{G}. (B4) gives δ(G,g,G) = G, hence by (B2) δ(g,G,g) = g. Weak (B1) gives δ(g,G,g) = G. So I(G) = G in both readings.
- **(c) l.648–650.** The data show only that a refutation would need length ≥ 14 (≥ 15 for I = id and (L A)). Reword.
- **(d) l.552–556.** "Our necessary conditions restricted to lengths ≤ 14 are satisfiable" holds only in the checked ranges: half-line to 10^4, PUMP to 800, and Lemma 4.1 for n ≤ 5000, s ≤ 3, L ≤ 24. Qualify it.

**M5. Literature** (l.76–86, 109–116, bibliography).
- **(a) l.109–111.** Mazoyer's Prop. 2 is not a pigeonhole argument on repeated pairs, by the authors' own reading. Yamashita et al. and Settle's thesis (l.115–116) were not consulted, per the authors' record. Read them, or attribute via the sources actually read (Kobayashi 2019; Correa et al.).
- **(b) Missing references, all already in `refs.bib`:**
  - Yunès 2008 (IPL): four states for lengths 2^k, one step above minimal time.
  - Umeo–Yanagihara: five states for lengths 2^k, 3n−3 steps.
  - Berthiaume et al. 2004.
  - Kobayashi 2019.
  - D'Antonio–Delzanno 2004.
  - Mazoyer–Terrier, TCS 1999 (in `refs.bib` but never cited).
- **(c) Bibliography errors.**
  - Ref. [19] prints "J. Hunt, Warren A."; fix `refs.bib` l.310 to "Hunt, Jr., Warren A.".
  - Duprat 1997: the authors' own record cites the 2002 LIP report (HAL hal-02101837); check the year and source.

### Minor issues
1. **l.84–86:** the non-recursive-enumerability sentence is a non sequitur. Non-existence for fixed k reduces to finite N because there are finitely many rules; non-r.e. concerns existence.
2. **l.94–96, 655:** "explains a priori the speed-1/3 signal" and "structure along the line i = t/3" overstate a limsup bound on when transients end; use "reaching the line".
3. **l.53, 102:** write "five-state minimal-time solution".
4. **l.121–123:** require L, G and F to be pairwise distinct.
5. **l.218–222:** state the precedence of cases at κ' = N.
6. **l.233, 249, 264:** drop or justify n ≥ 4. Weaken the hypothesis of Lemma 3.3 to synchronisation of the lines n and n', which is exactly what the finite formulas use. "Pumping" is a misleading name; consider "separation lemma".
7. **l.279–281:** give the range of (3) and the border term; row j starts at time j.
8. **l.287–289:** define θ(j) precisely: the least t_0 from which the row is periodic with its least eventual period. Consider restating the theorem as "for every n ≥ 4, some input cell of cone_n lies in the transient part of its row".
9. **l.300–304:** P_0..P_{n−1} suffice; write "all input cells of the cone".
10. **l.326:** for n = 2 the chain −1 cell at i = n lies at time −1; state the convention.
11. **l.359:** s+L ≤ Y is redundant. Define "L-periodic". The period L clashes with the state 𝖫; the proof of Cor 5.3 uses both in one sentence. Rename the period, e.g. ℓ.
12. **l.413–419:** make the dependence of m, w_j, z_j, a_j, D_j on r explicit.
13. **l.455–464, 479:** MT_4(𝒩;M), without N', is undefined; say which optional families each formula contains.
14. **l.465–467:** the extracted Mazoyer table does not synchronise n = 2 (it synchronises 3..60); say "n ≥ 3".
15. **l.488–490:**
    - Yunès's 27 are counted with δ(∗,L,L) = L; the counts agree because none of the 27 uses (∗,L,L), which I confirmed.
    - Sanders gives one example rule, not the count.
16. **l.492–495:** "every instance … decided was satisfiable" cannot be checked from the note; list the instances or drop the sentence.
17. **l.549–552:**
    - Only cells ≥ 4 follow rule 22. Cell 3, with neighbourhoods (A,B,B), (A,B,L), (L,L,B), does not.
    - Say what "chaotic" means; for instance, B density ≈ 0.30–0.37 for t up to 10^4.
18. **l.558–560:** δ_12 is `results/uniformA_2-12.txt`. Name the files and print the 22 transitions of the common germ (three lines) so that Cor 5.3 can be checked from the note alone.
19. **l.600–608:**
    - "A selector variable" should be one selector per germ plus an at-least-one clause.
    - Explain N' = 39 versus PUMP to 40.
    - Write "upper anti-diagonal periodic on [1,Y], lower on [1,Y−1]".
    - Anti-diagonal 330 suffices (2·163−2 = 324).
20. **l.613–616:** these lines rely on an unrefereed "extended version". Include the regularity-certificate lemma, or label the sentence as a computational remark; cite the extended version properly (e.g. arXiv).
21. **l.641–646:** Prop 5.5 has no proof block, and its base formula (M, return chains, no symmetry breaking) is unspecified.
22. **Figure 2:** the legend text inside the figure is tiny and duplicates the caption.
23. **Overloaded or undefined symbols:** s (steps in the proof of Lemma 3.2), N in Ψ versus 𝒩 and N'; "auxiliary states", "working states" and "partial rules" are undefined.
24. **l.670–673:**
    - Archive the data with a DOI (Zenodo or Software Heritage).
    - Per the authors' own notes, the public git history still contains two Elsevier PDFs; purge them before pointing editors to the repository.
25. **l.674–677:** check the AI-use statement against the target journal's current policy. Some publishers distinguish AI help with writing from AI use in the research itself.

### Verified computations (re-run independently)
**Rule table and short lines**
- Table 1 equals `results/delta14.txt`: 96/96 entries.
- δ_14 synchronises n = 2..14 at time 2n−2. On n = 15 the first firing is at t = 22, cells 13, 14, 15. The configuration before firing is L G^{n−2} B.
- δ_12 synchronises 2..12; on n = 13 it fires at t = 23 (cell 5).
- δ_13 synchronises 2..13; on n = 14 it fires at t = 21 (cell 11).
- δ_14^b..e synchronise 2..14; on n = 15 they fire first at t = 25, 21, 22, 27.

**Half-line of δ_14, up to t+i ≤ 10^4**
- 16 neighbourhoods besides (L,L,L), the same set as below 78; none maps to F, and no cell is F.
- For 3 ≤ t < 1500: cell 1 ∈ {L,G}, cell 2 ∈ {L,A}, cells ≥ 3 ∈ {L,B}. The rule restricted to {L,B}³ is ECA 22.
- PUMP(n,n') holds for 4 ≤ n < n' ≤ 800 (0 violations).
- Lemma 4.1 never applies for n ≤ 5000, s ≤ 3, L ≤ 24; the largest ratio (Y−s)/bound is 0.06.

**Cor 5.3 data**
- The half-lines of δ_12 and δ_13 agree for t+i ≤ 78, with 22 neighbourhoods; this set equals `germ_delta12.txt`.
- No new neighbourhood occurs up to t+i = 1034.
- On t+i = 1034, cells 1..259 are A (cell 260 is L). On t+i = 1033, cells 2..258 are L (cell 1 is G).
- Lemma 4.1 first applies at n = 518 with (s, L, Y) = (2, 1, 259); there is no hit for smaller n with s ≤ 3, L ≤ 6.

**c_78:** Mazoyer 57, δ_12 22, δ_13 22, δ_14 16, δ_14^b 16, δ_14^c 15, δ_14^d 15, δ_14^e 17.

**Mazoyer's rule**
- For 1 ≤ j < 700, each depth-row has period 3 from θ(j) = 2j+2 (j even or j = 1) or 2j+1 (odd j ≥ 3); horizon t ≤ 2600.
- PUMP holds for 4 ≤ n < n' ≤ 120.

**δ_12, extra check:** θ(j) = 3j/2 + 2 (checked for j = 10..300), and PUMP holds for n' ≤ 650. This is the optimality remark in M1.

**Lemma 3.2:** the closed formula equals the BFS cone for 2 ≤ n ≤ 300.

**Theorem 5.1:** `gencnf.py 4 9` regenerates a formula with 753 variables and 17,605 clauses, whose SHA-256 equals the digest in the manuscript's appendix.

**Four states:** my own lazy enumerator finds 828,670 / 64,299 / 536 / 27 / 0 partial rules for N = 5..9, and none of the 27 uses (∗,L,L).

**Prop 5.4**
- The authors' `germdfs` reproduces 100,396,178 nodes and the same 244 germs.
- My independent enumerator (`refdfs.c`: time-major order, symmetry handled afterwards) finds the identical 244 germs (2/26/216 at complexity 12/13/14) and the identical 9,787 for complexity ≤ 16.
- The 14 survivors are closed to anti-diagonal 330, and Lemma 4.1 applies to each with s = 1, at n ∈ {28, 35, 36, 51, 52, 99, 163} and L ≤ 5. The note's example (n = 28, L = 1, Y = 19) is one of them.
- The selector formula `k14_n10.cnf` regenerates with its recorded SHA-256, and the 230/14 split is consistent with the files.

**Balzer-condition rules**
- Both five-state rules for 2..11 synchronise and fail at 12; they satisfy (B1)–(B4) with I = id in the strong and the weak reading respectively.
- Both six-state rules synchronise 2..14 and satisfy the strong conditions.

### Claims I could not verify
- No SAT or UNSAT result, LRAT check, timing or proof size was re-run (as instructed). This covers Thm 5.1, the 230-germ refutation, all four cases of Prop 5.5, and Mazoyer's rule satisfying MT_6({3..12};78,40).
- The sentence "every instance decided was satisfiable" (l.493–495).
- The 9,787 → 16 pipeline beyond the enumeration count: completion tests up to length 13 and the regularity certificates.
- That the four further rules lie on half-lines different from δ_14's.
- Literature content I could not see: Balzer p. 37, Yunès's weak reading, Mazoyer 1986 on (B3), Sanders, Settle, Yamashita et al., and Mazoyer 1996 Prop. 2.
- Novelty relative to Mazoyer's 1989 habilitation and the signals literature.
