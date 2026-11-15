# Stable generals, lines 2..14: tree search over the half-line (in progress)

- `g14_d7_prefixes.txt`: the 341 open nodes at depth 7 (`germsat.py 14 --budget 300 --maxdepth 7`), one job each.
- `g14_top.txt`: the 36 nodes closed above depth 7.
- `cubes_closed.tar.gz`: for every finished job, the nodes that the solver closed (one per line, transitions
  of the half-line in the order of the search).
- `jobs_summary.txt`: one line per finished job (nodes, solver seconds, result).

Job `j`: `germsat.py 14 --budget 3000 --prefix <line j of g14_d7_prefixes.txt> --cubes c<j>.txt`.
See `../../README.md`, Section 6.

Certification.

- `g14_parts_top.txt`: the 36 nodes of `g14_top.txt`, each with a checked LRAT proof
  (`certtree.py 14 g14_top.txt ... --pump 14`).
- `g14_parts_168-341.txt.gz`: output of `certtree.py 14 g14_d7_prefixes.txt ... --first 168 --last 341
  --pump 14 --tlim 4`: 27,280 certified cubes. One line per certified cube:
  cube | CaDiCaL seconds | proof bytes | SHA-256 of the cube formula | SHA-256 of the proof | VERIFIED.
  The formula $F_{14}$ has 3465 variables and 324,753 clauses; SHA-256 of its clause lines
  `67957a4ce7230559cf9fc2b463d66096be3056b00b8a01001465fd2ef260f057`.
  Four nodes are listed as not certified in the lines `# cube ...`: three with a complete half-line that were not
  refuted in 4 s, and one that is satisfiable (cube 309).
- `g14_parts_open.txt`: the three nodes with a complete half-line, certified with a longer time limit.
- `g15_sat_cube.txt`, `g15_parts_sat.txt`: the satisfiable node (its model is `../../rules/stable_generals_2-14.txt`)
  and its refutation for the lines 2..15: `certtree.py 15 g15_sat_cube.txt ... --pump 15`, three certified parts;
  $F_{15}$ has 4100 variables and 396,586 clauses, SHA-256 of its clause lines
  `7ec0e26566d2715467eb03728c0bfabec61ddf4a7caf94fee4d3d768f05549b1`.
- The subtrees 1 to 167 are being certified (`g14_parts_1-167`, to come).

Check of the case split, when all files are there:
`covercheck.py 15 g14_parts_top.txt g14_parts_1-167.txt g14_parts_168-341.txt g14_parts_open.txt g15_parts_sat.txt`.
