# Research log after the note (October 2026)

Notation: the note's (C∞ half-line, R_n reflected triangle, J_n input word, PUMP, Lemma 4.1).
Every number below was produced in this session by the commands named; nothing is copied from memory.

## 1. Where the five-state question stands

- Half-line classification (manuscript, Prop. 6.4 and §6.3): every five-state solution has c_78 ≥ 15.
- The complexity-15 survivors are two germs with the same half-line up to renaming of states; they are the half-lines of δ14c and δ14d.
- The remaining complexity-16 germs that are not certified regular (K16_remaining16, 16 germs including the two of complexity 15) have completions for the lengths 2..13, and several for 2..14 (δ14, δ14b..e).
- All five known rules for the lengths 2..14 fail at length 15 by early firing in the right half of the line.

## 2. Depth-row structure of the near misses (src/theta.py, research: rowperiods)

| rule | θ(j) (observed) | row periods |
|---|---|---|
| Mazoyer (6 states) | 2j+1 or 2j+2 | 3 |
| δ12, δ13 | ⌈3j/2⌉+2 | 1 |
| δ14b | 2j+2 | 3 |
| δ14e | ⌈3j/2⌉ + O(j/12) | 1, 2 |
| δ14 | ≈ 3j/2 | doubling: 4 (j ≈ 4..10), 8 (j ≈ 12..30), 16 (j ≈ 32..40) |
| δ14c, δ14d | – | no period ≤ 24 found on the rows (horizon 3000) |

δ14's half-line is the elementary rule 22 between a static boundary layer and the front.
- **The boundary layer:** cells 1, 2, 3 are L, A, B for t ≥ 4.
- **Near the front:** the pattern is a nested Sierpinski-type pattern whose depth rows have periods 2^m. The anti-diagonals J_n therefore carry the binary digits of n inside the cone of the right end.
- **Further back:** the pattern is chaotic.

This explains why neither barrier of the note excludes it. PUMP holds because the counter separates every n from every n′. Lemma 4.1 does not apply because the anti-diagonals near the border have no periodic stretches.

## 3. Partial-triangle realizability for a fixed half-line (research/gfix.py)

With the germ fixed, C∞ is a constant and every set of cells of R_n that is closed under predecessors gives necessary conditions on the remaining transitions. gfix.py encodes three such sets for any lengths, with the half-line as constants:
- full triangles;
- the cones of the right h+1 firing cells (h = 0: the right end, which is the region of PUMP);
- left bands of h chains (the region of Lemma 4.1).

The cone and band tests are exact versions of the two barriers: PUMP and Lemma 4.1 are sufficient conditions for the corresponding test to be unsatisfiable, for any table.

Validation with δ14's table fixed (CaDiCaL via PySAT):
- full:2-14 SAT; full:2-15 UNSAT;
- cone:2-14 SAT; cone:15 UNSAT;
- cone:15:7 UNSAT;
- band:2-14:4 SAT.

The union of the cones of all 14 firing cells of R_14 is R_14 itself (105 cells).

Results, δ14's germ, table free:
- cone:2-15 SAT (0.7 s); cone:2-20 SAT (121 s). The right ends alone are realizable on this half-line.

## 4. Pre-firing classes of the near misses

These are the neighbourhoods with δ(·) = F in the rule files; for Mazoyer's extracted table, only the used ones are listed.

| rule | F-neighbourhoods | pre-firing configuration |
|---|---|---|
| δ14 | ∗LL ∗LG ∗GG LG∗ LGG GGG GGB GB∗ | L G^(n−2) B |
| δ14b | ∗GG GG∗ GGG GGA GA∗ | – |
| δ14c | ∗GG GG∗ GGG | G^n |
| δ14d | ∗AL ∗AA AA∗ AAA | A^n |
| δ14e | ∗LA ∗AL ∗AA ∗AB LA∗ AG∗ AA∗ AAA | – |
| Mazoyer | only ∗GG, GGG, GG∗ are used | G^n |

So δ14c is in Balzer's class B3 in the strong reading: uniform pre-firing G^n, and no other neighbourhood gives F. This is the class that Mazoyer's solution satisfies.

In that class, the pre-firing configuration of every line is G^n, which has three consequences:
- the half-line's cell 1 is G at every odd time;
- its cell 2 is never G at an odd time;
- the echo reaches cell 2 at time 2n−3 in state G.

## 5. Division type and θ

**Interpretation.** In the known constructions, the transient boundary of the depth rows is the signal that meets the echo at the first division point. Let ρn be the distance of that point from the right end. Then θ(j) ≈ αj with ρ = 1/(2α−1).

**Examples.**
- The mid-way division has ρ = 1/2 and α = 3/2, as in Waksman's and Balzer's solutions.
- Mazoyer's two-thirds division (the point at 2n/3 from the general) has ρ = 1/3 and α = 2. This matches the θ(j) = 2j+O(1) measured on Mazoyer's rule.
- Clergue, Verel and Formenti (Appl. Soft Comput. 66, 2018) found 718 six-state solutions. 717 of them use the mid-way division and 1 the two-thirds division (as reported by Nguyen and Maignan, AUTOMATA 2020, who generate millions more by local simulation).

**The barrier in these terms.** Theorem 3.4 says that the first division point is never in the left half of the line, measured from the general.

**The near misses.** Among them, δ14 and δ14e are of the mid-way type (α ≈ 3/2) and δ14b of the two-thirds type (α = 2). δ14, δ14c and δ14d additionally have unbounded row periods.

**Data not obtained.** The 718 solutions are "freely available online" according to Nguyen–Maignan, but Verel's page now redirects to a 404 (lisic-prod.univ-littoral.fr), and web.archive.org is not reachable from this environment. They would be the natural data set for testing invariants of all known minimal-time solutions.

## 6. Duality: the reflected triangle is a half-line

In relative coordinates (τ, κ), R_n grows from the right border:
- its front is the echo (the hypotenuse);
- its chain c is the depth row c−1 behind that front;
- the chain recurrence v_c(κ) = δ(v_{c−2}(κ+1), v_{c−1}(κ), v_c(κ−1)) has the form of the depth-row recurrence (3).

It differs from C∞ in one way: the cells beyond its front are the input anti-diagonals J_n, not quiescent cells.

Under this correspondence:
- the left-border lemma (Lemma 4.1) is the pumping lemma (Lemma 3.3) for R_n;
- Remark 4.4 is Lemma 4.1 for R_n.

So the two barriers are dual, and combining them in this way yields no new constraint.

The same view says what a solution must provide twice:
- the left general must make the half-line complex enough (Theorems 3.4 and 4.2);
- the right border must make every R_n complex enough near the right end (Remark 4.4).

Both use the same table; the right border only through the 16 entries δ(a, b, ∗).

## 7. A weaker left analogue of Theorem 3.4

**Claim.** If the depth rows are P-periodic at all cells of the input anti-diagonals of line n at positions ≥ s+P, then the left band of line n−P equals that of line n shifted by P slices, so line n fires cell 2s at slice s+P: a contradiction.

**Proof.** Both bands start at the right border and read identical inputs, so the band of line n−P at slice y equals the band of line n at slice y+P.

**Strength.** This needs periodicity along the whole anti-diagonal, not only on the cone of the right end. It therefore gives only a bound near θ(j) ≥ j, weaker than Theorem 3.4.

## 8. How much of the table the near misses use

Distinct neighbourhoods used by the lines 2..N; the possible entries are W × (W∪{∗}) × (W∪{∗}) minus (∗,y,∗), i.e. 96 for k = 5 and 175 for k = 6.

