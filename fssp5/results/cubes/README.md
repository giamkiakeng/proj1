# Cube-and-conquer logs (paper, Appendix B.4)

`cube_logs.tar.gz` holds one line per cube run: `<cube index> <UNSAT|UNKNOWN|SAT> <seconds>`.

- `cc14c/`: first labelling (germ of delta14c), lengths 2..15, 2,731 cubes from `march_cu -d 12`.
  `w0.log`, `w1.log`: CaDiCaL under assumptions (`src/cnfcubes.py`, budgets up to 2e6 conflicts);
  `r*.log`, `kr*.log`: Kissat on formula + cube (`src/cubekissat.py`, 300 s per cube, reverse order).
- `cc16/`: second labelling (germ #16 of `germs/K16_remaining16.txt`, the germ of delta14d), lengths 2..15,
  3,070 cubes; `w*`, `u*`, `v*`: passes of CaDiCaL under assumptions (budgets between 2e4 and 2e6
  conflicts); `k0.log`: Kissat on formula + cube.

A cube counts as refuted if any run reports UNSAT.  Final counts: first labelling 2,694 refuted,
37 undecided, 0 untried; second labelling 1,376 refuted, 375 undecided, 1,319 untried; no SAT cube.
Total solver time about 16 CPU-hours.
