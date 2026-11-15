# Stable generals, lines 2..14: tree search over the half-line (in progress)

- `g14_d7_prefixes.txt`: the 341 open nodes at depth 7 (`germsat.py 14 --budget 300 --maxdepth 7`), one job each.
- `g14_top.txt`: the 36 nodes closed above depth 7.
- `cubes_closed.tar.gz`: for every finished job, the nodes that the solver closed (one per line, transitions
  of the half-line in the order of the search).
- `jobs_summary.txt`: one line per finished job (nodes, solver seconds, result).

Job `j`: `germsat.py 14 --budget 3000 --prefix <line j of g14_d7_prefixes.txt> --cubes c<j>.txt`.
See `../../README.md`, Section 6.
