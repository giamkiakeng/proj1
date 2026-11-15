# Five states: structured searches

Working notes and programs for the open question of the paper in `../paper`: is there a five-state
minimal-time solution of the firing squad synchronization problem? Nothing here answers it. The programs
search restricted classes of five-state rules, and this file records what each search found.

Conventions. States `L` (quiescent), `G` (general), auxiliary `A`, `B`, firing `F`; `*` is the border. A
*line* is the diagram $C_n$ of the line of length $n$; a rule *synchronizes* $n$ if $C_n$ is all `F` at time
$2n-2$ and has no `F` before. "UNSAT" means that a SAT solver or an exhaustive enumeration proved that the
class is empty for the stated lengths; "unknown" means that the run was stopped. Proof certificates (LRAT) exist for the results of Section 4 where stated there; the other results have the
status of solver answers, cross-checked where the tables say so.

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
- The classes of Section 3 that `decdfs.c` exhausts are also unsatisfiable for `msim.py`.

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

**Lemma (walls).** Let $\delta$ be a minimal-time solution, with any number of states, such that

- (B1), strong reading: $\delta(x,G,y)=G$ unless $x$ and $y$ are both in $\{G,\ast\}$, and
- (B3), weak reading: $\delta(G,G,G)=\delta(\ast,G,G)=\delta(G,G,\ast)=F$.

Then the first cell is in state $G$ at every time before the firing time, and on the half-line no cell
$i\ge2$ is ever in state $G$.

*Proof.* A cell of the half-line in state $G$ keeps this state: by (B1) it could only change if both its
neighbours were in $\{G,\ast\}$, and then it would fire by (B3), which never happens on the half-line. For
the first cell this gives the first claim. Suppose that the cell $p\ge2$ of the half-line is in state $G$ at
some time $t_w$, hence at all later times. Let $n$ be so large that $t_w+p\le 2n-2$. By the agreement lemma
(Lemma 2.2 of the paper) the cell $p$ of the line of length $n$ is in state $G$ at time $t_w$, and by (B1)
and (B3) it stays in this state until the firing time. So from time $t_w$ on, the cells $1,\dots,p-1$ of the
line have the constant right neighbour $G$: their states at the times $t\ge t_w$ are determined by their
states at time $t_w$, which are those of the half-line and do not depend on $n$. Then the first cell would
be in state $F$ for the first time at the same time in the lines of lengths $n$ and $n+1$, a contradiction.
$\square$

So in this class a general is a wall that no information crosses, a wall can only appear after the echo of
the right end has passed, and the half-line is a diagram over $\{L,A,B\}$ next to a constant $G$. The paper
(Proposition 6.6) excludes five states under (B1)-(B4), where (B2) is the image condition; the question here
is whether (B1) and (B3) alone suffice.

| class (five states) | result |
|---|---|
| (B1) strong, (B3) weak, with the conclusions of the lemma added as clauses | satisfiable for 2..12 (incremental, 8 s in one run; another run was stopped at $N=12$ after 95 s); $N=13$ running |
| (B1) strong, (B3) strong (exactly `GGG`, `*GG`, `GG*` fire) | satisfiable for 2..12 (incremental, 75 s); the rule synchronizes exactly 2..12 (`rules/stable_generals_2-12.txt`); $N=13$ running |
| the same, with the necessary conditions of the paper for the lines up to 40 (no `F` in the first 10 rows after the reflection, return chain different from the half-line, half-line without `F` to the anti-diagonal 79) and PUMP$(n,n')$ for $4\le n<n'\le40$ | satisfiable for 2..8 (incremental, 142 s); running |
| static general from time 1 and (B3) strong, same necessary conditions | satisfiable for 2..10 (incremental, 19 min); running |
| (B1) weak, (B3) strong, (B4), same necessary conditions | satisfiable for 2..9 (incremental, 4 min); running |
| image solutions with $I$ the identity, necessary conditions with 8 rows and without PUMP | satisfiable for 2..10; running |

Stronger necessary conditions were added after looking at the rules found: `--chains N3 C` (for every line up
to $N_3$: no `F` on the first $C$ anti-diagonals of the reflected triangle, and the cells $1,\dots,C$ fire at
$2n-2$), `--early N2 T` with $T\ge N_2$ (no `F` before $2n-2$ anywhere in the lines up to $N_2$) and
`--rfire C` (the last $C$ cells of these lines fire at $2n-2$). Mazoyer's table satisfies all of them, and the
rules found before violate them. They still do not decide the class: with the lengths up to 18 (no early
`F`, three cells at each end fire at $2n-2$; chains up to 24) the formula is satisfiable already for
$\delta(A,L,L)=A$, $\delta(A,L,\ast)=B$ (Kissat, 83 s), by a rule whose two ends fire at time $2n-2$ on
every line tested ($n\le 30$) while the cells between them never fire. As in Section 7 of the paper, the
conditions that are cheap to state do not constrain the middle of the firing row.

Mazoyer's table (six states, lengths from 3) satisfies the necessary conditions as encoded (`mcopy.py 6 12
--nmin 3 --nocopy --nosym --early 40 12 --pump 40 --fix mazoyer6.txt`: satisfiable).

The half-lines of this class cannot be listed exhaustively the way the germs of low complexity are listed in
the paper: `germw.c` (all half-lines over $\{L,A,B\}$ with the conditions on the front and PUMP) does not
finish even to the anti-diagonal 20.

## 7. Log of long runs

(appended as runs finish)
