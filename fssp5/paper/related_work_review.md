# Related work: retrieval record and novelty assessment

First retrieval on 2026-09-29 (search summaries only); updated on 2026-10-01 after the network
policy was opened, and on 2026-10-03 when the corresponding author supplied the two papers that
could not be downloaded automatically (Balzer 1967, Mazoyer 1996). All works that decide the
novelty of the manuscript's claims have now been read in full. Statements are marked with their
source; *(summary)* means a database summary, not the paper itself.

## 1. What was retrieved

| Work | Obtained | Location |
|---|---|---|
| R. Balzer, *An 8-state minimal time solution to the FSSP*, Information and Control 10 (1967) 22–42 | **full text** (supplied by the corresponding author) | https://doi.org/10.1016/S0019-9958(67)90032-0 (Elsevier open archive) |
| J. Mazoyer, *On optimal solutions to the FSSP*, TCS 168 (1996) 367–404 | **full text** (supplied by the corresponding author) | https://doi.org/10.1016/S0304-3975(96)00084-9 (Elsevier open archive) |
| P. Sanders, *Massively parallel search for transition-tables of polyautomata*, Parcella '94, 99–108 | **full text** (author's copy) | https://ae.iti.kit.edu/documents/people/sanders/papers/parcella94.pdf |
| J.-B. Yunès, *Synchronisation et automates cellulaires: la ligne de fusiliers*, PhD thesis, Paris 7, 1993 | **full text** (scanned; read by OCR) | HAL tel-00139049 |
| J. Mazoyer, *A six states minimal time solution to the FSSP*, Publ. Dépt. Math. Lyon 1A (1986) 1–92 (preprint of TCS 50, 1987) | **full text** | https://numdam.org/item/PDML_1986___1A_A1_0/ |
| J. Mazoyer, V. Terrier, *Signals in one dimensional cellular automata*, LIP Research Report 94-50 (1994) (report version of TCS 217, 1999) | **full text** | HAL hal-02101868 |
| J. Duprat, *Proof of correctness of the Mazoyer's solution of the firing squad problem in Coq*, LIP report (2002) | **full text** | HAL hal-02101837 |
| Gruska, La Torre, Napoli, Parente, arXiv cs/0511044 (2005); Correa, Gustavo, Lemos, Settle, arXiv 1701.01045 (2017) | **full text** | arXiv |
| K. Kobayashi, arXiv 1909.10125, 1909.05406, 1909.05408 (2019) | **full text** | arXiv |
| Durand-Lose, Emmanuel, arXiv 2106.11176 (2021); Nguyen, Maignan, arXiv 2005.08570 (2020); Yunès, arXiv 1212.3069; theses of Nguyen (2021) and Penet de Monterno (2023) | **full text** | arXiv, HAL |
| Average-user, GitHub gist 4241ca84777ae6ed38326710d8b47da4 (2021) | **full text** (code and description) | https://gist.github.com/Average-user/4241ca84777ae6ed38326710d8b47da4 |
| J. Mazoyer, V. Terrier, TCS 217 (1999) 53–80 | zbMATH summary; report version read in full | journal version not obtained |
| A. Settle, *New bounds for the distributed firing synchronization problem*, PhD thesis, Univ. of Chicago, 1999 | description in Correa et al. | not obtained |
| J. Mazoyer, *Solutions au problème de la synchronisation d'une ligne de fusiliers: étude de leur structure*, habilitation, ENS Lyon, 1989 | described in Mazoyer 1996 (a catalogue of constructed solutions) | not obtained |
| K. Yamashita et al., IPL 114 (2014) 60–65; M. D'Antonio, G. Delzanno, ACRI 2004, LNCS 3305 | bibliographic data; arguments described by Kobayashi 2019 and Semantic Scholar | not obtained |

