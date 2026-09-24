# Experiment log (5-state minimal-time FSSP)

All times single core (Intel/AMD cloud vCPU), kissat 4.x (git HEAD 2026-09) unless noted.
"MT(k,2..N)" = full lengths 2..N; "C_inf(M)" = half-line to anti-diagonal M (never fires);
"PUMP(N')" = pumping pairs 4<=n<n'<=N'; "BAND(h,Nb)", "CORNER(h,Nb)" = partial triangles.

## Calibration
- k=4: MT(4,2..9) UNSAT (24.7 s); MT(4,2..8) SAT; DFS count of partial rules:
  N=5: 828,670; N=6: 64,299; N=7: 536; N=8: 27; N=9: 0 (DFS nodes ~1.09e8).
  Lazy CEGAR with C_inf(78): UNSAT with lengths {2..8} (46.6 s, CaDiCaL 1.9.5).
  => reproduces Balzer (1967) / Sanders (1994), without assuming d(*,L,L)=L.
- k=6: Mazoyer's rule (from Duprat's Coq development) passes fsspcheck for 3<=n<=3000
  and satisfies every constraint family (soundness test).
- k=6: MT(6,2..12)+C_inf(78)+PUMP(40): SAT (534 s) but the model fails at n=13 ("lucky").

## k=5, plain encoding
- MT(5,2..10) SAT (10.8 s), fails n=11.  MT(5,2..11) SAT.  MT(5,2..12) SAT (~20 min, --sat), fails n=13.
- MT(5,{2..9,16}) SAT (23.6 s); MT(5,{2..9,20}) SAT (82 s): one long length is easy to satisfy by luck.
- Lucky rules: periodic half-line background (violate PUMP) or chaotic half-line (fires eventually).

## k=5, strengthened
- MT(5,2..8)+C_inf(78)+PUMP(40): SAT (68.7 s), fails n=9.
- MT(5,2..10)+C_inf(78)+PUMP(40): SAT (755.6 s), fails n=11; its half-line has a speed-1/3 signal.
- MT(5,2..6)+C_inf(98)+PUMP(50)+BAND(2,50): SAT (190.8 s); fires cells 1,2 correctly for all n<=50;
  half-line has front, ".G.G" wake and a speed-1/3 signal.
- MT(5,2..6)+C_inf(98)+PUMP(50)+BAND(2,50)+CORNER(6,50): SAT (342.5 s); fires at relative time 7.
- MT(5,2..8)+C_inf(78)+PUMP(40)+BAND(3,40): SAT (222.5 s), fails n=9.
- Lazy CEGAR + C_inf(78) (no pump): lengths 2..11 satisfiable (iteration 6 at 773.9 s).
- Structural cubes (front map f(x)=d(x,L,L) on the orbit of G, reflection r(x)=d(x,L,*)!=f(x)):
  201 cubes; on MT(5,2..12)+C_inf(78)+PUMP(40) with 30k-conflict budget about 40% are refuted instantly.
