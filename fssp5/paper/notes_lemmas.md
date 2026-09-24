# Working notes: lemmas (to be turned into LaTeX)

Notation. S = {L, G, F} ∪ Aux, W = S \ {F}; border symbol `*`.
δ : (W∪{*}) × W × (W∪{*}) → S, with δ(L,L,L) = δ(L,L,*) = L.
C_n(t,i), 0 ≤ t, 1 ≤ i ≤ n : line of length n, C_n(0,·) = G L^{n-1}.
C_∞(t,i), i ≥ 1 : half line, C_∞(0,·) = G L^ω, left border only.
Minimal time: C_n(2n-2, i) = F ∀i and C_n(t,i) ≠ F ∀t < 2n-2.

L1 (light cone). C_n(t,i) = C_∞(t,i) = L for t < i-1.
   Induction on t; uses δ(L,L,L) = δ(L,L,*) = L.

L2 (agreement). C_n(t,i) = C_∞(t,i) whenever t + i ≤ 2n-2.
   Induction on t. For i = n we have t ≤ n-2, both sides L by L1.
   For i < n all three neighbours have coordinate sum ≤ t+i and i+1 ≤ n.

L3 (return chain). For a minimal-time solution, n ≥ 2, 1 ≤ i ≤ n:
   C_n(2n-1-i, i) ≠ C_∞(2n-1-i, i).
   i=1: C_n(2n-2,1)=F, C_∞(2n-2,1) = C_{n+1}(2n-2,1) ≠ F (L2 with n+1).
   i → i+1: left/centre neighbours at time 2n-2-i have sums 2n-3, 2n-2: agree (L2);
   so the right neighbours (sum 2n-1) must differ.
   Corollary (front): s_i := C_∞(i-1,i) ≠ L for all i; δ(s,L,*) ≠ δ(s,L,L) on the front orbit.

L4 (C_∞ never fires). C_∞(t,i) ≠ F for all t,i  (choose n with t+i ≤ 2n-2 and t < 2n-2).

L5 (triangle). R_n = {(t,i): 1≤i≤n, t+i ≥ 2n-1, t ≤ 2n-2}. Every cell of R_n at time t
   has its three neighbours at time t-1 either in R_n, on anti-diagonals 2n-3 / 2n-2
   (C_∞ by L2), or the border. So C_n|R_n is a function of the input word
   J_n(k) = (C_∞(n-3+k, n-k), C_∞(n-2+k, n-k)), 0 ≤ k ≤ n-1, computed in relative
   coordinates τ = t-(n-1), k = n-i by a rule that does not depend on n (except that the
   left border sits at k = n).

L6 (pumping). cone(n) := input positions on which the relative cell (τ,k) = (n-1,0)
   depends (BFS). For n ≥ 4 the cone avoids the left border and
   cone(n) = {(0,2n-2)} ∪ {(k,2n-3),(k,2n-2): 1 ≤ k ≤ ⌊n/2⌋} ∪ ({(⌈n/2⌉,2n-3)} if n odd).
   If J_n = J_{n'} on cone(n) for some n' > n, then C_{n'}(n'+n-2, n') = C_n(2n-2, n) = F
   with n'+n-2 < 2n'-2: contradiction. So every minimal-time solution satisfies
   PUMP(n,n') for all 4 ≤ n < n'.  (Verified numerically: Mazoyer, 4≤n<n'≤120: 0 violations.)

T7 (front zone). Co-moving frame F_t(j) = C_∞(t, t+1-j) (depth j behind the front):
   F_{t+1}(j) = δ(F_t(j), F_t(j-1), F_t(j-2)) for t ≥ j, F_j(j) = C_∞(j,1).
   If all depth rows are eventually periodic with a common period P from time T(j),
   then limsup T(j)/j ≥ 3/2: the periodic front zone cannot overtake a line of
   speed 1/3 (in original coordinates) — cone(n) ends exactly on the line i = t/3.
