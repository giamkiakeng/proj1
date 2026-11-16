# Stable generals, lines 2..14: tree search over the half-line (Theorem 6.4 of ../../README.md)

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
- `g14_parts_1-167.txt.gz`: the same for `--first 1 --last 167`: 17,196 certified cubes; one node with a
  complete half-line is listed as not certified (cube 89).
- `g14_parts_open.txt`: the four nodes with a complete half-line, certified with a longer time limit
  (`certtree.py 14 <file with these cubes> ... --tlim 6000 --pump 14`).
- `g15s_sat_strict.txt`: the satisfiable node, refuted for the lines 2..15: strict formula of `mcopy.py` with (B1)
  and the 11 transitions of the node; LRAT proof verified by `lrat-check` and `cake_lpr`.
- `g15_sat_cube.txt`, `g15_parts_sat.txt`: the satisfiable node (its model is `../../rules/stable_generals_2-14.txt`)
  and its refutation for the lines 2..15: `certtree.py 15 g15_sat_cube.txt ... --pump 15`, three certified parts;
  $F_{15}$ has 4100 variables and 396,586 clauses, SHA-256 of its clause lines
  `7ec0e26566d2715467eb03728c0bfabec61ddf4a7caf94fee4d3d768f05549b1`.

Check of the case split (unpack the two `.gz` files first):
`covercheck.py 14 g14_parts_top.txt g14_parts_1-167.txt g14_parts_168-341.txt g14_parts_open.txt g15s_sat_strict.txt`
reports 44,517 cubes, all used, and no uncovered node. With `g15_parts_sat.txt` in place of the last file and
`covercheck.py 15` the result is the same with 44,519 cubes (the weaker statement for the lines 2..17).

The length 15 (unfinished; nothing is claimed from these files):
- `s15_D_partial.txt.gz`: the certified search of the formula $S_{15}\wedge D$ of Section 6 of the main README
  (`gcert.py 5 15 ... --b1s --b3 --wimp --strict --noghws --gstatic 1 --sgap --cellclause "24,3=G;...;14,13=G"
  --tlim 4 --nocake`), paused on 16 November after 8571 closed and 4475 split nodes, no satisfiable node. The
  file is the list that `gcert.py` continues from. A first pass of the same tree with the incremental solver
  (`hunt_run.py`, 193 subtrees) took over; its closed nodes can be certified from this list and from its own
  lists with `gcert.py --prefixfile`.
