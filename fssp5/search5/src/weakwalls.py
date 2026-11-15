"""weakwalls.py -- redundant clauses for the weak reading of (B1) with delta(G,G,G) = delta(*,G,G) = delta(G,G,*) = F.

Hypotheses: delta(x, G, y) = G for working states x, y that are not both G; the three neighbourhoods above give
F; the line n is synchronized at time 2n-2.  Then, in the line n (README, Lemmas 6.4 and 6.5):
  (a) before time 2n-3 no three adjacent positions are all "G or border";
  (b) an interior cell (2 <= i <= n-1) in state G at a time t <= 2n-4 is in state G at time t+1;
  (c) if an interior cell is in state G at time 2n-3, all cells are;
  (d) two interior cells in state G at time t <= 2n-4 at a distance d >= 2 need 2n-3-t <= M(d-1),
      M(1) = 3, M(l) = 3^l + M(l-1);
  (e) an interior cell y in state G at time t <= 2n-4 needs 2n-3-t <= Mb(y-1) and 2n-3-t <= Mb(n-y),
      Mb(1) = 3, Mb(l) = 4*3^(l-1) + Mb(l-1)   (the gap between a border and the nearest interior wall).
The clauses are added for the complete lines nmin..N of the model."""
MG = [0, 3, 12, 39, 120, 363, 1092]
MB = [0, 3, 15, 51, 159, 483, 1455]

def add_weak_walls(M, noghw=True):
    E, N = M.E, M.N
    count = 0
    for n in range(max(3, M.nmin), N + 1):
        E.level = n
        def g(t, i):
            if i < 1 or i > n:
                return True                      # border
            if noghw and i >= 2 and t + i <= 2 * n - 2:
                return False                     # half-line cell beyond the first: not G (unit clause of the class)
            x = M.cell(n, t, i)
            if isinstance(x, int):
                return x == 1
            return x[1]
        def add(lits):
            nonlocal count
            if any(v is False for v in lits):
                return                           # a literal "is G" that is false: the clause -v ... is satisfied
            E.add([-v for v in lits if v is not True]); count += 1
        for t in range(1, 2 * n - 3):                                   # 1 <= t <= 2n-4
            rho = 2 * n - 3 - t
            for i in range(1, n + 1):                                   # (a)
                add([g(t, i - 1), g(t, i), g(t, i + 1)])
            interior = [i for i in range(2, n) if g(t, i) is not False]
            for i in interior:                                          # (b)
                E.add([-g(t, i), g(t + 1, i)] if g(t, i) is not True else [g(t + 1, i)]); count += 1
            for x in interior:
                for y in interior:                                      # (d)
                    d = y - x
                    if d >= 2 and d - 1 < len(MG) and MG[d - 1] < rho:
                        add([g(t, x), g(t, y)])
                if x - 1 < len(MB) and MB[x - 1] < rho:                 # (e), left border
                    add([g(t, x)])
                if n - x < len(MB) and MB[n - x] < rho:                 # (e), right border
                    add([g(t, x)])
        t = 2 * n - 3                                                   # (c)
        for i in range(2, n):
            for j in (i - 1, i + 1):
                gi, gj = g(t, i), g(t, j)
                if gi is False or gj is True:
                    continue
                E.add(([-gi] if gi is not True else []) + ([gj] if gj is not False else [])); count += 1
    return count
