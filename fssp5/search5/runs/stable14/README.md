# Stable generals, lines 2..14: tree search over the half-line (in progress)

- `g14_d7_prefixes.txt`: the 341 open nodes at depth 7 (`germsat.py 14 --budget 300 --maxdepth 7`), one job each.
- `g14_top.txt`: the 36 nodes closed above depth 7.
- `cubes_closed.tar.gz`: for every finished job, the nodes that the solver closed (one per line, transitions
  of the half-line in the order of the search).
- `jobs_summary.txt`: one line per finished job (nodes, solver seconds, result).

Job `j`: `germsat.py 14 --budget 3000 --prefix <line j of g14_d7_prefixes.txt> --cubes c<j>.txt`.
See `../../README.md`, Section 6.

Certification (in progress).

- `g14_parts_top.txt`: the 36 nodes of `g14_top.txt`, each with a checked LRAT proof
  (`certtree.py 14 g14_top.txt ... --pump 14`).
- `g14_parts_168-341.partial.txt.gz`: output of `certtree.py 14 g14_d7_prefixes.txt ... --first 168 --last 341
  --pump 14 --tlim 4` so far (snapshot; the run is not finished). One line per certified cube:
  cube | CaDiCaL seconds | proof bytes | SHA-256 of the cube formula | SHA-256 of the proof | VERIFIED.
  The formula $F$ has 3465 variables and 324,753 clauses; SHA-256 of its clause lines
  `67957a4ce7230559cf9fc2b463d66096be3056b00b8a01001465fd2ef260f057`.
