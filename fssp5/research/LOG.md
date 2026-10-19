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
