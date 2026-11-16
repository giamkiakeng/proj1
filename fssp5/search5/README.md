# Five states: structured searches

Working notes and programs for the open question of the paper in `../paper`: is there a five-state
minimal-time solution of the firing squad synchronization problem? Nothing here answers it. The programs
search restricted classes of five-state rules, and this file records what each search found.

Conventions. States `L` (quiescent), `G` (general), auxiliary `A`, `B`, firing `F`; `*` is the border. A
*line* is the diagram $C_n$ of the line of length $n$; a rule *synchronizes* $n$ if $C_n$ is all `F` at time
$2n-2$ and has no `F` before. "UNSAT" means that a SAT solver or an exhaustive enumeration proved that the
class is empty for the stated lengths; "unknown" means that the run was stopped. Proof certificates (LRAT) exist for the results of Section 4, for Theorem 6.4 and for Propositions 7.1 to 7.4, where stated there; the
other computer results have the status of solver answers, cross-checked where the tables say so. Lemmas 6.1
to 6.3, 6.5 and 6.6 and Proposition 8.2 are proved by hand.

**Main results so far.** "Certified" means: every unsatisfiability claim has a proof that an independent
checker verified, and the completeness of every case split was checked by a program that uses no solver.

| statement | status | where |
|---|---|---|
| No five-state rule with a stable general, (B1), synchronizes all lines $2,\dots,16$; three such rules, and up to unused entries only these, synchronize $2,\dots,14$ under the conditions that the lines 15 and 16 impose | certified | Theorem 6.4 and the paragraph after it |
| No five-state rule with (B1) in the weak reading and the image condition (B2) for the neighbourhoods without a border, for any of the ten involutions, synchronizes all lines $2,\dots,14$ | certified | Proposition 7.3 |
| The same for Balzer's four conditions as Yunès states them (open at the end of Section 6.5 of the paper) | certified | Proposition 7.2 |
| The same class with a stable state that is not the initial state of the general: exact maxima 10, 6 and 2 for the nine involutions other than the identity | certified | Proposition 7.4 |
| (B1) and (B2) with borders: no rule for $2,\dots,12$, in both readings of (B1) | certified | Proposition 7.1 |
| No five-state rule is a local image of Mazoyer's six-state solution for windows up to radius 2, or radius 1 with one step of memory | certified | Section 4 |
| Consequences of a stable general: firing from three generals only, walls, gap bounds; the same in the weak reading | proved by hand | Lemmas 6.1 to 6.3, 6.5, 6.6 |
| The bound $(k-1)^{2s}\ell$ of the left-border lemma is attained for $s=1$ and is not attained for odd $k$ and $s\ge2$ | solver answer with simulated rules; proved by hand | Observation 8.1, Proposition 8.2 |
| Four states: no rule synchronizes all lines $3,\dots,9$ or all lines $4,\dots,9$ (42 and 399 rules reach the length 8), but 36 rules synchronize $5,\dots,9$ and none $5,\dots,10$; the numbers of four-state rules of every length range and class; no four-state rule with a stable general synchronizes both 6 and 7 | exhaustive enumeration without a solver | Section 5 |
| Sizes of the search trees of other classes, among them the open problem itself ($3\cdot10^{18}$ nodes for the lines up to 15) | estimates by random descents | Section 9 |

Open here: whether a five-state rule with a stable general synchronizes $2,\dots,15$ (running), the identity
in Propositions 7.3 (12 or 13) and 7.4, (B2) alone, (B3) alone, and the problem itself.

## 1. Programs (`src/`)

| program | what it does |
|---|---|
| `simlib.py` | reads rule tables (format of `../paper/supplementary/results`), simulates lines |
| `mcopy.py` | CNF of "synchronize the lengths `nmin..N`" plus the recursive structure of Section 2; solves it with Kissat or CaDiCaL (`KISSAT`, `CADICAL` or the `PATH`) and re-simulates every model |
| `mcopy_inc.py` | the same formula solved incrementally: one line at a time in one CaDiCaL instance (PySAT), keeping learnt clauses |
| `mdfs.c` | exhaustive depth-first enumeration of the same class (transitions fixed lazily, as `fsspdfs.c` of the supplement) |
| `msim.py` | CNF: a rule whose diagrams *decode* to the diagrams of a target solution (Section 3) |
| `decdfs.c` | exhaustive enumeration of the same decoding classes; the decoder is not searched but checked for consistency |
| `facsat.py` | CNF: a rule that is a *local image* of a target solution (Section 4) |
| `facdfs.c` | exhaustive enumeration of local images |
| `germw.c` | lists the half-lines of the stable-general class (Section 6) below an anti-diagonal, optionally with at most $K$ transitions |
| `germscan.py` | one incremental solver for a list of half-line germs or cases: each is passed as assumptions, the clauses of the longer lines are guarded by activation literals |
| `germsat.py` | stable generals: depth-first search over the half-line with the incremental solver at every node (Section 6) |
| `gsat.py` | the same search for any class of `mcopy.py` and any number of states |
| `wenum.c` | second enumerator for the stable-general class, independent of `mdfs.c` |
| `enumtree.py`, `covercheck.py` | enumeration of every closed node of a tree search; check that the closed nodes cover the tree |
| `certtree.py`, `germsat_cert.py` | LRAT / DRAT certificates for the closed nodes |
| `fix_open.py`, `recheck_ct.py` | for `certtree.py`: collect the nodes with a complete half-line that were not refuted within the time limit (they are then certified with a long limit); second check of the certified cubes, all or a random sample, with `lrat-check` and `cake_lpr` |
| `gcert.py` | the tree search of `gsat.py` with a certificate for every closed node: a new CaDiCaL process per node with a time limit and an LRAT proof, checked by `lrat-check` and, if `CAKELPR` names its binary, by the verified checker `cake_lpr`; a node that is not refuted in time is split. Resumable; `--recheck` rebuilds every cube formula, compares the SHA-256 digests and verifies the proofs again |
| `gcover.py` | checks without a solver that the certified cubes of `gcert.py` are a complete case split; shares no code with `gcert.py` |
| `nodecert.py` | certified refutation of single nodes under another formula of `gcert.py`, for example the strict formula of the lines $2,\dots,N$ at the nodes that are satisfiable at the level $N-1$ (this decides the exact maximum of a class, Proposition 7.3) |
| `node_model.py` | a rule at a node: solves a formula of `gcert.py` (for example the strict formula of the lines $2,\dots,N$) with the units of a node, writes the table and checks it without the encoder (simulation from the initial state of `--init`, (B1) weak and (B2) without borders on the table) |
| `gchain.py` | raises $N$ until the tree of `gcert.py` closes: a node at which the formula for $N$ is satisfiable is recorded, not split, and searched again with the formula for $N+1$ (every model of $F_{N+1}$ is a model of $F_N$, so the closed nodes of all levels together are a case split for the last level) |
| `weakwalls.py` | redundant clauses of Lemmas 6.5 and 6.6 (weak reading); `gsat.py --wwalls`, `gcert.py --wwalls` |
| `mstrict.py` | gap clauses of Lemma 6.3 that are sound for the strict formula of the lines $2,\dots,N$ (`gsat.py --sgap`, `gcert.py --sgap`); `--cellunit` and `--cellclause` of the two programs add a unit clause or one clause on cells of the half-line |
| `minit.py` | the lines start from `X L ... L` for another working state `X` (`gcert.py --init X`) |
| `check_balzer.py` | which of (B1) to (B4), in their weak and strong readings and for a given involution, hold on the table of a rule; then simulation |
| `ladder.py`, `freeset.py` | rules with (B3) in which at most $R$ of the entries that (B1) fixes are not `G`, or in which chosen entries are free (strict formula); the corresponding `--set` list for `gsat.py` and `gcert.py` |
| `enum_rules.py` | all rules of a class for the lines $2,\dots,N$ up to unused transitions (strict formula; feasible for four states) |
| `fsdfs.c` | exhaustive backtracking search without a SAT solver (`gcc -O2 -o fsdfs fsdfs.c -lm`): simulates the lines $n_0,\dots,N$ in this order and branches on every transition when it is first needed; counts the rules for $n_0,\dots,n$ up to unused transitions for every $n\le N$; class options `-b1s -b1w -b3s -b3w -b4 -set -neq`, lemma-based pruning for a fixed $N$ (`-front -chain -prefire -wall -gap`), `-knuth R SEED` for a size estimate by random descents. Complete for four states in seconds; an independent check of the encoders (Section 5) |
| `fsdfs2.c` | `fsdfs.c` with conflict-directed backjumping: every cell carries the set of transitions on which it depends, a failure returns the set that causes it, and a branching whose transition is not in that set is left at once. The number of rules for $n_0,\dots,N$ is that of `fsdfs.c` (compared for four states, all $N\le9$, and for the five-state cases of Section 5); 3 to 5 times fewer nodes. Options `-cell`, `-cellany` for conditions on half-line cells |
| `near2.py` | is there a rule for $2,\dots,N$ that differs from a given rule in at most $D$ of the transitions that it uses (strict formula, no class; the unused entries are free)? |
| `enum_satnode.py` | enumerates the models of $F_{14}$ at the satisfiable node of the stable-general tree, up to unused table entries, and writes the formula whose refutation certifies that there are no others |
| `check_rule_formula.py`, `check_weak_lemmas.py`, `check_wwalls_enc.py` | tests: a rule of a class that synchronizes $2,\dots,N+2$ must satisfy the formula of `gcert.py` at $N$; the statements of Lemmas 6.5, 6.6 and 6.2' on the diagrams of given rules |
| `leftb.py` | CNF: a rule that synchronizes one line with periodic input anti-diagonals at the left border (Section 8) |
| `ftime.py` | CNF for rules that synchronize the lines $2,\dots,N$ at some time chosen by the solver, not necessarily minimal (exploratory, Section 9) |

**What a refutation at $N$ means.** The formula of `mcopy.py K N` (also in `mcopy_inc.py` and `germscan.py`)
is $\Phi_N=\mathrm{MT}(2..N)\wedge\mathrm{RC}_N$: "the lines of lengths $2,\dots,N$ are synchronized at time
$2n-2$ and not before", together with three groups of clauses that follow from the synchronization of the line
$N+1$ (Lemma 2.4 and equation (2) of the paper): the front cell $(N-2,N-1)$ is not `L`, the return chain $t+i=2N-1$
of the line $N$ differs from the half-line, and the half-line has no `F` on $t+i=2N-1$. So
$\mathrm{MT}(2..N+1)\Rightarrow\Phi_N\Rightarrow\mathrm{MT}(2..N)$: a model is a rule for $2,\dots,N$ (and is
simulated), and a refutation says that no rule of the class synchronizes all lines $2,\dots,N+1$. With
`--strict` the three groups are left out, the half-line ends at $t+i=2N-2$, and the clauses of `--nogh`
(Lemma 6.2) are kept only where that lemma uses lines up to $N$; the formula is then $\mathrm{MT}(2..N)$ with
the clauses of the class. Below, "refuted at $N$" or "UNSAT for $2..N$" refers to $\Phi_N$ unless "strict" is
stated; with `--nogh` and without `--strict` it means that no rule of the class synchronizes $2,\dots,N+2$.
Further options: `--set xyz=d` fixes a transition; `--extra n1,n2` adds complete longer lines; `--early N2 T`
adds the first $T$ rows after the reflection of the lines up to $N_2$ (no `F`); `--wimp`, `--wgap` add the
clauses of Lemmas 6.1 and 6.3. With `--front1` the front cell $(N-1,N)$ on the last anti-diagonal of the
formula is not `L` either (Lemma 2.4 of the paper for the lines $N+1$ and $N+2$); with `--front1`, `--nogh` or
`--noghw` a refutation at $N$ says that no rule of the class synchronizes all lines $2,\dots,N+2$.

Checks of the programs:

- `mcopy.py` with Mazoyer's table fixed is satisfiable for the structure parameters measured on Mazoyer's
  diagrams and unsatisfiable when one parameter is tightened (Section 2).
- `mcopy.py` against `mdfs.c` for four states without structure: lengths 2..7 satisfiable (`mdfs.c`: 258 of the
  536 partial rules for 2..7 also pass the anti-diagonal 13 and the return-chain condition of the line 7);
  lengths 2..8 satisfiable with the half-line limited to the anti-diagonal 14; 2..8 unsatisfiable with the
  default half-line (anti-diagonal 15, and the return chain of the line 8 required to differ from the
  half-line), and `mdfs.c` finds 0 rules there. `mdfs.c` reproduces the numbers of partial four-state rules of
  the paper (828,670, 64,299, 536, 27, 0 for the lengths up to 5, ..., 9).
- Every satisfiable answer of `mcopy.py` is checked by simulating the decoded rule. This check found an error
  in the first version of `mcopy.py` (the cell $n$ at time $n-1$ had no transition clause); the results below
  are from the corrected program.
- `decdfs.c` and `facdfs.c` with six states and decoder radius 0 return exactly one rule, Mazoyer's.
- `lrat-check` prints `VERIFIED` also for a proof that does not contain the empty clause, so a satisfiable
  formula can look certified. `certify.sh` therefore reports a certificate only if CaDiCaL answers
  `UNSATISFIABLE` and the last lemma of the proof is the empty clause. This check was added when a satisfiable formula
  of Section 7 (strong reading, $I=(G\,B)$, $N=4$) passed `lrat-check`; the table of Proposition 7.1 is from
  runs with the check. All certificates of Section 4 had the answer `UNSATISFIABLE`.
- The classes of Section 3 that `decdfs.c` exhausts are also unsatisfiable for `msim.py`.
- `gcert.py 4 9 --front1 --tlim 1` (four states, no class) closes the tree with 38 certified cubes and 20
  splits (32 to 40 cubes in other runs: the time limit decides which nodes are split), and `gcover.py` reports a
  complete case split; with one cube removed from the file it reports the hole.
  `gcert.py 4 8 --strict` stops with a satisfiable node, in accordance with $N_4=8$. `--recheck` reproduces
  the 38 formulas and proofs digest for digest, and both checkers accept them again.
- `test_branching.py`, `test_branching_ct.py`: for 300 random rules per setting, the neighbourhood that the
  branching of `gcert.py` (five settings: no class, `--noghw`, `--nogh`, `--strict`, `--init A`) and of
  `certtree.py` asks for at every node is the neighbourhood above the first half-line cell, in the order of the
  search, that the transitions fixed so far do not determine, where the half-line is computed by a direct
  simulation of the rule; some 4000 to 7000 branching steps per setting, no disagreement.
- `check_rule_formula.py`: the rule `balzer_noborder12` of the paper (it synchronizes $2,\dots,12$) satisfies the
  formula of Proposition 7.2 at $N=9$ and $N=10$, as it must (and at $N=11$); the rule for 2..13 of Section 6
  satisfies the formula of the stable-general search at $N=11$, as it must (and at $N=12$).
