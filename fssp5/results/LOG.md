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

## Session 2 (continued)
- delta13 (results/delta13.txt): lazyk.py 13 200 --germ uniformA_2-12.txt, iteration 1 SAT in 107.9 s;
  synchronizes 2..13, fails n=14 (fires at 21 < 26); same 22 half-line neighbourhoods as delta12
  below anti-diagonal 78; PUMP to 40; uniform pre-firing A for 4 <= n <= 13.
- Left-border lemma (paper Lemma 3.5): proved; checked on Mazoyer (stretches <= 6, n <= 400).
  delta12/delta13 germ: CLOSED to anti-diagonal 1300 and refuted at n=518 (s=2, L=1, Y=259).
- Germ classification (germdfs, anti-diagonal 78, PUMP to 40):
  K<=14: 244 germs; 230 refuted at N=10 (one LRAT, 4.4 s / 0.6 s); 14 refuted by the
         left-border lemma with s=1 (n <= 163).  => c_78 >= 15 for every 5-state solution.
  K<=16: 9,787 germs; 8,824 refuted at N=10 (one LRAT, 2.0 GB, 556 s / 51 s);
         of the 963 survivors 929 refuted by the lemmas on extended half-lines (1300/3300/10000);
         34 left (results/germs/K16_surv34.txt), completion tests at N=16 running.
  Half-line arguments alone: K<=14 218/244, K<=16 >= 8,263/9,787.
- Equivariant classes (equiv.py, N=10, 120 s): sigma=(A B) UNSAT in 0.7 s; (G A), (G A B)-type and
  others UNKNOWN at 120 s (scan stopped).  Long-line tests of the delta12 germ (germlong.py):
  2..10 + {20} SAT; + {30}, {40} UNKNOWN (300 s).  Band tests (germband.py, h=4): UNKNOWN (300 s).
- lazyk_germ (delta12 germ, lengths 2..14, links): stopped after ~63 min without answer
  (architecture refuted by the lemma anyway).
- delta13' (results/delta13_chaotic.txt): first germ of K16_surv34 (chaotic half-line, complexity 16);
  completion for 2..12 in 2.4 s, for 2..13 in 442 s (rerun 485 s), fails n=14; 2..14 UNKNOWN (600 s).
- germext2 (streaming, N=20000): 2 more of the 34 K<=16 survivors refuted (s=3, L=2); 32 remain.
- fsspdfs -g (germ fixed, DFS over reflected transitions): no answer within 300 s even for N=8.
- Mirrored lemma (paper Remark 3.7) checked on Mazoyer: stretches <= 7 (n <= 300, n = 6 mod 7).
- delta14 (results/delta14.txt): lazyk.py 14 200 --germ results/delta13_chaotic.txt, iteration 1 SAT in 1758 s;
  synchronizes 2..14 (checked by fsspcheck and by an independent Python simulation), fails n=15 (fires at 22 < 28).
  Same 16-neighbourhood chaotic germ as delta13'.  NEW FRONTIER: N_max(5) >= 14.
- germdfs cross-checked by an independent Python enumerator (germdfs_check.py, pumping cones from pumping.py):
  identical germ sets for K=12 (2), 13 (28), 14 (244).
- 2..13 tests on the K<=16 survivors (germlong.py, 900 s): #0 SAT (delta13'), #1 UNKNOWN, #2 #3 #4 UNSAT, #5 SAT, ...
- Restricted class "germ of delta14 + pre-firing configuration L G^(n-2) B for 4<=n<=N" (src/class_prefire14.py):
  N=14 SAT (delta14 is in the class); N=15 UNSAT (kissat, about 30 min).  So delta14's mechanism does not
  extend to length 15.  Unrestricted delta14 germ at 2..15: kissat without links UNKNOWN after 4 h; with links
  and CaDiCaL still running.  delta14c germ at 2..15: UNKNOWN (2400 s).