| rule | lengths | used | cumulative count at the last 8 lengths |
|---|---|---|---|
| δ14 | 2..14 | 82 / 96 | 50 59 65 69 77 78 79 82 |
| δ14b | 2..14 | 80 / 96 | 48 59 69 73 74 77 80 80 |
| δ14c | 2..14 | 80 / 96 | 46 52 60 61 69 76 76 80 |
| δ14d | 2..14 | 81 / 96 | 47 56 62 66 73 78 79 81 |
| δ14e | 2..14 | 81 / 96 | 47 53 57 67 70 73 80 81 |
| δ12 | 2..12 | 82 / 96 | 33 48 54 61 68 74 80 82 |
| δ13 | 2..13 | 86 / 96 | 54 64 70 75 79 82 84 86 |
| Mazoyer (k = 6) | 2..60 | 119 / 175 | 119 at every length shown (53..60) |

Hence:
- The five-state near misses use 83–90 % of the table at their last good length, and still need new entries at every length.
- Mazoyer's solution settles on a fixed set of 119 entries.
- The six-state solutions of Clergue–Verel–Formenti use about 90 transitions; their solution 668 uses 93, and a local simulation of it 90.

This is no proof of anything, but it is consistent with a five-state table running out of room near length 15.

Split by the kind of neighbourhood (interior: no border; right border (a,b,∗); left border (∗,a,b)):

| rule | interior | right border | left border |
|---|---|---|---|
| δ14 | 64/64 | 13/16 | 5/16 |
| δ14b | 62/64 | 15/16 | 3/16 |
| δ14c | 63/64 | 14/16 | 3/16 |
| δ14d | 62/64 | 16/16 | 3/16 |
| δ14e | 62/64 | 13/16 | 6/16 |
| Mazoyer (k = 6) | 97/125 | 16/25 | 6/25 |

**Observation: the five-state near misses saturate the interior of the table by length 14.**
- Repairing a failure at length 15 can only reassign entries that the shorter lengths already rely on.
- The left-border entries, used only by cell 1, stay mostly unused.
- Mazoyer's solution leaves about a fifth of its interior entries unused.

## 9. Partial-triangle tests subsume the two barriers

**Proposition.** Let g be a germ that determines C∞ on t + i ≤ M. For each n in a finite set with 2n−2 ≤ M, let X_n ⊆ R_n be closed under predecessors in R_n. If no table extending g makes the cells of X_n at time 2n−2 equal to F, all other cells of X_n different from F, and the return chain different from C∞, then no rule containing g is a minimal-time solution.

**Proof.** In a minimal-time solution, every cell of R_n with t < 2n−2 is not F, every cell with t = 2n−2 is F, and the return chain differs from C∞ (Lemma 2.3). The cells of X_n are computed from C∞ and from cells of X_n alone, so the solution's table extends g and satisfies the constraints. ∎

**PUMP is a special case.** Suppose PUMP(n, n′) fails for g, i.e. J_n = J_{n′} on cone_n(n−1, 0). Then for every table, the relative cell (n−1, 0) of R_{n′} equals that of R_n, which must be F. That cell lies in cone_{n′}(n′−1, 0) at a time below n′−1, where it must not be F. So the tests {cone n, cone n′} are unsatisfiable.

**Lemma 4.1 is a special case.** If the hypothesis of Lemma 4.1 holds for line n and some s, ℓ, its proof shows, for every table, a cell of the first 2s chains of R_n that is F before time 2n−2. So the test band n:2s is unsatisfiable.

**Hence** an unsatisfiable cone/band/full test is a refutation tool at least as strong as both barriers on the same lengths. research/gcegar.py applies it lazily: it adds the cones of failing cells only, length by length.

**Practical difference.** On δ14's germ, kissat did not decide full:2-14 within 900 s, although δ14 itself is a solution. The refinement loop (gcegar.py, from full:2-6) reached length 14 in under 2 minutes, adding cones of failing cells only.

## 10. Iterated local search (ils5.c), calibration

Setup:
- **Score:** the number of consecutive lengths 2, 3, … that synchronize, then the quality of the first failing length.
- **Moves:** one used transition at a time; a move is accepted if the score does not decrease.
- **Perturbation:** after a stall, perturb from the best table.

Results:
- **Speed:** about 1.5·10^6 evaluations per second.
- **Four states:** 40·10^6 evaluations per seed (3 seeds) reach the lengths 2..7 once and 2..6 twice. The exhaustive maximum is 2..8.

So, without a better score, local search is weaker here than the SAT methods. It was not used for five states.

## 11. Refinement loops (gcegar.py), status on 2026-10-19 around 15:00 UTC

**δ14's germ** (from full:2-6):
- Lengths up to 13 in seconds per round.
- Round 15 (constraints for lengths ≤ 14 plus cone:14:2) is satisfiable in 1760 s. Every length 2..14 then synchronizes.
- Length 15 fires early at cells 12–15 (t = 24), so cone:15:3 is added; the loop is running.

**δ14d's germ** (from full:2-14 cone:15):
- Round 1 is satisfiable in 1020 s. The right end of length 15 fires correctly, but cells 4–14 do not fire.
- cone:15:11 is added; the loop is running, plus a copy with kissat --sat.

**Unrestricted (FREE)** (from full:2-6): at length 12 after 14 rounds; running.

**δ14c's germ, full:2-14 cone:15 (one formula, no loop):** running.

The earlier direct attempts at length 15 on these germs stayed undecided after 0.5–4 h (manuscript log).

## 12. Taxonomy of the five-state near misses by depth-row structure

Measured with research/../scratch rowperiods (horizon 4000 to 6000, depths ≤ 40).

| rule | row periods | θ(j) | reading |
|---|---|---|---|
| δ12, δ13 | 1 | ⌈3j/2⌉+2 | mid-way, bounded; regular half-line, refuted at n = 518 (Cor. 5.3) |
| δ14b | 3 | 2j+2 | two-thirds, bounded; certified eventually regular (manuscript) |
| δ14e | 1, 2 | ≈ 1.75 j (e.g. θ(20) = 35, θ(40) = 70) | bounded; division point at ≈ 0.4n from the right end |
| δ14 | 4, 8, 16, … (doubling with depth) | ≈ 1.5 j | binary counter (rule 22 Sierpinski region) |
| δ14c | even rows 1; odd rows 3, 6, 12, 24, 48, 96 | irregular, up to θ(39) = 254 | counter in base 2 with period-3 seed |

So the five-state rules for lengths ≤ 14 use at least four different architectures:
- two kinds of bounded-period half-line, with division ratios 1/2 and about 0.4;
- binary counters, with periods 2^m and 3·2^m.

Every one of them fails at length 15 in the right half.

## 13. The right band as a finite automaton; the "column lemma"

In R_n, the cells κ = 0..d−1 (the d cells next to the right border) evolve as a finite automaton:
- its states are W^d, i.e. at most (k−1)^d states without F;
- it is driven by the column κ = d, i.e. the sequence R_n(τ, d) for τ ≥ d;
- it must reach the all-F state exactly at τ = n−1.

**Column lemma.** If the driving column is ℓ-periodic on [τ0, n−2] with n−1−τ0 > (k−1)^d·ℓ, the right end fires early.

**Proof.** This is the pigeonhole argument of Lemma 4.1 in the time direction. Some state repeats at two times τ1 < τ2 ≤ n−2 with ℓ | τ2−τ1. The automaton is then periodic up to n−1, so the all-F state also occurs at n−1−(τ2−τ1). ∎

The same holds for the left band driven by the column of cell d+1.

**Status.** The lemma concerns cells of R_n, so it is not a condition on the half-line alone. It is implied by the cone tests of §9.

**How the near misses fail at 15.** For each rule, R_15's right part reaches the pre-firing configuration of a shorter length m at τ = m−2:

