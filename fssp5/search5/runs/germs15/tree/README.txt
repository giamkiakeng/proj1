Records of the tree searches for the germs of delta14c (germ15_1.txt) and delta14d (germ15_2.txt), lines 2..15
(README of search5, Section 12).  Snapshots taken while the searches run; they are updated from time to time.

ts15_j_up.cubes.gz      trisplit.py / trisplit2.py: 'U cube' = closed by the solver (CaDiCaL, conflict budget),
                        'S cube' = split; a cube is a comma-separated list of free transitions xyz=d.
ts15_j_helper.cubes.gz  trihelper.py: 'U cube' = closed by a direct CaDiCaL run from scratch, 'T cube | s' = time
                        limit reached (its children are tried instead), '#' lines are comments.
Resume a search with:  python3 ../../../src/trisplit2.py germ15_j.txt 15 --budget 25000 --workers 2 \
                           --cubes ts15_j_up.cubes --extra ts15_j_helper.cubes
