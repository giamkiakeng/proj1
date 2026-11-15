# Five states: structured searches

Working notes and programs for the open question of the paper in `../paper`: is there a five-state
minimal-time solution of the firing squad synchronization problem? Nothing here answers it. The programs
search restricted classes of five-state rules, and this file records what each search found.

Conventions. States `L` (quiescent), `G` (general), auxiliary `A`, `B`, firing `F`; `*` is the border. A
*line* is the diagram $C_n$ of the line of length $n$; a rule *synchronizes* $n$ if $C_n$ is all `F` at time
$2n-2$ and has no `F` before. "UNSAT" means that a SAT solver or an exhaustive enumeration proved that the
class is empty for the stated lengths; "unknown" means that the run was stopped. No proof certificate
(DRAT/LRAT) has been produced yet for the results below, so they have the status of solver answers,
cross-checked where the table says so.

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
| copies, wake 4, static general 2, periodic (3, 2) | satisfiable for $N\le 10$ (`mcopy.py` 51 s; `mcopy_inc.py` 42 s); the rule found synchronizes exactly 2..10 (`rules/strict_2-10.txt`) |
| the same, $N\ge 11$ | unknown (see the log at the end) |
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
| radius 2 | 649 | 2,185 | unknown (90 s; a longer run is in the log) |

Controls: with six states and the single-cell window the formula is satisfiable and returns Mazoyer's rule.

## 5. Log of long runs

(appended as runs finish)
