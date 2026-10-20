# Cube trees of rcube.py (state copied during the runs)

One folder per formula (x14c = X(r16_02), x14d = X(r16_15), x16_03 = X(r16_03); see LOG.md §30):

- `<T>_d10.icnf`: the top-level cubes (march_cu -d 10). The sha256 digests of x14c_d10.icnf and x14d_d10.icnf are in ../sha256_x14.txt.
- `<T>_p1.out` (and `_p2.out`): results of icube.py on top-level cubes.
- `rc<..>.rlog`: the rcube.py log. Only complete lines are copied.
- `rc<..>_split/<path>.icnf`: the relative cubes of every split on record. A split file is copied only once its S line is in the copied log.

The formulas themselves are not stored; gfix.py rebuilds them deterministically (commands in LOG.md §30).

To resume a tree, put the formula next to these files and rerun rcube.py with the same arguments (`rcube.py <T>.cnf <T>_d10.icnf <T>_p1.out rc<..> 1e5 6`).

To certify a closed tree, run rcert.py on it. Until a tree is ALL CLOSED (rfinal.py) and certified, these files are a snapshot of a run in progress.
