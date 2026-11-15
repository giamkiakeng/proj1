# Five states: structured searches

Working notes and programs for the open question of the paper in `../paper`: is there a five-state
minimal-time solution of the firing squad synchronization problem? Nothing here answers it. The programs
search restricted classes of five-state rules, and this file records what each search found.

Conventions. States `L` (quiescent), `G` (general), auxiliary `A`, `B`, firing `F`; `*` is the border. A
*line* is the diagram $C_n$ of the line of length $n$; a rule *synchronizes* $n$ if $C_n$ is all `F` at time
$2n-2$ and has no `F` before. "UNSAT" means that a SAT solver or an exhaustive enumeration proved that the
class is empty for the stated lengths; "unknown" means that the run was stopped. Proof certificates (LRAT) exist for the results of Section 4 and for Propositions 7.1 and 7.2, where stated there; the
other computer results have the status of solver answers, cross-checked where the tables say so. Lemmas 6.1
to 6.5 are proved by hand.

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
| `gcert.py` | the tree search of `gsat.py` with a certificate for every closed node: a new CaDiCaL process per node with a time limit and an LRAT proof, checked by `lrat-check` and, if `CAKELPR` names its binary, by the verified checker `cake_lpr`; a node that is not refuted in time is split. Resumable; `--recheck` rebuilds every cube formula, compares the SHA-256 digests and verifies the proofs again |
| `gcover.py` | checks without a solver that the certified cubes of `gcert.py` are a complete case split; shares no code with `gcert.py` |
| `weakwalls.py` | redundant clauses of Lemmas 6.4 and 6.5 (weak reading); `gsat.py --wwalls`, `gcert.py --wwalls` |
| `minit.py` | the lines start from `X L ... L` for another working state `X` (`gcert.py --init X`) |
| `check_rule_formula.py`, `check_weak_lemmas.py`, `check_wwalls_enc.py` | tests: a rule of a class that synchronizes $2,\dots,N+2$ must satisfy the formula of `gcert.py` at $N$; the statements of Lemmas 6.4, 6.5 and 6.2' on the diagrams of given rules |
| `ftime.py` | CNF for rules that synchronize the lines $2,\dots,N$ at some time chosen by the solver, not necessarily minimal (exploratory, Section 8) |

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
| static general: the first cell is `G` from time 1 (or 2) on | satisfiable for 2..12 (incremental, 9 min); $N=13$ running |
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
| the class, lines $2,\dots,N$ | rule for 2..13 (`rules/stable_generals_2-13.txt`, Kissat, 428 s); $N=14$: Kissat stopped after 58 min without an answer |
| the 21 cases, `mcopy_inc.py`, 900 s each (stopped after five cases) | case a with $\delta(A,L,\ast)=L$: refuted at 12 (236 s); case a with $G$ and case a with $B$: rules for 2..12 (the rule for 2..13 is in case a with $B$); case b with $\delta(A,L,\ast)=L$ and $\delta(B,L,\ast)\in\{L,A\}$: refuted at 3; case b with $L$, $G$: rule for 2..12 |
| the 126 half-lines up to the anti-diagonal 6 as cases (`germw 6 40`, `germscan.py`, 20,000 conflicts per call) | 5 refuted at $N\le11$; in the other 121 a rule for 2..9 (10 cases), 2..10 (73), 2..11 (35) or 2..12 (3) is found before the budget ends |
| with the conditions of Lemmas 6.1 and 6.3 on the first 10 rows after the reflection of the lines up to 40 (`--early 40 10 --wgap`) | rule for 2..11 (incremental, 300 s; it has three adjacent generals on the lines $12,\dots,50$ between 10 and 18 steps after the reflection, just after the rows constrained); $N=12$ running |
| lines $2,\dots,N$ and the complete line 20 (`--extra 20`) | rule for 2..9 and 20 (incremental, 451 s); its half-line is periodic with period 4 in time and space, which fits the length 20 |
| lines 2, 19, 22 complete, and PUMP$(n,n')$ for $n<n'\le22$ (`mcopy.py 5 2 --extra 19,22 --pump 22`) | not decided: no answer from the incremental solver in 8 minutes; Kissat running |

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

Status of the search for the lines $2,\dots,14$ (`runs/stable14/`): in progress, no rule found so far.
The first 167 of the 341 subtrees are closed by `germsat.py` (169,041 nodes, 13.2 hours of solver time; from
subtree 100 on with the clauses PUMP$(n,n')$, $4\le n<n'\le14$, which follow from the lines and make the
subtrees with $\delta(A,L,L)=B$ about 1.5 times cheaper). The other 174 subtrees are being searched by
`certtree.py`, which does the same search with a new CaDiCaL process at every node (4 s; on a time-out the
node is split) and has `lrat-check` verify the LRAT proof of every node that it closes; on one subtree that
`germsat.py` closed in 16 minutes it needed 20 minutes and closed it with 275 checked proofs. When this is
done, the first 167 subtrees will be certified in the same way. If all subtrees close, no five-state rule with
a stable general synchronizes all lines $2,\dots,16$ (the formula uses Lemma 6.2 up to the anti-diagonal 27 and
the front cell $(13,14)$, which need the lines up to 16).

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

**Lemma 6.4 (interior walls).** Let $\delta$ satisfy (B1w) and (B3w) and synchronize the line of length
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

**Lemma 6.5 (gaps, weak reading).** Let $\delta$ satisfy (B1w) and (B3w) and synchronize the line of length
$n\ge3$, and let $t\le2n-4$. With $M$ as in Lemma 6.3, put
$M_b(1)=|W'|$ and $M_b(\ell)=|W|\,|W'|^{\ell-1}+M_b(\ell-1)$.

1. If the interior cells $p<q$ are in state $G$ at time $t$, $q-p=\ell+1\ge2$, and no cell between them is in
   state $G$ at time $t$, then $2n-3-t\le M(\ell)$.
2. If the interior cell $q$ is in state $G$ at time $t$ and no interior cell to its left is, then
   $2n-3-t\le M_b(q-1)$; if the interior cell $p$ is in state $G$ at time $t$ and no interior cell to its
   right is, then $2n-3-t\le M_b(n-p)$.

For five states $M_b(1),M_b(2),M_b(3)=3,15,51$.

*Proof.* By Lemma 6.4 (b) an interior cell in state $G$ stays in state $G$ up to time $2n-3$, and since there
is one, every cell is in state $G$ at time $2n-3$ by Lemma 6.4 (c).
1. During $[t,2n-3]$ the $\ell$ cells between $p$ and $q$ have constant neighbours, so their configuration
evolves on its own. Let $s\ge t$ be the least time at which one of them is in state $G$; $s\le2n-3$. The
configurations at the times $t,\dots,s-1$ lie in $W'^{\ell}$ and are pairwise distinct: after a repetition
they would be periodic, and no cell of the gap would be in state $G$ at time $2n-3$. Hence
$s-t\le|W'|^{\ell}$. If $s=2n-3$ we are done. Let $s\le2n-4$. For $\ell=1$ the cells $p,p+1,p+2$ would be in
state $G$ at time $s$, contrary to Lemma 6.4 (a). For $\ell\ge2$, by Lemma 6.4 (a) some cell of the gap is not
in state $G$ at time $s$; it lies between two cells of $[p,q]$ in state $G$ at distance $\ell'+1$,
$1\le\ell'<\ell$, with no cell in state $G$ between them, and induction gives
$2n-3-s\le M(\ell')\le M(\ell-1)$.
2. By induction on $\ell=q-1$; the second statement is the mirror image. The cells $1,\dots,\ell$ have the
border on the left and the constant state $G$ on the right during $[t,2n-3]$. For $\ell=1$: the cell 1 is not
in state $G$ at a time $u\le2n-4$ (Lemma 6.4 (a) for the positions 0, 1, 2), so its states at the times
$t,\dots,2n-4$ lie in $W'$, and they are pairwise distinct because the cell is in state $G$ at time $2n-3$.
For $\ell\ge2$: let $s\ge t$ be the least time at which one of the cells $2,\dots,\ell$ is in state $G$. The
configurations of the cells $1,\dots,\ell$ at the times $t,\dots,s-1$ lie in $W\times W'^{\ell-1}$ and are
pairwise distinct as before, so $s-t\le|W|\,|W'|^{\ell-1}$. If $s\le2n-4$, the leftmost of the cells
$2,\dots,\ell$ in state $G$ at time $s$ is an interior cell $q'$ with no interior cell in state $G$ to its
left, and induction gives $2n-3-s\le M_b(q'-1)\le M_b(\ell-1)$. $\square$

Consequently, at a time $t\le2n-4$ with $\rho=2n-3-t$: no two interior cells at a distance $d\ge2$ with
$M(d-1)<\rho$ are both in state $G$ (between them lies a gap of length at most $d-1$, by Lemma 6.4 (a)), and no
interior cell $y$ with $M_b(y-1)<\rho$ or $M_b(n-y)<\rho$ is in state $G$. `weakwalls.py` adds these clauses
and those of Lemma 6.4 (`--wwalls`). `check_weak_lemmas.py` finds no violation of Lemmas 6.4, 6.5 and 6.2' on
the diagrams of the 31 stored rules that satisfy (B1w) and (B3w) on the transitions they use, nor on 41 rules
for $2,\dots,10$ generated for this test with seven different beginnings of the first cell (in some of them the
lines 3 and 4 have no interior cell in state $G$); these 41 rules and five of the stored ones, all of which
synchronize $2,\dots,10$, satisfy the formula with the clauses at $N=8$ (`check_wwalls_enc.py`).

Sizes (estimates by random descents in the tree of `gsat.py`, 30 descents each, budget 3000; standard errors
30 to 50 per cent, and such estimates tend to be too low): the weak class with (B3) in the strong reading,
lines $2,\dots,14$: $4\cdot10^6$ to $2\cdot10^7$ nodes in four runs, with or without the clauses of Lemmas
6.4 and 6.5, which do not make the tree smaller; with (B3w): $1.3\cdot10^7$; the strong class of this section:
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
or 14. A second verification of the proofs with `cake_lpr` (`gcert.py ... --recheck`, which also compares
the digests) is recorded in Section 8.

Yunès admits a state other than $G$ in (B1), (B3) and (B4). A state $g$ that is stable, fires in threes and
is not the initial state of the general is the same class with the roles of two names exchanged: the lines
start from `A L ... L` and the conditions speak about $G$ (`gcert.py --init A`). Lemma 6.2' does not use the
initial configuration, so the half-line has no cell $i\ge2$ in state $G$ in this class either. This class has
rules for $2,\dots,9$ with $I$ the identity; the search for longer lines is running (Section 8).

## 8. Log of long runs

**Tree sizes (15 November).** Estimates of the number of nodes of the tree of `gsat.py` (budget 3000 conflicts
per node) by random descents (Knuth's estimator, `gsat.py ... --knuth 30` or `40`); the standard error of the
mean is given, but the distribution is heavy-tailed and the estimates are to be read as orders of magnitude.
No descent ended in a model unless stated.

| class (five states) | lines | estimated nodes | standard error |
|---|---|---|---|
| no class (the open problem) | 2..15 | $3\cdot10^{18}$ | same order |
| stable general, Section 6 (`--b1s --b3 --nogh --wimp --wgap`) | 2..14 | $1.07\cdot10^6$ | $0.41\cdot10^6$ |
| (B1) weak, (B3) strong (`--b1 --b3 --noghw`) | 2..14 | $3.6\cdot10^6$; with another seed $1.7\cdot10^7$ | $1.0\cdot10^6$; $0.8\cdot10^7$ |
| the same with the clauses of Lemmas 6.4, 6.5 (`--wwalls`) and PUMP (`--pump 14`) | 2..14 | $1.2\cdot10^7$; $5.2\cdot10^6$ (two seeds) | $0.7\cdot10^7$; $1.7\cdot10^6$ |
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
of them (299 s, 244 s, 795 s). The recheck of the 2550 cubes for the identity is running. Independently of the
tree, Kissat refutes each of the three formulas $F_I$, written by `writef.py`, as a whole (no proof kept):
$(L\,B)$ 216 s, $(L\,A)$ 220 s, $(A\,B)$ 664 s; for the identity ($N=13$) Kissat is running.

**Other probes (15 November), not pursued.** Rules in which one working state never occurs in an interior cell
(`gsat.py 5 N --nointerior X --front1`): for each of $X=G,A,B$ a rule for $2,\dots,8$ is found in seconds;
$2,\dots,9$ was not decided in 250 s. Rules that synchronize at a time chosen by the solver (`ftime.py`):
with the time fixed to $2n-2$ the encoder reproduces $N_4=8$ (four states: $2,\dots,8$ satisfiable in 0.7 s,
$2,\dots,9$ unsatisfiable in 37 s); four states with any firing time in $[2n-2,3n+2]$: a rule for $2,\dots,6$
(firing times 3, 5, 11, 14, 10, so nothing regular), and $2,\dots,8$ not decided in 120 s. The free firing
time makes the formulas much harder, and no five-state run was made.