- `test_reduction.py`: the reduction for the length 15 (Section 6: a rule with (B1) for $2,\dots,N_0+1$ satisfies
  the formula of the level $N_0$ or has a `G` on the anti-diagonal $2N_0-1$ of its half-line, at a cell
  $3\le i\le N_0-1$) is tested on 60 rules each for $N_0=8,9,10$, enumerated from the strict formula of the
  lines $2,\dots,N_0+1$: 36, 52 and 60 of them satisfy the formula of the level, the other 24, 8 and 0 have such
  a wall, and none has neither. This also exercises the strict formula and the gap clauses of `mstrict.py`:
  with and without the redundant clauses, the strict formula with a unit clause for the front cell or for one
  cell of the last anti-diagonal has the same answer in all 22 cases tried for $N=6,\dots,9$.

## 2. Rules with the recursive structure of Mazoyer's solution

**Observation (simulation, $3\le n\le 45$).** In Mazoyer's six-state solution the line of length $n\ge 10$
contains verbatim copies of shorter lines. With $m=\lceil n/3\rceil$ and $T=2n-2m$,
$$C_n(T+s,\;n-m+i)=C_m(s,i)\qquad(s\ge 2,\ 1\le i\le m),$$
and the same holds for the remaining part: with $r_0=n$, $m_j=\lceil r_j/3\rceil$, $r_{j+1}=r_j-m_j$, the
cells $r_j-m_j+1,\dots,r_j$ carry a copy of $C_{m_j}$ from its row 2 on, shifted to end at time $2n-2$, as
long as $m_j\ge 3$. The right third of the line is a line of its own that starts when the echo of the right
end meets the first signal of the general, and so on.

**Class $\mathcal M(a,s_0,m_{\min})$.** Rules that synchronize $n_{\min}..N$ and satisfy the copy equations
with $m(r)=\lfloor (r+a)/3\rfloor$, from the row $s_0$ of the copy on, for all sub-lines with
$m\ge m_{\min}$. Optional further conditions, all satisfied by Mazoyer's solution with the values in brackets:

- *wake* $w$ [4]: above its copy region, a cell of a sub-line that is more than $w$ cells behind the return
  chain and to the right of the seed of the copy is quiescent;
- *static general* $g$ [2]: the first cell is `G` from time $g$ on;
- *periodic depth rows* $(P,c)$ [(3, 2)]: $C_\infty(t,i)=C_\infty(t-P,i-P)$ whenever $t-P\ge 2j+c$, where
  $j=t+1-i$ is the depth behind the front.

Calibration on Mazoyer's table ($N=36$, lengths from 3): satisfiable for $(a,s_0,m_{\min})=(2,2,3)$, wake 4,
static general 2, $(P,c)=(3,2)$; unsatisfiable for $s_0=1$, for $a=1$, for wake $\le 3$, for $c\le 1$.

**Five states** (lengths from 2, $(a,s_0,m_{\min})=(2,2,3)$):

| conditions | result |
|---|---|
| copies, wake 4, static general 2, periodic (3, 2) | satisfiable for $N\le 11$ (`mcopy.py` $N=10$: 51 s; `mcopy_inc.py` $N=10$: 42 s, $N=11$: 15 min); the rules found synchronize exactly 2..10 and 2..11 (`rules/strict_2-10.txt`, `rules/strict_2-11.txt`) |
| the same, $N\ge 12$ | unknown |
| copies only; copies and wake 4 | satisfiable for $N\le 9$; $N\ge 10$ unknown |

`mdfs.c` cannot exhaust these classes: the lines 5 to 7, which are too short to contain a copy, admit millions
of partial rules (with all conditions: 170, 312,182 and 4,003,463 partial rules pass the lines 5, 6 and 7 in
the first 8·10⁹ nodes, 61,234 pass the line 8, 2,447 the line 9 and none the line 10).

## 3. Rules whose diagrams decode to Mazoyer's diagrams

**Class.** A five-state rule with diagrams $c_n$ and a map $\varphi$ such that, for every line
$n_0\le n\le N$, every time $t<2n-2$ and every cell $i$, the state of Mazoyer's diagram is
$M_n(t,i)=\varphi(\text{window of } c_n \text{ around } (t,i))$; the five-state rule must fire at $2n-2$.

