# Related work: retrieval record and novelty assessment

First retrieval on 2026-09-29 (search summaries only). Updated on 2026-10-01, after the
network policy was opened: full texts were obtained for the works marked **full text** below. The
PDFs are kept outside the repository (copyrighted works are not redistributed); every source is
given with its public location. Statements are marked with their source. *(summary)* means a
search-engine or database summary, not the paper itself.

## 1. What was retrieved

| Work | Obtained | Location |
|---|---|---|
| P. Sanders, *Massively parallel search for transition-tables of polyautomata*, Parcella '94, 99–108 | **full text** (author's copy) | https://ae.iti.kit.edu/documents/people/sanders/papers/parcella94.pdf |
| J.-B. Yunès, *Synchronisation et automates cellulaires: la ligne de fusiliers*, PhD thesis, Paris 7, 1993 | **full text** (scanned; read by OCR) | HAL tel-00139049 |
| J. Mazoyer, *A six states minimal time solution to the FSSP*, Publ. Dépt. Math. Lyon 1A (1986) 1–92 (preprint of TCS 50, 1987) | **full text** | https://numdam.org/item/PDML_1986___1A_A1_0/ |
| J. Mazoyer, V. Terrier, *Signals in one dimensional cellular automata*, LIP Research Report 94-50 (1994) (report version of TCS 217, 1999) | **full text** | HAL hal-02101868 |
| J. Duprat, *Proof of correctness of the Mazoyer's solution of the firing squad problem in Coq*, LIP report (2002) | **full text** | HAL hal-02101837 |
| Gruska, La Torre, Napoli, Parente, *Various solutions to the FSSP*, arXiv cs/0511044 (2005) | **full text** | arXiv |
| Correa, Gustavo, Lemos, Settle, *An overview of recent solutions to and lower bounds for the FSP*, arXiv 1701.01045 (2017) | **full text** | arXiv |
| K. Kobayashi, arXiv 1909.10125, 1909.05406, 1909.05408 (2019) | **full text** | arXiv |
| J. Durand-Lose, A. Emmanuel, arXiv 2106.11176 (2021); Nguyen, Maignan, arXiv 2005.08570 (2020); Yunès, arXiv 1212.3069 | **full text** | arXiv |
| Average-user, GitHub gist 4241ca84777ae6ed38326710d8b47da4 (2021) | **full text** (code and description) | https://gist.github.com/Average-user/4241ca84777ae6ed38326710d8b47da4 |
| R. Balzer, Information and Control 10 (1967) 22–42 | zbMATH summary (Zbl 1347.68249); conditions via Mazoyer 1986 and Yunès 1993 | full text **not obtained** |
| J. Mazoyer, *On optimal solutions to the FSSP*, TCS 168 (1996) 367–404 | zbMATH summary (Zbl 0878.68088); description in Gruska et al. | full text **not obtained** |
| J. Mazoyer, V. Terrier, TCS 217 (1999) 53–80 | zbMATH summary (Zbl 0915.68125); report version read in full | journal version **not obtained** |
| A. Settle, *New bounds for the distributed firing synchronization problem*, PhD thesis, Univ. of Chicago, 1999 | description in Correa et al. | **not obtained** |
| K. Yamashita et al., *The FSSP with sub-generals*, IPL 114 (2014) 60–65 | bibliographic data (Crossref); argument described by Kobayashi 2019 | **not obtained** |
| M. D'Antonio, G. Delzanno, *SAT-based analysis of cellular automata*, ACRI 2004, LNCS 3305, 745–754 | bibliographic data, Semantic Scholar summary | **not obtained** |

Why some full texts are missing: ScienceDirect and Springer answer HTTP 403 to automated clients
(bot protection, also for headless Chromium with the proxy CA trusted); the Elsevier article API
returns only metadata without an API key; archive.org and scholar.archive.org rate-limit the
shared egress address; CORE sits behind a Cloudflare challenge. Balzer 1967, Mazoyer 1996 and
Mazoyer–Terrier 1999 are free in Elsevier's open archive and can be downloaded by hand.

## 2. Findings, source by source

