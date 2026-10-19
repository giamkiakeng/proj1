#!/bin/bash
# certify.sh CNF -- re-solve an unsatisfiable formula with a proof and check it
#   kissat (binary DRAT) -> drat-trim -L (LRAT) -> lrat-check; prints the SHA-256 digests
set -e
CNF=$1; B=${CNF%.cnf}
KISSAT=${KISSAT:-/home/user/tools/kissat/build/kissat}
DRATTRIM=${DRATTRIM:-/home/user/tools/drat-trim/drat-trim}
LRATCHECK=${LRATCHECK:-/home/user/tools/drat-trim/lrat-check}
t0=$(date +%s)
set +e; $KISSAT -q "$CNF" "$B.drat"; rc=$?; set -e
[ $rc -eq 20 ] || { echo "kissat exit $rc (expected 20 = UNSAT)"; exit 1; }
t1=$(date +%s)
$DRATTRIM "$CNF" "$B.drat" -L "$B.lrat" -t 50000 | grep -E "^s |VERIFIED|ERROR" || true
t2=$(date +%s)
$LRATCHECK "$CNF" "$B.lrat" | grep -E "VERIFIED|FAIL|ERROR"
t3=$(date +%s)
echo "times: kissat $((t1-t0)) s, drat-trim $((t2-t1)) s, lrat-check $((t3-t2)) s; sizes: $(stat -c %s $B.drat) B DRAT, $(stat -c %s $B.lrat) B LRAT"
sha256sum "$CNF" "$B.lrat"