| rule | m | first firing |
|---|---|---|
| δ14 | 9 | cells 13–15 at t = 22 |
| δ14c | 8 | cell 11 at t = 21 |
| δ14d | 9 | cells 11–15 at t = 22 |
| δ14e | 14 | cells 9–11 at t = 27 |
| δ14b | 12 | cell 12 at t = 25 |

For δ14, the width-3 right band of R_15 at τ = 7 is "G G B", the right part of R_9's pre-firing configuration L G^7 B.

PUMP guarantees that the cone inputs differ. So it is the finite right band that merges the two lengths: its driving column leads to the same state.

## 14. Where the four-state wall sits, and why five states differ

gfix.py FREE, k = 4, full triangles 2..8 (CaDiCaL via PySAT). GFIX_MARGIN is the number of half-line anti-diagonals beyond 2N−2 that are encoded and required not to fire. GFIX_NORC lists the lengths without the return-chain condition.

| half-line margin | return chain at 8 | result |
|---|---|---|
| 0 | omitted | SAT (the 27 partial rules of the note exist) |
| 1 | omitted | UNSAT (56 s) |
| 1 | kept | UNSAT (48 s) |
| 2 | omitted | UNSAT (48 s) |

The cells of anti-diagonal 15 lie in line 9's agreement region. So every four-state rule that synchronizes 2..8 makes line 9 fire early inside its half-line part: some cell (t, i) with t + i = 15 is F.

The four-state wall is therefore a half-line phenomenon. It is detected before the echo of line 9 matters.

The five-state near misses are different:
- their half-lines are closed and F-free up to anti-diagonal 10^4;
- all of them fail inside the reflected triangle R_15, in its right half (§13).

**Caveat for the tools.** By default gfix.py uses margin 2 and the return chain at every encoded length. Both are necessary conditions for minimal-time solutions, so refutations stay valid. But a table reported FOUND for lengths 2..N also satisfies these conditions of line N+1.

## 15. The two complexity-15 germs are one problem for n ≥ 3; first look at firing classes

**δ14c's germ, full:2-14 cone:15 (kissat, one formula).** No answer within 7200 s (`s UNKNOWN`). The same formula on δ14d's germ was satisfiable in 690 s (single shot) and in 1020 s (round 1 of the loop).