**Sanders 1994 (full text).**
- The specification imposes only σ(Z0,Z0,Z0) = σ(Z0,Z0,#) = Z0, exactly the conditions
  (eq. quiescence) of the manuscript. The manuscript's "even without the left quiescence condition"
  is therefore not new relative to Sanders.
- Balzer's backtracking heuristic was incorrect, "rendering the proof incomplete"; the corrected
  search has about 16,000,000 nodes instead of 60,000; the MasPar program proves the four-state
  bound in less than 11 s. Figure 2 shows a four-state rule that works up to length 8.
  **Checked:** the transcribed rule (34 transitions besides the quiescence ones) synchronizes the
  lengths 2..8 and hits an undefined neighbourhood (G,G,L) at length 9; it is exactly one of the 27
  partial rules of the manuscript's Table 3 (number 26 in the output of `fsspdfs 4 8 -s`).
- "Whether one accepts the output of a C program as a proof is a philosophical question" — the
  LRAT certificate of Theorem 5.1 answers exactly this point.
- Five states: estimated "about 10^16 times the age of the universe on a MasPar" (checked on the
  page image); a 24-hour randomized search found nothing; Balzer's approach of postulating
  properties of a solution "looked better than it is" because of the wrong heuristics, and "his
  strongest postulates do not hold for Mazoyer's six-state solution".

**Yunès 1993 (full text, OCR).**
- §3.1: Balzer's search re-implemented with the three latent transitions ($,L,L), (L,L,L), (L,L,$)
  fixed to L: 23,925,498 automata scanned in 153 s; "it suffices to look at the lines of lengths
  2 to 9"; there are exactly **27** four-state automata synchronizing all lengths 2..8, none also
  length 9; five states out of reach. **This is the manuscript's Table 3 (27 and 0).** None of the
  manuscript's 27 partial rules uses the neighbourhood (*,L,L), so the two counts refer to the
  same set.
- §2.7 "Verifying Balzer's conditions": (1) image solution with an involution I, (2) a resident
  state R: (x,R,y) → R for (x,y) ∈ Q² − {(R,R)}, (3) a pre-synchronization state S:
  (x,S,y) → F for x,y ∈ {S,$}, (4) a dominant state D: (D,x,D) → D for x ≠ D.
- §3.2: no three-state solution in any time.

**Mazoyer 1986 (full text), §7.** "Balzer has shown that no minimal time solution exists with 4
states; no minimal time solution satisfying extra conditions exists with 5 states. However, the
solution presented here does not satisfy Balzer's four extra conditions: in particular his
conditions 1 (the stability of state G) and 4 (rules (G,V,G) → G for V ≠ G) are violated, the very
idea of our solution is not to be an 'image solution' (his condition 2), the only condition
satisfied is condition 3 (the fire is introduced only by environments GGG, XGG, GGX)." Together
with Yunès this fixes Balzer's conditions up to two details (border neighbours in condition 1,
"only" in condition 3), which the manuscript now treats as a weak and a strong reading.

**Mazoyer–Terrier 1994 (full text of the report).** Signals generated by a single impulse,
Fischer-constructible functions and their closure properties. The "impossible moves of data" are
a gap theorem (report, Prop. 1): a rightward signal of ratio φ has φ(n) − n eventually constant or
φ(n) ≥ n + log_q n, q the number of states. Its proof is a pigeonhole argument on the words of the
first log_q n0 diagonals behind the front, which become periodic once two columns coincide — the
eventual periodicity of the depth-rows used as the first step of the manuscript's Theorem 3.4
(now cited). No statement about minimal-time solutions, the reflected triangles, the line i = t/3
or the left border. Prop. 12 (real-time recognition) uses the agreement of the diagrams of a^n and
a^m below the anti-diagonal c + t = n, the analogue of the manuscript's Lemma 2.2.

**Mazoyer 1996 (zbMATH summary; Gruska et al.).** "After proving that the sets of solutions and of
minimal time solutions to the FSSP are not recursively enumerable, he constructs particular
solutions for one-way and two-way information flow channels" (zbMATH); "Mazoyer, in [15] showed
that a minimal time synchronization exists for a 1-Line", i.e. with one bit exchanged per step
(Gruska et al.). The manuscript's former description ("studied the structure of optimal solutions
and the information flow they require") was inaccurate and is corrected.