| window of the decoder | extra condition | lines | result |
|---|---|---|---|
| $(c(t,i),c(t,i+1))$, $(c(t,i-1),c(t,i))$ or $(c(t-1,i),c(t,i))$ | none | 3..8, 3..10 | UNSAT (< 2 s each) |
| radius 1 | none | 3..8 | satisfiable; the rule found synchronizes 2..8 only |
| radius 1 | none | 3..9, ..., 3..12 | unknown (28 min) |
| radius 1, ..., 5 | `L` and `G` cells preserved ($c=$ `L` iff $M=$ `L`, $c=$ `G` iff $M=$ `G`) | 3..N for $N\le 24$; also only $n_0..24$ for $n_0=7,10,13,16$; $10..30$ | UNSAT, exhaustive (`decdfs.c`, at most 17,358 nodes; no partial rule passes the line 6, and for $n_0\ge 7$ none completes the half-line); `msim.py` agrees for radius 1 |
| radius 1 | `L` cells preserved | 3..8, 3..10, 3..12, 6..12, 8..14, 10..16, 12..18, 14..20 | UNSAT (< 3 s each) |
| radius 1 | $M=$ `L` implies $c=$ `L` | 3..10, 8..16 | UNSAT (36 s, 7 s) |
| radius 1 | $c=$ `L` implies $M=$ `L` | 3..10 | UNSAT (41 s) |
| radius 1 | $c=$ `L` implies $M=$ `L` | 8..16 | unknown (100 s) |
| radius 1 | `G` cells preserved | 3..10, 8..16 | UNSAT (< 1 s) |
| no decoder | `L` cells preserved (same quiescent cells as Mazoyer's solution) | 3..8 | satisfiable |
| no decoder | `L` cells preserved | 3..10 | UNSAT (85 s) |

## 4. Rules that are local images of Mazoyer's solution

**Class.** A map $\pi$ from windows of Mazoyer's diagrams to $\{$`L`, `G`, `A`, `B`$\}$ such that
$c_n(t,i)=\pi(\text{window of } M_n \text{ around } (t,i))$ are the diagrams of one five-state rule that
starts from `G L ... L` and fires at $2n-2$. Every such rule would be a five-state minimal-time solution for
all lengths that Mazoyer's rule synchronizes, because the conditions only involve the finitely many local
configurations of Mazoyer's diagrams. They were collected from the lines 3..80.

| window of $\pi$ | windows | constraints | result |
|---|---|---|---|
| the cell (two states merged) | 5 | 117 | UNSAT |
| radius 1 | 117 | 649 | UNSAT (3 s) |
| the cell and the same cell one step earlier | 23 | 254 | UNSAT (3 s) |
| the cell and radius 1 one step earlier | 116 | 647 | UNSAT (29 s) |
| radius 1 and the same cell one step earlier | 144 | 744 | UNSAT (3 s) |
| radius 1 and radius 1 one step earlier | 254 | 1,102 | UNSAT (73 s) |
| radius 2 | 649 | 2,185 | UNSAT (Kissat, 1,171 s; again 1,050 s with a DRAT proof of 554 MB that drat-trim verifies) |
| the cell, with $\pi$ depending on $t \bmod 2$, on $i \bmod 2$, on both, on $t\bmod 3$, on $(t+i)\bmod 3$, or on $t\bmod 6$ (lines 3..60) | 10 to 30 | 179 to 527 | UNSAT (< 1 s each) |
| radius 1, with $\pi$ depending on $t\bmod 2$ or on $i\bmod 2$ (lines 3..60) | 179, 225 | 799, 1,127 | UNSAT (5 s, 6 s) |

Controls: with six states and the single-cell window the formula is satisfiable and returns Mazoyer's rule.

Certificates. For every row of the table and for the variants with residues of $t$ and $i$ below, the
refutation is certified: for radius 2 by Kissat's DRAT proof and drat-trim, for the others by CaDiCaL 3.0.1 with
an LRAT proof that `lrat-check` verifies; `CERTIFICATES.txt`
lists the commands, the SHA-256 digests of the formulas and of the proofs, and the proof sizes (0.2 MB to
283 MB). The formulas are written deterministically by `facsat.py ... --cnf FILE`.

Variants. Restricted to the lines 10..90, 20..90 or 40..90 the radius-1 formula is still unsatisfiable (7 s
each), so the short lines are not the obstruction. With six states, a radius-1 image that maps at most
$B$ of the 117 windows to the fifth working state does not exist for $B\le 12$ (UNSAT, at most 17 s each;
$B=16$ unknown after 100 s): the extra state of Mazoyer's solution is not confined to a few local situations.

## 5. Other classes

All without copies; "incremental" is `mcopy_inc.py`, which reports the largest $N$ reached, not an upper limit.

| class | result |
|---|---|
| static general: the first cell is `G` from time 1 (or 2) on | satisfiable for 2..12 (incremental, 9 min); $N=13$ not decided (run stopped) |
| (B3) of the paper in the strong reading: exactly `GGG`, `*GG`, `GG*` give `F` (the line fires from the row `G...G`) | satisfiable for 2..11 (14 s) |
| (B3) and (B4) ($\delta(G,v,G)=G$) | satisfiable for 2..12 (29 s) |
| (B3) and (B1) weak ($\delta(x,G,y)=G$ for working $x,y$, not both `G`); (B3), (B1) and (B4) | satisfiable for 2..11 (7 s; 12 s) |
| walls of Mazoyer's solution: a cell is `G` wherever Mazoyer's diagram has `G` at $t$ and $t+1$ (`msim.py --keepW --nodec`, lines 3..N) | satisfiable for 3..11 (17 s; incremental 10 s) |
| walls of Mazoyer's solution, and quiescent wherever Mazoyer's diagram is quiescent | 3..9 satisfiable; 3..10 and 3..11 UNSAT (< 1 s) |
| quiescent wherever Mazoyer's diagram is quiescent | 3..10 satisfiable (29 s); 3..11 unknown |

Image solutions, that is (B2) of the paper alone, $\delta(I(z),I(y),I(x))=I(\delta(x,y,z))$ for an involution
$I$ of the states: satisfiable for 2..11 with $I$ the identity (Kissat, 345 s), and for 2..9 with $I=(A\,B)$
(61 s) and $I=(L\,B)$ (37 s); longer lengths unknown. (Proposition 6.6 of the paper excludes them only together
with (B1), (B3) and (B4).)

Neighbourhoods of the five rules of Proposition 6.3 (`near.py`, plain formula, half-line to the anti-diagonal
28): no rule within Hamming distance 8 of $\delta_{14}$, $\delta_{14}^b$, ..., $\delta_{14}^e$ synchronizes
2..15 (UNSAT, at most 263 s each).

The strict class of Section 2 has a rule for 2..11 (`rules/strict_2-11.txt`, incremental, 15 min); it fires
early on the line 16, and so do all rules found so far in these classes on some line shortly after $N$: with
$N\le 12$ the structure does not yet force a rule that generalizes.

**Four states for comparison (16 November; solver answers on strict formulas, each in less than a second).**
For four states every class is decided at once, and the exact maxima show which conditions cost length. The
last column recalls what is known for five states.

| class | four states: largest $N$ with a rule for $2,\dots,N$ | five states |
|---|---|---|
| no class | 8 (the value $N_4=8$ of the paper) | at least 14 |
| (B3) strong; (B3) weak; first cell `G` from time 1 on | 8; 8; 8 | at least 14 (the rules of Theorem 6.4 are in these classes) |
| (B4) | 7 | at least 12 with (B3) |
| (B2) for the identity, with or without the borders | 6 | at least 11 |
| (B1) weak, with or without (B3) | 6 | at least 14 (the same rules) |
| (B1) weak and (B2) for the identity without borders | 5 | 12 or 13 (Proposition 7.3) |
| (B1) strong | 4 | 14 or 15 (Theorem 6.4) |

So with four states a stable general costs half of the length, and firing from generals or a static first
cell costs nothing. `ladder.py K N R` asks for rules with (B3) in which at most $R$ of the entries
$\delta(x,G,y)$ that (B1) fixes differ from $G$ (12 entries for four states, 21 for five). For four states the
largest $N$ is 4 for $R=0$, 6 for $R=1,2,3$, 7 for $R=4$ and 8 for $R\ge5$. With chosen exceptions
(`--free`): a general that may change when its left neighbour is quiescent ($\delta(L,G,y)$ free) gives 5, the
same on the right ($\delta(x,G,L)$ free) gives 5, both together give 8, and so do the five entries
$\delta(L,G,y)$ and $\delta(A,G,L)$; the border entries alone (the weak reading) give 6. In Mazoyer's six-state
solution the general also changes only next to a quiescent cell, apart from two entries: it leaves `G` in the
neighbourhoods $(x,G,L)$ and in $(C,G,\ast)$, $(C,G,G)$. For five states the class $R=0$ already reaches 14;
the classes with a few exceptions are being searched for a rule beyond 14 (Section 9).

`enum_rules.py K N` lists all rules for the lines $2,\dots,N$ up to the transitions that are not used in these
lines (each model of the strict formula is excluded by a clause on its used transitions). For four states
there are 536 rules for $2,\dots,7$ and exactly 27 for $2,\dots,8$. Of the 27, 26 fire from the row of generals
with the neighbourhoods $GGG$, $\ast GG$, $GG\ast$ only; the first cell is constantly `G` in 5 of them and
alternates between `G` and `A` from time 1 on in 21; and 5 to 9 of the entries that (B1) fixes are not `G`.
With (B1) in the strong reading there is exactly one four-state rule for $2,\dots,4$, and with (B1) in the weak
reading there are 19 for $2,\dots,6$. So the number of rules falls quickly just below the maximum (536, 27, 0
for $N=7,8,9$), as it does for five states in the class of Theorem 6.4 (three rules at $N=14$).

**Enumeration without a solver (16 November).** `fsdfs.c` is a second, independent way to the same numbers: it
simulates the lines $n_0,n_0+1,\dots$ in this order, cell by cell, and branches over the admissible values of a
transition at the moment when a line first needs it; a branch dies when a cell fires before the time $2n-2$ or
does not fire at that time. Each partial rule (the transitions that the lines $n_0,\dots,n$ use) is reached
exactly once, so the program counts the rules for $n_0,\dots,n$ up to unused transitions, for every $n$ at
once. It shares no code with the encoders and uses no solver. For four states the search is complete in
seconds ($3\cdot10^7$ nodes per second):

| four states, lines $n_0,\dots,n$ | $n=n_0$ | $3$ | $4$ | $5$ | $6$ | $7$ | $8$ | $9$ | nodes |
|---|---|---|---|---|---|---|---|---|---|
| $n_0=2$ | 7 | 664 | 96,169 | 828,670 | 64,299 | 536 | 27 | 0 | $1.17\cdot10^8$ |
| $n_0=3$ | 1566 | | 480,682 | 4,382,062 | 396,718 | 2671 | 42 | 0 | $6.98\cdot10^8$ |
| $n_0=4$ | 1,108,449 | | | 49,676,762 | 4,316,958 | 51,872 | 399 | 0 | $9.44\cdot10^9$ |
| $n_0=5$ | | | | | | | | 36 | $4.31\cdot10^{10}$ (with backjumping, `fsdfs2.c`); none for $5,\dots,10$ |

The row $n_0=2$ repeats $N_4=8$ and the numbers 536 and 27 of `enum_rules.py`. The other rows are new here
(exhaustive enumeration; not certified by a proof checker): **no four-state rule synchronizes all lines of
lengths $3,\dots,9$, and none synchronizes all lines $4,\dots,9$; but 36 four-state rules synchronize the
lines $5,\dots,9$, and none synchronizes $5,\dots,10$.** So if $N_4(n_0)$ denotes the largest $N$ with a
four-state rule for $n_0,\dots,N$, then $N_4(2)=N_4(3)=N_4(4)=8$ and $N_4(5)=9$: the bound 8 depends on the
lines 2, 3 and 4, and the number of consecutive lengths that one rule can serve falls from 7 to 6, 5 and 5. One
of the 36 rules is `rules/k4_lines_5-9.txt` (40 transitions; by simulation it synchronizes the lengths 5 to 9
and none of the lengths 2, 3 and $10,\dots,40$, and the line of length 4 needs a transition that is not among
the 40); the general walks to the right as a single `G`, and the line fires from
the row `G A ... A` one step after the row of generals. Kissat refutes the strict formula of the lines
$3,\dots,9$ as well (127 s) and gives no answer for $4,\dots,9$, $5,\dots,9$ or $5,\dots,10$ in 150 s each.
With a class the same question has smaller answers (`fsdfs2 4 16 CLASS -nmin n0`, all trees complete): for
$n_0=2,3,4,5,6$ the largest $N$ is $4,4,5,6,6$ with (B1) strong (with or without (B3) strong) and $6,6,7,7,7$
with (B1) weak; for $n_0=2,3,4$ it is $8,8,8$ with (B3) strong and $7,8,8$ with (B4). In particular **no
four-state rule with a stable general synchronizes both lines 6 and 7.** For five states the corresponding
statement fails for pairs: Kissat finds rules with a stable general for the two lines $7,8$, for $11,12$ and for
$15,16$ (0.2 s, 2 s, 36 s), and gives no answer in 400 s for the three lines $14,15,16$, for $13,\dots,16$ and
for $12,\dots,16$. With the class options the enumeration also repeats the
four-state column of the table above, with the numbers of rules: (B1) strong 1 rule for $2,\dots,4$ and none
for $2,\dots,5$; (B1) weak 19 rules for $2,\dots,6$, none for $2,\dots,7$ (the same with (B3) weak in addition);
(B3) strong and (B3) weak 26 rules each for $2,\dots,8$, none for $2,\dots,9$; (B4) 86 rules for $2,\dots,7$, none for
$2,\dots,8$; (B3) strong with (B4) 2 rules for $2,\dots,7$.

For five states the two programs agree where both can count: without the naming rule for $A$ and $B$, (B1)
strong with (B3) has 20 rules for $2,3$ and 6062 for $2,3,4$, and (B3) alone has 98 rules for $2,3$, by
`enum_rules.py 5 N --b3 [--b1s]` and by `fsdfs 5 N -b3s [-b1s] -nosym`. Beyond that the enumeration is not
feasible: with the naming rule the class of Theorem 6.4 has 10, 3031 and 4,094,650 rules for $2,\dots,3$,
$2,\dots,4$ and $2,\dots,5$. Random descents (`-knuth`, 3 million descents per run) estimate the tree for
$N=15$ at $6\cdot10^{12}$ and $1.1\cdot10^{13}$ nodes (two runs) for this class with all the pruning of
Lemmas 6.1 to 6.3, at $3\cdot10^{20}$ for (B3) strong alone and at $3\cdot10^{22}$ for the unrestricted problem
(both with the front and return-chain pruning). These are estimates: in the four-state case, where the true
size is $1.17\cdot10^8$, four runs of 2 million descents gave between $4.6\cdot10^7$ and $1.3\cdot10^8$. The tree searches of
Sections 6 and 7 close the first of these classes with $7\cdot10^4$ solver calls because a solver call excludes
all completions of a half-line at once; the enumeration visits them one by one.

**A sub-class of Theorem 6.4 by both methods (16 November).** A part of the class of Theorem 6.4 is small enough
for the enumeration and large enough to test the whole tree search. Name the auxiliary states so that
$\delta(G,L,L)=A$, and split the class by the reaction of the last cell to the front,
$(\delta(A,L,\ast),\delta(B,L,\ast))$; random descents estimate the 16 parts at $10^{10}$ to $2\cdot10^{13}$
nodes for $N=15$ (three of them die at once), about $6\cdot10^{13}$ in all. The part
$\delta(A,L,\ast)=L$, $\delta(B,L,\ast)=G$ was done completely, in three ways:

- `fsdfs 5 16 -b1s -b3s -prefire -gap -set "AL*=L,BL*=G" -max` (no pruning that depends on $N$; $7.26\cdot10^{10}$
  nodes, 4955 s): the numbers of rules for $2,\dots,n$ are 1, 1, 58, 18,131, 7,896,760, 272,536,715, 167,602,723,
  7,434,219, 96,868, 896, 4, 0 for $n=2,\dots,13$. So this part has exactly four rules for $2,\dots,12$ and none
  for $2,\dots,13$.
- `fsdfs2 5 12 ... -front -chain -wall -keepsym -print 10` (backjumping and the pruning of Lemmas 6.1 to 6.3 for
  $N=12$; $5.0\cdot10^9$ nodes, 810 s): four rules, with 65, 68, 68 and 68 transitions. Each satisfies (B1) and
  synchronizes exactly the lengths $2,\dots,12$ (simulation); one is `rules/stable_generals_sub_LG_2-12.txt`.
- The tree search of Section 6 with the incremental solver, `gsat.py 5 N --b1s --b3 --wimp --strict --noghws
  --gstatic 1 --set "AL*=L,BL*=G"`: for $N=13$ every node is closed (4838 nodes, 2070 s); for $N=12$ with
  `--all` (the search continues below satisfiable nodes down to complete half-lines) it finds 7 models (4864
  nodes, 2039 s), and on the transitions that the lines $2,\dots,12$ use they are exactly the four rules of the
  enumeration.

So on this part the encoder, the lemma clauses of the strict formula, the branching of the tree and the
enumeration agree in every number that both produce. Kissat, on the strict formula of this part as a whole,
finds a rule for $2,\dots,11$ in 23 s and gives no answer for $2,\dots,12$ in 400 s. The part
$\delta(A,L,\ast)=A$, $\delta(B,L,\ast)=G$, which contains the three rules of Theorem 6.4, is estimated at
$3\cdot10^{12}$ nodes and is running; the whole class would need about 15 processor-days with backjumping.

## 6. Stable generals

In this section (B1) is read in the strong reading of the paper,
$$\delta(x,G,y)=G\quad\text{unless }x,y\in\{G,\ast\},$$
and $\delta$ may have any number of states; $W$ is the set of working states and $W'=W\setminus\{G\}$.
Lemmas 6.1 to 6.3 are proved here by hand; everything after them is a computer result with the status stated.

**Lemma 6.1 (a stable general fires only from three generals).** Let $\delta$ satisfy (B1).

1. If $\delta$ synchronizes the lines of lengths 2 and 3 at the times 2 and 4, then $\delta(G,L,\ast)=G$ and
   $\delta(\ast,G,G)=\delta(G,G,\ast)=\delta(G,G,G)=F$.
2. If moreover $\delta$ synchronizes the line of length $n\ge2$ at time $2n-2$, then in this line
   (a) the first cell is in state $G$ at all times $t\le2n-3$;
   (b) every cell is in state $G$ at time $2n-3$;
   (c) at no time $t\le2n-4$ are three adjacent positions in $\{G,\ast\}$, where the positions $0$ and $n+1$
       are the borders;
   (d) a cell in state $G$ at a time $t\le2n-4$ is in state $G$ at time $t+1$.

*Proof.* 1. In the line of length 2, $C_2(1,1)=\delta(\ast,G,L)=G$ by (B1), and $F=C_2(2,1)=\delta(\ast,G,x)$
with $x=C_2(1,2)=\delta(G,L,\ast)\in W$. By (B1) this value is $G$ unless $x=G$. Hence $x=G$,
$\delta(\ast,G,G)=F$, and $F=C_2(2,2)=\delta(G,G,\ast)$. In the line of length 3 the first cell stays in state
$G$ as long as the second cell is not in state $G$, by (B1), and it is in state $F$ one step after the second
cell is in state $G$; so the second cell is in state $G$ at time 3. Then $F=C_3(4,2)=\delta(G,G,z)$ with
$z=C_3(3,3)\in W$, and (B1) gives $z=G$ and $\delta(G,G,G)=F$.

2. (c) If three adjacent positions are in $\{G,\ast\}$ at time $t$, the middle one is a cell in state $G$
(two borders are not adjacent to the same cell for $n\ge2$), and it is in state $F$ at time $t+1$ by part 1; so
$t+1\ge2n-2$. (d) By (B1) and (c). (a) The first cell is in state $G$ at time 0; by (d) it stays so up to time
$2n-3$. (b) By (a), $F=C_n(2n-2,1)=\delta(\ast,G,y)$ with $y=C_n(2n-3,2)$, so $y=G$ by (B1). If the cell $i<n$
is in state $G$ at time $2n-3$, then $F=C_n(2n-2,i)=\delta(x,G,z)$ with $z=C_n(2n-3,i+1)\in W$, and (B1)
gives $z=G$. $\square$

So a rule with a stable general fires, on every line that it synchronizes, from the row $G^n$ and from the
neighbourhoods $GGG$, $\ast GG$, $GG\ast$ only. Condition (B3) of the paper need not be assumed: its weak
reading is part 1, and its strong reading holds on all transitions that are used; a transition that is not
used can be redefined (for instance to its middle state, which also preserves (B2)).

**Lemma 6.2 (walls).** Let $\delta$ satisfy (B1) and synchronize the lines of lengths $2,\dots,N$ in minimal
time, $N\ge3$. Then $C_\infty(t,1)=G$ for $t\le2N-3$, and $C_\infty(t,i)\ne G$ for all $i\ge2$ and $t$ with
$t+i\le2N-4$. In particular, on the half-line of a minimal-time solution with (B1) the first cell is always
in state $G$ and no other cell ever is.

*Proof.* The first claim is Lemma 6.1 (a) and the agreement lemma (Lemma 2.2 of the paper). Let $p\ge2$ and
$t_w+p\le2N-4$, and suppose $C_\infty(t_w,p)=G$. Put $n=N-1$. The cells $(t_w,i)$, $i\le p$, lie on
anti-diagonals $\le2n-2$, so the lines of lengths $n$ and $n+1$ agree with the half-line there. In both lines
the cell $p$ is in state $G$ from time $t_w$ to time $2n-3$, by Lemma 6.1 (d). Hence the cells $1,\dots,p-1$
have the same states in both lines at time $t_w$ and the same constant right neighbour $G$ at the times
$t_w,\dots,2n-3$, so they have the same states at all times $t_w\le t\le2n-2$. Then
$C_{n+1}(2n-2,1)=C_n(2n-2,1)=F$, although $2n-2<2(n+1)-2$. $\square$

So a general is a wall that no information crosses, a wall other than the first cell can only appear after
the echo of the right end has passed, and the half-line is a diagram over $W'$ next to a constant $G$.

**Lemma 6.2' (walls, weak reading).** Let $\delta$ synchronize the lines of lengths $2,\dots,N$, $N\ge3$, and
suppose that $\delta(x,G,y)=G$ for all working states $x,y$ that are not both $G$ (the weak reading of (B1))
and that $\delta(G,G,G)=F$. Then $C_\infty(t,i)\ne G$ for all $i\ge2$ and $t$ with $t+i\le2N-4$.

*Proof.* As for Lemma 6.2, with $n=N-1$. A cell $p\ge2$ of the half-line in state $G$ at a time $t_w$ with
$t_w+p\le2n-2$ satisfies $t_w\ge p-1$, hence $p\le n-1$: in the lines of lengths $n$ and $n+1$ both its
neighbours are cells. In either line it keeps the state $G$ up to time $2n-3$: by the hypothesis unless both
neighbours are in state $G$, and then it would fire before the firing time. So the cells $1,\dots,p-1$ evolve
in the same way in both lines up to time $2n-2$, and the first cell would fire at the same time in both.
$\square$

In the weak reading the first and the last cell are not protected, so Lemma 6.1 (2) does not hold as stated;
but the half-line is again a diagram over $W'$ beyond its first cell (`--noghw`). This covers the weak reading
of the paper and the conditions as Yunès states them (Section 7).

**Lemma 6.3 (gaps).** Let $\delta$ satisfy (B1) and synchronize the lines of lengths 2, 3 and $n$ in minimal
time. Call the cells of the line $n$ in state $G$ and the two borders its *barriers*. If at a time $t\le2n-4$
two barriers at distance $\ell+1\ge2$ have no barrier between them, then
$$2n-3-t\le M(\ell),\qquad M(1)=|W'|,\quad M(\ell)=|W'|^{\ell}+M(\ell-1).$$
For five states $M(1),M(2),M(3)=3,12,39$.

*Proof.* Barriers persist up to time $2n-3$ (Lemma 6.1 (d)), so the $\ell$ cells of the gap are driven only by
themselves and two constant neighbours. As long as none of them is in state $G$ their configuration lies in
$W'^{\ell}$ and cannot repeat: after a repetition it would be periodic for ever, and the cells would never be
in state $G$, contrary to Lemma 6.1 (b). So there is $m\le|W'|^{\ell}$ such that some cell of the gap is in
state $G$ at time $t+m$. If $t+m=2n-3$ we are done. Otherwise $t+m\le2n-4$, and by Lemma 6.1 (c) some cell
of the gap is not in state $G$ at time $t+m$ (for $\ell=1$ this case does not occur); it lies in a gap of some
length $1\le\ell'<\ell$ at time $t+m$, and induction gives $2n-3-(t+m)\le M(\ell')\le M(\ell-1)$. $\square$

Equivalently: at a time $t$ with $2n-3-t>M(\ell)$ no two barriers are at a distance $d$ with $2\le
d\le\ell+1$. For the right border this sharpens the right-band lemma of the paper (Lemma 3.6) in this class:
a general at distance $d$ from the right border can only appear in the last $M(d)$ steps. The rules found
below violate exactly this on the lines beyond those they synchronize: on these lines two generals at
distance 2 appear a few steps after the reflection, one step before three adjacent generals.

**The front and the 21 cases (five states).** By Lemma 6.2 and the return-chain lemma the front cells
$f_t=C_\infty(t,t+1)$, $t\ge1$, are in $\{A,B\}$; $f_1=A$ after renaming, and $f_{t+1}=\delta(f_t,L,L)$. So
the front is $A\,A\,A\cdots$ (type a), $A\,B\,B\cdots$ (type b) or $A\,B\,A\,B\cdots$ (type c). The right end
at time $n-1$ is $\delta(f_{n-1},L,\ast)\ne f_n$ (return chain). This gives $3+9+9=21$ cases, named by the
front type and the values of $\delta(A,L,\ast)$ and, for the types b and c, $\delta(B,L,\ast)$.

