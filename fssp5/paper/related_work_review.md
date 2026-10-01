# Related work retrieved for the assessment of the manuscript

Retrieved on 2026-09-29. **Full texts could not be downloaded**: the session's network policy
blocks the publisher and preprint hosts (arxiv.org, sciencedirect.com, elsevier.com,
link.springer.com, epubs.siam.org, dl.acm.org, hal.science, numdam.org, semanticscholar.org,
researchgate.net, wikipedia.org and others). What follows was retrieved through web search:
titles, bibliographic data and the abstracts or summaries that the search index returns. Every
statement below is marked with its source; statements marked *(summary)* come from a search
engine's summary of the page and must be checked against the paper before being cited.

## 1. Works the manuscript does not cite but should

| Work | What is known about it | Relevance |
|---|---|---|
| R. Balzer, *An 8-state minimal time solution to the FSSP*, Information and Control 10 (1967) 22–42 (already cited) | Besides the four-state bound, the paper apparently "presents a reasonable set of conditions for which no five state minimal time solution exists" *(quoted in the gist below, attributed to Balzer; not checked against the paper)* | **High.** A conditional five-state non-existence result from 1967, of the same kind as our Proposition 6.4 and the class results. The manuscript must state Balzer's conditions and compare. |
| Average-user, *Search to prove the nonexistence of a 4-states minimal time solution to the FSSP*, GitHub gist 4241ca84777ae6ed38326710d8b47da4 (not a publication) | An independent exhaustive search (LuaJIT): of 241,176,313 nodes, none synchronizes all lengths 2..9 in minimal time *(summary)* | **High for Theorem 5.1.** Independently confirms that the lengths 2..9 suffice for four states, so the threshold 9 is not new; only the LRAT certificate and dropping the left quiescence condition remain new. |
| M. D'Antonio, G. Delzanno, *SAT-Based Analysis of Cellular Automata*, ACRI 2004, LNCS 3305 | Encodes CA evolution in propositional logic and applies zChaff to forward and inverse reachability for classical examples, including the FSSP *(summary)* | **Medium.** Earlier SAT work on the FSSP (analysis of given rules, not a search for rules). The sentence "we are not aware of previous SAT-based work on the state complexity of the FSSP" can stay, but this work must be cited. |
| J. Mazoyer, V. Terrier, *Signals in one-dimensional cellular automata*, TCS 217 (1999) 53–80 | "We study generation of some signals ... a notion of constructibility of increasing functions ... We also exhibit some impossible moves of data" *(abstract)* | **High for Lemma 3.5.** Impossibility results for moving data in 1-D CA are the closest known relative of the left-border argument. Needs a direct comparison. |
| D. Goldstein, K. Kobayashi, *On the complexity of network synchronization*, SIAM J. Comput. 35 (2005) 567–589 | If a minimal-time solution exists for 3-D undirected grid networks then P = NP *(summary)* | Medium: non-existence of minimal-time solutions for variants. |
| D. Goldstein, K. Kobayashi, *On minimal-time solutions of firing squad synchronization problems for networks*, SIAM J. Comput. 41 (2012) 618–669 | Bibliographic data only | Medium: same line of work. |
| K. Kobayashi, *Nonexistence of minimal-time solutions for some variations of the FSSP having simple geometric configurations*, arXiv:1909.10125 (2019) | Proves non-existence of minimal-time solutions for L-shaped paths and rectangular walls with fixed side ratios *(abstract)* | Medium: the closest modern non-existence proofs for minimal time. |
| K. Kobayashi, *Minimum firing times of FSSPs for paths in grid spaces*, arXiv:1909.05406 (2019) | Minimal-time solutions for paths in 2-D/3-D grids "are not known and are unlikely to exist"; no non-existence proofs yet; one result suggests what study is needed *(abstract)* | Low to medium: methodology of non-existence proofs. |
| J. Durand-Lose, A. Emmanuel, *Abstract Geometrical Computation 11: Slanted firing squad synchronisation on signal machines*, TCS 894 (2021) 103–120; arXiv:2106.11176 | Most FSSP constructions translate to signal machines and "generate fractal figures with an accumulation" *(summary)* | Medium for Theorem 3.6: describes the accumulation of signals that our barrier proves necessary; our result is a necessity statement for CA, theirs a construction. |
| C. S. Calude, M. Napoli, M. Parente, *Minimum and non-minimum time solutions to the FSSP*, LNCS 8808 (2014) | Survey *(abstract)* | Low: survey to cite. |
| L. Maignan, J.-B. Yunès, *A spatio-temporal algorithmic point of view on FSSP*, ACRI 2012, LNCS 7495 | Solves the FSSP by recursive division expressed with fields *(abstract)* | Low: describes the recursive division structure. |
| H. Umeo, T. Yanagihara, *A small five-state non-optimum-time solution to the FSSP*, Fundamenta Informaticae (2009) | Five-state protocol for lengths 2^k, non-optimum time *(summary)* | Low: partial five-state solutions (families of lengths). |
| H. Umeo, N. Kamikawa, G. Fujita, *A new class of the smallest 4-state semi-symmetric FSSP partial solutions for 1D arrays*, ACRI 2024, LNCS 14978 | Four-state protocols for rings of length 2^k−1 *(summary)* | Low: recent partial solutions. |