The two Elsevier papers could not be fetched automatically: ScienceDirect, its PDF host and
CORE answer automated clients with a Cloudflare check (a CAPTCHA on ScienceDirect, which also
declares text and data mining reserved); OpenAlex and Semantic Scholar list no repository copy;
the Internet Archive has only tables of contents for TCS; a Scopus-level Elsevier API key is not
entitled to the ScienceDirect article API. The corresponding author downloaded both PDFs in a
browser and placed them in `fssp5/literature/`. **Note:** this repository is public, and the
Elsevier user license that governs open-archive articles lets users "access, download, copy,
translate, text and data mine (but may not redistribute, display or adapt)" them for non-commercial
purposes (https://www.elsevier.com/open-access/userlicense/1.0). The two PDFs should therefore be
removed from the repository, and ideally from its history, before the repository accompanies the
submission.

## 2. Findings, source by source

**Balzer 1967 (full text).**
- p. 36: "Program One" (lazy definition of productions with backjumping to the "last relevant
  alterable production" and symmetry breaking on unused states) "proved that no minimal time
  solution exists with 4 states", examining about 60,000 possibilities in 15 min; the five-state
  run "was terminated after it had run for three hours and had examined approximately 570,000
  possibilities". Productions per table: 45 for 4 states, 96 for 5 states (the manuscript's 43 and
  94 after removing the two quiescence transitions).
- p. 37, verbatim: "The weakest conditions we found which enabled the program to prove that no
  five state minimal time solution existed were: Let G = the state the general is initially set
  to. 1. The solution is an Image Solution. 2. G is a Resident State, that is, U, G, V → G for all U
  and V, where if U equals G or the end of the line, then V does not equal either G or the end of
  the line. 3. G is the Get-Ready-To-Fire state, that is, U, G, V → Firing State, where U and V are
  either equal to G or the end of the line. Furthermore, these are the only productions whose
  Resultant is equal to the Firing State. 4. If any machine has machines on both sides of it in the
  G state, then it goes into the G state, that is G, V, G → G where V is not equal to G. These
  conditions were insufficient to prove no six state solution exists."
- p. 32: image solutions: for every production U, V, W → Y there is a production Image(W),
  Image(V), Image(U) → Image(Y), where Image is a map of the states with Image(Image(E)) = E.
- p. 37: the eight-state solution of the paper satisfies all four conditions; Balzer's first,
  hand-made eight-state solution satisfied only condition 4.
- The general is the rightmost machine (mirror image of the manuscript's convention); the four
  conditions are invariant under reflection.
- **Effect:** Balzer's own wording is exactly the *strong* reading of Section 6.4 (his condition 2
  includes the border neighbours; his condition 3 includes "the only productions" yielding F).
  Mazoyer 1986 numbers the first two conditions the other way round; the manuscript keeps
  Mazoyer's numbering and states Balzer's order. Yunès 1993 gives a weaker form (the *weak*
  reading). Proposition 6.5 certifies both.

**Mazoyer 1996 (full text).**
- §1.1: "In this paper, we do not study Balzer's question. We only aim to put in light some facts:
  1. The set of all solutions (or of all minimal time solutions) of the FSSP is not simple. We
  prove in 2 that it is not recursively enumerable. 2. It is easy to synchronize with few
  information." Definition 2 imposes δ(L,L,L) = δ(L,L,!) = δ(!,L,L) = L.
- §2, Theorem 1: the sets of solutions and of minimal-time solutions are not recursively
  enumerable (reduction from the halting problem via Smith's simulation of Turing machines). After
  it: in the habilitation [7] "we have described a lot of solutions. Three main features arise:
  1. All solutions use a 'divide and conquer' strategy. Only the ratio in which the segment is cut
  changes (it may be any ratio in [1/2, 1[)" (checked on the page image).
- §3, Theorem 2: a minimal-time solution in which only one bit is exchanged on each two-way
  channel; tested for lengths 2..1000 ("it is sufficient to test it for segments from 2 up to
  300", proof not given).
- §4: one-way channels. Proposition 2 compares the lines of lengths 2, 3 and 4 (if two lines give
  the first cell the same information, it fires at the same time) to show that one-way solutions
  cannot synchronize all lengths in time 2n − 2; Theorem 3: a one-way solution with t(n) = 2n − 2 for
  n ≥ 7.
- §5: with messages separate from states, no solution with 2 states (Theorem 4) and a minimal-time
  solution with 3 states and about 4500 pieces of information on 12 channels (Theorem 5).
- **Effect:** no statement about the half-line, the reflected triangles, periodicity behind the
  front, the line i = t/3 or the left border; no necessary condition on minimal-time solutions of
  the standard problem beyond the classical time bound. **No overlap with Lemma 3.3, Theorem 3.4,
  Lemma 3.5 or Theorem 3.6.** Proposition 2 is a small-length instance of the pumping mechanism in
  a restricted model; the divide-and-conquer remark is an observation about constructed solutions.
  Both are now cited in the introduction, and the description of Mazoyer 1996 is corrected (it
  states Theorems 1, 2 and 5 and that the paper leaves the five-state question aside).

**Sanders 1994 (full text).** Specification with only δ(Z0,Z0,Z0) = δ(Z0,Z0,#) = Z0 (the
manuscript's conditions); Balzer's backtracking "not correct, rendering the proof incomplete"
(about 16,000,000 nodes instead of 60,000); the MasPar program proves the four-state bound in less
than 11 s; Figure 2 shows a four-state rule for lengths up to 8, **which is entry 26 of the
manuscript's 27 partial rules** (checked by transcription and comparison); "whether one accepts the
output of a C program as a proof is a philosophical question"; five states estimated at "about
10^16 times the age of the universe on a MasPar"; a 24-hour randomized search found nothing;
Balzer's postulates "look better than [they are]" because of the wrong heuristics and do not hold
for Mazoyer's solution.

**Yunès 1993 (full text, OCR).** §3.1: Balzer's search re-implemented (with δ($,L,L) = L):
exactly **27** four-state automata for the lengths 2..8, none for 2..9 — the manuscript's Table 3
(none of the 27 uses (*,L,L)); five states out of reach. §2.7: Balzer's conditions restated for
arbitrary states (resident R, pre-synchronization S, dominant D) in a weaker form. §3.2: no
three-state solution in any time.

**Mazoyer 1986 (full text), §7.** Balzer's results quoted; Mazoyer's six-state solution violates
conditions 1 (stability of G), 2 (image solution) and 4 ((G,V,G) → G) and satisfies only condition
3. Reproduced by `src/balzer_mazoyer.py` on the 117 transitions the solution uses (lengths 3..150).

**Mazoyer–Terrier 1994 (full text of the report).** Gap theorem for the ratios of signals
(report, Prop. 1), proved by the pigeonhole argument that makes the cells at bounded depth behind
the front periodic along the diagonals — the first step of the manuscript's Theorem 3.4 (now
cited). No statement about minimal-time solutions or the left border.

**Kobayashi 2019; Yamashita et al. 2014 (via Kobayashi).** Non-existence of minimal-time
solutions for variants: a repeated pair of states, forced by the pigeonhole principle, makes a node
fire too early — the mechanism of the pumping lemma, used there to exclude all solutions of a
variant (now cited).

**Correa et al. 2017.** Settle's thesis (1999): no three-state solution and conditional four- and
five-state results (cited via the survey). **Gist (Average-user).** Search with δ(*,L,L) = L:
0 rules for 2..9, 27 for 2..8 (cited). **Durand-Lose–Emmanuel 2021.** Constructions on signal
machines; no necessity statements.

## 3. Computation prompted by the retrieval: Balzer's conditions

`src/balzer.py` adds (B1)–(B4) to MT_5({2..N}) without symmetry breaking, for each involution I of
{L,A,B} (I(F) = F forces I(G) = G). Results (`results/balzer.log`, certificates checked, digests
recorded):

| involution | weak reading (Yunès) | strong reading (Balzer's wording) |
|---|---|---|
| (A B) | UNSAT at N = 10 (LRAT) | UNSAT at N ≤ 10 (implied) |
| (L A), (L B) | UNSAT at N = 9 (LRAT) | UNSAT at N ≤ 9 (implied) |
| identity (symmetric rules) | SAT up to N = 11, **UNSAT at N = 12** (Kissat; LRAT of 3.1 GB via drat-trim, lrat-check 66 s) | SAT up to N = 11, **UNSAT at N = 12** (LRAT, 477 MB, lrat-check 8.5 s) |

Check of the formalization: on the transitions Mazoyer's solution uses, only (B3) holds, as
Mazoyer states.

Six states (`src/balzer_k.py`, strong reading, `results/balzer6.log`): for each of the four
involution types of {L,A,B,C}, rules satisfying (B1)–(B4) exist for all lengths up to 13 (up to 14
for I = id and (L A); files `results/balzer6_sym14.txt`, `results/balzer6_LA14.txt`); the next
length was undecided within 30 minutes in every case. As for Balzer, the conditions are not known to
exclude six states; this is now open problem (5) of the manuscript. Proposition 6.5: no five-state rule satisfying Balzer's conditions, even in the
weak form, synchronizes the lengths 2..12; lengths up to 11 do not suffice. This is the first
independent check of Balzer's 1967 conditional claim, whose original search was incomplete
(Sanders).

## 4. Effect on the claims (final)

| Claim | Assessment |
|---|---|
| 1. Pumping lemma, speed-1/3 barrier (L3.3, T3.4) | **New.** Not in any retrieved work, including Balzer 1967 and Mazoyer 1996. Its mechanism appears for variants (Yamashita et al., Kobayashi) and for small lengths in the one-way model (Mazoyer 1996, Prop. 2); the eventual periodicity of the depth-rows is classical (Mazoyer–Terrier). All cited. |
| 2. Left-border barrier, no eventually regular half-line (L3.5, T3.6, C3.8, L3.9) | **New**, the strongest contribution; no related statement in the literature read. |
| 3. Certified four-state bound (T5.1) | **Only the certificate is new.** Threshold 9 and the 27 near misses: Yunès 1993; same quiescence conditions as Sanders 1994; Sanders's near miss is one of the 27. Attributed in the manuscript. |
| 4. Five-state rules for all lengths ≤ 14 | **New.** Balzer (3 h), Yunès and Sanders (24-hour random search) report no five-state results. |
| 5. c_78 ≥ 15 (P6.4) | **New**, unconditional. |
| 6. Balzer's conditions (P6.5) | **New, certified**; conditions now checked against Balzer's own wording. |

Count of claims worth peer review: five, of which two are new theorems (claims 1 and 2); claim 3
is a certificate of a known result; claim 6 is a small certified addition.

## 5. Changes made to the manuscript

- Introduction: four-state history (Balzer, Yunès, Sanders); Balzer's conditional five-state
  result; Mazoyer 1996 described from the full text (non-r.e.; one-bit solution; three states with
  separate messages; five-state question left aside; divide-and-conquer remark; Prop. 2 as an
  instance of the pumping mechanism); citations of Settle 1999, Yamashita et al. 2014, Kobayashi
  2019, Mazoyer–Terrier 1994/1999, D'Antonio–Delzanno 2004; contributions (i), (iii), (iv) and the
  results table adjusted.
- Abstract: "of the known fact that no four-state minimal-time solution exists".
- Section 2: Mazoyer's non-recursive-enumerability theorem and its consequence for existence proofs.
- Section 3: the eventual periodicity of the depth-rows credited to Mazoyer–Terrier.
- Section 5: Table 3 attributed to Yunès 1993, Sanders 1994 and the gist; the certificate stated as
  the contribution.
- Section 6.4: Balzer's conditions quoted from his paper (p. 37), the strong reading identified as
  Balzer's wording, Proposition 6.5; check against Mazoyer's verdict. Section 6.5: Balzer's,
  Yunès's and Sanders's five-state attempts.
- Glossary: entry "Image solution; Balzer's conditions". Bibliography: nine new entries.

## 6. Remaining items

1. The two Elsevier PDFs were removed from the current tree (commit c13aa25) and
   `fssp5/literature/` is ignored; they remain in the history (commit ffcd4c4), from which only a
   history rewrite by the repository owner can remove them.
2. Optional: Settle's thesis and the journal version of Mazoyer–Terrier, to cite section numbers of
   the published versions; Mazoyer's 1989 habilitation (a catalogue of constructed solutions,
   low risk for the necessity theorems).
