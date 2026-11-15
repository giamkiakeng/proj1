# Five states: structured searches

Working notes and programs for the open question of the paper in `../paper`: is there a five-state
minimal-time solution of the firing squad synchronization problem? Nothing here answers it. The programs
search restricted classes of five-state rules, and this file records what each search found.

Conventions. States `L` (quiescent), `G` (general), auxiliary `A`, `B`, firing `F`; `*` is the border. A
*line* is the diagram $C_n$ of the line of length $n$; a rule *synchronizes* $n$ if $C_n$ is all `F` at time
$2n-2$ and has no `F` before. "UNSAT" means that a SAT solver or an exhaustive enumeration proved that the
class is empty for the stated lengths; "unknown" means that the run was stopped. Proof certificates (LRAT) exist for the results of Section 4 and for Proposition 7.1, where stated there; the
other computer results have the status of solver answers, cross-checked where the tables say so. Lemmas 6.1
to 6.3 are proved by hand.

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
clauses of Lemmas 6.1 and 6.3.

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

## 7. Balzer's conditions, taken apart

Proposition 6.6 of the paper excludes five states under the four conditions (B1)-(B4) together. Which of
them are needed? (B1): stable general. (B2): image condition $\delta(I(z),I(y),I(x))=I(\delta(x,y,z))$ for an
involution $I$ of the working states, also at the borders. (B3): exactly `GGG`, `*GG`, `GG*` give `F`.
(B4): $\delta(G,v,G)=G$ for $v\ne G$. Strong reading unless stated.

**Proposition 7.1 (computer-assisted).** No five-state rule that satisfies (B2), for some involution $I$ of
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
the identity, and for the identity Kissat refutes the formula (529 s) and the certificate is being produced.
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

## 8. Log of long runs

(appended as runs finish)