**Formulas.** `mcopy.py 5 N --nocopy --b1s --b3 --nogh --wimp [--wgap] [--set ...]`: the lines $2,\dots,N$,
(B1), the normalization of Lemma 6.1 (`--b3`: no other neighbourhood gives `F`), and as redundant clauses the
conclusions of Lemma 6.1 (`--wimp`), Lemma 6.2 (`--nogh`) and Lemma 6.3 (`--wgap`). Without `--strict` the
clauses of `--nogh` reach the anti-diagonal $2N-1$, where Lemma 6.2 uses the lines up to $N+2$; so a
refutation at $N$ says that no rule of the class synchronizes all lines $2,\dots,N+2$ (Section 1).

**Results (solver answers; the rules are checked by simulation).**

| formula | result |
|---|---|
| the class, lines $2,\dots,N$ | rule for 2..13 (`rules/stable_generals_2-13.txt`, Kissat, 428 s); $N=14$: Kissat stopped after 58 min without an answer; the tree search below found a rule for 2..14 (`rules/stable_generals_2-14.txt`) |
| the 21 cases, `mcopy_inc.py`, 900 s each (stopped after five cases) | case a with $\delta(A,L,\ast)=L$: refuted at 12 (236 s); case a with $G$ and case a with $B$: rules for 2..12 (the rule for 2..13 is in case a with $B$); case b with $\delta(A,L,\ast)=L$ and $\delta(B,L,\ast)\in\{L,A\}$: refuted at 3; case b with $L$, $G$: rule for 2..12 |
| the 126 half-lines up to the anti-diagonal 6 as cases (`germw 6 40`, `germscan.py`, 20,000 conflicts per call) | 5 refuted at $N\le11$; in the other 121 a rule for 2..9 (10 cases), 2..10 (73), 2..11 (35) or 2..12 (3) is found before the budget ends |
| with the conditions of Lemmas 6.1 and 6.3 on the first 10 rows after the reflection of the lines up to 40 (`--early 40 10 --wgap`) | rule for 2..11 (incremental, 300 s; it has three adjacent generals on the lines $12,\dots,50$ between 10 and 18 steps after the reflection, just after the rows constrained); $N=12$ not decided (run stopped) |
| lines $2,\dots,N$ and the complete line 20 (`--extra 20`) | rule for 2..9 and 20 (incremental, 451 s); its half-line is periodic with period 4 in time and space, which fits the length 20 |
| lines 2, 19, 22 complete, and PUMP$(n,n')$ for $n<n'\le22$ (`mcopy.py 5 2 --extra 19,22 --pump 22`) | not decided: no answer from the incremental solver in 8 minutes; the Kissat run was stopped without an answer |

The rule for 2..13 synchronizes exactly the lengths 2..13 among 2..80. On its half-line the cells 2, 3, 4 are
constant ($A$, $B$, $L$) from time 5 on and the cells beyond are in $\{L,A\}$ (checked for $t<380$), where the
table is the elementary rule 62; the echo of the right end is a signal in state $B$. So the class contains the
same kind of rule as the unrestricted problem (compare $\delta_{14}$ of the paper, elementary rule 22): a
chaotic half-line over two states that happens to fit all short lengths. Such rules exist in almost every
case of the case analysis, which is why splitting into cases does not help at these lengths.

Half-lines of low complexity. `germw M NP -k K` lists the half-lines of the class (over $\{L,A,B\}$, first
cell $G$) below the anti-diagonal $M$ that use at most $K$ transitions, with the front and pumping conditions.
For $M=78$, $NP=40$: none with $K\le12$, and 5, 41, 201, 956, 4004, 16856 with exactly $13,\dots,18$
transitions; the count grows by a factor of about 4.2 per transition. Of the 35 neighbourhoods $(G,y,z)$ and
$(x,y,z)\ne(L,L,L)$ over $\{L,A,B\}$ that `germw` counts, a half-line of the class uses at most 34: a wall
that is not next to a barrier is created from a neighbourhood in $\{L,A,B\}^3$, which by Lemma 6.2 never
occurs on the half-line, and every line of length $n\ge5$ has such a wall among its cells 3, 4, 5 (otherwise
the cells 4, 5 and the cell 6 or the right border would be three adjacent barriers before time $2n-3$). So
listing the half-lines by complexity cannot settle the class with these programs: it would have to reach 34.

**The search over the half-line.** As one formula the class is hard for the solvers (lines $2,\dots,14$: no
answer from Kissat in 58 minutes), but it is easy once the half-line is fixed: `germscan.py` refutes each of the
1203 half-lines of the class with at most 16 transitions (`germw 78 40 -k 16`) at some $N\le13$, in 9 seconds
for all of them. `germsat.py` uses this. It walks the tree of half-lines: the transitions of the half-line are
fixed one at a time, in the order in which the anti-diagonals need them, with the values $L,A,B$ (the front
never $L$); at every node the formula for the lines $2,\dots,N$ is solved incrementally under the assumption
of the transitions fixed so far, with a budget of 3000 conflicts. A node that the solver refutes is closed, a
node with a model ends the search with a rule, and a node where the budget runs out is branched on the next
transition. The branching is complete: by Lemma 6.2 and the clauses of the formula a half-line cell $i\ge2$ is
in $\{L,A,B\}$, and $\delta(G,L,L)=A$ after renaming. So if every node is closed, the formula is
unsatisfiable. The tree is cut at depth 7 into 341 subtrees (and 36 nodes closed above them), which run as
separate jobs.

Checks. The same program for four states and without the class (`gsat.py 4 9`) closes every node in about 20 s
(212 nodes with the default budget of 3000 conflicts, 2877 with `--budget 300`), and `gsat.py 4 8 --strict` finds rules for $2,\dots,8$, in accordance with $N_4=8$. Rules of the
class that were found without the redundant clauses satisfy the formula with them (`mcopy.py ... --fix`):
the rule for 2..13 at $N=11,12,13$, and four other rules at $N=10$ or 11.

**A rule with a stable general for 2..14.** The search for the lines $2,\dots,14$ found one satisfiable node,
in the subtree 309 (11 transitions of the half-line fixed):
`GLL=A,GAL=B,ALL=B,GBB=A,BBL=L,BLL=A,ALA=B,LAL=L,BLB=L,LBL=B,LLB=L`. The rule extracted from it,
`rules/stable_generals_2-14.txt` (SHA-256 `dec76662...0a359415`), satisfies (B1) on its whole table, has
exactly the neighbourhoods $GGG$, $\ast GG$, $GG\ast$ with image $F$, and synchronizes the lines
$2,\dots,14$ and no other length up to 120 (direct simulation). So the stable-general class reaches the same
length 14 as the unrestricted rules $\delta_{14},\dots$ of the paper. Its front is of type c ($A\,B\,A\,B\cdots$),
and its half-line is eventually periodic: the cells 2 to 6 have period 2 in time from time 6 on, and every cell
$i\ge7$ is constant from time $i-1$ on ($B$ for odd $i$, $A$ for even $i$; checked for $t<150$). The half-line
uses 26 neighbourhoods, the lines $2,\dots,14$ use 78. On every line $15\le n\le120$ the last cell is
in state $F$ too early (2 steps for $n=15,16$, 26 steps for $n=40$, 106 steps for $n=120$). A half-line of this kind cannot
belong to a solution (Theorem 4.2 of the paper); the rule shows that the lines up to 14 do not exclude it.

**Theorem 6.4 (computer-assisted, certified).** No five-state rule with a stable general, that is with (B1),
synchronizes all lines of lengths $2,\dots,16$ in minimal time. The rule `rules/stable_generals_2-14.txt`
satisfies (B1) and synchronizes all lines of lengths $2,\dots,14$.

So the largest $N$ for which some five-state rule with a stable general synchronizes $2,\dots,N$ is 14 or 15.

*Proof.* Let $\delta$ be a five-state rule with (B1) that synchronizes the lines $2,\dots,16$. By Lemma 6.1 the
only neighbourhoods with image $F$ that occur in these lines are $GGG$, $\ast GG$ and $GG\ast$; every other
neighbourhood with image $F$ is given its middle state as image, which changes neither the lines nor (B1). By
Lemma 2.4 of the paper $\delta(G,L,L)\ne L$, and by Lemma 6.2 it is not $G$; the names are chosen such that
$\delta(G,L,L)=A$.

The formula $F_{14}$ is the formula of `certtree.py 14 ... --pump 14`, that is `Model(5, 14, b1s, b3, nogh, wimp,
wgap, front1, pump=14)` of `mcopy.py` without symmetry clauses: 3465 variables, 324,753 clauses, SHA-256 of
the clause lines `67957a4ce7230559cf9fc2b463d66096be3056b00b8a01001465fd2ef260f057`. Its clauses say:

1. the cells of the half-line up to the anti-diagonal 27 and the cells of the lines $2,\dots,14$ are working
   states that follow $\delta$, and every cell of the line $n\le14$ has a neighbourhood with image $F$ at time
   $2n-3$ (the half-line cells agree with the line 15, at times before 28);
2. (B1), and exactly $GGG$, $\ast GG$, $GG\ast$ have the image $F$;
3. the return chain of every line $n\le14$ differs from the half-line (Lemma 2.4 of the paper for the lines
   $n$ and $n+1\le15$);
4. the front cells $(t,t+1)$, $t\le13$, are not $L$ (Lemma 2.4 for the lines up to 16);
5. the first cell of the half-line is $G$ and no other cell of the half-line up to the anti-diagonal 27 is
   (Lemma 6.2 with $N=16$, which reaches the anti-diagonal 28);
6. the conclusions of Lemma 6.1 and of Lemma 6.3 for the lines $n\le14$;
7. PUMP$(n,n')$ for $4\le n<n'\le14$ (Lemma 3.3 of the paper for the lines $n$ and $n'$).

So $\delta$ with its diagrams satisfies $F_{14}$. A *node* of the search tree is a set of transitions of the
half-line, fixed in the order in which the anti-diagonals $3,\dots,27$ need them; the root is
$\{\delta(G,L,L)=A\}$, and the children of a node give the next transition that the half-line needs the values
$L$, $A$, $B$, except $L$ if the cell is a front cell. By the items 4 and 5 the half-line of $\delta$ is a path
from the root through this tree.

| nodes | closed for | number | CaDiCaL time | LRAT proofs |
|---|---|---|---|---|
| above depth 7 (`g14_parts_top.txt`) | $F_{14}$ | 36 | < 1 s | 0.02 GB |
| subtrees 1 to 167 (`g14_parts_1-167.txt.gz`) | $F_{14}$ | 17,196 | 35,384 s | 178.1 GB |
| subtrees 168 to 341 (`g14_parts_168-341.txt.gz`) | $F_{14}$ | 27,280 | 57,808 s | 260.5 GB |
| nodes with a complete half-line that need more than 4 s (`g14_parts_open.txt`) | $F_{14}$ | 4 | 15 s | 0.07 GB |
| the node $\gamma^\ast$ at which $F_{14}$ is satisfiable (`g15s_sat_strict.txt`) | $S_{15}$ | 1 | 12 s | 0.08 GB |

For each of the 44,516 nodes $\gamma$ of the first four rows, CaDiCaL 3.0.1 refutes $F_{14}$ with the units
of $\gamma$, with an LRAT proof that `lrat-check` verified (answer `UNSATISFIABLE` and empty last lemma
required; the proofs were deleted after the check, the lists record the SHA-256 digests of every cube formula
and proof). At the node $\gamma^\ast$ of the preceding paragraph $F_{14}$ is satisfiable. For it the formula
$S_{15}$ is used: the lines $2,\dots,15$ are synchronized, (B1), and the 11 transitions of $\gamma^\ast$
(`mcopy.py 5 15 --nocopy --nosym --strict --b1s --set ...`; 3556 variables, 384,704 clauses, SHA-256 of the
file `32bd639e...ce773c1`). CaDiCaL refutes it in 12 s, and `lrat-check` and `cake_lpr` verify the proof
(80 MB, SHA-256 `37bdc5d6...8c5a95f6`). `covercheck.py 14` on the five lists reads 44,517 cubes, uses all of them,
walks 66,808 nodes and finds no uncovered node: the cubes are a complete case split. Hence the path of
$\delta$ passes through one of the 44,517 nodes. But $\delta$ satisfies $F_{14}$ and, since it synchronizes
$2,\dots,15$ and has (B1), also $S_{15}$, together with the units of every node on its path. This contradicts
the refutation of that node. $\square$

Second checks. (1) `recheck_ct.py` rebuilds a cube formula, compares its digest with the recorded one, runs
CaDiCaL again and has `lrat-check` and the verified checker `cake_lpr` check the new proof. This was done for
the 36 top nodes and the 4 nodes of the fourth row, and for a random sample of 600 of the 44,476 nodes of the
subtrees (`--sample 600 --seed 20261116`): every formula has the recorded digest, every new proof has the recorded
digest as well, and both checkers accept all of them (1582 s for the sample). (2) The first pass of the search (`germsat.py`, incremental
solver, no proofs) had closed the subtrees 1 to 167 without a model (169,041 nodes, 13.2 hours of solver time)
and had found the same single satisfiable node in the subtree 309. (3) With the formula $F_{15}$ of
`certtree.py 15 ... --pump 15` (4100 variables, 396,586 clauses), which uses the lines up to 17, $\gamma^\ast$
is closed by three certified parts in 10 s (`g15_parts_sat.txt`), and `covercheck.py 15` with this file in place
of `g15s_sat_strict.txt` also reports a complete case split; this alone gives the weaker statement for the
lines $2,\dots,17$.

**The three rules of the node $\gamma^\ast$ (certified).** Up to the table entries that are used neither in the
lines $2,\dots,14$ nor in the half-line up to the anti-diagonal 27, the formula $F_{14}$ has exactly three
models with $\delta(G,L,L)=A$ (the other models are their images under the exchange of $A$ and $B$): `rules/stable_generals_2-14.txt`, `rules/stable_generals_2-14_b.txt` and
`rules/stable_generals_2-14_c.txt`. `enum_satnode.py` enumerates the models of $F_{14}$ with the units of
$\gamma^\ast$: after each model the conjunction of the transitions that it uses is excluded by a clause; after
three models the formula is unsatisfiable, and for $F_{14}$ with the 11 units and the three clauses (3465
variables, 324,767 clauses, SHA-256 of the file `0e4f7032...98d5b9d3`) CaDiCaL gives an LRAT proof (16.8 MB,
SHA-256 `a77db8bc...2622eec0`) that `lrat-check` and `cake_lpr` verify (`runs/stable14/f14_node_three.txt`). All
other nodes of the tree are closed for $F_{14}$ (Theorem 6.4). The three rules have 75 used transitions in
common and differ in $\delta(A,A,A)=L,A,A$ and $\delta(G,A,A)=B,A,L$; they use 78, 81 and 80 transitions in the
lines $2,\dots,14$. Each satisfies (B1) on its table and synchronizes exactly the lines $2,\dots,14$ among
$2,\dots,120$ (with the unused entries as in the files); on the line 15 each of them has a cell in state $F$ at
time 26. So, after the normalization and the choice of names in the proof of Theorem 6.4, a five-state rule
with a stable general that synchronizes $2,\dots,14$ either agrees with one of these three rules on all
transitions that it uses in these lines and in the half-line up to the anti-diagonal 27, or it violates a
condition that the lines 15 and 16 would impose (items 3 to 5 of the proof).

**The length 15.** Is there a five-state rule with a stable general for $2,\dots,15$? Such a rule satisfies
every clause of $F_{14}$ except possibly those that use the line 16: the unit clause of item 4 for the front
cell $(13,14)$, and the unit clauses of item 5 for the cells $i\ge2$ of the anti-diagonal 27 (Lemma 6.2 with
$N=15$ reaches the anti-diagonal 26). If it satisfied these as well, its half-line would be a path of the
tree above and the proof of Theorem 6.4 would apply to it, because the node $\gamma^\ast$ is closed for the
lines $2,\dots,15$. The front cell $(13,14)$ is $\delta(f,L,L)$ for the front state $f$ of the cell 13, which is
$A$ or $B$ and has occurred as a front state before (the front states of the cells $2,\dots,13$ are in
$\{A,B\}$ and each is the image of its predecessor); so this cell is $A$ or $B$ again. The cell $(25,2)$ is not
$G$, because the first cell is $G$ and the line 15 would fire at time 26. Hence:

> every five-state rule with (B1) that synchronizes $2,\dots,15$ has a wall on the anti-diagonal 27 of its
> half-line: $C_\infty(27-i,i)=G$ for some $3\le i\le13$.

The formula $S_{15}\wedge D$, the strict formula of the lines $2,\dots,15$ with (B1) and the clause
$D=\bigvee_{i=3}^{13}[C_\infty(27-i,i)=G]$, is being searched with certificates (`gcert.py 5 15 --b1s --b3
--wimp --strict --noghws --gstatic 1 --sgap --cellclause ...`; 3556 variables, 386,734 clauses, SHA-256 of
the clause lines `5419585e...1acd8edb`; Section 9). The first attempts, one tree for each of the eleven cells,
were stopped: each of them is almost as large as the tree for the whole clause, which random descents
estimate at $3\cdot10^5$ nodes with a budget of 3000 conflicts (standard error $1.4\cdot10^5$). If the tree
closes, the largest $N$ of the class is exactly 14; a satisfiable node would give a five-state rule for
$2,\dots,15$.

Second method, without a solver. A closed node is a small problem for plain enumeration: with the transitions
of the node fixed, `mdfs` (depth-first enumeration of all partial rules of the class, transitions fixed lazily)
finds no rule after $10^4$ to $4\cdot10^7$ nodes for each of the first 60 closed nodes of one subtree. `wenum.c`
is a second enumerator, written separately and with a different order of enumeration; the two agree on the
number of partial rules of the class for the lines $2,\dots,N$ with nothing fixed ($N=3,4,5$: 57, 19,407,
16,197,888) and with the first transitions of the half-line of the rule for 2..13 fixed ($N=10,11,12,13$ with
12, 13, 14, 16 transitions: 171,797, 983, 40, 4). `enumtree.py` runs an enumerator on every closed node (and
splits a node further if a node limit is reached), and `covercheck.py` checks, without solver or enumeration,
that the closed nodes are a complete case split. Together they give a proof by exhaustive enumeration that
does not depend on the SAT solver or on Lemmas 6.1 (b)-(d) and 6.3. It is affordable for the subtrees with
$\delta(A,L,L)=A$ (some $10^6$ to $10^7$ nodes per closed node) but not for those with $\delta(A,L,L)=B$ (about
$3\cdot10^7$ nodes per closed node and far more closed nodes, some $10^{13}$ nodes in all); it has not been run on
all nodes yet.

**The weak reading.** In the weak reading of the paper the two end cells are not protected:

- (B1w) $\delta(x,G,y)=G$ for all working states $x,y$ that are not both $G$;
- (B3w) $\delta(G,G,G)=\delta(\ast,G,G)=\delta(G,G,\ast)=F$ (other neighbourhoods may give $F$ as well).

A rule with (B1w) and (B3w) in which $\delta(\ast,G,y)=\delta(x,G,\ast)=G$ for all $x,y\in W'$ satisfies (B1),
and by Lemma 6.1 a rule with (B1) that synchronizes 2 and 3 satisfies (B3w). So for five states the weak class
is the class of this section together with the rules in which one of these six transitions has another
value. The cells $2,\dots,n-1$ of the line $n$ are its *interior* cells.

**Lemma 6.5 (interior walls).** Let $\delta$ satisfy (B1w) and (B3w) and synchronize the line of length
$n\ge3$. Then in this line
(a) at no time $t\le2n-4$ are three adjacent positions in $\{G,\ast\}$ (the positions 0 and $n+1$ are the
borders);
(b) an interior cell in state $G$ at a time $t\le2n-4$ is in state $G$ at time $t+1$;
(c) if some interior cell is in state $G$ at time $2n-3$, then every cell is in state $G$ at time $2n-3$.

*Proof.* (a) The middle position is a cell in state $G$ with neighbourhood $GGG$, $\ast GG$ or $GG\ast$; by
(B3w) it is in state $F$ at time $t+1$, so $t+1\ge2n-2$. (b) Both neighbours of an interior cell are cells, in
working states at time $t$ and not both in state $G$ by (a); apply (B1w). (c) Let the interior cell $i$ be in
state $G$ at time $2n-3$ and let $x,y\in W$ be the states of its neighbours. Then $F=\delta(x,G,y)$, and (B1w)
gives $x=y=G$. The same holds for the cell $i-1$ if it is interior, and for $i+1$; by induction all cells are
in state $G$. $\square$

So a line either never has an interior cell in state $G$, or it fires from the row $G^n$.

**Lemma 6.6 (gaps, weak reading).** Let $\delta$ satisfy (B1w) and (B3w) and synchronize the line of length
$n\ge3$, and let $t\le2n-4$. With $M$ as in Lemma 6.3, put
$M_b(1)=|W'|$ and $M_b(\ell)=|W|\,|W'|^{\ell-1}+M_b(\ell-1)$.

1. If the interior cells $p<q$ are in state $G$ at time $t$, $q-p=\ell+1\ge2$, and no cell between them is in
   state $G$ at time $t$, then $2n-3-t\le M(\ell)$.
2. If the interior cell $q$ is in state $G$ at time $t$ and no interior cell to its left is, then
   $2n-3-t\le M_b(q-1)$; if the interior cell $p$ is in state $G$ at time $t$ and no interior cell to its
   right is, then $2n-3-t\le M_b(n-p)$.

For five states $M_b(1),M_b(2),M_b(3)=3,15,51$.

*Proof.* By Lemma 6.5 (b) an interior cell in state $G$ stays in state $G$ up to time $2n-3$, and since there
is one, every cell is in state $G$ at time $2n-3$ by Lemma 6.5 (c).
1. During $[t,2n-3]$ the $\ell$ cells between $p$ and $q$ have constant neighbours, so their configuration
evolves on its own. Let $s\ge t$ be the least time at which one of them is in state $G$; $s\le2n-3$. The
configurations at the times $t,\dots,s-1$ lie in $W'^{\ell}$ and are pairwise distinct: after a repetition
they would be periodic, and no cell of the gap would be in state $G$ at time $2n-3$. Hence
$s-t\le|W'|^{\ell}$. If $s=2n-3$ we are done. Let $s\le2n-4$. For $\ell=1$ the cells $p,p+1,p+2$ would be in
state $G$ at time $s$, contrary to Lemma 6.5 (a). For $\ell\ge2$, by Lemma 6.5 (a) some cell of the gap is not
in state $G$ at time $s$; it lies between two cells of $[p,q]$ in state $G$ at distance $\ell'+1$,
$1\le\ell'<\ell$, with no cell in state $G$ between them, and induction gives
$2n-3-s\le M(\ell')\le M(\ell-1)$.
2. By induction on $\ell=q-1$; the second statement is the mirror image. The cells $1,\dots,\ell$ have the
border on the left and the constant state $G$ on the right during $[t,2n-3]$. For $\ell=1$: the cell 1 is not
in state $G$ at a time $u\le2n-4$ (Lemma 6.5 (a) for the positions 0, 1, 2), so its states at the times
$t,\dots,2n-4$ lie in $W'$, and they are pairwise distinct because the cell is in state $G$ at time $2n-3$.
For $\ell\ge2$: let $s\ge t$ be the least time at which one of the cells $2,\dots,\ell$ is in state $G$. The
configurations of the cells $1,\dots,\ell$ at the times $t,\dots,s-1$ lie in $W\times W'^{\ell-1}$ and are
pairwise distinct as before, so $s-t\le|W|\,|W'|^{\ell-1}$. If $s\le2n-4$, the leftmost of the cells
$2,\dots,\ell$ in state $G$ at time $s$ is an interior cell $q'$ with no interior cell in state $G$ to its
left, and induction gives $2n-3-s\le M_b(q'-1)\le M_b(\ell-1)$. $\square$

Consequently, at a time $t\le2n-4$ with $\rho=2n-3-t$: no two interior cells at a distance $d\ge2$ with
$M(d-1)<\rho$ are both in state $G$ (between them lies a gap of length at most $d-1$, by Lemma 6.5 (a)), and no
interior cell $y$ with $M_b(y-1)<\rho$ or $M_b(n-y)<\rho$ is in state $G$. `weakwalls.py` adds these clauses
and those of Lemma 6.5 (`--wwalls`). `check_weak_lemmas.py` finds no violation of Lemmas 6.5, 6.6 and 6.2' on
the diagrams of the 31 stored rules that satisfy (B1w) and (B3w) on the transitions they use, nor on 41 rules
for $2,\dots,10$ generated for this test with seven different beginnings of the first cell (in some of them the
lines 3 and 4 have no interior cell in state $G$); these 41 rules and five of the stored ones, all of which
synchronize $2,\dots,10$, satisfy the formula with the clauses at $N=8$ (`check_wwalls_enc.py`).

Sizes (estimates by random descents in the tree of `gsat.py`, 30 descents each, budget 3000; standard errors
30 to 50 per cent, and such estimates tend to be too low): the weak class with (B3) in the strong reading,
lines $2,\dots,14$: $4\cdot10^6$ to $2\cdot10^7$ nodes in four runs, with or without the clauses of Lemmas
6.5 and 6.6, which do not make the tree smaller; with (B3w): $1.3\cdot10^7$; the strong class of this section:
$1.1\cdot10^6$. The parts of the weak class outside the strong class are defined by $\delta(\ast,G,y)\ne G$ or
$\delta(x,G,\ast)\ne G$ for one $x$ or $y$. With (B3) in the strong reading $\delta(\ast,G,L)=G$ is forced by
the line 2; the four other parts estimated so far have $1.6\cdot10^6$ to $7\cdot10^6$ nodes each, so
they cannot be treated as small corrections to the strong class. The weak class without (B2) and (B4) has
not been searched. With (B4) and (B2) without borders it is small: Proposition 7.2.

## 7. Balzer's conditions, taken apart

Proposition 6.6 of the paper excludes five states under the four conditions (B1)-(B4) together. Which of
them are needed? (B1): stable general. (B2): image condition $\delta(I(z),I(y),I(x))=I(\delta(x,y,z))$ for an
involution $I$ of the working states, also at the borders. (B3): exactly `GGG`, `*GG`, `GG*` give `F`.
(B4): $\delta(G,v,G)=G$ for $v\ne G$. Strong reading unless stated.

**Proposition 7.1 (computer-assisted, certified).** No five-state rule that satisfies (B2), for some involution $I$ of
$\{L,G,A,B\}$, and (B1) synchronizes all lines of lengths $2,\dots,12$ in minimal time; this holds for the
strong and for the weak reading of (B1). For $I$ the identity the lengths up to 11 do not suffice.

*Proof.* The clauses of (B1) and (B2) are added to the formula "the lines $2,\dots,N$ are synchronized at
time $2n-2$ and not before" (`mcopy.py 5 N --nocopy --strict --b1s --b2 I` for the strong reading, `--b1` for
the weak one; `--strict` leaves out every clause that uses a line longer than $N$, see Section 1). The formula
requires that the auxiliary state $A$ occurs before $B$ on the half-line, so all ten involutions are treated,
not one of each pair exchanged by renaming $A$ and $B$. The formulas are unsatisfiable for the following $N$
and, where $N>2$, satisfiable for $N-1$ (CaDiCaL):

| $I$ | $(L\,G)$ | $(L\,G)(A\,B)$ | $(G\,A)$ | $(L\,B)(G\,A)$ | $(G\,B)$ | $(L\,A)(G\,B)$ | $(L\,A)$ | $(L\,B)$ | $(A\,B)$ | identity |
|---|---|---|---|---|---|---|---|---|---|---|
| (B1) strong: $N=$ | 2 | 2 | 3 | 3 | 5 | 5 | 9 | 9 | 10 | 12 |
| (B1) weak: $N=$ | 3 | 3 | 6 | 6 | 7 | 6 | 10 | 10 | 10 | 12 |

Certificates (`CERTIFICATES.txt`): for the strong reading, CaDiCaL refutes each of the ten formulas with an
LRAT proof that `lrat-check` verifies; for the weak reading the same holds for the nine involutions other than
the identity, and for the identity Kissat refutes the formula with a DRAT proof (713 MB) that `drat-trim`
verifies.
The rule `rules/b1_b2_id_2-11.txt`, found by the solver, satisfies (B1) in the strong reading and (B2) with
$I$ the identity (both checked on the table) and synchronizes the lines $2,\dots,11$ (and 18 and 34, and no
other length below 40; direct simulation). $\square$

By Lemma 6.1, (B3) follows from (B1) in the strong reading on the transitions that are used. So the image
condition and the stable general alone are incompatible with five states: (B3) and (B4) are not needed in
Proposition 6.6 of the paper, in either reading of (B1).

The other subsets, strong reading, `mcopy_inc.py` with 600 s per class on a loaded machine; "reached $N$"
means that a rule for $2,\dots,N$ was found and the next length was not decided in the time:

| conditions | $I$ = identity | $(A\,B)$ | $(L\,A)$ | $(L\,B)$ |
|---|---|---|---|---|
| (B1), (B2) (with or without (B3), (B4)) | refuted at 12 | at 10 | at 9 | at 9 |
| (B2), (B3), (B4) | reached 11 | reached 10 | reached 10 | reached 9 |
| (B2), (B3) | reached 10 | reached 10 | reached 10 | reached 11 |
| (B2), (B4) | reached 10 | reached 9 | not run | not run |
| (B2) | reached 11 (Kissat, 345 s) | reached 9 | reached 9 | reached 9 |

Without (B2): (B1) alone is Section 6 (rule for 2..13); (B1) and (B4): rule for 2..12, 13 not decided in 16
minutes; (B3) and (B4): rule for 2..12; (B3): rule for 2..11.

**Proposition 7.2 (Balzer's conditions as Yunès states them; computer-assisted, certified).**
No five-state rule that satisfies (B1) and (B3) in the weak reading, (B4), and (B2) for the neighbourhoods
without a border, for some involution $I$ of the working states, synchronizes all lines of lengths
$2,\dots,15$ in minimal time. For $I\ne\mathrm{id}$ the lengths $2,\dots,12$ suffice.

This is the case left open at the end of Section 6.5 of the paper, where the rule `balzer_noborder12` shows
that the lines up to 12 do not suffice for $I$ the identity.

*Proof.* As in the paper, $I(G)=G$: otherwise $g=I(G)\ne G$, and (B2) for the neighbourhood $(G,g,G)$ with
(B4) gives $\delta(g,G,g)=I(\delta(G,g,G))=I(G)=g$, against (B1w). So $I$ is the identity, $(A\,B)$, $(L\,A)$ or
$(L\,B)$. For each of them let $F_I$ be the formula of
`gcert.py 5 N --b1 --b3w --b4 --b2 I --b2nb --noghw --front1`, with $N=13$ for the identity and $N=10$
otherwise: the lines $2,\dots,N$ are synchronized, with the clauses of (B1w), (B3w), (B4) and of (B2) for the
64 neighbourhoods without a border, and with clauses that follow if the lines up to $N+2$ are synchronized as
well: the return chain of the line $N$ and the half-line in working states up to the anti-diagonal $2N-1$
(line $N+1$), the front cell $(N-1,N)\ne L$ (Lemma 2.4 of the paper for the lines $N+1$ and $N+2$), and no
cell $i\ge2$ of the half-line in state $G$ up to the anti-diagonal $2N-1$ (Lemma 6.2' for the lines up to
$N+2$). `gcert.py` searches the tree of half-lines: the transitions of the half-line are fixed one at a
time in the order of the anti-diagonals; the values excluded at a node are `L` for a front cell and `G` for a
cell $i\ge2$ (unit clauses of $F_I$) and `B` before `A` has been used (naming). The classes for the identity
and for $(A\,B)$ are invariant under exchanging the names $A$ and $B$, and this exchange maps the class for
$(L\,A)$ onto the class for $(L\,B)$; so a rule of one of the four classes that synchronizes $2,\dots,N+2$
gives, after renaming, a model of one of the four formulas in the tree that is searched. Every node is
either split or closed by CaDiCaL 3.0.1 (at most 4 s) with an LRAT proof that `lrat-check` verified (answer
`UNSATISFIABLE` and empty last lemma required):

| $I$ | $N$ | variables, clauses of $F_I$ | SHA-256 of the clause lines | nodes split | nodes closed | CaDiCaL time on closed nodes | proofs |
|---|---|---|---|---|---|---|---|
| identity | 13 | 2608, 259,770 | `e827af0b...3a0ce0` | 1176 | 2550 | 5219 s | 34.5 GB |
| $(A\,B)$ | 10 | 1536, 121,456 | `edeb38b1...2a70317` | 137 | 265 | 556 s | 2.7 GB |
| $(L\,A)$ | 10 | 1536, 121,456 | `f3e68742...334f7f5` | 62 | 131 | 243 s | 1.1 GB |
| $(L\,B)$ | 10 | 1536, 121,456 | `346a6003...4004d26` | 40 | 89 | 169 s | 0.9 GB |

The proofs were deleted after the check; `runs/yunes/yun_I_N.txt` lists for every closed node its cube and
the SHA-256 digests of the cube formula ($F_I$ plus the units of the cube) and of the proof.
`gcover.py 5 N runs/yunes/yun_I_N.txt --noghw --front1`, which replays the branching rules without a solver,
reports for each of the four files that the cubes are a complete case split. So the four formulas are
unsatisfiable. $\square$

For $I$ the identity the largest $N$ such that a rule of the class synchronizes $2,\dots,N$ is therefore 12, 13
or 14; by Proposition 7.3 below it is 12 or 13. A second verification of the proofs with `cake_lpr` (`gcert.py ... --recheck`, which also compares
the digests) is recorded in Section 9.

Yunès admits a state other than $G$ in (B1), (B3) and (B4). A state $g$ that is stable, fires in threes and
is not the initial state of the general is the same class with the roles of two names exchanged: the lines
start from `A L ... L` and the conditions speak about $G$ (`gcert.py --init A`). Lemma 6.2' does not use the
initial configuration, so the half-line has no cell $i\ge2$ in state $G$ in this class either. This class has
rules for $2,\dots,11$ with $I$ the identity (the tree search at $N=11$ ends at a satisfiable node; $N=12$ was
not finished). Without (B3) and (B4) this class is
Proposition 7.4 below.

**Proposition 7.3 (weak stable general and image condition without borders; computer-assisted, certified).**
No five-state rule that satisfies (B1) in the weak reading and (B2) for the neighbourhoods without a border,
for some involution $I$ of the working states, synchronizes all lines of lengths $2,\dots,14$ in minimal time.
Nothing is assumed about firing, about $\delta(G,v,G)$ or about the neighbourhoods with a border. More precisely,
let $N^\ast_I$ be the largest $N$ such that some rule of the class for $I$ synchronizes all lines $2,\dots,N$.
Then

| $I$ | identity | $(A\,B)$ | $(L\,A)$, $(L\,B)$ | $(G\,A)$, $(G\,B)$, $(L\,A)(G\,B)$, $(L\,B)(G\,A)$ | $(L\,G)$, $(L\,G)(A\,B)$ |
|---|---|---|---|---|---|
| $N^\ast_I$ | 12 or 13 | 10 | 10 | 6 | 2 |

*Proof.* The front. For any rule, the front cells $g_t:=C_\infty(t,t+1)$ satisfy $g_0=G$ and
$g_{t+1}=\delta(g_t,L,L)$, because the two cells to the right of the front are quiescent. If $g_1,g_2,g_3$ are
working states other than $L$, two of $g_0,\dots,g_3\in\{G,A,B\}$ are equal, so the sequence is periodic from
there on with values in $\{G,A,B\}$: no front cell is $L$. If a rule synchronizes the lines $2,\dots,N+1$, then
$g_t\ne L$ for $t\le N-2$ by Lemma 2.4 of the paper (the front cell $(n-2,n-1)$ for the lines $n$ and
$n+1\le N+1$). So for $N\ge5$ all its front cells are working states other than $L$.

Let $F^I_N$ be the formula of `gcert.py 5 N --b1 --b2 I --b2nb --front1`: the lines $2,\dots,N$ are
synchronized, with the clauses of (B1w) and of (B2) for the 64 neighbourhoods without a border, the return
chains of the lines up to $N$, the half-line in working states up to the anti-diagonal $2N-1$, and the front
cells $(t,t+1)\ne L$ for $t\le N-1$. All cell variables of $F^I_N$ are functions of the transition table. If
$N\ge5$ and a rule of the class synchronizes the lines $2,\dots,N+1$, its table and diagrams satisfy $F^I_N$:
the half-line up to the anti-diagonal $2N-1$ agrees with the line $N+1$ before its firing time, the return
chains are Lemma 2.4 of the paper for the lines $n$ and $n+1\le N+1$, and the front cells are the preceding
paragraph. For the same reason they satisfy $F^I_{N'}$ for every $N'\le N$.

`gchain.py` searches the tree of half-lines of Proposition 7.2 level by level. At the level $N$ the node is
closed (CaDiCaL refutes $F^I_N$ plus the units of the cube in at most 4 s, with an LRAT proof), split, or
satisfiable (CaDiCaL finds a model in 4 s); a satisfiable node is recorded and searched again at the level
$N+1$. The order in which the half-line needs its transitions does not depend on the level, and the values
excluded at a node of the level $N$ (`L` for a front cell up to $(N-1,N)$, and `B` before `A` has been used) are
also excluded at every higher level; so a node of a lower level is a node of the tree of every higher level.
The tree for $I$ is finished at the first level $N_I'$ at which no node is satisfiable. Then
`gcover.py 5 N runs/b1b2/w_I_*.txt --front1` with $N=N_I'$, which replays the branching of the level $N_I'$
without a solver, reports that the closed nodes of all levels are a complete case split. Suppose that $N_I'\ge5$ and that a
rule of the class for $I$, in whose half-line `B` does not occur before `A`, synchronizes $2,\dots,N_I'+1$. Its
half-line is a path of the tree of the level $N_I'$ and passes through a node that was closed at some level
$N\le N_I'$; the rule satisfies $F^I_N$ and the units of that cube, which is a contradiction.

Exchanging the names $A$ and $B$ maps the class for $I$ onto the class for $(A\,B)\,I\,(A\,B)$. The identity,
$(A\,B)$, $(L\,G)$ and $(L\,G)(A\,B)$ are fixed, and $(L\,A)\leftrightarrow(L\,B)$,
$(G\,A)\leftrightarrow(G\,B)$, $(L\,A)(G\,B)\leftrightarrow(L\,B)(G\,A)$. So a rule of the class for $I$ is, after
renaming if `B` occurs first, covered by the tree for $I$ or by the tree for its mirror, and the larger of the
two last levels counts for both. The last levels are 13 for the identity, 11 for $(A\,B)$, and 10 and 11 for
$(L\,A)$ and $(L\,B)$; this gives $N^\ast_I\le13$ for the identity and $N^\ast_I\le11$ for the other three.

The length 11. A rule of the class for $(A\,B)$ or $(L\,B)$ that synchronizes $2,\dots,11$ satisfies the
formulas of the levels up to 10, so its half-line passes through a node that is closed at a level up to 10 or
through one of the nodes that are satisfiable at the level 10: one node for $(A\,B)$
(`*GL=G,GLL=A,*GA=G,GAL=B,*GB=G,ALL=B`) and two for $(L\,B)$ (`*GL=G,GLL=A,*GA=B` and
`*GL=G,GLL=A,*GA=A,GAL=L,*AL=G`); the tree for $(L\,A)$ has none. For each of these three nodes the strict
formula of the lines $2,\dots,11$ with the units of the node
(`mcopy.py 5 11 --nocopy --nosym --strict --b1 --b2 I --b2nb --set ...`) is unsatisfiable, with an LRAT proof
that `lrat-check` and `cake_lpr` verified (`runs/b1b2/ws_AB_11_nodes.txt`, `ws_LB_11_nodes.txt`), and
`gcover.py 5 10 --front1` on the lists of the levels up to 10 together with these nodes reports a complete case
split for $(A\,B)$ (678 cubes) and for $(L\,B)$ (252 cubes), as it does for $(L\,A)$ without them (305 cubes).
So no rule of these classes synchronizes $2,\dots,11$, and $N^\ast_I\le10$. `nodecert.py 5 11 ... --b1 --b2 LB --b2nb --strict`, which builds the
strict formula with the encoder of `gcert.py` instead of `mcopy.py`, refutes the two nodes of $(L\,B)$ as well
(both checkers). As a further cross-check, Kissat refutes the
strict formulas of the lines $2,\dots,11$ for $(L\,A)$ and for $(L\,B)$ as whole formulas (400 s and 376 s, no
proof kept); for $(A\,B)$ it gave no answer in 800 s. The trees and their certificates (every proof was verified by
`lrat-check` and by `cake_lpr`; at the levels that are not listed the root is satisfiable):

| $I$ | level | variables, clauses of $F^I_N$ | SHA-256 of the clause lines | nodes closed | split | satisfiable | CaDiCaL time on closed nodes | proofs |
|---|---|---|---|---|---|---|---|---|
| identity | 13 | 2608, 259,620 | `4c411838...cbfefe4` | 12,296 | 4213 | 0 | 20,727 s | 102.3 GB |
| $(A\,B)$ | 10 | 1536, 121,369 | `dfa6f6a5...9436a59` | 677 | 258 | 1 | 1090 s | 4.62 GB |
| $(A\,B)$ | 11 | 1840, 160,062 | `84672a30...a43d405` | 4 | 1 | 0 | 8 s | 0.03 GB |
| $(L\,A)$ | 9 | 1280, 89,308 | `c2c2cb4f...10ce6f4` | 115 | 50 | 12 | 193 s | 0.79 GB |
| $(L\,A)$ | 10 | 1536, 121,369 | `cd805cb5...e545e09` | 190 | 67 | 0 | 290 s | 1.25 GB |
| $(L\,B)$ | 9 | 1280, 89,308 | `9bbde38c...373ce45` | 32 | 15 | 7 | 58 s | 0.25 GB |
| $(L\,B)$ | 10 | 1536, 121,369 | `29797ea4...13a5fe1` | 218 | 81 | 2 | 382 s | 1.66 GB |
| $(L\,B)$ | 11 | 1840, 160,062 | `e2b20c60...9021e0a` | 26 | 10 | 0 | 39 s | 0.18 GB |
| $(G\,A)$ | 7 | 896, 42,750 | `814679a7...04ed256` | 1 (the root) | 0 | 0 | 0.2 s | 2 MB |
| $(G\,B)$ | 7 | 896, 42,750 | `e3ab0f4a...dde197c` | 1 (the root) | 0 | 0 | 0.2 s | 2 MB |
| $(L\,A)(G\,B)$ | 6 | 760, 27,111 | `afbb033f...b828039` | 1 (the root) | 0 | 0 | < 1 s | < 2 MB |
| $(L\,B)(G\,A)$ | 6 | 760, 27,111 | `2c6f2cd5...a5eaf69` | 1 (the root) | 0 | 0 | < 1 s | < 2 MB |
| $(L\,G)$ | 3 | 528, 3,566 | `fdfb6f9f...31c434a` | 1 (the root) | 0 | 0 | < 1 s | < 1 MB |
| $(L\,G)(A\,B)$ | 3 | 528, 3,590 | `3a9b12ff...0a7a1b1` | 1 (the root) | 0 | 0 | < 1 s | < 1 MB |

The identity was searched at the level 13 only. `runs/b1b2/` holds the lists of the closed nodes with the
digests of their cube formulas and proofs, and the summaries of all levels.

For the six involutions that move $G$ the strict formulas decide $N^\ast_I$ at once
(`mcopy.py 5 N --nocopy --nosym --strict --b1 --b2 I --b2nb`: the lines $2,\dots,N$ and the class, nothing
else). For $(L\,G)$ and $(L\,G)(A\,B)$ the formula for $N=3$ is unsatisfiable, and for $(G\,A)$, $(G\,B)$,
$(L\,A)(G\,B)$ and $(L\,B)(G\,A)$ the formula for $N=7$ is; each of the six refutations has an LRAT proof that
`lrat-check` and `cake_lpr` verified (`CERTIFICATES.txt`). The formulas for $N=2$ and $N=6$ are satisfiable, and
the rules that the solver returns synchronize the lines 2 and $2,\dots,6$ (simulation). The lower bounds for
the other four involutions are the rules named below. $\square$

Proposition 7.3 contains Proposition 7.2, with the lengths up to 14 in place of 15 for the identity, and,
with the lengths up to 14 in place of 12, the weak case of Proposition 7.1: in Proposition 6.6 of the paper the conditions (B3) and (B4) and the border part of (B2) can
be dropped and (B1) can be read weakly. A satisfiable node carries a model of $F^I_N$, which is a rule of the
class that synchronizes $2,\dots,N$. So the class for $(A\,B)$ has a rule for $2,\dots,10$ (and none for
$2,\dots,11$), and the same holds for the class for $(L\,B)$, which is the class for $(L\,A)$ with the names
exchanged: `rules/b1w_b2nb_AB_2-10.txt` and `rules/b1w_b2nb_LB_2-10.txt` (found by `mcopy.py`; conditions
checked on the tables by `check_balzer.py`; each synchronizes exactly the lines $2,\dots,10$ among
$2,\dots,60$). The second of them does not fire from `GGG`, so (B3) does not follow from these conditions.
For the identity the rule `balzer_noborder12` of the paper shows that the largest $N$ with a rule for
$2,\dots,N$ is 12 or 13.

**Proposition 7.4 (a stable state that is not the initial state; computer-assisted, certified).** Let the
first cell start in the state $A$ and let $G$ be another working state, which need not occur in the initial
configuration: the lines are $A\,L\cdots L$, and the conditions are (B1) in the weak reading for $G$ and (B2)
for the neighbourhoods without a border, for an involution $I$ of $\{L,G,A,B\}$. Let $N^\ast_I$ be the largest
$N$ such that some five-state rule of this class synchronizes all lines $2,\dots,N$. Then

| $I$ | $(A\,B)$, $(L\,A)$, $(L\,B)$ | $(G\,A)$, $(G\,B)$, $(L\,A)(G\,B)$, $(L\,B)(G\,A)$ | $(L\,G)$, $(L\,G)(A\,B)$ | identity |
|---|---|---|---|---|
| $N^\ast_I$ | 10 | 6 | 2 | at least 11; not decided |

*Proof.* As for Proposition 7.3, with `gchain.py ... --init A`. In this class the four working states are
distinguished (quiescent, initial, stable, the fourth), so no names are exchanged and the ten involutions are
ten classes; the remark on the front holds with $g_0=A$. For $(A\,B)$, $(L\,A)$ and $(L\,B)$ the trees close at
the level 11 (`gcover.py 5 11 ... --front1 --init A`: complete case splits with 821, 443 and 431 cubes), so
$N^\ast_I\le11$; the nodes that are satisfiable at the level 10 (one, two and one) are refuted for the strict
formula of the lines $2,\dots,11$ (`nodecert.py 5 11 ... --strict --init A`), and with them the case splits of
the level 10 are complete (815, 441 and 431 cubes), so $N^\ast_I\le10$; a satisfiable node of the level 10
carries a rule for $2,\dots,10$. For the six involutions that move $G$ the strict formulas of the root decide:
unsatisfiable for $N=3$ and satisfiable for $N=2$ for $(L\,G)$ and $(L\,G)(A\,B)$, unsatisfiable for $N=7$ and
satisfiable for $N=6$ for the other four (`runs/b1b2A/strict_roots.txt`). Every refutation has an LRAT proof
verified by `lrat-check` and `cake_lpr`. For the identity the level 10 has 4597 closed and 111 satisfiable
nodes; the level 11 is not finished (1033 closed, 355 split and three satisfiable nodes so far). At each of the
three satisfiable nodes of the level 11 the strict formula of the lines $2,\dots,11$ has a model
(`node_model.py 5 11 ... --b1 --b2 id --b2nb --strict --init A`), and the three tables satisfy (B1) weak for $G$
and (B2) without borders and synchronize the lines $A\,L\cdots L$ of lengths $2,\dots,11$ (the checks of
`node_model.py`, which do not use the encoder); one of them is `rules/stableA_b1w_b2nb_id_2-11.txt`, which
synchronizes exactly $2,\dots,11$ among $2,\dots,60$. $\square$

| $I$ | level | variables, clauses | SHA-256 of the clause lines | nodes closed | split | satisfiable | CaDiCaL time on closed nodes | proofs |
|---|---|---|---|---|---|---|---|---|
| $(A\,B)$ | 9 | 1280, 89,308 | `1c280f94...76fd4e9` | 414 | 160 | 23 | 625 s | 2.53 GB |
| $(A\,B)$ | 10 | 1536, 121,369 | `d49c0009...0a2e94c` | 400 | 134 | 1 | 669 s | 2.78 GB |
| $(A\,B)$ | 11 | 1840, 160,062 | `24f3fe8e...6b7e0d6` | 7 | 2 | 0 | 14 s | 0.06 GB |
| $(L\,A)$ | 9 | 1280, 89,308 | `d1fdd049...9363982` | 121 | 45 | 10 | 201 s | 0.86 GB |
| $(L\,A)$ | 10 | 1536, 121,369 | `406fac32...083fac9` | 318 | 114 | 2 | 465 s | 2.11 GB |
| $(L\,A)$ | 11 | 1840, 160,062 | `80b98d5f...3ab5fdf` | 4 | 1 | 0 | 9 s | 0.04 GB |
| $(L\,B)$ | 10 | 1536, 121,369 | `893e40e2...c62dc46` | 430 | 156 | 1 | 688 s | 2.96 GB |
| $(L\,B)$ | 11 | 1840, 160,062 | `2d2aefe2...9323792` | 1 | 0 | 0 | 1 s | 0.01 GB |

So for the nine involutions other than the identity it makes no difference for the maximum whether the stable
state is the initial state of the general or another state: the values 10, 6 and 2 are those of
Proposition 7.3.

## 8. The left-border lemma: is its bound attained?

Question (3) at the end of the paper asks whether the bound of Lemma 4.1 can be made polynomial in $s$. The
lemma: if $\delta$ has $k$ states and synchronizes the line $n$, and the input anti-diagonals
$y\mapsto C_\infty(2n-2-y,y)$ ($s\le y\le Y$) and $y\mapsto C_\infty(2n-3-y,y)$ ($s\le y\le Y-1$) are
$\ell$-periodic, $Y\le n-s$, then $Y-s\le(k-1)^{2s}\ell$. Its proof only uses that the band of the first $2s$
chains, read from right to left, cannot repeat a state. `leftb.py K n s l Y` asks a solver for a rule that
synchronizes the line $n$ (only this line, as in the lemma) with periodic inputs on the stretch.

**Observation 8.1 (solver; the rules are re-simulated).** For $s=1$, $\ell=1$ the bound is attained for four,
five and six states: `rules/leftborder_k4_s1_n11.txt` synchronizes the line 11 and has constant inputs for
$1\le y\le10$ ($Y-s=9=3^2$), and `rules/leftborder_k5_s1_n18.txt` synchronizes the line 18 with constant
inputs for $1\le y\le17$ ($Y-s=16=4^2$), and `rules/leftborder_k6_s1_n27.txt` (six states) synchronizes the
line 27 with constant inputs for $1\le y\le26$ ($Y-s=25=5^2$; found in 107 s). In the first two, the pairs
$(u_1(y),u_2(y))$ of the two chains were listed and take every value of $W^2$ exactly once along the stretch,
as they must. With the same $Y$ and a longer line ($n=12$; $n=19,20$) the
formulas are unsatisfiable. For five states and $s=2$ a stretch with $Y-s=20$ exists (lines 24 and 25,
`rules/leftborder_k5_s2_n24.txt`), so the maximum for $s=2$ exceeds the bound for $s=1$; $Y-s=32$ was not
decided in 240 s. Three states say nothing: no three-state rule synchronizes a single line of length 4, 5
or 6.

**Proposition 8.2 (proved by hand).** Let $k$ be odd and $s\ge2$. Under the hypotheses of Lemma 4.1,
$Y-s\le(k-1)^{2s}\ell-1$: the bound is not attained. (The proof is written out for all $\ell$ in
`notes/stable_general.pdf`, last section; here it is given for $\ell=1$.)

*Proof for $\ell=1$.* Put $q=k-1$ (even), $m=2s\ge4$, and suppose $Y-s=q^m$. In the notation of the proof of Lemma 4.1 the
band vectors $X_j=\mathbf u(Y-j)\in W^m$, $0\le j<q^m$, are pairwise distinct, so they are all of $W^m$, and
$X_{j+1}=\Gamma_0(X_j)$, where the component $c$ of $\Gamma_0(X)$ depends on the components $1,\dots,c$ of
$X$ only (the inputs are constant).
(1) Let $c\le m-1$. The first $c$ components of $X_j$ take every value of $W^c$ exactly $q^{m-c}\ge2$ times.
A sequence generated by a map in which the first element occurs again is periodic, so the first $c$
components run through one cycle $\Phi_c$ of length $q^c$ that contains all of $W^c$.
(2) Call $j\bmod q^{m-1}$ the phase of $j$. The component $m$ of $X_{j+1}$ is $g_\varphi$ applied to the
component $m$ of $X_j$, where $\varphi$ is the phase of $j$ and
$g_\varphi=\delta(\alpha_\varphi,\beta_\varphi,\cdot)$ with $\alpha_\varphi$ the component $m-2$ of $X_{j+1}$ and
$\beta_\varphi$ the component $m-1$ of $X_j$; both depend on the phase only. At a fixed phase the component
$m$ takes $q$ distinct values in the $q$ periods, because the $X_j$ are distinct. So for a phase that is not
the last one, $g_\varphi$ maps $W$ onto $W$.
(3) Every pair in $W^2$ is $(\alpha_\varphi,\beta_\varphi)$ for exactly $q^{m-3}$ phases: $\beta$ is the last
of the first $m-1$ components, and $\alpha$ is a component of the image under the bijection $\Phi_{m-2}$ of
the first $m-2$ components. As $q^{m-3}\ge2$, every map $\delta(\alpha,\beta,\cdot)$ occurs at a phase that is not
the last one, so all $g_\varphi$ are permutations of $W$.
(4) Let $G$ be the product of the $g_\varphi$ over one period. The components $m$ of
$X_0,X_{q^{m-1}},X_{2q^{m-1}},\dots$ are $q$ distinct values and each is the image of the previous one under
$G$, so $G$ is a cycle of length $q$, an odd permutation because $q$ is even. But by (3) the sign of $G$ is
$\prod_{(\alpha,\beta)}\operatorname{sgn}(\delta(\alpha,\beta,\cdot))^{q^{m-3}}=1$, because $q^{m-3}$ is even.
$\square$

So for five states the bound $(k-1)^{2s}\ell$ is sharp for $s=1$, $\ell=1$, and it is not attained for $s\ge2$. The
argument removes only one from the bound. On the other hand the band alone, as an automaton, can run
exponentially long: with $q=4$ and the states read as pairs (bit, carry), the components $c,c-2,c-4,\dots$
form a binary counter with ripple carry, since the component $c$ sees the new state of the component $c-2$;
this gives $2^s$ steps without repetition. Whether a rule that synchronizes a line realizes such a counter
for large $s$ is not known. So question (3) stays open, but a polynomial bound cannot come from the band
alone: it would have to use the firing of the cells to the right of the band.

## 9. Log of long runs

**Tree sizes (15 November).** Estimates of the number of nodes of the tree of `gsat.py` (budget 3000 conflicts
per node) by random descents (Knuth's estimator, `gsat.py ... --knuth 30` or `40`); the standard error of the
mean is given, but the distribution is heavy-tailed and the estimates are to be read as orders of magnitude.
No descent ended in a model unless stated.

| class (five states) | lines | estimated nodes | standard error |
|---|---|---|---|
| no class (the open problem) | 2..15 | $3\cdot10^{18}$ | same order |
| stable general, Section 6 (`--b1s --b3 --nogh --wimp --wgap`) | 2..14 | $1.07\cdot10^6$ | $0.41\cdot10^6$ |
| stable general, strict formula $S_{15}$ of Section 6 (`--b1s --b3 --wimp --strict --noghws --gstatic 1`; 16 November) | 2..15, strict | $7.4\cdot10^5$ | $5.5\cdot10^5$ |
| the same with the wall clause $D$ and `--sgap` (16 November) | 2..15, strict | $3.2\cdot10^5$ | $1.4\cdot10^5$ |
| (B1) weak, (B3) strong (`--b1 --b3 --noghw`) | 2..14 | $3.6\cdot10^6$; with another seed $1.7\cdot10^7$ | $1.0\cdot10^6$; $0.8\cdot10^7$ |
| the same with the clauses of Lemmas 6.5, 6.6 (`--wwalls`) and PUMP (`--pump 14`) | 2..14 | $1.2\cdot10^7$; $5.2\cdot10^6$ (two seeds) | $0.7\cdot10^7$; $1.7\cdot10^6$ |
| (B1) weak, (B3) weak (`--b1 --b3w --noghw`) | 2..14 | $1.3\cdot10^7$ | $0.4\cdot10^7$ |
| (B1) weak, (B3) weak, (B4) | 2..14 | $9\cdot10^7$ | $5\cdot10^7$ |
| Yunès's form, $I$ identity (Proposition 7.2) | 2..13; 2..14 | $2.4\cdot10^4$; $2.2\cdot10^4$ | $0.5\cdot10^4$ |
| Yunès's form, $I=(A\,B)$ | 2..11 | $1.9\cdot10^3$ | $0.3\cdot10^3$ |
| (B1) weak alone (`--b1`) | 2..13 | $8\cdot10^7$, some descents end in a rule | $4\cdot10^7$ |
| (B2) alone, $I$ identity | 2..12; 2..13 | $5\cdot10^8$; $9\cdot10^8$ | $3\cdot10^8$ |
| (B2) alone, $I=(A\,B)$ | 2..12 | $2.7\cdot10^6$ | $1.2\cdot10^6$ |
| (B2) alone, $I=(L\,A)$ | 2..12 | $7.9\cdot10^5$ | $3.0\cdot10^5$ |
| (B3) strong alone (`--b3`) | 2..13 | $1.6\cdot10^{15}$ | $0.8\cdot10^{15}$ |
| (B3) strong, first cell `G` from time 2 on (as in Mazoyer's solution) | 2..13 | $8\cdot10^{13}$ | $3\cdot10^{13}$ |
| first cell `G` from time 1 on | 2..13 | $9\cdot10^{12}$ | $5\cdot10^{12}$ |
| (B3) strong, no `G` on the half-line beyond the first cell | 2..13 | $1.6\cdot10^{10}$, many descents end in a rule | $0.8\cdot10^{10}$ |
| (B4) alone | 2..13 | $2\cdot10^{18}$ | same order |
| the class of Section 2 with all conditions (copies, wake 4, static general 2, periodic (3, 2)) | 2..11 | $3\cdot10^{10}$ | $2\cdot10^{10}$ |

The tree of Proposition 7.2 had 3726 nodes in `gcert.py` (4 s per node instead of 3000 conflicts), and it
took 93 minutes with two processes on a machine that was running six processes on four cores. On this
machine a class is within reach of the tree search up to some $10^6$ to $10^7$ estimated nodes; this includes
the classes with a stable general and the image condition for $(A\,B)$ or $(L\,A)$, but neither the image
condition for the identity, nor a firing condition alone, nor the open problem.

**Yunès's form, identity (15 November).** `gcert.py 5 13 --b1 --b3w --b4 --b2 id --b2nb --noghw --front1 --tlim 4
--workers 2`: 5552 s, 2550 certified leaves, 1176 splits, no node left open, no model; 5219 s of CaDiCaL
time on the leaves; cubes of 4 to 12 transitions (most have 8 or 9).

**Yunès's form, the other involutions, and second checks (15 November).** `gcert.py 5 10 ...` for $(L\,A)$,
$(L\,B)$, $(A\,B)$: 278 s, 185 s and 616 s; no node left open, no model. `gcert.py ... --recheck` on the three
files: every cube formula is rebuilt with the same SHA-256 digest, CaDiCaL produces the same proof (same
digest) for each of the 131, 89 and 265 cubes, and `lrat-check` and the verified checker `cake_lpr` accept all
of them (299 s, 244 s, 795 s). The recheck of the 2550 cubes for the identity ended on 16 November after 44,796 s (one process at low priority): every formula and every proof has the recorded digest, and both checkers accept all 2550. Independently of the
tree, Kissat refutes each of the three formulas $F_I$, written by `writef.py`, as a whole (no proof kept):
$(L\,B)$ 216 s, $(L\,A)$ 220 s, $(A\,B)$ 664 s; for the identity ($N=13$) Kissat gave no answer in 20,000 s (below).

**Weak (B1) with (B2) without borders, identity (15 to 16 November).** `gcert.py 5 13 --b1 --b2 id --b2nb --front1`
(no (B3), no (B4), no wall lemma): the tree closes with 12,296 nodes closed and 4213 split, no node open and
none satisfiable; 28,685 s with three processes, 20,727 s of CaDiCaL time on the closed nodes, 102.3 GB of
LRAT proofs, each verified by `lrat-check` and by `cake_lpr`. $F$: 2608 variables, 259,620 clauses, SHA-256 of
the clause lines `4c411838...cbfefe4`. `gcover.py 5 13 runs/b1b2/w_id_13.txt.gz` (unpacked) `--front1`: complete
case split. So no five-state rule with (B1) in the weak reading and the image condition for the identity on
the neighbourhoods without a border synchronizes all lines $2,\dots,15$ (and, by the remark on the front in the
proof of Proposition 7.3, not even $2,\dots,14$); this contains Proposition 7.2 for the identity and
Proposition 7.1 for the identity (with 14 in place of 12). The other nine involutions
followed on 16 November (`gchain.py`, levels 3 to 11, 25 minutes in all); together they are Proposition 7.3.

**Stable generals: the certification is complete (16 November).** `certtree.py 14 ... --first 1 --last 167 --pump 14
--tlim 4 --workers 4` ended after 20,003 s: 17,196 nodes closed with verified LRAT proofs (35,384 s of CaDiCaL
time, 178.1 GB of proofs), one node with a complete half-line left for a longer limit (closed in 5 s), no
satisfiable node. With the subtrees 168 to 341 this is Theorem 6.4: 44,516 nodes closed for $F_{14}$ (93,207 s
of CaDiCaL time, 438.7 GB of proofs in all) and the one satisfiable node closed for the lines $2,\dots,15$;
`covercheck.py 14`: complete case split. The cubes have 5 to 18 transitions (most have 12 to 14). Sizes of the
two halves: 17,196 and 27,280 closed nodes for 167 and 174 subtrees.

**Stable state other than the initial state, and a fault of `gchain.py` (16 November).** `gchain.py ... --init A`
closed nine of the ten involutions (levels 3 to 11). For the identity it stopped after the level 10 (4597 nodes
closed, 1596 split, 111 satisfiable, 7945 s) with the message that the run had not finished. The run had
finished: `gchain.py` looked for the final line of `gcert.py` among the last 60 lines of the log, and the 111
satisfiable nodes are listed after it. The test now reads the whole output of the last run. The fault could
only stop a chain early, not close one wrongly. The chain for the identity was continued at the level 11.

**The node of the three rules with free border entries (16 November, solver answers).** With the 11 transitions
of $\gamma^\ast$ fixed, (B1) in the weak reading and a stable left end ($\delta(\ast,G,y)=G$), so that only the
entries $\delta(x,G,\ast)$ are added to the class of Theorem 6.4: the strict formula is satisfiable for the lines
$2,\dots,14$ and unsatisfiable for $2,\dots,15$ and $2,\dots,16$ (89 s and 93 s). So this half-line does not reach
the length 15 in that larger class either.

**Almost stable generals, five states (16 November, in progress).** `ladder.py 5 13 1` (Kissat, 1941 s): a rule
for $2,\dots,13$ with (B3) in which exactly one of the 21 entries is not `G`, namely $\delta(G,G,L)=B$
(`rules/almost_stable_GGL_2-13.txt`; it synchronizes exactly $2,\dots,13$ among $2,\dots,60$). This is one of the
entries in which Mazoyer's solution leaves `G` as well. The class "all entries `G` except $\delta(G,G,L)$" is
estimated at $3\cdot10^5$ nodes for the lines up to 14 (10 random descents, standard error $0.9\cdot10^5$),
the size of the class of Theorem 6.4, so it can be searched completely; a first pass is running. The class
"$\delta(x,G,y)=G$ unless $y=L$" is much larger: $7\cdot10^6$ after 10 descents and $5\cdot10^8$ after 20 (one deep
descent), and with $\delta(L,G,y)$ free as well $8\cdot10^9$. The neighbourhoods of the three rules of
Theorem 6.4 in the unrestricted class: no rule for $2,\dots,15$ differs from one of them in at most 6 of the
transitions that it uses (`near2.py`, Kissat, 28 s to 453 s per formula; distance 8 was not decided in 2300 s).

**Six states with a stable general (16 November, solver answers).** By Theorem 6.4 a minimal-time solution
with a stable general needs at least six states. Mazoyer's six-state solution does not satisfy (B1): of the 22
entries $\delta(x,G,y)$, $x,y$ not both in $\{G,\ast\}$, that its lines of lengths $3,\dots,300$ use, seven differ from
$G$, namely those for $(\ast,G,L)$, $(A,G,L)$, $(B,G,L)$, $(C,G,L)$, $(G,G,L)$, $(C,G,\ast)$ and $(C,G,G)$; it fires
from `GGG`, `*GG` and `GG*` only. We have not checked (B1) on the
solutions of Balzer (eight states) and Gerken (seven states), so we do not know the least number of states of
a solution with a stable general. With six states the formulas behave
like the five-state ones, a few lengths later: `mcopy.py 6 N --nocopy --strict --b1s --b3` (Kissat) returns
rules for $2,\dots,8$, $2,\dots,10$, $2,\dots,12$ and $2,\dots,14$ in 3 s, 9 s, 22 s and 83 s, and gives no answer for
$2,\dots,16$ in 1400 s. The rule for $2,\dots,14$ (`rules/k6_stable_general_2-14.txt`) synchronizes exactly
these lengths among $2,\dots,80$. With all four of Balzer's conditions ((B1) strong, (B2) with borders for
the identity, (B3), (B4)) the incremental solver `mcopy_inc.py` finds rules up to $2,\dots,12$ within 48 s
(`rules/k6_balzer_conditions_2-12.txt`, exactly these lengths among $2,\dots,80$); with (B1) strong and (B2)
alone it reaches $2,\dots,12$ after 72 s for the identity and 200 s for $(A\,B)$. The runs were stopped there;
none of these rules synchronizes a longer line, and nothing is claimed about six states.

**A stable firing state that is not the initial state (16 November, in progress; solver answers).** Theorem 6.4
is about the state `G` in which the first cell starts. A rule can also have a stable state from which it fires
that is not the initial state: the lines are $A\,L\cdots L$, and $G$ is another working state with (B1) in the
strong reading such that exactly `GGG`, `*GG` and `GG*` give `F`. (For the initial state the second condition
follows from the first, Lemma 6.1; here it is an assumption, because a line need not contain `G` at all.) Call
this class $\mathcal A$. The line of length 2 forces $\delta(\ast,A,L)=\delta(A,L,\ast)=G$, so the first cell is
`G` from time 1 on; the wall lemma holds for the cells $i\ge2$ with the same proof, which does not use the first
cell, and so do the gap bounds. The formula and the tree are those of Theorem 6.4 with the initial row
$A\,L\cdots$ (`gsat.py 5 N --b1s --b3 --nogh --wimp --wgap --front1 --init A`); the four working states have
four different roles, so there is no naming rule. Together with Theorem 6.4 a bound for $\mathcal A$ gives the
statement without reference to the initial state: no five-state solution has a stable state from which alone
it fires.

What is known so far: $\mathcal A$ has a rule for the lines $2,\dots,13$
(`rules/stable_firing_initA_2-13.txt`; it synchronizes exactly these lengths among $2,\dots,120$, and its table
satisfies the two conditions; found by `node_model.py` at a node that the first pass reported as satisfiable for
the level 12, where the strict formula of $2,\dots,14$ is unsatisfiable). So this class reaches 13, one less than
the class of Theorem 6.4 so far. Random descents estimate the tree at $4\cdot10^5$ to $5\cdot10^5$ nodes for
each of the levels 12, 13 and 14, six times the tree of Theorem 6.4; a first pass at the level 12 with the
incremental solver is running (338 subtrees), and every node that it finds satisfiable is tested with the strict
formulas of $2,\dots,13$, $2,\dots,14$, ... (`logs` of the session; not certified). A larger class that contains
both, five states and a separate start state that is never entered again (six states, `--init A`, and
$\delta(e)\ne A$ for all $e$), is estimated at $2.7\cdot10^6$ nodes at the level 12 and was not started.

**Conditions that do not prune (16 November, solver answers).** A minimal-time solution satisfies more than
the synchronization of the lines $2,\dots,N$, and three such conditions were tried as cheap substitutes for long
lines; each of them is satisfiable within seconds and so excludes nothing. (1) Single long lines: with four
states there are rules that synchronize the lines 2, 3 and $e$ for each $e\in\{9,10,11,12\}$ (`mcopy.py 4 3
--nocopy --extra e`, 0.2 s to 65 s), although no four-state rule synchronizes $2,\dots,9$; a rule can be tuned to
one long line. (2) Chains (`--chains N3 C`: for every $n\le N_3$ the first $C$ anti-diagonals after the
reflection contain no `F` except that the cells $1,\dots,C$ fire at the time $2n-2$, and the return chain
differs from the half-line): in the class of Theorem 6.4, with the lines $2,\dots,8$ complete and the chains for
all $n\le24$, $C=1,2$, or the lines $2,\dots,10$ and $n\le30$, $C=2$, a rule is found in 2 s to 16 s. Firing the
first cells in time is easy; the difficulty is to fire all cells. (3) The pumping lemma on a long half-line
(`--half 58 --pump 30`: the half-line in working states up to the anti-diagonal 58 and $\mathrm{PUMP}(n,n')$ for
all $4\le n<n'\le30$): with the lines $2,\dots,12$ of the class of Theorem 6.4 a rule is found in 21 s, and with
`--half 78 --pump 40` in 535 s. So the lines themselves, all of them up to $N$, are what excludes rules.

**Second checker on a sample (16 November).** `recheck_ct.py 14 g14_parts_1-167.txt g14_parts_168-341.txt --sample 600
--seed 20261116 --pump 14 --workers 2`: 600 of the 44,476 certified cubes, 1582 s; 600 verified again by `lrat-check`
and `cake_lpr` with the recorded formula digest, proof digest equal for 600, no failure.

**The satisfiable node and the length 15 (16 November).** With the 11 transitions of the node fixed,
`mcopy.py 5 N --nocopy --nosym --strict --b1s`: satisfiable for $N=14$ (14 s), unsatisfiable for $N=15$ (22 s,
certified, Theorem 6.4) and $N=16$ (22 s, solver answer). The search for a rule for $2,\dots,15$ elsewhere in
the class (formula $S_{15}\wedge D$ of Section 6) is running: `gcert.py`, three processes; Kissat on the same
formula as a whole has no answer yet.

**Yunès's form, identity: Kissat on the whole formula (15 to 16 November).** `kissat` on $F_I$ for the
identity, $N=13$ (2608 variables, 259,770 clauses): no answer in 20,000 s. The tree search closes the same
formula with 5219 s of CaDiCaL time on 2550 nodes.

**No return to the quiescent state (15 November).** The class $\delta(x,y,z)\ne L$ for $y\ne L$ (a cell that has
left the quiescent state never returns to it; `gsat.py 5 N --neq ... --front1`): rules for $2,\dots,8$ and for
$2,\dots,9$ are found (2 s, 538 s); for $2,\dots,10$ no rule in the first 30,000 nodes, and the tree is
estimated at $4\cdot10^6$ nodes (standard error $2.4\cdot10^6$). Not pursued.

**Stable generals, nodes with a complete half-line (15 November).** `certtree.py` splits a node that CaDiCaL does
not refute in 4 s; a node whose 12 to 15 transitions already determine the whole half-line up to the
anti-diagonal 27 cannot be split. Three such nodes occurred so far (half-lines of low complexity, one of them
a Sierpinski-like pattern over $\{L,B\}$ to the right of the constant cells `GAAB`); each is refuted and
certified in 6 to 7 s with a longer limit (`cert/g14_parts_open.txt`). The 36 top nodes and these three
were verified again with `cake_lpr` (`recheck_ct.py`), with the recorded digests. Without (B1): (B3w), (B4)
and (B2) without borders for the identity are estimated at $1.7\cdot10^9$ nodes at $N=13$, so the stable
general is what makes the image classes small.

**One condition of Yunès's form dropped (15 November, estimates).** Without (B4): $2.1\cdot10^4$ nodes at
$N=13$ and $2.2\cdot10^4$ at $N=14$ for the identity, $2.1\cdot10^3$ at $N=11$ for $(A\,B)$. Without (B3) and
(B4), that is (B1w) and (B2) without borders only: $3.9\cdot10^4$ nodes at $N=13$ for the identity; with (B4)
but without (B3): $3.6\cdot10^4$. So the tree is small because of the image condition; (B3) and (B4) hardly
matter. With (B4) and (B3) strong but without the image condition the weak class is estimated at
$4.2\cdot10^6$ nodes. The certified search for (B1w) with (B2) without borders, for all ten involutions, is
Proposition 7.3.

**A note on running several searches at once.** The kernel of the machine groups processes by session
(`sched_autogroup_enabled`), and the nice value of a process only counts within its group. Several searches
started from different shells therefore shared the processors equally, whatever their nice values: for
some hours the four processes of the main certification had two thirds of one core. Since 19:35 the
grouping is switched off. Timings of runs between about 16:00 and 19:35 on this day are not comparable
with the others.

**Other probes (15 November), not pursued.** Rules in which one working state never occurs in an interior cell
(`gsat.py 5 N --nointerior X --front1`): for each of $X=G,A,B$ a rule for $2,\dots,8$ is found in seconds;
$2,\dots,9$ was not decided in 250 s. Rules that synchronize at a time chosen by the solver (`ftime.py`):
with the time fixed to $2n-2$ the encoder reproduces $N_4=8$ (four states: $2,\dots,8$ satisfiable in 0.7 s,
$2,\dots,9$ unsatisfiable in 37 s); four states with any firing time in $[2n-2,3n+2]$: a rule for $2,\dots,6$
(firing times 3, 5, 11, 14, 10, so nothing regular), and $2,\dots,8$ not decided in 120 s. The free firing
time makes the formulas much harder, and no five-state run was made.