**Why the two germs are almost the same problem.** Let σ rename δ14d's states by A ↦ G, B ↦ A, G ↦ B (L and F fixed).
- σ maps the 13 transitions of δ14d's germ that occur at t ≥ 1 onto the 13 transitions of δ14c's germ that occur at t ≥ 1. The remaining two transitions of each germ are the step t = 0 → 1: δ14d has ∗GL>A, GLL>B and δ14c has ∗GL>G, GLL>A.
- At t = 1 both half-lines are A B L L … in δ14d's names, so σ maps δ14d's half-line onto δ14c's from t = 1 on.
- For n ≥ 3, line n at t = 1 is A B L … L in both problems (in δ14d's names). Its later evolution, and hence every constraint of R_n, involves only the table and the cells at t ≥ 1.
- So for the lengths n ≥ 3 the two completion problems coincide, except on four entries. In δ14d's names, δ14d fixes (∗,G,L) ↦ A and (G,L,L) ↦ B and leaves (∗,A,L) and (A,L,L) free; δ14c fixes (∗,A,L) ↦ A and (A,L,L) ↦ B and leaves the other two free.
- They also differ on the line of length 2, which reads (G,L,∗) in δ14d and (A,L,∗) in δ14c (δ14d's names).
- Hence the relaxation "δ14d's half-line from t = 1, lengths 3..N, the four entries free" contains both problems. If it is unsatisfiable for some N, both complexity-15 germs are refuted at once, and c78 ≥ 16 follows.

The two known rules on this half-line are genuinely different completions: of the 80 entries that δ14d uses at t ≥ 1 on the lengths 2..14, only 38 agree with δ14c under σ.

**Architecture of δ14d.** Its return chain (t + i = 2n−1, read from i = n down to 1) is G^{n−2} A F for every 3 ≤ n ≤ 14.
- The spare state G, which the half-line never uses after t = 0, carries the echo as a clean speed-1 signal: δ(B,L,∗) = G at the right end, then δ(x,y,G) = G for the pairs (x,y) of the half-line.
- At cell 2, δ(A,B,G) = A, and then δ(∗,A,A) = F.
- The pre-firing configuration is A^n.

**Uniform pre-firing classes.** For a state X put P_X = {XXX, ∗XX, XX∗}. Consider the formula with `--P P_X`, i.e. exactly these three neighbourhoods give F.
- *Reduction.* A rule that synchronizes 2..N with pre-firing configuration X^n for every n ≤ N satisfies this formula after its unused F-entries are changed to non-F values:
  - such an entry never occurs before the firing time in the lines 2..N, nor in the encoded half-line, because it would produce F there;
  - at time 2n−3 the configuration X^n has only windows in P_X.
- Conversely, `--P P_X` forces the configuration X^n at time 2n−3, since only X^n has all its windows in P_X.
- *Consequence.* If the formula is unsatisfiable, no rule synchronizing 2..N fires from X^n at all these lengths.
- *Cases.* X = L is impossible because δ(L,L,L) = L. X = B is the case X = A with A and B exchanged.
- So two FREE runs decide the class "uniform pre-firing" (pre-firing configuration X^n for one X and all n ≤ N): X = G, which is Balzer's (B3) in the strong reading and Mazoyer's class, and X = A.
- δ14c lies in the class X = G and synchronizes 2..14, so N ≥ 15 is needed for X = G. δ14d fires from A^n at every length up to 14 (its F-entry ∗AL is unused), so N ≥ 15 is needed for X = A as well.

Runs started 16:12 and 16:17 UTC: `gcegar.py FREE 16 … full:2-6 --P 'GGG,*GG,GG*'` and the same with `--P 'AAA,*AA,AA*'`. Both reached length 12 within two minutes, much faster than the unrestricted FREE loop (length 12 after about 80 minutes).

## 16. Early rows of all reflected triangles: a finite test for infinitely many lengths (asymp.py)

**Observation.** Every known near miss fails at every length n ≥ 15, and always within a bounded number of steps after the reflection. Simulation of n = 15..120 gives the first firing at relative time τ = t − (n−1):
- δ14: 7..10;
- δ14d: 6..12;
- δ14e: 9..14;
- δ14b: 8..14;
- δ14c: 7..22.

So their failure is a property of the *early rows* τ ≤ T of R_n, uniformly in n.

**Lemma A (early cells).** Let T ≥ 0 and n, n′ ≥ T+3. Define the signature σ_n(T) as the input cells J_n(κ) for κ ≤ T+1 together with the return-chain values C∞(n−1+κ, n−κ) = Φ_{n−1+κ}(2κ) for κ ≤ T.
- *Claim.* If σ_n(T) = σ_{n′}(T), then R_n and R_{n′} agree on E(T) = {(τ,κ): 0 ≤ κ ≤ τ ≤ T}, up to the first F in E(T).
- *Proof.* A path from (τ,κ) to an input cell at κ′ after r steps has κ′ ≤ κ+r and τ−r ∈ {κ′−1, κ′−2}, so κ′ ≤ T+1. Its cells have κ″ ≤ T < n−1, so the left border is never adjacent. Now apply the determinacy lemma (note, Lemma 3.1). ∎

**Lemma B (certified periodicity).** For D ≥ 0 and t ≥ D, put V_t = (Φ_t(0), …, Φ_t(D)).
- By (3), V_{t+1} is a function of V_t alone, since j ≤ D ≤ t keeps the border out.
- *Claim.* If V_{t0} = V_{t0+p} for some t0 ≥ D, then V_t = V_{t+p} for all t ≥ t0.

**Consequence.** Take D = 2T+4 (the program's choice; 2T+1 would suffice).
- For n ≥ t0+3, σ_n(T) depends only on n mod p.
- So the conditions "no cell of E(T) fires and the return chain differs from C∞", for all n ≥ N0, reduce to one length per signature in N0 ≤ n < max(N0, t0+3)+p.
- `asymp.py GERM T N0` computes the certificate (t0, p) and these representative lengths as specs early:n:T. Lemma A needs n ≥ T+3, so every length N0 ≤ n < T+3 is kept individually.
- gfix.py has the region `early:n:h`: the cells of R_n with τ ≤ h.

**Proposition (each near miss synchronizes exactly the lengths 2..14).** Proved by the certificate plus simulation of all representative lengths (`failall.py RULE T`). Each line n ≥ 15 fires early, at τ ≤ T:

| rule | T | depth rows 0..2T+4 periodic from t0, period p | lengths simulated (each below T+3, one per signature above) |
|---|---|---|---|
| δ14 | 10 | t0 = 51, p = 8 | 35 (15..49) |
| δ14b | 14 | t0 = 66, p = 3 | 39 (15..53) |
| δ14c | 22 | t0 = 257, p = 192 | 413 (15..427) |
| δ14d | 12 | t0 = 95, p = 48 | 116 (15..130) |
| δ14e | 14 | t0 = 56, p = 2 | 28 (15..42) |

**Reading.** For large n, the early rows of R_n are the early rows of a limit object D_r, a "dual half-line" that grows from the right border on the periodic background of the shallow depth rows. In a minimal-time solution every D_r must never fire, exactly as C∞ never fires. The near misses violate this: for n ≤ 14 they time the right end from the shallow, periodic part of the input, and the same mechanism fires the right end early for all larger n.

**Validation.**
- Mazoyer's solution (germ of 57 transitions; depth rows 0..20 periodic from t0 = 42 with period 3; 21 representatives) satisfies the early-rows constraints, T = 8, for all n ≥ 15 (CaDiCaL, table fixed: SAT).
- δ14d's table violates them (UNSAT).

**As a refutation test, with the table free.**
- full:2-9 + early rows (T = 8) of all n ≥ 10 on δ14d's germ: SAT (3 s).
- full:2-11 + early rows (T = 10) of all n ≥ 12: SAT (62 s).
- Running since 16:40 UTC: full:2-14 + early rows (T = 8) of all n ≥ 15 on δ14d's germ (44 lengths), and the δ14 loop's cones for 2..14 + early rows (T = 10) of all n ≥ 15 on δ14's germ (35 lengths).

## 17. Repair distance of the near misses at length 15

The question: how many entries of a near miss must change, with its germ fixed, for the table to synchronize 2..15?

**Encoding.** The formula is full:2-15 on the germ plus a cardinality constraint (PySAT sequential counter): at most D of the free entries that the rule uses on the lengths 2..14 may differ from the rule. Free entries that the rule does not use on 2..14 are unconstrained. Solver: kissat (script `scratch/anal/neardist.py`, not in the repository).

| rule | used free entries | D = 0 | 2 | 4 | 6 | 8 | 10 | 12 |
|---|---|---|---|---|---|---|---|---|
| δ14d | 64 | UNSAT 0 s | UNSAT 0 s | UNSAT 1 s | UNSAT 2 s | UNSAT 11 s | UNSAT 42 s | UNSAT 193 s |
| δ14e | 62 | – | UNSAT 1 s | UNSAT 1 s | UNSAT 2 s | UNSAT 5 s | UNSAT 18 s | UNSAT 67 s |

So any completion of these germs for 2..15 differs from δ14d (resp. δ14e) in at least 13 of the entries that the rule uses on 2..14. This holds even for δ14e, whose line of length 15 misses by one step. The runs for D = 16 were stopped to free the cores. These are not certified, since no proofs were logged.

## 18. Structural sharing in the encoding; the families among the 16 surviving germs

**GFIX_SHARE=1** (gfix.add_line) gives one variable to all cells that compute the same function of the table, across all encoded lengths.
- Two cells compute the same function when their dependency trees coincide down to the same half-line input values and borders. The key of a cell is the triple of its predecessors' keys, interned.
- If a firing cell and a non-firing cell get the same key, the formula receives an empty clause. This is exactly how a violation of PUMP(n, n′) appears.

Sizes:

| formula | without sharing | with sharing |
|---|---|---|
| full:2-14 (δ14's germ) | 2,210 vars, 88,060 clauses | 1,854 vars, 80,075 clauses |
| cone:2-30 (δ14's germ) | 10,670 vars, 520,701 clauses | 7,654 vars, 404,917 clauses |
| δ14d full:2-14 + early rows (T = 8) of all n ≥ 15 | 10,135 vars, 393,587 clauses | 3,691 vars, 156,087 clauses |

The answers with δ14's table fixed are unchanged (SAT for 2..14, UNSAT for 2..15 and for cone:2-30). The three early-rows runs were restarted with sharing at 16:55 UTC.

**The 16 surviving germs (K16_remaining16) form a few families.**
- Rule 22 driven at the left border, 9 germs:
  - r16_00 is δ14's germ, rule 22 on {L, B}.
  - r16_03..r16_10 run rule 22 on {L, G} (GLL, LGL, LLG > G; GGL, GLG, LGG, GGG > L), with different boundary layers in A, B.
  - For T = 8, all nine have the same certificate shape: depth rows 0..20 periodic from t0 = 39, with p = 8 for r16_00 and r16_03..r16_10; 23 signatures each.
- Elementary rule 124, the mirror image of rule 110, on {L, G}: r16_11 and r16_13 (GGL, GLG, GLL, LGG, LGL > G; LLG, GGG > L).
- The complexity-15 half-line: r16_02 (δ14c) and r16_15 (δ14d).
- r16_01, r16_12 and r16_14: three-state patterns that do not fall into these families.

## 19. Direct LRAT certificates; the joint test for the two complexity-15 labellings

**certify_lrat.sh.** CaDiCaL 3.0.1 writes an LRAT proof itself (`--lrat=true --binary=false`), and lrat-check verifies it with no DRAT-to-LRAT conversion. Test on the repair-distance formula D = 8 (3,057 vars, 111,537 clauses):
- CaDiCaL: UNSAT in 6 s;
- proof: 35 MB;
- lrat-check: `c VERIFIED` in 0.7 s.

**The common relaxation is implemented.** GFIX_UNFIX=*GL,GLL keeps the two time-0 transitions of a germ for computing the half-line but leaves them free in the table. GCEGAR_START1=AB makes gcegar.py simulate the lines n ≥ 3 from A B L…L at time 1.

Validation on δ14d's germ with the lengths 3..14 (CaDiCaL, table fixed):

| | δ14d's table | δ14c's table, renamed by σ⁻¹ |
|---|---|---|
| germ as is | SAT | UNSAT (the fixed time-0 entries differ) |
| time-0 entries free | SAT | SAT |

So both labellings' rules are models of the relaxation, as Lemma 6 of early_rows.tex predicts.

**Run started 17:02 UTC (er_cd_8).** δ14d's germ with GFIX_UNFIX=*GL,GLL, full:3-14 and the early rows (T = 8) of all n ≥ 15 (44 lengths), with sharing. If it is unsatisfiable, both complexity-15 germs are refuted at once and every five-state minimal-time solution has c78 ≥ 16.

## 20. What the limit triangles look like: Mazoyer's echo resets the line, the near misses' do not

**Mazoyer's six-state solution, line of length 600, rows τ = 0..40, right 44 cells.**
- The echo is a signal B A C B of width 4 on the diagonal, moving left at speed 1.
- Behind it every cell is quiescent (L); checked by program, the reset horizon of the line of length 600 is H(600) = 201.
- Ahead of it lies the periodic background C A A B B C … of the half-line's front region.

So the limit triangles of Mazoyer's solution are trivial: an echo of width 4 followed by L. Define the reset horizon H(n) as the last relative time up to which all cells with κ ≤ τ − 4 are L:

| n | 8 | 10 | 12 | 15 | 20 | 25 | 30 | 40 | 60 | 90 | 120 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H(n) | 4 | 4 | 5 | 6 | 8 | 9 | 11 | 14 | 21 | 31 | 41 |

H(n) ≈ n/3: the quiet region lasts until the echo reaches Mazoyer's division point, at distance n/3 from the right end, where a new general starts a smaller line in the quiescent cells. With width 3 the horizons collapse (e.g. H = 1 or 2 for most n), so the echo is exactly 4 cells wide.

**The near misses.**
- δ14d: the echo is the spare state G. Behind it, the cells mix A, B, G, L, and AAA appears after 6..12 steps (§16).
- δ14e: a doubly periodic background, an echo of A's, and again AAA behind it.

None of them clears the line behind the echo.

**A structural class to test: "reset behind the echo".** gfix region `reset:n:T:w` = `early:n:T` plus R_n(τ,κ) = L for κ ≤ τ−w.
- Validation with Mazoyer's table fixed (full:3-10): reset:24-40:6:4 and reset:30-40:9:4 SAT; reset:24-40:6:3 UNSAT.
- Probe for five states started 17:05 UTC: FREE, full:2-12 + reset:40-46:10:4. The formula has 12,106 vars and 875,426 clauses, because the half-line must be encoded to anti-diagonal 92.

**Probe result.** The FREE reset probe (full:2-12 + reset:40-46:10:4, 875k clauses) gave no answer within 25 minutes and was stopped. It is too large in this form, because the free half-line must be encoded to anti-diagonal 92.

## 21. Mazoyer's borders: the left border acts as L, the right border as G

On every neighbourhood that Mazoyer's six-state solution uses on the lines 3..120:
- δ(∗,y,z) = δ(L,y,z) for all 5 left-border entries used;
- δ(x,y,∗) = δ(x,y,G) for all 15 right-border entries used. Against every other state at least 8 of the 15 entries differ.
- δ(L,L,x) = L for every state x.

So a quiescent cell behaves exactly like the left border, and a general exactly like the right border. This is the file header's remark (borders: left ~ L, right ~ G) seen in the table. It is what lets one G at a division point split the line into two lines that run independently, which is the recursion of the two-thirds construction.

**Class BE(X_L, X_R) ("border emulation").** The constraints are δ(∗,y,z) = δ(X_L,y,z) and δ(x,y,∗) = δ(x,y,X_R) for all x, y, z ∈ W (environment variable GFIX_BE=X_L,X_R; `-` leaves a side free). They remove the 32 border entries as free choices.
- Validation: Mazoyer's germ with BE(L,G) and full:3-12, table free, is SAT.
- Run started 17:20 UTC: FREE, k = 5, BE(L,G), gcegar from full:2-6. It reached length 12 in about 6 minutes (round 11 SAT in 268 s).

**The near misses do not emulate their borders.** For each rule, the table below gives the number of border entries used on 2..14 whose value differs from that of the same neighbourhood with the border replaced by X.

| rule | left entries used | mismatches vs L / G / A / B | right entries used | mismatches vs L / G / A / B |
|---|---|---|---|---|
| δ14 | 5 | 4 / 4 / 4 / 5 | 13 | 12 / 9 / 9 / 11 |
| δ14b | 3 | 2 / 2 / 3 / 3 | 15 | 12 / 11 / 10 / 12 |
| δ14c | 3 | 3 / 2 / 3 / 3 | 14 | 7 / 8 / 10 / 8 |
| δ14d | 3 | 2 / 1 / 1 / 2 | 16 | 12 / 12 / 11 / 13 |
| δ14e | 6 | 5 / 5 / 4 / 6 | 13 | 9 / 11 / 7 / 7 |

So the five-state near misses rely on transitions specific to the borders, while Mazoyer's solution treats its borders as an L cell (left) and a G cell (right).

**Combined class BE(L,G) with pre-firing G^n.**
- With the exact firing set {GGG, ∗GG, GG∗} the formula is UNSAT at once. This is not a result: border emulation forces δ(L,G,G) = δ(∗,G,G) = F, and Mazoyer's table also maps the unused LGG to F.
- The correct combination is BE(L,G) together with `--upf G` (pre-firing G^n), the F-set otherwise free. Started 17:31 UTC; it reached length 12 within a minute.

## 22. The early-rows condition on the unrestricted problem (shallow half-line)

In FREE mode, the early rows (τ ≤ T) of a long line read only the depth rows j ≤ 2T+1 of the half-line, which are closed under predecessors. With GFIX_SHALLOW=1, gfix.py therefore encodes:
- the whole half-line only as far as the complete triangles and cones need it;
- for longer lines, only the depth rows 0..2T+2 up to time n+T.

Validation with δ14's table fixed, FREE, full:2-14 + early:15-30:T:

| T | shallow encoding | full encoding |
|---|---|---|
| 6 | SAT (6,074 vars, 399,599 clauses) | SAT (7,798 vars, 534,800 clauses) |
| 8 | UNSAT (7,546 vars, 509,831 clauses) | UNSAT (8,886 vars, 615,104 clauses) |

This matches the first early firing of δ14 at τ = 7..10.

**The decisive formula.** Lengths 2..14 complete, plus "no cell of R_n fires at τ ≤ 9" for every n = 15..30.
- All five known near misses violate the second part: δ14 at τ ≤ 10, δ14b at τ = 8 (n = 19), δ14c at τ = 7 (n = 15), δ14d at τ ≤ 8 (n = 15, 17), δ14e at τ = 9 (n = 16).
- Both parts are necessary for every minimal-time solution. So an unsatisfiable answer would prove that no five-state minimal-time solution exists; a satisfiable one gives a new kind of near miss.
- Run started 17:35 UTC as a refinement loop (gcegar.py FREE 16, from full:2-6 early:15-30:9, cones added lazily for 7..16). Round 1: 434,704 clauses, SAT in 9 s.

## 23. Symmetry breaking for the free mode (A ↔ B)

GFIX_SYMBREAK=1 requires the first half-line cell (in the order of t, then i) whose state is A or B to be A. This is valid whenever no constraint singles out A or B. It does not apply to the class X = A.
- Validation, FREE full:2-10: δ14 SAT; δ14 with A and B swapped UNSAT.
- Effect: FREE full:2-10 with CaDiCaL went from 575 s without symmetry breaking to 23 s with it (same overloaded machine).

At 17:50 UTC, three runs were restarted from their current constraints with symmetry breaking: free_er9, upf_G and be_LG_upfG. The A-class run (upf_A) was stopped at length 13 to free a core. Its constraints are in runs/upf_A_v3_paused.log.

## 24. Status at 19:00 UTC; cubes of the joint formula; sweep of the surviving germs at length 14

**Cube-and-conquer on er_cd_8.** The formula has 158,037 clauses. march_cu at depth 10 splits it into 1,012 cubes, 10 of them refuted during cubing. The first three cubes each stayed undecided after 120 s of kissat on formula plus cube. At this depth the cubes are hard, so the worker was stopped. The single run on the whole formula continues: 2 h so far, no answer.

**Phase split for the unrestricted early-rows search.** With the early rows of lengths 15..30 included, every refinement round was heavy, even at length 11 (more than 40 min). It now runs in two phases:
- Phase 1 (free_p1): FREE + symmetry breaking for the lengths 2..14 only. Started at 18:40 UTC; at length 12 after 5 minutes.
- Phase 2 (runs/phase2.sh): when phase 1 finds a table for 2..14, it restarts the loop from phase 1's constraints plus early:15-30:9.

**Sweep16.** Among the 16 germs of K16_remaining16, 2..14 completions are known only for r16_00 (δ14), r16_02 (δ14c) and r16_15 (δ14d). The other 13 are run through the refinement loop to length 14, with sharing and 30 minutes each. An UNSAT answer refutes a germ already at length 14.

**Paused.** upf_G at 18:52 UTC; its constraints are in runs/paused.txt.

## 25. Enumeration, exhaustive search, and a smaller decisive formula (19:00–20:20 UTC)

**Projected enumeration (allsat.py).** A table synchronizes the lines 2..N iff its restriction to the entries those lines use does, so the completions for 2..N fall into classes, one per projected table. allsat.py lists the classes with one incremental CaDiCaL instance: a refinement loop as in gcegar_inc.py, and a blocking clause "some used entry takes another value" for every class found. Each class can then be extended to longer lengths by depth-first search.

The counts make this infeasible at the sizes that matter. The budget was 180 s per run, and no run finished.

| problem | classes found within the budget |
|---|---|
| FREE, lengths 2..4 | > 470,957 |
| FREE, lengths 2..5 | > 388,044 |
| FREE, lengths 2..6 | > 288,749 |
| δ14d's germ, lengths 2..14 | none within 14 minutes (the first class was not yet found) |

**Exhaustive depth-first search (research/dfs_timeorder.c).** This is a Balzer–Sanders style search. It is an independent re-implementation of src/fsspdfs.c, written before I noticed that tool; it evaluates the cells in time order instead of along anti-diagonals.
- The lines are simulated in time order: the half-line first, then the reflected triangles.
- A table entry is branched on when a cell first needs it: F in a firing row, a working state otherwise.
- A branch dies on early or missing firing, or when the half-line would fire.
- It also dies when a return-chain cell equals the half-line's cell.
- The first auxiliary state to be assigned is called A.

Validation with four states, in plain mode (lines 2..N only):

| N | nodes | complete assignments |
|---|---|---|
| 5 | 2.10·10^9 | 1,829,258 |
| 6 | 6.30·10^9 | 49,893 |
| 7 | 6.60·10^9 | 342 |
| 8 | 6.62·10^9 | 27 |

The 27 for N = 8 are the 27 partial rules of the note (and of Yunès 1993), so the two implementations agree.
- In the default mode, two consequences of line 9 not firing early at its left cells are added: the return chain of line 8 differs from the half-line, and the half-line does not fire on t + i ≤ 16. Then N = 8 has no completion (6.64·10^9 nodes).
- So for four states, the lines 2..8 together with these two conditions already admit no rule.

For five states the tree is far too large for this method. The solvers' clause learning is essential.

**Edge tests on δ14d's germ.**
- full:2-9 plus the early rows (T = 8) of all n ≥ 10 (49 representative lengths from asymp.py) is SAT in 4.2 s. The early rows alone do not contradict the short lines.
- Adding the left bands band:10-40:4 gives UNKNOWN after 600 s.

**Every known near miss fires early at τ ≤ 9.** Script: scratchpad anal/firstF.py; lines 2 ≤ n ≤ 60 simulated. N is the last length of the run of synchronized lines 2..N; n is the smallest length with an F at relative time τ ≤ 9 (and τ < n−1).

| rule | N | n | τ | relative time of the first F, N < n ≤ 60 |
|---|---|---|---|---|
| δ13 | 13 | 14 | 8 | τ = 8 for every n |
| uniformA_2-12 | 12 | 16 | 7 | 11, 10, 10 for n = 13, 14, 15; τ = 7 for n ≥ 16 |
| δ13_chaotic | 13 | 14 | 9 | 7 ≤ τ ≤ 15; period 8 in n for n ≥ 22 |
| δ14 | 14 | 15 | 8 | 7 ≤ τ ≤ 10; period 8 in n for n ≥ 18 |
| δ14b | 14 | 19 | 8 | 8 ≤ τ ≤ 14; τ = 8, 12, 14 with period 3 for n ≥ 25 |
| δ14c | 14 | 15 | 7 | 7 ≤ τ ≤ 18 |
| δ14d | 14 | 15 | 8 | 6 ≤ τ ≤ 12 |
| δ14e | 14 | 16 | 9 | 9 ≤ τ ≤ 14; τ = 9, 11 with period 2 for n ≥ 20 |

The failures recur periodically in n. These are the limit triangles of §16 firing early.

**A smaller decisive formula.** Let F(N0, T, N1) be full:2..N0 plus early:(N0+1)..N1:T.
- Every part is a necessary condition, because a line of length n > T+1 may not fire at τ ≤ T.
- For T = 9, the lines up to 10 are complete anyway. So F(10, 9, N1) is the smallest formula of this type that excludes every rule in the table.
- It is a relaxation of the decisive formula of §22: it drops the complete lines 11..14, whose early rows it keeps.
- If it is unsatisfiable, no five-state minimal-time solution exists.

Runs (FREE, sharing, shallow half-line, A/B symmetry breaking; kissat with a 4 h limit):

| formula | vars | clauses | started (UTC) |
|---|---|---|---|
| F(10, 9, 60) | 17,275 | 1,186,016 | 19:42 |
| F(10, 9, 30) | 8,155 | 538,376 | 20:05 |

## 26. Early-row formulas G_k(T, N1); four states refuted with complete lines 2..7

**Definition.** G_k(T, N1) = full:2..(T+1) + early:(T+2)..N1:T, in the free mode. Requirements:
- the half-line is encoded cell by cell to the anti-diagonal 2·N1 (default margin, no GFIX_SHALLOW);
- the return chains are included.

Every condition holds for every minimal-time solution (early_rows.tex, Lemma "G"). F(10, 9, N1) of §25 is G_5(9, N1) with the shallow half-line.

**Why not shallow.** The shallow run F(10,9,60) returned SAT after 27 min, but the model is spurious. Its general fires at time 22 (cell 1, anti-diagonal 23), outside the half-line cells that the shallow encoding constrains (anti-diagonals ≤ 20). The model was decoded with scratchpad anal/decode.py, which rebuilds the encoding and reads the kissat model.

The decisive formula of §22 and the phase-2 loop used the shallow encoding too. An UNSAT answer from them would still have been valid, but a SAT answer could be spurious. runs/phase2.sh now runs without GFIX_SHALLOW, with GFIX_SHARE=1.

**Four-state calibration** (CaDiCaL, FREE k = 4, sharing):

| formula | result |
|---|---|
| G_4(4, 30) = full:2-5 early:6-30:4 | SAT (0.0 s) |
| G_4(5, 30) = full:2-6 early:7-30:5 | SAT (0.8 s) |
| full:2-7 early:8-30:5 | SAT (4.2 s) |
| G_4(6, 30) = full:2-7 early:8-30:6 | UNSAT (76 s) |
| G_4(6, 20) | UNSAT (45 s) |
| G_4(6, 14) | UNSAT (36 s) |
| G_4(6, 10) | UNSAT (34 s) |
| G_4(6, 9) | SAT (12 s) |
| G_4(6, 8) | SAT (8 s) |
| G_4(6, 10) without the return chains of 8, 9, 10 (GFIX_NORC) | SAT (12 s) |
| G_4(7, 30) = full:2-8 early:9-30:7 | UNSAT (66 s) |

**Certificate for G_4(6, 10)** (certify_lrat.sh):
- 919 vars, 22,960 clauses; CNF sha256 0e0ba286ec7b60d05f6edee470b5cbd4d6655cd184186e630a96bd4187932e03;
- CaDiCaL 41 s; LRAT 166,919,248 B, sha256 7943a69803f934814a80c731060747afeee9317d205b6330c4325a039f6da6fb;
- lrat-check VERIFIED in 5 s.

So the four-state impossibility needs only the complete lines 2..7, plus the first seven rows and the return chains of lines 8, 9, 10. With complete lines alone it needs 2..9: 27 partial rules synchronize 2..8.

**Five states.** G_5(9, 30) is running since 20:17 UTC (10,175 vars, 635,332 clauses). G_5(9, 60) (30,425 vars, 1,960,762 clauses) was started then and stopped at 20:25 to free a core. G_5(10, 26) and G_5(11, 28) are running since 20:25:
- G_5(10, 26): full:2-11 early:12-26:10, 8,815 vars, 555,373 clauses;
- G_5(11, 28): full:2-12 early:13-28:11, 10,661 vars, 687,648 clauses.

By the four-state calibration, the threshold in T may lie a few lengths below the complete-line threshold.

Also stopped at 20:25: the sweep of the complexity-16 germs, after r16_01 and r16_03, both UNKNOWN at 30 min.

## 27. Early-row formulas for a fixed germ (20:30–20:50 UTC)

With the germ fixed, the early rows of all lengths reduce to the representatives of asymp.py. The per-germ formula at level T is:
- full:2-(T+1);
- plus the early rows (τ ≤ T) of all n ≥ T+2, i.e. the representatives of asymp.py at T with NMIN = T+2.

This is the strongest form of G_5(T, ·) for that half-line, since it covers every n.

**δ14d's germ (= r16_15).**
- T = 10: 59 representatives, kissat SAT in 18.7 s.
- The model (scratchpad runs/germ14d_T10.rule; extracted with CaDiCaL in 105 s) synchronizes 2..11.
- Lines 12..16 fire at the right time 2n−2, but not all cells.
- Every longer line up to 40 first fires at τ ≥ 11.
- With A and B exchanged, this model satisfies G_5(10, N1) and G_5(9, N1) for every N1. So the free runs G_5(9, 30) and G_5(10, 26) can only end SAT, and they were stopped at 20:33.
- T = 11: 82 representatives; kissat UNKNOWN after 900 s (machine overloaded).
- T = 12 (117 representatives): running.

**Joint test for the two labellings of the complexity-15 half-line** (runs/joint15.sh T):
- δ14d's germ with GFIX_UNFIX=*GL,GLL, full:3-(T+1), and the early-row representatives;
- line 2 is left out, because it differs between the labellings (early_rows.tex, Lemma labellings);
- if it is unsatisfiable, both complexity-15 germs are refuted and c78 ≥ 16;
- T = 11 started 20:49, kissat 2 h.

**Sweep of the 16 germs of K16_remaining16** (runs/gsweep.sh): the per-germ formula at T = 11, then T = 12, kissat 20 min each; results in runs/gsweep.log. Started 20:38.

**Stopped:**
- free_p1 at round 4 (length 13), 2.2 h in;
- the phase-2 waiter;
- er_cd_8 after 3 h 37 min without an answer.

The early-row formulas are stronger tests per unit of encoding than the old formulas (full:2-14 + early rows at T = 8).

**Certification status.** A refutation of all 16 germs would give c78 ≥ 17, but only after the classification behind K16_remaining16 is certified. Only its complexity ≤ 14 part is LRAT-certified (results/germs/CERTIFICATES.txt).

## 28. Right-end cones lower the threshold; four states refuted with complete lines 2..5

Adding the right ends (region cone:n, i.e. τ + κ ≤ n − 1: the right end fires at 2n−2 and nothing in its cone before) to the early-row formulas gives G_k(T, N1, C) (early_rows.tex, condition (G5)).

**Four-state calibration** (CaDiCaL, FREE k = 4, sharing):

| formula | result |
|---|---|
| full:2-5 early:6-30:4 cone:6-12 | UNSAT (56 s) |
| full:2-5 early:6-12:4 cone:6-12 | UNSAT (30 s) |
| full:2-5 early:6-30:4 cone:6-11 | UNSAT (49 s) |
| full:2-5 early:6-30:4 cone:6-10 | UNSAT (49 s) |
| full:2-5 early:6-30:4 cone:6-9 | SAT (6 s) |
| full:2-5 early:6-11:4 cone:6-10 | UNSAT (39 s) |
| full:2-5 early:6-10:4 cone:6-10 = G_4(4, 10, 10) | UNSAT (33 s) |
| full:2-4 early:5-30:3 cone:5-12 | SAT (1 s) |
| full:2-3 early:4-30:2 cone:4-12 | SAT (2 s) |
| full:2-5 cone:6-12 (no early rows) | SAT (2 s) |
| full:2-6 early:7-30:5 cone:7-12 | UNSAT (55 s) |
| full:2-6 early:7-30:5 cone:7-12:2 | UNSAT (49 s) |

**Certificate for G_4(4, 10, 10)** (certify_lrat.sh):
- 874 vars, 20,461 clauses; CNF sha256 124f095450ee725be06f07271e1d752c4cbacce9f4bff190ddea1907d39e4f51;
- CaDiCaL 36 s; LRAT 172,820,213 B, sha256 7f76fe69c6158ebf03891cb9aa6fe0fb61b5e7e60f1b5b317f10baa4e944c8d8;
- lrat-check VERIFIED in 4 s.

So four states are refuted by the complete lines 2..5, plus the first five rows, the return chains and the right ends of the lines 6..10. Neither part suffices alone.

**Five states, cone-augmented free formulas** (share, symbreak, full half-line; kissat 4 h), started 21:17:
- C_7 = full:2-8 early:9-30:7 cone:9-20: 9,999 vars, 612,003 clauses;
- C_8 = full:2-9 early:10-30:8 cone:10-20: 10,471 vars, 649,616 clauses.

They replace G_5(11, 28) and G_5(12, 30), stopped after about an hour without an answer.

**Joint complexity-15 test with cones** (runs/joint15c.sh 10 20; started 21:11, kissat 2 h): T = 10, the early rows of all n ≥ 12, and the right ends of lines 12..20.

**Other per-germ results (overloaded machine).** All three were UNKNOWN:
- δ14d's germ at T = 11 and at T = 12, after 900 s each;
- δ14d's germ at T = 10 plus cone:12-20, after 1200 s.

The joint test without cones at T = 11 (runs/joint15.sh 11) runs until 22:49.

**Per-germ results with right-end cones (δ14d's germ; kissat, 600 s each, overloaded machine):**
- T = 7, full:2-8, the early rows (τ ≤ 7) of all n ≥ 9, cone:9-20: SAT (556 s). So the free C_7 is SAT as well (same lifting argument as in §27), and it was stopped at 21:36.
- T = 8, cone:10-20: UNKNOWN.
- T = 10, cone:12-20: UNKNOWN (1200 s).

**The T = 7 cone model fires at both ends.** The model of δ14d's germ at T = 7 with cone:9-20 was re-solved and decoded (scratchpad runs/d14d_T7c.rule).
- It synchronizes the lines 2..8 and 10.
- In the lines 9, 11–17 and 19, the left cells (via the return chain) and the right end (via the cones) fire exactly at 2n−2, but the middle cells do not. For n = 9 the firing row is F F L G L L G B F.
- Lines 18, 20, 21, 23 and 24 fire early, outside the encoded cones (at τ = 16, 13, 10, 10, 11).

The T = 10 model without cones (§27) failed at the right end instead. So the cheap regions (early rows, right-end cones, left bands) control the two ends of each line. Some five-state tables get both ends right but not the middle, which four-state tables cannot do (§28). Excluding them needs the firing of middle cells, whose dependency cones cover most of R_n. That is where the cost of complete lines comes back.

**Joint complexity-15 test at T = 11: SAT** (kissat, 79 min, finished 22:08). The model was decoded with scratchpad anal/decode.py into runs/joint15_T11.rule. With the time-1 configuration A B L…L of δ14d's labelling:
- it synchronizes the lines 3..12;
- lines 13 and 14 fire at the right time, but only partially (line 13: F F F F G B L B L L B B F);
- lines 15–25 fire early at τ = 12..17.

So the complexity-15 half-line passes the early-row level T = 11 for all lengths. T = 12 excludes this model (line 13 complete; lines 17 and 24 fire at τ = 12). The joint test at T = 12 started 22:15 (kissat 2 h).

δ14d's germ at T = 7 with cone:9-20 and the middle cones mid:9-16 (gfix.py region mid): UNKNOWN after 1200 s.

**Joint test with cones at T = 10 (cone:12-20): UNKNOWN** after 2 h of kissat (23:11). The same CNF is now running in CaDiCaL (-t 21600) since 23:13. Still running at 23:13:
- joint15 T = 12 (kissat 2 h, from 22:15);
- joint15c T = 9 with cone:11-20 (kissat 2 h, from 21:40);
- the free C_8 (kissat 4 h, from 21:17).

The models found so far are saved in research/models/ and described in early_rows.tex, Proposition "germmodels".

**Joint test with cones at T = 9 (cone:11-20): UNKNOWN** after 2 h of kissat (23:53). CaDiCaL (-t 21600) runs on the same CNF since 23:54. Both cone-augmented joint formulas (T = 9, 10) are in the hard zone; T = 7 with cones is SAT (Proposition "germmodels" (ii) of early_rows.tex).

**Joint test at T = 12 (no cones): UNKNOWN** after 2 h of kissat (00:15).

Started 00:16: the joint test at T = 7 with the cones of the right four firing cells (cone:9-20:3; runs/joint15h.sh 7 20 3, kissat 2 h). At T = 7 with only the right end (cone:9-20) the single labelling of δ14d is SAT. In that model, line 9 fires its right-end cell but not its neighbour.

**Free C_8 (full:2-9 early:10-30:8 cone:10-20): UNKNOWN** after 4 h of kissat (01:17).

Started 01:18: C_7h3 = FREE full:2-8 early:9-30:7 cone:9-20:3, i.e. the right four firing cells of lines 9..20, kissat 4 h. C_7, with the right end only, is SAT by the δ14d model of §28. That model fires the right-end cell of line 9 but not its neighbour, so C_7h3 excludes it.

**Joint test with cones at T = 9 (cone:11-20): SAT** (CaDiCaL, from 23:54 to 01:52). Decoded with anal/decode.py (same environment GFIX_UNFIX='*GL,GLL' GFIX_SHARE=1 and the same specs) into runs/joint15c_T9_20.rule, 96 entries. As in the joint relaxation at T = 11, the model maps *GL → F and GLL → G, so it is a model of the relaxation, not a rule that synchronizes the line of length 2. Hence the complexity-15 half-line also passes T = 9 together with the right ends of the lines 11..20, and this test cannot show c_78 ≥ 16. Still running: the joint test at T = 10 with cones (CaDiCaL until about 05:13), joint15h T = 7 (kissat until about 02:16) and C_7h3 (kissat until about 05:18).

**Joint test with the right four firing cells at T = 7 (joint15h, cone:9-20:3): UNKNOWN** after 2 h of kissat (02:16). Still running: the joint test at T = 10 with cones (CaDiCaL until about 05:13) and C_7h3 (kissat until about 05:18).

**Left bands alone on δ14d's germ (02:20).** band:10-60:2 is satisfiable; band:10-60:4 (870k clauses) is UNKNOWN after 280 s of kissat. In the half-line of this germ, the periodic triangles (b.b.b / abab, period 2) start at cell 7 or 8, behind a boundary layer (cell 1 is always A, cell 2 always B). Lemma 4.1 would need s ≥ 8, hence a periodic stretch longer than 4^16·2, so it cannot reach this half-line.

**Per-germ tests at T = 10 with cones, started 02:31 (scratchpad runs/pergerm.sh).** For each complexity-15 germ separately, without the relaxation: full:2-11, the early rows (τ ≤ 10) of all n ≥ 12 (asymp.py representatives), and cone:12-20. δ14d's germ runs in CaDiCaL and δ14c's germ in kissat, 6 h each. These formulas are stronger than the joint one, so they may be decided sooner. If both are unsatisfiable, every five-state minimal-time solution has c_78 ≥ 16 (after LRAT certification).

**PUMP on the complexity-15 half-line, larger range.** The fast checker scratchpad anal/pumpfast.c reproduces the recorded results (δ12: 0 violations up to 650; δ14: 0 up to 800). As a positive control, it finds all 351 pairs violated for a trivial rule whose general never moves, as src/pumping.py does. On δ14c and δ14d (both labellings of the complexity-15 half-line), PUMP(n, n′) holds for 4 ≤ n < n′ ≤ 3000. PUMP does not exclude this half-line.

**Parity structure of the complexity-15 half-line.** In the half-line of δ14d's germ, every cell with i ≥ 2 on an odd anti-diagonal (t + i odd, equivalently even depth) is B. So the lower input anti-diagonal of every R_n is B except at its two ends. The half-line is therefore a 3-state automaton network on the odd-depth rows: C(t+1, i) = g(C(t, i−1), C(t, i+1)) with g(x, y) = δ(x, B, y), which is defined by the germ entries ABA>A, ABB>B, ABL>B, BBA>L, BBB>B, BBL>L, LBA>B, LBB>L, LBL>A. For a fixed driving value y, g(·, y) is a 3-cycle (y = L), a transposition of L and B (y = A), or the map A, B ↦ B, L ↦ L (y = B). Each odd depth row is a finite automaton driven by the odd row two depths ahead.

Consequences for R_n:
- The return chain obeys r(κ) = δ(B, u_κ, r(κ−1)), where u_κ is the upper input.
- (G3) for this germ says that r(κ) ≠ B for every κ ≤ n−2, because the half-line cell compared with r(κ) has even depth.

These constraints are already contained in the band and early-row encodings; they explain why the lower inputs carry no information about n.

**Whole return chains (03:04).** gfix.py imposes (G3) only on the return-chain cells inside the encoded region. The region band:n:1 is the whole return chain together with the firing cell of cell 1; band:n:2 adds chain 2. Both are closed under predecessors and cheap with a germ fixed. With complete lines 2..11 on δ14d's germ, adding band:12-120:1, or band:12-120:2 (581k clauses), is satisfiable within seconds. The return chain avoids the forbidden value B, which the germ's entry BLL>B would otherwise produce, by passing through G. So whole return chains add no strength to this germ.

**Container restart at about 03:37: four runs lost without a verdict.**
- joint15c T = 10 with cone:12-20, CaDiCaL, after 4 h 25 min;
- C_7h3, kissat, after 2 h 20 min;
- the per-germ tests at T = 10 with cone:12-20, δ14d's germ in CaDiCaL and δ14c's germ in kissat, after 1 h 5 min each.

None had answered. They are restarted when the machine is free again; the scripts are scratchpad runs/joint15c.sh, runs/pergerm.sh and runs/pergerm2.sh.

**Restarted at 04:37:** the per-germ tests at T = 10 with cone:12-20 (δ14d's germ in CaDiCaL, δ14c's germ in kissat, 6 h each) and C_7h3 (kissat, 4 h), on the same CNF files. The joint test joint15c T = 10 is not restarted, because the two per-germ formulas are stronger.