**Kobayashi 2019 and Yamashita et al. 2014 (via Kobayashi).** Non-existence of minimal-time
solutions for variants (sub-generals, L-shaped paths, rectangular walls): a repetition of a pair of
consecutive states at two times, forced by the pigeonhole principle once the configuration is
long, propagates through the quiescent region and makes a node fire too early. This is the same
mechanism as the manuscript's pumping lemma (two lengths whose input words agree on the cone fire
at the same relative time); now cited, with the difference stated (there it excludes all solutions
of a variant, here it constrains the solutions of the original problem).

**Correa et al. 2017.** Settle's thesis (1999) proves that no three-state minimal-time solution
exists and "weaker results ... for 4-state and 5-state solutions, showing that there are no
solutions subject to a small number of constraints"; now cited as Settle99 via the survey.

**Gist (Average-user).** LuaJIT search with δ(*,L,L) = L imposed; reports 241,176,313 nodes and 0
solutions for the lengths 2..9, and 27 for 2..8, "as reported by Sanders". Independent
confirmation of Yunès's numbers; cited in the four-state section.

**Durand-Lose–Emmanuel 2021.** Constructions on signal machines (accumulations, fractal
structure); no necessity statements for cellular automata. Not in conflict with Theorem 3.6.

## 3. New computation prompted by the retrieval: Balzer's conditions