## 2. Works that decide novelty but could not be retrieved

* **J. Mazoyer, *On optimal solutions to the FSSP*, TCS 168 (1996) 367–404.** No abstract was
  retrievable. It studies the structure of optimal (minimal-time) solutions and is the most likely
  place for results overlapping with Lemma 3.3, Theorem 3.4 and Theorem 3.6. It must be read before
  submission.
* **Balzer 1967, Section on five states.** The conditions of the conditional five-state result are
  unknown.
* **P. Sanders, Parcella '94.** Only the account "Balzer's search was incomplete; Sanders
  reaffirmed the four-state result with a corrected search" *(summary)*.

### Retry on 2026-10-01

After a container restart the gateway still answered 403 ("policy denial") to every scholarly
host tried, from the shell and from the fetch tool: arxiv.org, export.arxiv.org,
www.sciencedirect.com, pdf.sciencedirectassets.com, api.crossref.org, api.openalex.org,
api.semanticscholar.org, core.ac.uk, scholar.archive.org, web.archive.org, link.springer.com,
hal.science, eudml.org, drops.dagstuhl.de, dblp.org, zbmath.org, academia.edu, osti.gov,
books.google.com, citeseerx, wikipedia.org, the DePaul and Yunès homepages. Only package
registries and GitHub are reachable, and no public GitHub repository with these papers was found.

### The four papers to obtain (all free in Elsevier's open archive)

| Paper | Link |
|---|---|
| R. Balzer, Information and Control 10(1) (1967) 22–42 | https://www.sciencedirect.com/science/article/pii/S0019995867900320 |
| J. Mazoyer, TCS 50(2) (1987) 183–238 | https://www.sciencedirect.com/science/article/pii/0304397587901241 |
| J. Mazoyer, TCS 168(2) (1996) 367–404 | https://doi.org/10.1016/S0304-3975(96)00084-9 (DOI from the search index) |
| J. Mazoyer, V. Terrier, TCS 217(1) (1999) 53–80 | https://www.sciencedirect.com/science/article/pii/S0304397598001509 |

Placing the PDFs in `fssp5/literature/` (they should not be committed to the public repository)
or allowing `www.sciencedirect.com` and `pdf.sciencedirectassets.com` in the environment's network
settings would let the comparison be completed.

Not relevant after checking the abstract: G. Richard, *On the synchronisation problem over cellular
automata*, STACS 2017 (global synchronisation on infinite and periodic configurations, a different
problem).

## 3. Effect on the claims of the manuscript

| Claim | Before | After retrieval |
|---|---|---|
| 1. Pumping lemma and speed-1/3 barrier (L3.3, T3.4) | plausibly new | still plausibly new; overlap with Mazoyer 1996 and Mazoyer–Terrier 1999 unresolved |
| 2. Left-border barrier, no eventually regular half-line (L3.5, T3.6, C3.8, L3.9) | plausibly new, strongest | plausibly new as a necessity statement; signal-machine work describes the phenomenon; overlap with Mazoyer–Terrier's impossibility results unresolved |
| 3. Certified four-state bound (T5.1) | known result, certificate new | weaker: the threshold 9 is independently known (gist); novelty reduces to the LRAT certificate and the dropped left quiescence condition |
| 4. Five-state rules for all lengths ≤ 14 | apparently new | no earlier report found; must be compared with Balzer's conditional five-state result |
| 5. c_78 ≥ 15 (P6.4) | new, low weight | new, low weight; conceptually close to Balzer's conditional result, which must be discussed |

## 4. Sources

* https://gist.github.com/Average-user/4241ca84777ae6ed38326710d8b47da4
* https://link.springer.com/chapter/10.1007/978-3-540-30479-1_77 (D'Antonio, Delzanno)
* https://www.sciencedirect.com/science/article/pii/S0304397598001509 (Mazoyer, Terrier)
* https://doi.org/10.1137/S0097539705447086 (Goldstein, Kobayashi 2005)
* https://arxiv.org/abs/1909.10125 and https://arxiv.org/abs/1909.05406 (Kobayashi)
* https://arxiv.org/abs/2106.11176 (Durand-Lose, Emmanuel)
* https://link.springer.com/chapter/10.1007/978-3-319-13350-8_9 (Calude, Napoli, Parente)
* https://link.springer.com/chapter/10.1007/978-3-642-33350-7_11 (Maignan, Yunès)
* https://journals.sagepub.com/doi/10.3233/FI-2009-0038 (Umeo, Yanagihara 2009)
* https://link.springer.com/chapter/10.1007/978-3-031-71552-5_6 (Umeo, Kamikawa, Fujita 2024)
* https://www.sciencedirect.com/science/article/pii/S0019995867900320 (Balzer 1967)