`src/balzer.py` adds (B1)–(B4) (Mazoyer's formulation, for the state G) to MT_5({2..N}) without
symmetry breaking, for each involution I of {L,A,B} (I(F) = F forces I(G) = G). Results
(`results/balzer.log`, LRAT certificates checked by lrat-check, digests recorded):

| involution | weak reading | strong reading |
|---|---|---|
| (A B) | UNSAT at N = 10 (LRAT) | UNSAT at N ≤ 10 (implied) |
| (L A), (L B) | UNSAT at N = 9 (LRAT) | UNSAT at N ≤ 9 (implied) |
| identity (symmetric rules) | SAT up to N = 11, **UNSAT at N = 12** (Kissat 16 min; DRAT 958 MB verified by drat-trim in 31 min) | SAT up to N = 11, **UNSAT at N = 12** (LRAT, 477 MB, checked in 8.5 s) |

Check of the formalization: on the 117 transitions that Mazoyer's six-state solution uses on the
lines of lengths 3..150, (B1) and (B4) fail, (B2) fails for every involution and (B3) holds in the
strong reading (`src/balzer_mazoyer.py`), which is exactly Mazoyer's own statement (1986, §7).

Hence the new Proposition 6.5: no five-state rule satisfying Balzer's conditions, in either
reading, synchronizes the lengths 2..12 — a certified version of Balzer's conditional
five-state result, whose original search was incomplete (Sanders); lengths up to 11 do not
suffice. Both rules for 2..11 were checked with the independent simulator `fsspcheck`.

## 4. Effect on the claims

| Claim | Before retrieval | After retrieval |
|---|---|---|
| 1. Pumping lemma, speed-1/3 barrier (L3.3, T3.4) | plausibly new | **new as far as the retrieved literature shows**; its mechanism (early firing forced by a repeated pair of states) is that of Yamashita et al. and Kobayashi for variants, and the eventual periodicity of the depth-rows is classical (Mazoyer–Terrier) — both now cited. Residual risk: the full text of Mazoyer 1996 was not read; its documented results (non-r.e., one-bit solutions) do not overlap. |
| 2. Left-border barrier, no eventually regular half-line (L3.5, T3.6, C3.8, L3.9) | plausibly new, strongest | **new as far as the retrieved literature shows**; Mazoyer–Terrier's impossibility results concern signal ratios near the front, not periodicity at the border. Same residual risk. |
| 3. Certified four-state bound (T5.1) | known result, certificate new | **only the certificate is new.** The threshold 9 and the count 27 are Yunès 1993; Sanders used the same quiescence conditions; Sanders's near miss is one of the 27. Minor additional facts: lengths 2..8 suffice with the half-line to anti-diagonal 78; pumping constraints alone are weak. The manuscript now attributes all of this. |
| 4. Five-state rules for all lengths ≤ 14 | apparently new | **new**: no earlier report of five-state rules for long initial segments of lengths; Sanders's randomized search found nothing, Yunès and Balzer could not search five states. |
| 5. c_78 ≥ 15 (P6.4) | new, low weight | **new**, unconditional (unlike Balzer's conditional result). |
| 6. Balzer's conditions (P6.5, added) | — | **new, certified**; first independent check of Balzer's 1967 conditional claim. Caveat: the conditions are taken from two secondary sources (Mazoyer 1986, Yunès 1993), which agree in substance; Balzer's own wording should be checked against the paper. |

Count of claims worth peer review: the earlier answer (five, of which two are new theorems)
stands, with claim 3 reduced to "certificate of a known result" and one small certified result
(claim 6) added.

## 5. Changes made to the manuscript

- Introduction: four-state history (Balzer, Yunès, Sanders) and Balzer's conditional five-state
  result; corrected description of Mazoyer 1996 (non-r.e.; one-bit solutions); new citations of
  Settle 1999, Yamashita et al. 2014, Kobayashi 2019, Mazoyer–Terrier 1994/1999, D'Antonio–Delzanno
  2004; contribution (i) marked as elementary; contribution (iii) marked as a certificate of a
  known fact; contribution (iv) mentions Proposition 6.5; results table extended.
- Abstract: "of the known fact that no four-state minimal-time solution exists".
- Section 2: Mazoyer's non-recursive-enumerability theorem and its consequence for existence proofs.
- Section 3: the eventual periodicity of the depth-rows credited to Mazoyer–Terrier.
- Section 5: Table 3 numbers attributed to Yunès 1993, Sanders 1994 and the gist; Sanders's near
  miss identified among the 27; the certificate stated as the contribution.
- Section 6: new subsection 6.4 "Balzer's conditions" with Proposition 6.5; Sanders's five-state
  estimate added to Section 6.5.
- Glossary: entry "Image solution; Balzer's conditions". Bibliography: nine new entries.

## 6. Still to do before submission

Status of the two missing full texts (2026-10-01, second attempt). Every automated route was
tried: ScienceDirect and its PDF host answer with a Cloudflare CAPTCHA ("Are you a robot?") and
declare text and data mining reserved (`tdm-reservation: 1`); OpenAlex and Semantic Scholar list
no repository copy (`any_repository_has_fulltext: false`); the Internet Archive's journal scans
contain only tables of contents for TCS and nothing for Information and Control; HAL has
metadata only; the authors' homepages have no copies; web.archive.org and api.fatcat.wiki close
the connection. Elsevier's sanctioned route for programmatic access is its article API, which
needs a (free) API key. With a key stored in the environment as `ELSEVIER_API_KEY`:

```
for pii in S0304397596000849 S0019995867900320; do
  curl -sS -H "X-ELS-APIKey: $ELSEVIER_API_KEY" -H "Accept: application/pdf" \
       "https://api.elsevier.com/content/article/pii/$pii" -o "$pii.pdf"
done
```

(the PDFs belong in the scratch directory or in `fssp5/literature/`, never in a public commit).

Attempt with an Elsevier API key (2026-10-03): the key supplied by the corresponding author is
a basic Scopus key. It works for Scopus Search and the standard view of Scopus Abstract Retrieval
(metadata only, no abstract: 49 Scopus citations of Mazoyer 1996, 159 of Balzer 1967), but the
ScienceDirect article API answers every request for either paper with
`AUTHENTICATION_ERROR - Requestor configuration settings insufficient` and the entitlement view
with `NOT_ENTITLED`. Full-text API access requires institutional entitlement, so this route cannot
deliver the two papers either. The key is not stored anywhere in the repository.

CORE also holds Balzer 1967 (its discovery API returns record 82657788 for the DOI); the
download link `https://core.ac.uk/download/pdf/82657788.pdf` is behind a Cloudflare bot check that
also stops a plain browser, and the discovery call for Mazoyer 1996 was rate-limited. With a free
CORE API key (`CORE_API_KEY`) the file is available as
`https://api.core.ac.uk/v3/outputs/82657788/download` (header `Authorization: Bearer $CORE_API_KEY`).

1. Download Balzer 1967 (free, open archive) by hand and check the wording of the four conditions
   and of his five-state statement against Section 6.4.
2. Download Mazoyer 1996 (free, open archive) and check it for statements overlapping Lemma 3.3,
   Theorem 3.4, Lemma 3.5 and Theorem 3.6. This is the only remaining risk for the two theorems.
3. Optional: Settle's thesis (conditional four- and five-state results) and the journal version of
   Mazoyer–Terrier, to cite section numbers of the published versions.
